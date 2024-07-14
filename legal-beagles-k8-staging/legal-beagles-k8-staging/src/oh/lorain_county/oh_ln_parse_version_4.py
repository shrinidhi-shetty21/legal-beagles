import json
import re
from bs4 import BeautifulSoup as bsoup4
from oh_ln_parse_base import LorainCountyParseBase
from core.extractor import extractor_globals, extractor_utils
from core.extractor.extractor_utils import get_datetime_obj
from core.extractor.extractor_constants import DocketTag
from core.extractor.extractor_utils import ExStructureDocketEntryList
from core.constants.case import JUDGE, ATTORNEY
from core.constants.case import REPRESENTATION_TYPE_REGEX
from core.constants.misc import S3Bucket

# Default courthouse string for unresolved cases
DEFAULT_COURTHOUSE = "LORAIN COUNTY COURT OF COMMON PLEAS -"

# This variable is used to represent unknown or unspecified values in our program.
UNKNOWN = "UNKNOWN"

# Define docket_tag strings as global variables
DOCKET = "DOCKET"
BOND = "BOND"
BOND_SURCHARGE = "BOND SURCHARGE (IDSF 2937.22)"
SENTENCE = "SENTENCE"
SENTENCING = "SENTENCING"
FINANCIAL = "FINANCIAL"
FEES = "FEES"
SUMMON = "SUMMON"
SUMMONS = "SUMMONS"
WARRANT = "WARRANT"

# Dictionary key for storing docket tables
DOCKET_ENTRY_KEY = "DOCKET"



