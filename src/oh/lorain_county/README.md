
**State: Ohio (OH)

**Courts: Lorain 

**Website Url: https://cp.onlinedockets.com/LorainCP/index.aspx

                                        **IMPORTANT NOTE**

    [1] 

 
************************************************************************************************************************
                                                    **Extraction:**
************************************************************************************************************************

**Date Range Extractor**
    
    Step 1: Gather extractor start and end date and create the required post paraneter.

    Step 2: Hit the URL - SEARCH_PAGE_URL with the necessary post parameter constructed using the start and end date.
    
    Step 3: The result from above hit is the search result page which holds all cases to search in court site. The case 
            numbers displayed here are saved in self.case_number_list

    Step 4: For each case found in search result page, hit the URL CASE_PAGE_URL with necessary post/get parameters 
            and get case page.

    Step 5: Parse the case response obtained from court site and save the data parsed into database.

**Refresh by case number Extractor**

    Step 1: For the case_id obtained from extractor queue entry, query out the case number and other details if required.
    
    Step 2: Given the case number, hit the URL - CASE_PAGE_URL to get case response from court site.

    Step 3: Parse the response obtained from court site and save the data into database.

**County import Extractor**

    Step 1: Get the case number and other relevant information related to the case being county imported from extractor
            queue.

    Step 2: For the case number obtained, hit the URL CASE_PAGE_URL with necessary post/get data to obtain the case page
            response for current case from court site.

    Step 3: Parse the response obtained from court site and save the data into database. 

**Case Extraction Health Check Extractor**

    Step 1: Follow step 1 & 2 of "County import Extractor" for the case number given at random by framework.

    Step 2: If case page is successfully obtained, then health check extractor is passed, else it failes.

**Proxy Health Check Extractor**

    Step 1: For the proxy set by framework, hit the URL HOME_PAGE_URL/SEARCH_PAGE_URL.

    Step 2: Validate if the response obtained is correct or not by means of regex.

    Step 3: If valid page is obtained, return health check as passed else failed.

