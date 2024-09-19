from time import sleep
from datetime import datetime
from libs.web_scraping import WebScraping


class Scraper(WebScraping):
    
    def __init__(self, headless: bool = False):
        super().__init__(
            auto_chrome_folder_windows=True,
            headless=headless,
            start_killing=True,
        )
        
        self.home_page = "https://research.txcourts.gov/CourtRecordsSearch/#!"
        
        # Global data
        self.global_selectors = {
            "spinner": '[mdb-progress-spinner]',
        }
        self.events = []
        self.parties = []
        
        # Setup
        self.set_page(self.home_page)
        sleep(2)
        self.refresh_selenium()
        self.__validate_login__()
        self.__accept_close_session__()
        sleep(3)
        
    def __validate_login__(self):
        """ Validate if the user is logged in """
        
        selectors = {
            "btn_login": '#signInLink'
        }
        
        btn_login_btn = self.get_elems(selectors["btn_login"])
        if btn_login_btn:
            print(">>> ERROR: User is not logged in")
            print("Open chrome and login to the website manually")
            quit()
    
    def __accept_close_session__(self):
        """ Accept message for closing session (if exists) """
        
        selectors = {
            "btn_close": '[ng-click="endOtherSessions()"]'
        }
        
        print("Looking for close session message")
        
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
            "table_rows": '#searchResultsTable tbody tr',
            "case_link": 'a',
            "case_date": 'td:nth-child(6)',
        }
        
        print(f"\nSearching case '{case_id}'...")
        
        # Load research page
        search_page = f"{self.home_page}/search?q={case_id}"
        self.set_page(search_page)
        sleep(2)
        
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
        
        print("Loading case page...")
        
        # Open case page
        self.set_page(case_link)
        self.refresh_selenium()
        
        # Wait to fetch case data
        for _ in range(2):
            self.wait_die(self.global_selectors["spinner"], 20)
    
    def __save_parties__(self):
        """ Load and save parties data of the current case """
        
        selectors = {
            "wrapper": "#partiesTable",
            "parties": '#partiesTable tbody tr',
            "type": '[data-title="Type"]',
            "name": '[data-title="Name"]',
            "attorney": '[data-title="Attorneys"]'
        }
        
        print("Saving parties data...")
        
        # Delete comments in section
        self.delete_comments_js(selectors["wrapper"])
        
        # Save parties data
        parties = []
        parties_num = len(self.get_elems(selectors["parties"]))
        for party_num in range(1, parties_num + 1):
            party_selector = f"{selectors['parties']}:nth-child({party_num})"
            party_type = self.get_text(f"{party_selector} {selectors['type']}").lower()
            party_name = self.get_text(f"{party_selector} {selectors['name']}")
            party_attorney = self.get_text(f"{party_selector} {selectors['attorney']}")
            
            # Save parties
            parties.append({
                "type": party_type,
                "name": party_name,
                "attorney": party_attorney,
            })
                
        self.parties = parties
    
    def __save_events__(self):
        """ Load and save events data of the current case """
        
        selectors = {
            "btn_events_date": '[ng-click="onFilingsSortChange()"]',
            "events": '#caseDetailsFilingsTable tr',
            "data": 'td:nth-child(1)',
            "type": 'td:nth-child(3)',
            "comment": 'td:nth-child(4)',
            "btn_next": '.page-item:not(.disabled) '
                        '[ng-click="selectPage(page + 1, $event)"]',
        }
        
        print("Saving events data...")
        
        self.go_bottom()
        
        # Loop events pages
        events = []
        while True:
            
            # Wait to load
            self.wait_die(self.global_selectors["spinner"], 20)
            sleep(2)
            self.refresh_selenium()
            
            # Loop events to get data
            events_num = len(self.get_elems(selectors["events"]))
            for event_num in range(1, events_num + 1):
                event_selector = f"{selectors['events']}:nth-child({event_num})"
                event_date_str = self.get_text(f"{event_selector} {selectors['data']}")
                event_type = self.get_text(f"{event_selector} {selectors['type']}")
                event_comment = self.get_text(f"{event_selector} {selectors['comment']}")
                
                # Skip if the filing is empty
                if not event_type:
                    continue
                
                # Convert date to datetime in
                # format 11/21/2018
                event_date = datetime.strptime(event_date_str, "%m/%d/%Y")
                
                events.append({
                    "type": event_type,
                    "comment": event_comment,
                    "date": event_date,
                })
                
            # Go next page
            next_elem = self.get_elems(selectors["btn_next"])
            if not next_elem:
                break
            
            self.click_js(selectors["btn_next"])
            
        self.events = events
    
    def __get_defendants_attorneys__(self) -> tuple[list, list]:
        """ Get defendants of the case from parties daya

        Returns:
            list: list of defendants (usually two)
        """
        
        print("\tGetting defendants attorneys...")
        
        # Get defendants names and attorneys
        defendants_rows = list(filter(
            lambda party: "defendant" in party["type"].lower(),
            self.parties
        ))
        defendants_names = list(map(
            lambda party: party["name"],
            defendants_rows
        ))
        defendants_attorneys = list(map(
            lambda party: party["attorney"],
            defendants_rows
        ))
        
        # Remove duplicates
        defendants_names = list(set(defendants_names))
        defendants_attorneys = list(set(defendants_attorneys))
                
        return defendants_names, defendants_attorneys
    
    def __get_filings__(self) -> list[str]:
        """ Get last three filings/events of the case.
        
        returns:
            list[str]: list of filings/events names for the case
        """
        
        print("\tGetting filings...")
        
        # Get type and comments from last 3 events
        filings = list(map(
            lambda event: f"{event['type']}-----{event['comment']}",
            self.events[-3:]
        ))
        
        return filings
    
    def __get_in_events__(self, keyword: str) -> bool:
        """ Validate if specific keyword is in types or event comments
        
        Args:
            keyword (str): keyword to search

        Returns:
            bool: True if there is a match, False otherwise
        """
        
        print(f"\tChecking if there is a '{keyword}' events...")
        
        comments = list(map(lambda event: event["comment"], self.events))
        types = list(map(lambda event: event["type"], self.events))
        in_comments = any(keyword in comment.lower() for comment in comments)
        in_types = any(keyword in type.lower() for type in types)
        return in_comments or in_types
    
    def __get_case_status__(self) -> str:
        """ Return case status.

        Returns:
            str: Case status value. Return None if the status is not
                found.
        """
        
        selectors = {
            "status": '[ng-bind="::case.status"]'
        }
        
        print("\tGetting case status...")
        
        status_elem = self.get_elems(selectors["status"])
        if not status_elem:
            return None
        
        return self.get_text(selectors["status"])
    
    def get_case_data(self, case_id: str, date: str) -> dict:
        
        # Search case
        case_link = self.__search_case__(case_id, date)
        if not case_link:
            print(f"Case '{case_id}' not found")
            return None
        self.__load_case_page__(case_link)
        
        # Get case data
        self.__save_parties__()
        self.__save_events__()
        defendants, attorneys = self.__get_defendants_attorneys__()
        filings = self.__get_filings__()
        is_judgment = self.__get_in_events__("judgment")
        is_trial = self.__get_in_events__("trial")
        is_sale = self.__get_in_events__("sale")
        case_status = self.__get_case_status__()
        
        # Return case data
        return {
            "defendants": defendants,
            "filings": filings,
            "is_judgment": is_judgment,
            "is_trial": is_trial,
            "is_sale": is_sale,
            "case_status": case_status,
            "defendants": defendants,
            "attorneys": attorneys,
        }