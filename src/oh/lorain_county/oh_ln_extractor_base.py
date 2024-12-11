import botocore.exceptions
from datetime import datetime
import re
from bs4 import BeautifulSoup

# Mandatory to import ExCourtCaseBase first before any other core packages.
from core.extractor.courtcase_extractor_base import ExCourtCaseBase
from oh_ln_parse_version_4 import ParseV4
from core.constants.job import LogSeverity, ExtractorErrorType, JobType
from core.exceptions import ExceptionNoRetry, ExceptionRetry, SetupError
from core.extractor.extractor_constants import (CourtcaseSourceFile, BACKOFF_START_TIME_5_SEC_IN_MINS,
                                                REFRESH_CASE_BY_CASE_NUMBER_BACKOFF_DELAY_TIME_IN_MINS, ProxyStatus,
                                                DOWNLOAD_DOCUMENT_BACKOFF_DELAY_TIME_IN_MINS)
from core.utilities.model_cache import MultiDbCache as Unresolved_Cache
from core.dals.case_utility import DalCourtcaseSourceDataPath
from core.constants.misc import Application
from core.globals.pod import get_instance_info, get_is_production_instance
from core.extractor.extractor_utils import get_datetime_obj
from core.extractor.extractor_connection import ConnectionType

# Court Site URLs
MAIN_PAGE_URL = "https://cp.onlinedockets.com/LorainCP/case_dockets/Search.aspx?PassedSearchType=4"
SEARCH_PAGE_URL = "https://cp.onlinedockets.com/LorainCP/case_dockets/Search.aspx"
CASE_DETAILS_URL = "https://cp.onlinedockets.com/LorainCP/case_dockets/Docket.aspx?CaseID="
HOME_PAGE_URL = "https://cp.onlinedockets.com/LorainCP/index.aspx"

# THRESHOLD VALUES
SEARCH_RESULT_THRESHOLD = 3