class ParseV4(LorainCountyParseBase):
    def __init__(self, case_id=None):
        super(ParseV4, self).__init__(case_id)
        self.newline_tab_carriage_return_regex = re.compile(r'\>[\n\r\t\s]+\<')
        # Regex pattern used to remove multiple spaces
        self.multi_space_regex = re.compile(r'\s\s+')
        # Regex pattern used to match various attorney and law firm suffixes and titles
        self.attorney_law_firm_name_regex = re.compile(r'(?P<attorney_firm>\sPA$|\sP\sA$|\sLLP$|P\.C\.$|'
                                                       r'\sPC$|\sP\.\sC\.$|\sLLC$|\sLAW\s|\sLAW$|\sPLLC$|'
                                                       r'\,PLLC$|\sP\s*L$|\s&\s|\sPLC$|\sP\.L\.C\.$|'
                                                       r'\sP\sL\sC$|LAW\s*OFFICES|OFFICE|LAW\s*OFCS?|LAW\s*OFF|'
                                                       r'\sAND\s|CO[\s,\.\;]+LPA|DEFENDER[\s,\.\;]+OFC|\s&$)', re.I)
        # Regex pattern to extract the website case ID from the form action element
        self.website_case_id_pattern = re.compile(r'CaseID=(\d+)')
        # Regex pattern to extract attorney information
        self.attorney_info_pattern = re.compile(r'<span.*?>(.*?)</span>', re.DOTALL)
        # Regex pattern to match "SE', PRO" (SELF_REPRESENTATION_TYPE_REGEX)
        # self.se_pro_regex = re.compile(r"SE',\s*PRO")
        self.representation_type_regex = re.compile(r"\bPRO\s+SE\b|SE',\s*PRO", flags=re.IGNORECASE)
        # Regex pattern to match invalid terms within parentheses followed by <br> tags
        self.remove_invalid_term_within_parantheses_regex = re.compile(r'\([^)]*\)<br\s*/?>')   
        # Regex pattern to match various unwanted parts in party addess
        self.unwanted_prefix_pattern = re.compile(r'^[A-Za-z\s,.\-]*\d{1,2}/\d{1,2}/\d{2,4}<br>', flags=re.MULTILINE)   
        # Regex pattern for matching and segregating state and zip code   
        self.state_zip_pattern = re.compile(r'([A-Z\s]+)(?: (\d{5})(\d{4})?)?$')
        # Regex pattern for address detection in attorney_address_fields
        self.address_pattern = re.compile(r'[A-Za-z\s]+,\s[A-Za-z]+\s\d{5}(?:-\d{4})?$')
        # Regex pattern to match  city, state and zipcode in attorney_address_fields  
        self.city_state_zip_pattern = re.compile(r'[A-Z]+,\s+[A-Z]{2,}\s+\d{5,9}', re.I)      

    # ******************************************* Parsing case Data ****************************************************

    def parse(self, case_details_html):
        """
        Parses basic information, participants information, and returns the courtcase object associated with the case.
        Args:
        - case_details_html: Case details HTML page.
        Returns:
        - DalCourtcase object.
        """
        # Create bsoup object
        case_details_soup = bsoup4(case_details_html, "html.parser")

        # Retrieving the case IDs from the website's form tag
        form_action_element = case_details_soup.form['action']
        match = self.website_case_id_pattern.search(form_action_element)
        website_case_id = match.group(1)

        case_details_html = self.get_cleaned_html_page(case_details_html)

        # ************************************ Parse Basic Case Information ********************************************
        courtcase_object = self.parse_basic_case_details(case_details_soup, website_case_id)

        # ***************************************** Parse Participant Information **************************************
        self.parse_participants(courtcase_object, case_details_soup)

        # ************************************** Saving Docket details *************************************************
        self.set_docket_dict(courtcase_object, case_details_soup)
        
        # Check if a open_balance_info table exists,
        open_balance_info_table_exists = case_details_soup.find('table', id='DG_Payment') is not None

        # If the table exists, then Parse Source Page Data JSON
        if open_balance_info_table_exists:
            self.parse_source_page_json(courtcase_object, case_details_soup)

        return courtcase_object

    def get_structured_party_addition_data_json(self, party_info_tr_tag):
        """
        This method generates structured party additional information dictionary similar to sourcePageData json
        Structure is as follows:
        { "pageName": "partyInformation", "additionalSourceData":
            { "rawOrderedDataArray": [
                { "lbl": key0, "val": value0, "ord": 0, "childArray": [] },
                { "lbl": key1, "val": value1, "ord": 1, "childArray": [] },
                                      :
                                      :
                                      :

                { "lbl": keyN, "val": valueN, "ord": N , "childArray": [] }
        ]
        }
        """
        structured_party_addition_data_dict = {"pageName": "partyInformation",
                                               "additionalSourceData": {
                                                   "rawOrderedDataArray": []
                                               }}

        # Extract data from party_info_tr_tag
        party_info_list = party_info_tr_tag.find_all('td')
        
        # Extract birth date
        birth_date_key = 'Birth Date'
        birth_date_value = party_info_list[1].text.strip()
        birth_date_element = {"lbl": birth_date_key, "val": str(birth_date_value), "ord": 0, "childArray": []}
        structured_party_addition_data_dict["additionalSourceData"]["rawOrderedDataArray"].append(birth_date_element)

        # Extract full address and split it to get organization name
        party_address_with_br_tags = party_info_list[3].get_text(separator="<br>")
        party_address_split_with_delimiter = party_address_with_br_tags.replace("<br>", "<<>>")
        split_address = party_address_split_with_delimiter.split("<<>>")

        if len(split_address) == 4:
            organization_name = split_address[0]
            organization_name_key = 'Organization Name'
            organization_name_element = {"lbl": organization_name_key, "val": str(organization_name), "ord": 1, "childArray": []}
            structured_party_addition_data_dict["additionalSourceData"]["rawOrderedDataArray"].append(organization_name_element)

        return structured_party_addition_data_dict

    def parse_source_page_json(self, courtcase_object, case_details_soup):
        """
        This method parses the open balance information of criminal cases from the source page into a JSON format.
        Args:
        - courtcase_object: The court case object to which the parsed information will be added.
        - case_details_soup: The BeautifulSoup object representing the case details page.
        """
        source_page_data_model = courtcase_object.extractor_courtcase_custom_fields_model.source_page_data_model
        source_page_data_model.pageName = "caseDetails"

        first_order_source_page_data_json = source_page_data_model.rowOrderDataArray.append(label="", value="Open Balance Information")

        party_id = 2
        while True:
            party_name_span = case_details_soup.find('span', id=f'DG_Payment_ctl{party_id:02d}_lblName')
            if party_name_span is not None:
                party_name = party_name_span.text
                second_order_source_page_data_json = first_order_source_page_data_json.append(label="", value=party_name)

                party_info_span = case_details_soup.find(id=f'DG_Payment_ctl{party_id:02d}_lblName')
                if party_info_span:
                    parent_td = party_info_span.parent
                    parent_tr = parent_td.parent
                    open_balance_info_divs = parent_tr.find_all('td')[1].find_all('div')
                    for div in open_balance_info_divs:
                        span_elements = div.find_all('span')
                        if len(span_elements) == 2:
                            label = span_elements[0].text.strip()
                            value = span_elements[1].text.strip()
                            amount_value = re.sub(self.multi_space_regex, ' ', value)
                            second_order_source_page_data_json.append(label=label, value=amount_value)

                party_id += 1
            else:
                break

        if source_page_data_model.rowOrderDataArray:
            source_page_data_model.set_source_page_data_json()

    def parse_basic_case_details(self, case_details_soup, website_case_id):
        """
        @Args:- case_details_soup: BeautifulSoup object case details html page
        @Return:- courtcase_object: DalCourtcase instance
        @Description:-
                This method parses case basic details to create courtcase_object       
        """
        # -- Parsing Basic Case Information --
        # getting case_name,Filling_date,case number and unresolved courthouse
        case_name = [td.get_text(strip=True) for td in case_details_soup.select('span#lblCaption')][0]
        Filling_date = [td.get_text(strip=True) for td in case_details_soup.select('span#lblDateFiled')][0]
        unresolved_case_type = [td.get_text(strip=True) for td in case_details_soup.select('span#lblDescription')][0]
        default_courthouse = DEFAULT_COURTHOUSE       
        case_number = [td.get_text(strip=True) for td in case_details_soup.select('span#lblCaseNumber')][0]
        case_type_code = case_number[2:4]
        unresolved_courthouse = f"{default_courthouse} {case_type_code}"

        # Create courtcase_object
        extractor_object = extractor_globals.get_extractor_object()
        courtcase_object = extractor_object.get_courtcase_object(case_number, unresolved_courthouse)
        courtcase_object.extractor_courtcase_custom_fields_model.website_case_id = website_case_id

        # set court case number,filing date,court case number,case name,unresolved case type,unresolved case status
        courtcase_object.filing_date = Filling_date
        courtcase_object.case_number = case_number
        courtcase_object.case_name = case_name
        courtcase_object.unresolved_case_type = unresolved_case_type
        unknown_value = UNKNOWN
        courtcase_object.unresolved_case_status = unknown_value

        self.parse_participants(courtcase_object, case_details_soup) 
        return courtcase_object
    
    def process_attorney_block(self, block):
        """
        Processes each attorney block to extract and clean the attorney information.

        Args:
        - block (str): The HTML block containing attorney details, separated by <br> tags.

        Returns:
        - str: A string containing the attorney information, cleaned and properly formatted.
        """
        # Split the block by <br> to get individual lines of information
        lines = block.split('<br>')

        # Initialize split_index to None; this will be used to determine where the address starts
        split_index = None

        # Iterate over the lines with an enumerator to get both index and line content
        for iterator, line in enumerate(lines):
            # If a line matches the address pattern, set split_index to the current index and break the loop
            if self.address_pattern.search(line.strip()):
                split_index = iterator
                break

        # If an address pattern was found (split_index is not None)
        if split_index is not None:
            # Join the lines up to and including the address line, stripping extra spaces
            attorney_info = '<br>'.join([line.strip() for line in lines[:split_index + 1]])
        else:
            # If no address pattern was found, return the entire block as it is
            attorney_info = block

        return attorney_info


    def parse_participants(self, courtcase_object, case_details_soup):
        """
        @Args:- courtcase_obj: DalCourtcase instance
                case_details_soup: Case details soup
        @Return:-
        @Description:-
            This method parses party-attorney and judge details present in case page.

        @Methods to use:
        courtcase_object.set_party(party_name, party_type)
        ourtcase_object.set_attorney(attorney_name, attorney_type)
        courtcase_object.set_judge(judge_name, judge_type)
        """
        parties_table = case_details_soup.find('table', {'class': 'datagrid_parties'})
        if parties_table:
            party_list = parties_table.find_all('tr')

            for party in party_list[1:]:
                party_model = None
                attorney_model = None

                party_info_list = party.find_all('td')
                party_name = party_info_list[0].text.strip()
                party_type = party_info_list[2].text.strip()
                party_full_address_with_br_tag = party_info_list[3].get_text(separator="<br>")

                party_full_address_with_br_tag = self.unwanted_prefix_pattern.sub('', party_full_address_with_br_tag)
  
                party_full_address_with_br_tag = self.remove_invalid_term_within_parantheses_regex.sub('', party_full_address_with_br_tag).strip()
                """ 
                Logic to Handle invalid Street Address :(NAME UNKNOWN)
                The above regex removes the matched pattern from the string, which in this example 
                
                example:
                Original String:
                (NAME UNKNOWN)
                2730 GLENMORE DR.
                WESTLAKE, OHIO 44145

                Cleaned String:
                2730 GLENMORE DR.
                WESTLAKE, OHIO 44145

                After Address Handling:
                Street Address 1: 2730 GLENMORE DR.
                Street Address 2: 
                City: WESTLAKE
                State: OHIO
                Zip Code: 44145
                """
                party_full_address = party_full_address_with_br_tag.replace("<br>", "<<>>")
                
                party_model = courtcase_object.set_party(party_name, party_type)
                # Case numbers: 98CA007085, 24CA012127
                # Ensure the full address is not just an invalid symbol (',') or empty.
                # If it contains valid address information, set the full address for the party
                if party_full_address.strip() != ',' :
                    party_model.set_full_address(party_full_address)

                # Get the structured additional data for party
                structured_party_addition_data_dict = self.get_structured_party_addition_data_json(party)
                # Validate and set additional data for party.
                party_model.extractor_party_custom_fields_model.set_party_additional_data(structured_party_addition_data_dict)
                
                # ------------------------- parsing attorney details present in case page --------------------------------------
                attorney_info = party_info_list[4].find('span')
                if attorney_info is None:
                    continue
                elif attorney_info.get_text(strip=True) == "":
                    continue
                else:
                    # (Used the compiled regex pattern to extract attorney information text from span tag)
                    attorney_info_text = self.attorney_info_pattern.search(str(attorney_info)).group(1)

                    # Split the content by double line breaks to separate each attorney's information
                    elements = attorney_info_text.split('<br/><br/>')

                    # List to store the final processed_attorney_information
                    processed_attorney_information = []  

                    # Iterate over elements
                    iterator = 0
                    while iterator < len(elements):
                        current_element = elements[iterator].strip()

                        if len(current_element.split('<br/>')) > 1:
                            # Check if the current element matches the city, state ,zipcode pattern
                            if self.city_state_zip_pattern.search(current_element):
                                processed_attorney_information.append(current_element)
                            else:
                                # If no match, append the current element to the next element
                                if iterator + 1 < len(elements):
                                    elements[iterator + 1] = current_element + ' <br> ' + elements[iterator + 1]
                                else:
                                    processed_attorney_information.append(current_element)
                        else:
                            processed_attorney_information.append(current_element)

                        iterator += 1

                    attorney_blocks = processed_attorney_information  

                    # Process each attorney block and store the results in a list
                    split_attorney_info = [self.process_attorney_block(block) for block in attorney_blocks if block.strip()]                  
                     
                    # Iterate over the entries to get structured attorney address
                    for entry in split_attorney_info:
                
                        # Remove any leading or trailing <br/> tags
                        entry = re.sub(r'^(<br\s*/>)+|(<br\s*/>)+$', '', entry)
    
                        # Initialize variables
                        address_variable = ''
                        firm_name = ''
                        
                        # Split each entry by '<br/>' to separate name and address
                        parts = entry.split('<br/>')
                        parts = [part.strip() for part in parts if part.strip()]  # Clean empty and whitespace-only parts
                        attorney_name = parts[0] if parts else ''
                      
                        address_list = []
                        address_list.append('\n'.join(parts[1:]))
                        address_string = ", ".join([f'{address.strip()}' for address in address_list])
                        address_modified = address_string.replace('\n', ' <<>> ').replace('<br>', ' <<>> ')
                        address_parts = address_modified.split(' <<>> ')
    
                        # Check if law firm exists 
                        for name in address_parts:
                            if self.attorney_law_firm_name_regex.search(name):
                                firm_name = name
                                address_parts.remove(name)
                                break                        
                        
                        #-------------------------------------------------------------------------------------------------
                        if address_parts and not any(char.isdigit() for char in address_parts[0]):
                            """
                            This condition checks if the first part of the address_parts list does not contain any digits.
                            If this condition is met, it considers it as a [additional info]-:(attorney_title) or (company_name): 
                            and assigns the remaining parts (if any) to address_variable.
                            If the condition is not met, it assigns the entire entry to address_variable.
                            """        
                            additional_info = address_parts[0]
                            if len(address_parts) >= 2:
                                address_variable = '<<>>'.join(address_parts[1:])
            
                        else:
                            address_variable = '<<>>'.join(address_parts)                                  
                        #-------------------------------------------------------------------------------------------------                          

                        if attorney_name:
                            if (REPRESENTATION_TYPE_REGEX.search(attorney_name) or self.representation_type_regex.search(attorney_name)):
                                attorney_name = 'PRO SE'
                                if party_model:
                                    party_model.set_representation_type(attorney_name)
                            else:
                                attorney_model = courtcase_object.set_attorney(attorney_name, ATTORNEY)
                                if attorney_model:
                                    if address_variable:
                                        attorney_model.set_full_address(address_variable)
                                    attorney_model.set_lawfirm(firm_name)
                                    self.resolve_party_full_address(address_variable, True)
                                else:
                                    print("Failed to set attorney for:",attorney_name)

                        if party_model and attorney_model:
                            party_model.set_attorney(attorney_model)

        # -- Parsing Judge Information --
        case_details_table = case_details_soup.find('table', {'class': 'docket'})
        if case_details_table:
            judge_row = case_details_table.find('td', string='Judge:')
            if judge_row:
                judge_name = judge_row.find_next_sibling('td').text.strip()

        courtcase_object.set_judge(judge_name, JUDGE)
        return  

    def set_docket_dict(self, courtcase_object, case_details_soup):
        """
        @Args:- courtcase_object: DalCourtCase instance
                case_details_soup: bsoup object of case page
        @Return:-
        @Description:-
                This method sets docket dict for the given case
        """
        # ------- saving the docket tables and the tag in dictionary ------
        docket_dict = dict()
        dockets_table = case_details_soup.find('table',  {'class': 'datagrid'})
        docket_dict[DOCKET_ENTRY_KEY] = str(dockets_table)
        # populate docket_dict accordingly
        courtcase_object.docket = json.dumps(docket_dict)
        return

    # ******************************************** Parsing Dockets *****************************************************
    def parse_dockets(self, courtcase_object, docket_string, is_latest):
        """
        @Args:- courtcase_object: DalCourtCase instance
                docket_string: HTML table tag containing entire docket as string
                is_latest: Boolean value if the current docket string is recent one or not.
        @Return:- List of Tuple: summary_info_tuple_list
        @Description:-
                This method parses all dockets and returns a list containing structured summary tuple.
        """
        summary_info_tuple_list = []
        order_number = 0
        if not docket_string:
            return summary_info_tuple_list

        docket_dict = json.loads(docket_string)

        # logic to parse dockets
        if DOCKET_ENTRY_KEY in docket_dict:
            docket_table_soup = bsoup4(docket_dict[DOCKET_ENTRY_KEY], "html.parser")
            if docket_table_soup:
                docket_table_rows = docket_table_soup.find_all('tr')
                for row in docket_table_rows[1:]:
                    cols = row.find_all('td')
                    if len(cols) == 3:
                        date = cols[0].text.strip()
                        type_of_docket = cols[1].text.strip()
                        description = cols[2].text.strip()

                        docket_type = self.get_docket_tag(type_of_docket)

                        if docket_type == BOND:

                            structured_docket_list = ExStructureDocketEntryList()
                            structured_docket_list.append('Type', type_of_docket)

                            structured_docket_list.append('Description', description)
                            action_date = extractor_utils.get_datetime_obj(date)
                            summary_info_tuple_list.append(
                                (action_date, structured_docket_list, None, None, order_number, None, None, DocketTag.BOND, None, None, None, None, None, None, None))
                            order_number = order_number + 1

                        elif docket_type == DOCKET:

                            structured_docket_list = ExStructureDocketEntryList()
                            structured_docket_list.append('Type', type_of_docket)

                            structured_docket_list.append('Description', description)
                            action_date = extractor_utils.get_datetime_obj(date)
                            summary_info_tuple_list.append(
                                (action_date, structured_docket_list, None, None, order_number, None, None, DocketTag.DOCKET, None, None, None, None, None, None, None))
                            order_number = order_number + 1

                        elif docket_type == SENTENCE:

                            structured_docket_list = ExStructureDocketEntryList()
                            structured_docket_list.append('Type', type_of_docket)

                            structured_docket_list.append('Description', description)
                            action_date = extractor_utils.get_datetime_obj(date)
                            summary_info_tuple_list.append(
                                (action_date, structured_docket_list, None, None, order_number, None, None, DocketTag.SENTENCE, None, None, None, None, None, None, None))
                            order_number = order_number + 1

                        elif docket_type == FINANCIAL:

                            structured_docket_list = ExStructureDocketEntryList()
                            structured_docket_list.append('Type', type_of_docket)

                            structured_docket_list.append('Description', description)
                            action_date = extractor_utils.get_datetime_obj(date)
                            summary_info_tuple_list.append((action_date, structured_docket_list, None, None, order_number,
                                                           None, None, DocketTag.FINANCIAL, None, None, None, None, None, None, None))
                            order_number = order_number + 1

                        elif docket_type == SUMMON:

                            structured_docket_list = ExStructureDocketEntryList()
                            structured_docket_list.append('Type', type_of_docket)

                            structured_docket_list.append('Description', description)
                            action_date = extractor_utils.get_datetime_obj(date)
                            summary_info_tuple_list.append(
                                (action_date, structured_docket_list, None, None, order_number, None, None, DocketTag.SUMMON, None, None, None, None, None, None, None))
                            order_number = order_number + 1

                        elif docket_type == WARRANT:

                            structured_docket_list = ExStructureDocketEntryList()
                            structured_docket_list.append('Type', type_of_docket)

                            structured_docket_list.append('Description', description)
                            action_date = extractor_utils.get_datetime_obj(date)
                            summary_info_tuple_list.append(
                                (action_date, structured_docket_list, None, None, order_number, None, None, DocketTag.WARRANT, None, None, None, None, None, None, None))
                            order_number = order_number + 1                            

        return summary_info_tuple_list

    def get_docket_tag(self, type_of_docket):
        """
        This method get_docket_tag takes a docket_type parameter and returns a corresponding tag based on predefined lists.
        """
        bond_tag_list = [BOND, BOND_SURCHARGE]
        sentence_tag_list = [SENTENCING]
        fees_tag_list = [FEES]
        summon_tag_list = [SUMMON,SUMMONS]
        warrant_tag_list = [WARRANT]

        if type_of_docket in bond_tag_list:
            return BOND
        elif type_of_docket in sentence_tag_list:
            return SENTENCE
        elif type_of_docket in fees_tag_list:
            return FINANCIAL
        elif type_of_docket in summon_tag_list:
            return SUMMON
        elif type_of_docket in warrant_tag_list:
            return WARRANT        
        else:
            return DOCKET

    def parse_case_hearing_info(self, courtcase_object, docket_string):
        """
        @Args:- courtcase_object: Dalcourtcase instance
                    docket_string
        @Return:- hearing_info_docket_tuple_list: tuple list for case hearing v2
        @Description:-
                This method returns hearing info tuple list for hearing v2.
        """
        # Method not implemented yet
        return None

    # ********************************************* Resolving Address **************************************************

    def resolve_party_full_address(self, party_full_address, is_attorney=True):
        """
        @Args:- party_full_address: string representing full address
                is_attorney: Boolean value indicating if address resolution is for attorney of party.
                Useful if street address 1 for attorney is being checked if it is a law firm
        @Return:- List of Tuple holding resolved address
        @Description:-
                This method is used to resolve both attorney address and party address.
                step-1) Write a logic to get resolved address  
                step-2) Split the address into street address and city, state, zip code   
        """
        first_street_address = None
        second_street_address = None
        city = None
        state = None
        zip_code = None

        split_address = party_full_address.split("<<>>")

        if len(split_address) == 2:
            first_street_address = split_address[0]
            second_street_address = ""

        elif len(split_address) == 3:
            first_street_address = split_address[0]
            second_street_address = split_address[1]
            
        elif len(split_address) == 4:
            # Address likely includes organization name as additional info
            # This format might be relevant to use the get_structured_party_addition_data_json method.                      
            first_street_address = split_address[1]
            second_street_address = split_address[2]            

        # Split the address into city, state, zip code
        city_state_parts = split_address[-1].split(", ")
        if len(city_state_parts) >= 2:
            city = city_state_parts[0]
            state_zip_parts = city_state_parts[1]         
            # Match the state and zip code using the regex pattern
            # (The regex pattern is to make the zip code part optional, meaning if there's no zip code in the input, it won't cause an error.)
            match = self.state_zip_pattern.match(state_zip_parts)
            if match:
                # Extract the state
                state = match.group(1).strip()
                # Extract the 5-digit zip code if available
                zip_code = match.group(2) if match.group(2) else None
                # Extract the 4-digit extension if available
                zip4 = match.group(3) if match.group(3) else None
                if zip_code and zip4:
                    # Combine the 5-digit zip code and 4-digit extension into zip+4 format
                    zip_code = f"{zip_code}-{zip4}"                     

        return first_street_address, second_street_address, city, state, zip_code


    # ******************************************************************************************************************

    def get_cleaned_html_page(self, case_details_html):
        """
        @Args:- case_details_html: string holding case details page
        @Return:- Cleaned html string
        @Description:-
            This method cleans the html page from garbage characters that are an obstacle for bsoup
        """
        case_details_html = self.newline_tab_carriage_return_regex.sub('><', case_details_html)
        case_details_html = self.multi_space_regex.sub(' ', case_details_html)
        return case_details_html
