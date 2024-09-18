from time import sleep
from libs.web_scraping import WebScraping


class Scraper(WebScraping):
    
    def __init__(self, headless: bool = False):
        super().__init__(
            auto_chrome_folder_windows=True,
            headless=headless,
            start_killing=True,
        )
        
        self.home_page = "https://research.txcourts.gov/CourtRecordsSearch/#!"
        
        # Setup
        self.__accept_close_session__()
        sleep(3)
    
    def __accept_close_session__(self):
        """ Accept message for closing session (if exists) """
        
        selectors = {
            "btn_close": '[ng-click="endOtherSessions()"]'
        }
        
        print("Looking for close session message")
        
        self.set_page(self.home_page)
        sleep(2)
        self.refresh_selenium()
        
        btn_close_elem = self.get_elems(selectors["btn_close"])
        if btn_close_elem:
            self.click(selectors["btn_close"])
            self.refresh_selenium()
    
    def __search_case__(self, case_id: str, date: str) -> bool:
        """ Search case in the website.

        Args:
            case_id (str): case identifier
            date (str): case date (to filter if there are multiple cases
                with the same identifier)
        
        Returns:
            bool: True if the case is found, False otherwise
        """
        
        selectors = {
            "loading": '[ng-if="IsLoading"]',
            "table_rows": '#searchResultsTable tr',
            "case_link": 'a',
            "case_date": 'td:nth-child(6)',
        }
        
        print(f"\tSearching case '{case_id}'...")
        
        # Load research page
        search_page = f"{self.home_page}/search?q={case_id}"
        self.set_page(search_page)
        self.refresh_selenium()
        
        # Wait to load results
        self.wait_die(selectors["loading"], 20)
        self.delete_comments_js()
        self.refresh_selenium()
        
        # Find the correct case
        case_link = None
        rows_num = len(self.get_elems(selectors["table_rows"]))
        for row_num in range(1, rows_num + 1):
            row_selector = f"{selectors['table_rows']}:nth-child({row_num})"
            case_link_selector = f"{row_selector} {selectors['case_link']}"
            case_date_selector = f"{row_selector} {selectors['case_date']}"
            
            # Validate date only if there are more than one case
            case_date = self.get_text(case_date_selector)
            if rows_num > 1 and date != case_date:
                continue
            
            case_link = self.get_attrib(case_link_selector, "href")
        
        # End when the case is found
        return case_link
    
    def __load_case_page__(self, case_link: str) -> bool:
        """ Load case page and wait to load.
        
        Args:
            case_link (str): case link
        """
        
        selectors = {
            "loading": '[mdb-progress-spinner]'
        }
        
        print("Loading case page...")
        
        # Open case page
        self.set_page(case_link)
        self.refresh_selenium()
        
        # Wait to fetch case data
        self.wait_die(selectors["loading"], 20)
        self.refresh_selenium()
        
        # Delete html comments
        self.delete_comments_js()
    
    def __get_defendants__(self) -> list[str]:
        """ Get defendants of the case.

        Returns:
            list: list of defendants (usually two)
        """
        
        selectors = {
            "parties": '#partiesTable tr',
            "type": '[data-title="Type"]',
            "name": '[data-title="Name"]',
        }
        
        # Loop partines to get defendants
        defendants = []
        parties_num = len(self.get_elems(selectors["parties"]))
        for party_num in range(1, parties_num + 1):
            party_selector = f"{selectors['parties']}:nth-child({party_num})"
            party_type = self.get_text(f"{party_selector} {selectors['type']}").lower()
            party_name = self.get_text(f"{party_selector} {selectors['name']}")
            
            # Check if the party is a defendant
            if "defendant" in party_type:
                defendants.append(party_name)
                
        return defendants
    
    def __get_filings__(self) -> list[str]:
        """ Get last three filings of the case.
        
        returns:
            list[str]: list of filings for the case
        """
    
    def __get_is_judgment__(self) -> bool:
        """ Validate if there is a judgment in the case.

        Returns:
            bool: True if there is a judgment, False otherwise
        """
    
    def __get_is_trial__(self) -> bool:
        """ Validate if there is a trial in the case.

        Returns:
            bool: True if there is a trial, False otherwise
        """
    
    def __get_is_sale__(self) -> bool:
        """ Validate if there is a sale in the case.

        Returns:
            bool: True if there is a sale, False otherwise
        """
    
    def __get_case_status__(self) -> str:
        """ Return case status.

        Returns:
            str: Case status value. Return None if the status is not
                found.
        """
    
    def __get_defendants_attorneys__(self) -> list:
        """ Get defendants' attorneys.

        Returns:
            list: list of attorneys for the defendants
        """
    
    def get_case_data(self, case_id: str, date: str) -> dict:
        
        # Search case
        case_link = self.__search_case__(case_id, date)
        if not case_link:
            print(f"Case '{case_id}' not found")
            return None
        self.__load_case_page__(case_link)
        
        # Get case data
        print("Getting case data...")
        defendants = self.__get_defendants__()
        filings = self.__get_filings__()
        is_judgment = self.__get_is_judgment__()
        is_trial = self.__get_is_trial__()
        is_sale = self.__get_is_sale__()
        case_status = self.__get_case_status__()
        defendants_attorneys = self.__get_defendants_attorneys__()
        
        # Return case data
        return {
            "defendants": defendants,
            "filings": filings,
            "is_judgment": is_judgment,
            "is_trial": is_trial,
            "is_sale": is_sale,
            "case_status": case_status,
            "defendants_attorneys": defendants_attorneys,
        }