class ExLorainCountyBase(ExCourtCaseBase):
    class Meta:
        PARSE_VERSIONS = {
            4: ParseV4
        }

    def __init__(self, s3bucket_folder):
        ExCourtCaseBase.__init__(self, s3bucket_folder=s3bucket_folder)
        self.parse_obj = None
        # For date range extractor case number tracking
        self.total_case_id_to_hit = 0
        self.count_index = 0
        self.case_number_list = []
        # Regular expressions
        # Regular expression pattern to match the error message indicating that the search query produced zero records.
        # This pattern is  Used to detect if the search result page contains this message, indicating an invalid case number.       
        self.error_pattern = re.compile(r'Sorry, your query produced 0 records\. Please try again\.')
        # Regular expression to extract the case ID from a URL
        self.case_id_regex = re.compile(r'CaseID=(\d+)')
        # Regular expression to match a criminal case number format
        self.criminal_case_number_regex = re.compile(r'^\d{2}CR\d+$', re.IGNORECASE)
        # Regular expression to match words indicating a criminal case type
        self.criminal_case_type_regex = re.compile(r'crim|criminal', re.IGNORECASE) 
        # Regex pattern to extract the event target from a JavaScript function call
        self.event_target_pattern = re.compile(r"javascript:__doPostBack\('([^']*)',''\)")          
        # This regex supports both MM[-/]DD[-/]YYYY and MM[-/]DD[-/]YY format dates
        self.future_hearing_date_regex = re.compile(r'\D((?P<months>\d{1,2})[\-\/](?P<date>\d{1,2})[\-\/](?P<year>\d{2}|\d{4}))\D')
        # The determine_lorain_county_portal_regex is used in this method to check the status of the proxy health.
        self.determine_lorain_county_portal_regex = re.compile('Home', re.I)
        return
    
    def rotate_proxy(self):
        """
        This method rotates the proxy used by the extractor_connection_object.

        If the proxy count in proxy_obj_list reaches zero, a new connection is created.
        The proxy_obj_list is refreshed with all active proxies from the database.
        """
        self.extractor_connection_object.active_proxy.update_proxy_rating(ProxyStatus.DECREMENT)
        if len(self.extractor_connection_object.proxy_obj_list) <= 1:
            self.extractor_connection_object = self.create_connection(ConnectionType.URL_LIB, set_cookie=True)
            msg = f"Proxy count reaches zero, Created new connection"
            self.parselog.add("ROTATE PROXY", ExtractorErrorType.GENERIC, LogSeverity.INFO,
                              "rotate_proxy", None, msg)
        else:
            self.extractor_connection_object.set_next_proxy()
            self.extractor_connection_object.cookie = None
            self.extractor_connection_object.set_handler(set_cookie=True, do_not_use_proxy=False)    

    def fetch_case_num_to_hit_by_date_range(self, args):
        """
        This method is used to for date range extractors to get the cases filed on the given date.

        The following logic is implemented to handle the number of cases listed in the search result page based on the ddPageSize parameter:
        1. Get the main page and extract the POST parameter to obtain the search page response.
        2. Use the POST parameter from the search page to retrieve the search page result with a maximum of 1000 cases.
        Note: Sending a value above 1000 may result in an HTTP 500: Internal server error, and sending a value other than 
        the default (50) may cause the court site to state that the session has expired.
        """
        # Step 1: Get the required parameters from the job such as dates,prefixes etc to search court site.
        start_date = args.dre_start_date.strftime('%m/%d/%Y')
        end_date = args.dre_end_date.strftime('%m/%d/%Y')
        
        # Step 2: Hitting the Main Page
        retry_count = 0
        while True:
            retry_count += 1
            if retry_count > SEARCH_RESULT_THRESHOLD:
                msg = "Failed to get main page multiple times"
                self.parselog.add("Date Range", ExtractorErrorType.GENERIC, LogSeverity.INFO,
                                  "fetch_case_num_to_hit_by_date_range", None, msg)
                raise ExceptionRetry(error_message=msg, retry_time_in_mins=BACKOFF_START_TIME_5_SEC_IN_MINS)   
                 
            main_page_response = self.extractor_connection_object.get_decoded_response(MAIN_PAGE_URL)
            if not main_page_response:
                msg = "Failed to get main page"
                self.parselog.add("DATE RANGE", ExtractorErrorType.URL_ISSUE, LogSeverity.INFO,
                                "fetch_case_num_to_hit_by_date_range", None, msg)
                raise ExceptionRetry(error_message=msg, retry_time_in_mins=BACKOFF_START_TIME_5_SEC_IN_MINS)
            
            # Extract necessary values from the main page
            (handle, main_page_html) = main_page_response
            main_page_html_soup = BeautifulSoup(main_page_html, "html.parser")
            main_page_viewstate_value = main_page_html_soup.find('input', {'id': '__VIEWSTATE'})['value']
            main_page_viewstate_generator = main_page_html_soup.find('input', {'id': '__VIEWSTATEGENERATOR'})['value']
            main_page_event_validation = main_page_html_soup.find('input', {'id': '__EVENTVALIDATION'})['value']

            post_param_dict = {
                '__EVENTTARGET': '',
                '__EVENTARGUMENT': '',
                '__LASTFOCUS': '',
                '__VIEWSTATE': main_page_viewstate_value,
                '__VIEWSTATEGENERATOR': main_page_viewstate_generator,
                '__EVENTVALIDATION': main_page_event_validation,
                'txtCaseNumber': '',
                'txtFileDate_Start': f'{start_date}',
                'txtFileDate_End': f'{end_date}',
                'ddCaseTypes': '-1',
                'btnSubmit': 'Submit',
                'ddPageSize': '50',
            }
            
            # Step 3: Hitting the search page to fetch the cases between 'start_date' & 'end_date'
            retry_count = 0
            while True:
                if retry_count == SEARCH_RESULT_THRESHOLD:
                    msg = "Failed to get the search page multiple times"
                    self.parselog.add("Date Range", ExtractorErrorType.GENERIC, LogSeverity.INFO,
                                    "fetch_case_num_to_hit_by_date_range", None, msg)
                    raise ExceptionRetry(error_message=msg, retry_time_in_mins=BACKOFF_START_TIME_5_SEC_IN_MINS)
                
                search_result_page_response = self.extractor_connection_object.get_decoded_response(MAIN_PAGE_URL, data=post_param_dict)
                if not search_result_page_response:
                    retry_count += 1
                    msg = "Failed to get search page"
                    self.parselog.add("DATE RANGE", ExtractorErrorType.URL_ISSUE, LogSeverity.INFO,
                                    "fetch_case_num_to_hit_by_date_range", None, msg)  
                    self.rotate_proxy()
                    continue
                break
                              
            (_, search_result_html) = search_result_page_response
            search_details_html_soup = BeautifulSoup(search_result_html, "html.parser")
            
            # Extract post parameters for search_details_response to get 1000 cases
            search_page_viewstate_value = search_details_html_soup.find('input', {'id': '__VIEWSTATE'})['value']
            search_page_viewstate_generator_value = search_details_html_soup.find('input', {'id': '__VIEWSTATEGENERATOR'})['value']
            search_page_event_validation_value = search_details_html_soup.find('input', {'id': '__EVENTVALIDATION'})['value']

            post_param_dict = {
                '__EVENTTARGET': 'ddPageSize',
                '__EVENTARGUMENT': '',
                '__LASTFOCUS': '',
                '__VIEWSTATE': search_page_viewstate_value,
                '__VIEWSTATEGENERATOR': search_page_viewstate_generator_value,
                '__EVENTVALIDATION': search_page_event_validation_value,
                'txtCaseNumber': '',
                'txtFileDate_Start': f'{start_date}',
                'txtFileDate_End': f'{end_date}',
                'ddCaseTypes': '-1',
                'btnSubmit': 'Submit',
                'ddPageSize': '1000',
            }
            
            # step 4: Hitting the search page to fetch the 1000 cases
            retry_count = 0
            while True:
                if retry_count == SEARCH_RESULT_THRESHOLD:
                    msg = "Failed to get the search details page multiple times"
                    self.parselog.add("Date Range", ExtractorErrorType.GENERIC, LogSeverity.INFO,
                                    "fetch_case_num_to_hit_by_date_range", None, msg)
                    raise ExceptionRetry(error_message=msg, retry_time_in_mins=BACKOFF_START_TIME_5_SEC_IN_MINS) 
                        
                search_details_response = self.extractor_connection_object.get_decoded_response(MAIN_PAGE_URL, data=post_param_dict)
                if not search_details_response:
                    retry_count += 1
                    msg = "Failed to get search details page"
                    self.parselog.add("DATE RANGE", ExtractorErrorType.URL_ISSUE, LogSeverity.INFO,
                                    "fetch_case_num_to_hit_by_date_range", None, msg)      
                    self.rotate_proxy()
                    continue
                break       
                         
            (_, search_details_html) = search_details_response                      
            search_details_html_soup = BeautifulSoup(search_details_html, "html.parser")
            search_details_table =search_details_html_soup.find('table',class_= "datagrid")
            

            if search_details_table:
                # Extract case info rows, excluding header and footer rows
                case_info_rows = search_details_table.find_all('tr')
                filtered_case_info_rows = case_info_rows[2:-1]
                
                self.cases_dict = {}

                for case_info_row in filtered_case_info_rows:
                    case_id_case_number_a_tag = case_info_row.find('a', class_='blue_link')
                    case_number = case_id_case_number_a_tag.text.strip()
                    case_id_content = case_id_case_number_a_tag['href']
                    case_id_match = self.case_id_regex.search(case_id_content)
                    if case_id_match:
                        case_id = case_id_match.group(1)
                    
                    case_info_td_tags = case_info_row.find_all('td')
                    case_type = case_info_td_tags[1].text.strip()

                    # Storing case details in dictionary
                    self.cases_dict[case_number] = {'case_id': case_id, 'case_type': case_type}  
                
                # Logic to segregate cases for civil and criminal databases based on the case type code present in case numbers,
                # else identifying the type of case based on the case_type info.
                for case_number, case_info in self.cases_dict.items():
                    case_type = case_info['case_type']
                    if (self.criminal_case_number_regex.match(case_number) or self.criminal_case_type_regex.search(case_type)) and self.job_obj.args.prefix == 'CR':
                        self.case_number_list.append(case_number)
                    elif not (self.criminal_case_number_regex.match(case_number) or self.criminal_case_type_regex.search(case_type)) and self.job_obj.args.prefix == 'CV':
                        self.case_number_list.append(case_number)
   
            self.total_case_id_to_hit = len(self.case_number_list)
            msg = "Total case number's to extract:{0}, For Date Range: {1} - {2} ".format(
                self.total_case_id_to_hit, start_date, end_date)
            self.parselog.add("Date Range", ExtractorErrorType.GENERIC, LogSeverity.INFO,
                            "fetch_case_num_to_hit_by_date_range", None, msg)
            if not self.case_number_list:
                message = "No cases found in search result page from %s to %s" % (
                    start_date, end_date)
                self.parselog.add("No Case Number", ExtractorErrorType.GENERIC, LogSeverity.INFO,
                                "fetch_case_num_to_hit_by_date_range", None, message)
            return


    def get_case_id_for_county_import(self, case_number):
        """
            ******** this method is for fetching the case_id for county import extractor *********
        """
        # step 1: Hitting the Main Page            
        retry_count = 0
        while True:
            if retry_count == SEARCH_RESULT_THRESHOLD:
                msg = "Failed to get the main page multiple times"
                self.parselog.add("COUNTY IMPORT", ExtractorErrorType.GENERIC, LogSeverity.INFO,
                                  "get_case_id_for_county_import", None, msg)
                raise ExceptionRetry(error_message=msg, retry_time_in_mins=BACKOFF_START_TIME_5_SEC_IN_MINS) 
            
            main_page_response = self.extractor_connection_object.get_decoded_response(MAIN_PAGE_URL)
            if not main_page_response:
                retry_count += 1
                msg = "Failed to get main page"
                self.parselog.add("COUNTY IMPORT", ExtractorErrorType.URL_ISSUE, LogSeverity.INFO,
                                "get_case_id_for_county_import", None, msg) 
                self.rotate_proxy()
                continue
            break
        
        # Extract necessary values from the main page
        (handler, main_page_html) = main_page_response
        main_page_soup = BeautifulSoup(main_page_html, "html.parser")           
        main_page_viewstate_value = main_page_soup.find('input', {'id': '__VIEWSTATE'})['value']
        main_page_viewstate_generator = main_page_soup.find('input', {'id': '__VIEWSTATEGENERATOR'})['value']
        main_page_event_validation = main_page_soup.find('input', {'id': '__EVENTVALIDATION'})['value']

        post_param_dict = {
            '__EVENTTARGET': '',
            '__EVENTARGUMENT': '',
            '__LASTFOCUS': '',
            '__VIEWSTATE': main_page_viewstate_value,
            '__VIEWSTATEGENERATOR': main_page_viewstate_generator,
            '__EVENTVALIDATION': main_page_event_validation,
            'txtCaseNumber': f'{case_number}',
            'txtFileDate_Start': 'mm/dd/yy',
            'txtFileDate_End': 'mm/dd/yy',
            'ddCaseTypes': '-1',
            'btnSubmit': 'Submit',
            'ddPageSize': '50',
        }

        # step 2: Hitting the search page to fetch the case-details
        retry_count = 0
        while True:
            if retry_count == SEARCH_RESULT_THRESHOLD:
                msg = "Failed to get the search page multiple times"
                self.parselog.add("COUNTY IMPORT", ExtractorErrorType.URL_ISSUE, LogSeverity.INFO,
                                "get_case_id_for_county_import", None, msg)                    
                raise ExceptionRetry(error_message=msg, retry_time_in_mins=BACKOFF_START_TIME_5_SEC_IN_MINS)  
                
            search_result_page_response = self.extractor_connection_object.get_decoded_response(MAIN_PAGE_URL, data=post_param_dict)
            if not search_result_page_response:
                retry_count += 1
                msg = "Failed to get search details page"
                self.parselog.add("DATE RANGE", ExtractorErrorType.URL_ISSUE, LogSeverity.INFO,
                                "get_case_id_for_county_import", None, msg)      
                self.rotate_proxy()
                continue
            break      
              
        (_, search_result_html) = search_result_page_response
        
        # Check for specific error message
        if self.error_pattern.search(search_result_html):
            message = 'Invalid case number. Case not present in court site'
            self.parselog.add(case_number, ExtractorErrorType.INVALID_CASE, LogSeverity.INFO, "get_case_id_for_county_import", None,
                            message)
            raise ExceptionNoRetry(error_message=message, error_type=ExtractorErrorType.INVALID_CASE)     
                    
        else:
            search_details_html_soup = BeautifulSoup(search_result_html, "html.parser")  
            
            case_id_case_number_tag = search_details_html_soup.find_all('a', class_='blue_link')

            for tag in case_id_case_number_tag:
                case_number = tag.text
                content = tag['href']
                case_id_match = self.case_id_regex.search(content)
                if case_id_match:
                    case_id = case_id_match.group(1)
                    return case_id  
                   

    def parse_url_data(self, case_number):
        """
        @Args:- case_number :- case number to search in court site
        @Return:-
        @Description:-
            This method makes a hit to the court site to get case detail page, and then forward the page for
            parsing and populating data.
        """
        # Extract website_case_id based on job type
        if self.job_obj.args.job_type in (JobType.DATE_RANGE, JobType.DATE_RANGE_NEXT_GEN):
            website_case_id = self.cases_dict[case_number]['case_id']
        elif self.job_obj.args.job_type == JobType.COUNTY_IMPORT_CASE:
            website_case_id = self.get_case_id_for_county_import(case_number)
        elif self.job_obj.args.job_type == JobType.REFRESH_CASE_BY_CASE_NUMBER:
            website_case_id = self.website_case_id
        elif self.job_obj.args.job_type == JobType.CASE_EXTRACTION_HEALTH_CHECK:
            # Case health check extractor is only meant to check if court site is given case details
            # page or not. Hence, returning here as parsing case data is not required.
            return

        retry_count = 0
        while True:
            if retry_count == SEARCH_RESULT_THRESHOLD:
                msg = "Failed to get the search result page multiple times"
                self.parselog.add("Extractor", ExtractorErrorType.GENERIC, LogSeverity.INFO,
                                  "parse_url_data", None, msg)
                raise ExceptionRetry(error_message=msg, retry_time_in_mins=BACKOFF_START_TIME_5_SEC_IN_MINS)
            
            # Fetch case details HTML response              
            case_details_html_response = self.extractor_connection_object.get_decoded_response(CASE_DETAILS_URL + str(website_case_id))            
            if not case_details_html_response:
                retry_count += 1
                msg = "Failed to get search page"
                self.parselog.add("Extractor", ExtractorErrorType.URL_ISSUE, LogSeverity.INFO,
                                "parse_url_data", None, msg)      
                self.rotate_proxy()
                continue   
            break             
         
        (_, case_details_html) = case_details_html_response  
          
        # pagination logic to retrieve all available pages of docket details for a given case number.
        case_details_soup = BeautifulSoup(case_details_html, "html.parser")

        num_pages_to_iterate = None
        case_details_table = case_details_soup.find('table', {'class': 'datagrid', 'id': 'dgrdResults'})
        if case_details_table:
            td = case_details_table.find('td', {'colspan': '3'})
            if td:
                pagination_links = td.find_all('a')
                if len(pagination_links) > 0:
                    last_pagination_link = pagination_links[-1]
                    num_pages_to_iterate = last_pagination_link.get_text()

        if num_pages_to_iterate:
            # Get the first docket table for modification
            first_dockets_table = case_details_soup.find('table',  {'class': 'datagrid'})
            if first_dockets_table:
                rows = first_dockets_table.find_all('tr')
                if len(rows) >= 2:
                    # Remove the last row, which may contain pagination controls, to isolate the main docket entries
                    rows[-1].extract()    
                                            
            # Pagination Logic to get docket details
            for no_of_pages in range(int(num_pages_to_iterate) - 1):
                # Extract post parameters for the next page request
                event_target, viewstate, viewstate_generator, event_validation = self.extract_post_parameters(case_details_html)

                post_param_dict = {
                    '__EVENTTARGET': event_target,
                    '__EVENTARGUMENT': '',
                    '__LASTFOCUS': '',
                    '__VIEWSTATE': viewstate,
                    '__VIEWSTATEGENERATOR': viewstate_generator,
                    '__EVENTVALIDATION': event_validation,
                }

                # Make a POST request to fetch the next page of docket details                
                case_dockets_html_response = self.extractor_connection_object.get_decoded_response(CASE_DETAILS_URL + str(website_case_id), data=post_param_dict)
                if not case_dockets_html_response:
                    msg = "Failed to get  case_dockets page"
                    self.parselog.add("Extractor", ExtractorErrorType.URL_ISSUE, LogSeverity.INFO,
                                    "parse_url_data", None, msg)
                    raise ExceptionRetry(error_message=msg, retry_time_in_mins=BACKOFF_START_TIME_5_SEC_IN_MINS)                 
                
                # Extract necessary values from the main page
                (_, case_details_html) = case_dockets_html_response
                case_dockets_soup = BeautifulSoup(case_details_html, 'html.parser')

                # Dockets modification
                next_dockets_table = case_dockets_soup.find('table',  {'class': 'datagrid'})
                if next_dockets_table:
                    rows = next_dockets_table.find_all('tr')
                    if len(rows) >= 2:
                        rows[0].extract()
                        rows[-1].extract()                     
                        #The extract() method in BeautifulSoup is used to remove an element from a parsed document. 
                        """
                        Example:

                        fruits = ['apple', 'banana', 'orange', 'kiwi']
                        removed_fruit = fruits.pop()
                        print("Removed fruit:", removed_fruit)
                        print("Remaining fruits:", fruits)

                        Output:
                        Removed fruit: kiwi
                        Remaining fruits: ['apple', 'banana', 'orange']

                        In BeautifulSoup, the extract() method works similarly. 
                        If we have a list of rows in a table and want to remove the last row,
                        we can use extract() to remove it from the list of rows.
                        """
                        pagination_rows = next_dockets_table.find_all('tr')
                        case_details_table = case_details_soup.find('table', {'class': 'datagrid'})
                        # Append each row from pagination to the case details table
                        for row in pagination_rows:
                            case_details_table.append(row)
                                            
        case_details_html = str(case_details_soup)
        # Step 3: Saving case details in codaxtr_html directory.
        (case_details_relative_path, _) = self.save_source_data(case_number, html_buffer=case_details_html,
                                                                source_tag=CourtcaseSourceFile.CASE)

        # Step 4: Initiating case parsing and saving data
        parse_version = self.get_current_parse_version()
        self.parse_obj = self.get_parse_version_obj(parse_version)
        courtcase_model = self.parse_obj.parse(case_details_html)

        # it's attaching a file path to a model , where the details of the case were stored or retrieved from.
        courtcase_model.set_source_path(CourtcaseSourceFile.CASE, case_details_relative_path)

        # Step 5: Saving court case data into database
        self.populate_db(courtcase_model)
        return

    def extract_post_parameters(self, case_details_response):
        """
        Function to extract data parameters from the case_details_response:
        Extracts the __EVENTTARGET,__VIEWSTATE, __VIEWSTATEGENERATOR, and __EVENTVALIDATION parameters from the response HTML.
        """
        event_target = None
        viewstate = None
        viewstate_generator = None
        event_validation = None

        updated_case_details_soup = BeautifulSoup(case_details_response, 'html.parser')
        event_target_td_values = updated_case_details_soup.find('table', {'class': 'datagrid', 'id': 'dgrdResults'}).find('td', {'colspan': '3'})
        span_tag = event_target_td_values.find('span')
        if span_tag:
            anchor_tag = span_tag.find_next_sibling('a')
            if anchor_tag:
                event_target = self.event_target_pattern.search(anchor_tag['href']).group(1)                

        viewstate = updated_case_details_soup.find('input', {'id': '__VIEWSTATE'})['value']
        viewstate_generator = updated_case_details_soup.find('input', {'id': '__VIEWSTATEGENERATOR'})['value']
        event_validation = updated_case_details_soup.find('input', {'id': '__EVENTVALIDATION'})['value']

        return event_target, viewstate, viewstate_generator, event_validation

    def get_next_num_to_fetch(self, prev_tried_number):
        """
        @Args:- prev_tried_number: the previous seed number with which previously tried case number was created.
        @Return:- next seed number to try.
        @Description:-
                This method is used to support both incremental extractor and date range extractor.
                For incremental extractor, increment the seed for which case extraction has to be
                attempted based on the prev_tried_number.
                For date range extractor, get the next case number to fetch from self.case_number_list
        """
        if self.job_obj.args.job_type == JobType.INCREMENTAL:
            return prev_tried_number + 1
        else:

            if self.count_index < self.total_case_id_to_hit:
                case_number = self.case_number_list[self.count_index]
                self.count_index += 1
                return case_number
        return None

    def get_case_number_to_fetch_from_url(self, case_number):
        """
        @Args:- case_number: serial part of a case.
        @Return:- case_number: Case number used for court site search
        @Description:-
                This method generates case number to be used by incremental extractor.
                For incremental extractors, the new seed part of case number is generated by
                get_next_num_to_fetch() and here the complete case number is created using various
                job args.
        """
        if self.job_obj.args.job_type == JobType.INCREMENTAL:
            return case_number
        return case_number

    def get_case_number_from_county_import_case(self, case_number_model):
        """
        @Args:- case_number_model: extractor queue model
        @Return:- case_number
        @Description:-
                This method returns case number from extractor queue model.
                This method is used by county import extractors
        """
        case_number = case_number_model.case_number
        return case_number

    def get_case_number_for_refresh(self, case_id):
        """
        @Args:- Case_id :- case id to refresh
        @Return:- case_number :- court site case number to refresh
        @Description:-
            This method gets case number to search from case_id.
            Used by refresh case by case number extractor
        """
        # ********* fetch case_number ************
        query_to_get_case_number = "SELECT case_number FROM courtcase cc WHERE cc.id=%s"
        self.cursor.execute(query_to_get_case_number, (case_id,))
        (case_number,) = self.cursor.fetchone()
        # ********* fetching website case_id from court_case_custom_fields ***************
        query_to_get_website_case_id = "SELECT website_case_id FROM court_case_custom_fields cccf WHERE cccf.case_id=%s"
        self.cursor.execute(query_to_get_website_case_id, (case_id,))
        (website_case_id,) = self.cursor.fetchone()
        self.website_case_id = website_case_id

        return case_number

    def get_potential_transferred_case_id(self, courtcase_object):
        """
        @Args:- courtcase_object: Dalcourtcase instance for which similar case_id has to be looked for.
        @Return:- old_case_id/None
        @Description:-
            This method is used to handle transferred case scenario based on either courthouse changes or
            website case id.
        """
        case_number = courtcase_object.case_number
        old_case_id = None

        query = 'SELECT cc.id, cc.case_number, cc.unresolved_courthouse_id FROM courtcase cc inner join court_case_custom_fields' \
                ' cf ON cc.id=cf.case_id WHERE cf.website_case_id=%s'

        # some logic to get website case id associated to the case being extracted currently
        self.website_case_id = courtcase_object.extractor_courtcase_custom_fields_model.website_case_id
        website_case_id = self.website_case_id

        self.cursor.execute(query, (str(website_case_id),))
        result_tuple_list = self.cursor.fetchall()
        for result in result_tuple_list:
            (case_id, db_case_number, db_courthouse_id) = result
            unresolved_courthouse_id = \
                Unresolved_Cache.get_unresolved_courthouse_info_by_name(
                    courtcase_object.unresolved_courthouse)[0]
            if (case_number != db_case_number) or (unresolved_courthouse_id != db_courthouse_id):
                old_case_id = case_id
                self.parselog.add("FOUND TRANSFERRED CASE", None,
                                  LogSeverity.INFO, db_case_number, None, case_number)
        return old_case_id

    def is_transferred_case(self, court_case_data, db_court_case_data):
        return True

    # ************************************* Health Check Extractor Logic ***********************************************

    def get_health_check_status_of_case_extraction(self, case_id, url_timeout):
        """
        @Args:- case_id: Courtcase table id.
                url_timeout:
        @Return:- True if case detail page is received, else false
        @Description:-
                Hits court site for the given case to check if response is received to conclude if the portal is
                active or not during health check extractor run.
        """
        case_number = self.get_case_number_for_refresh(case_id)
        try:
            self.parse_url_data(case_number)
        except Exception:
            message = ' Failed to reach case details page.'
            self.parselog.add(case_id, ExtractorErrorType.GENERIC, LogSeverity.INFO,
                              "get_health_check_status_of_case_extraction", None, message)
            return False

        message = "Successfully reached Case Details Page"
        self.parselog.add(case_number, ExtractorErrorType.GENERIC, LogSeverity.INFO,
                          "get_health_check_status_of_case_extraction", None, message)
        return True

    def get_proxy_health_check_for_extractor(self):
        """
        @Args:-
        @Return:- Proxy Status
        @Description:-
                This method is used to determine proxy health.
        """
        # ------- replacing COURTSITE_URL_TO_HIT with appropriate URL and determine_our_county_portal_regex --------

        response = self.extractor_connection_object.get_decoded_response(SEARCH_PAGE_URL)
        if response:
            (_, search_page) = response
            if self.determine_lorain_county_portal_regex.search(search_page):
                return ProxyStatus.INCREMENT
        return ProxyStatus.DECREMENT

    # ******************************************************************************************************************

    # **************************************** Local parser logic ******************************************************
    def parse_local_data(self, case_number, case_id):
        """
        @Args:- case_number: Court case number
                case_id: courtcase table id
        @Return:-
        @Description:- This method fetches the court case page that has been saved locally and then parses the page.
        """
        parse_version = self.get_current_parse_version()
        self.parse_obj = self.get_parse_version_obj(parse_version)
        if self.job_obj.args.job_type == JobType.COUNTY_IMPORT_CASE:
            case_html_path_without_extension = "%s_1_1" % case_number

            if get_is_production_instance() or get_instance_info().is_local_dev or get_instance_info().application == Application.CODAXTR_REGRESSION:
                case_details_relative_path = '%s/data/%s.html' % (
                    self.s3bucket_folder, case_html_path_without_extension)

            else:
                # staging and production have separate folder in s3 bucket
                status = get_instance_info().instance_status.lower()
                case_details_relative_path = '%s/%s/data/%s.html' % (
                    status, self.s3bucket_folder, case_html_path_without_extension)

        else:
            # For Local Refresh
            case_details_relative_path = DalCourtcaseSourceDataPath.get_source_path_from_tag(case_id,
                                                                                             source_tag=CourtcaseSourceFile.CASE)

        # Initiating fetching case HTMl and parsing it
        try:
            case_details_html_response = self.parse_obj.get_file_data(case_details_relative_path)
        except (FileNotFoundError, botocore.exceptions.ClientError):
            message = 'The html associated to case number does not exist.'
            self.parselog.add(case_number, ExtractorErrorType.GENERIC, LogSeverity.INFO,
                              "parse_local_data", None, message)
            raise ExceptionNoRetry(
                error_type=ExtractorErrorType.GENERIC, error_message=message)

        # Parsing HTML page
        courtcase_model = self.parse_obj.parse(case_details_html_response)
        # Set the path of case details html
        courtcase_model.set_source_path(
            CourtcaseSourceFile.CASE, case_details_relative_path)
        self.populate_db(courtcase_model)
        return

    # ******************************************************************************************************************

    # **************************************** Schedule run extractor **************************************************
    def schedule_run(self):
        """
        @Args:-
        @Return:-
        @Description:-
            This method is used to create schedule run extractors to perform required task.
        """
        # Method not implemented yet
        return None

    # ******************************************************************************************************************

    def parse_dockets(self, courtcase_object, is_latest):
        """
        This function is used to parse the docket information
        :param courtcase_object: court case model object
        :param is_latest: flag to indicate which version to use
        :return: tuple containing docket information
        """
        (docket_string, parse_version) = self.get_relevant_docket_and_version(
            courtcase_object, is_latest)
        parse_version_object = self.get_parse_version_obj(parse_version)
        return parse_version_object.parse_dockets(courtcase_object, docket_string, is_latest)

    def parse_case_hearing_info(self, courtcase_obj, is_latest=True):
        """
        This method parse the future hearing info from future hearing table and save in case hearings table.
        """
        # Method not implemented yet
        return None

    def get_next_earliest_future_hearing_date_obj(self, courtcase_object):
        """
        @Args:- courtcase_object: Dalcourtcase instance
        @Return:- next_earliest_future_hearing: Datetime object representing next earliest future hearing/activity.
        @Description:-
            This method gets the next earliest future hearing dates from docket
        """
        # Method not implemented yet
        return None

    def get_current_parse_version(self):
        return 4

    def resolve_attorney_name(self, attorney_fullname):
        return self.parse_obj.resolve_party_name(attorney_fullname)

    def resolve_company_name(self, company_name):
        return self.parse_obj.resolve_company_name(company_name)

    def resolve_party_name(self, party_fullname):
        return self.parse_obj.resolve_party_name(party_fullname)

    def resolve_judge_name(self, judge_fullname):
        return self.parse_obj.resolve_party_name(judge_fullname)

    def resolve_party_full_address(self, full_address):
        return self.parse_obj.resolve_party_full_address(full_address)

    def resolve_attorney_full_address(self, full_address):
        return self.parse_obj.resolve_party_full_address(full_address, is_attorney=True)
