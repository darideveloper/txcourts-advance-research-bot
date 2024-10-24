import os
import pickle
from time import sleep
from datetime import datetime

from libs.web_scraping import WebScraping


# Paths
current_path = os.path.dirname(os.path.abspath(__file__))
cookies_path = os.path.join(current_path, "cookies.pkl")


class Scraper(WebScraping):
    
    def __init__(self, user_email: str, user_password: str, headless: bool = False):
        """ Initialize the scraper.
        
        Args:
            user_email (str): user email
            user_password (str): user password
            headless (bool): run the browser in headless mode
        """
        
        print("Starting scraper...")
        
        super().__init__(
            headless=headless,
        )
        
        # Global data
        self.home_page = "https://research.txcourts.gov/CourtRecordsSearch/#!"
        self.global_selectors = {
            "spinner": '[mdb-progress-spinner]',
            "btn_login": '#signInLink',
        }
        self.events = []
        self.parties = []
        self.user_email = user_email
        self.user_password = user_password
                
        # Setup
        self.__load_cookies__()
        self.__login__()
        self.__accept_close_session__()
        sleep(3)
        
    def __set_home_page__(self):
        """ Load home page and refresh """
        
        self.set_page(self.home_page)
        sleep(2)
        self.refresh_selenium()
    
    def __load_cookies__(self):
        """ Load cookies from local file """
        
        if not os.path.exists(cookies_path):
            return
        
        with open(cookies_path, "rb") as file:
            cookies = pickle.load(file)
        self.set_cookies(cookies)
        self.driver.refresh()
        self.refresh_selenium()
    
    def __validate_login__(self) -> bool:
        """ Validate if user is logged in
        
        Args:
            bool: True if the user is logged in, False otherwise
        """
        
        print("Validating login...")
        
        self.__set_home_page__()
        
        btn_login_btn = self.get_elems(self.global_selectors["btn_login"])
        if btn_login_btn:
            return False
        return True
    
    def __login__(self):
        """ Login with user credentials """
        
        selectors = {
            "email": '#UserName',
            "password": '#Password',
            "btn_submit": '#sign-in-btn',
        }
        
        is_logged = self.__validate_login__()
        
        # sKip if the user is already logged in
        if is_logged:
            print("User is already logged in")
            return
        
        # Login if the user is not logged in
        print("User is not logged in")
        print(f"Login with email '{self.user_email}'...")
        
        # Go to login page
        self.click_js(self.global_selectors["btn_login"])
        self.refresh_selenium()
        
        self.clear_input(selectors["email"])
        self.clear_input(selectors["password"])
        
        self.send_data(selectors["email"], self.user_email)
        self.send_data(selectors["password"], self.user_password)
        
        self.click_js(selectors["btn_submit"])
        sleep(5)
        self.refresh_selenium()
        
        self.__accept_close_session__()
        
        # Validate login (again)
        is_logged = self.__validate_login__()
        if not is_logged:
            print("ERROR: Login failed. Check credentials and try again.")
            self.kill()
            quit()
        
        # Save cookies in local file
        cookies = self.driver.get_cookies()
        with open(cookies_path, "wb") as file:
            pickle.dump(cookies, file)
    
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
        
        print(f"Searching case '{case_id}'...")
        
        # Move to new tab
        self.open_tab()
        self.switch_to_tab(0)
        self.close_tab()
        self.switch_to_tab(0)
        
        # Load research page
        search_page = f'{self.home_page}/search?q=%22{case_id}%22'
        self.set_page(search_page)
        sleep(2)
        
        # Wait to load results
        self.wait_die(selectors["loading"], 60)
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
        
        # Wait to fetch case data
        for _ in range(3):
            self.refresh_selenium()
            self.wait_die(self.global_selectors["spinner"], 60)
        sleep(5)
        self.refresh_selenium()
    
    def __save_parties__(self):
        """ Load and save parties data of the current case """
        
        selectors = {
            "wrapper": "#partiesTable",
            "parties": '#partiesTable tbody tr',
            "type": '[data-title="Type"]',
            "name": '[data-title="Name"]',
            "attorney": '[data-title="Attorneys"]'
        }
        
        print("Getting parties data...")
        
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
            "documents": '.documentsCell',
        }
        
        print("Getting events data...")
        
        self.go_bottom()
        
        # Loop events pages
        events = []
        while True:
            
            # Wait to load
            for _ in range(3):
                self.wait_die(self.global_selectors["spinner"], 60)
                sleep(1)
            self.refresh_selenium()
            
            # Loop events to get data
            events_num = len(self.get_elems(selectors["events"]))
            for event_num in range(1, events_num + 1):
                event_selector = f"{selectors['events']}:nth-child({event_num})"
                date_str = self.get_text(f"{event_selector} {selectors['data']}")
                type = self.get_text(f"{event_selector} {selectors['type']}")
                comment = self.get_text(f"{event_selector} {selectors['comment']}")
                documents = self.get_text(f"{event_selector} {selectors['documents']}")
                
                # Skip if the filing is empty
                if not type:
                    continue
                
                # Convert date to datetime in
                # format 11/21/2018
                date = datetime.strptime(date_str, "%m/%d/%Y")
                
                events.append({
                    "type": type,
                    "comment": comment,
                    "date": date,
                    "documents": documents,
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
        
        def get_event_str(event_data: dict) -> str:
            """ Return event as string in format "date - type---comment---documents",

            Args:
                event_data (dict): event data

            Returns:
                str: event as string
            """
            
            date_str = event_data["date"].strftime("%Y-%m-%d")
            documents = event_data["documents"].replace("\n", ", ")
            event_str = f"{date_str} - {event_data['type']}"
            event_str += f"---{event_data['comment']}---{documents}"
            return event_str
        
        print("\tGetting filings...")
        
        # Get type and comments from last 3 events
        events_reverse = self.events[::-1]
        filings = list(map(
            lambda event: get_event_str(event),
            events_reverse
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
        """ Get case data from the website.

        Args:
            case_id (str): case identifier
            date (str): case date (to filter if there are multiple cases)

        Returns:
            dict: case data
                defendants (list): list of defendants
                filings (list): list of filings
                is_judgment (bool): True if there is a judgment event
                is_trial (bool): True if there is a trial event
                is_sale (bool): True if there is a sale event
                case_status (str): case status
                defendants (list): list of defendants
                attorneys (list): list of attorneys
        """
        
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
        is_nonsuit = self.__get_in_events__("nonsuit")
        is_non_suit = self.__get_in_events__("non-suit")
        is_non__suit = self.__get_in_events__("non_suit")
        is_dismissal = self.__get_in_events__("dismissal")
        is_dismiss = self.__get_in_events__("dismiss")
        is_judgment = self.__get_in_events__("judgment")
        is_trial = self.__get_in_events__("trial")
        is_sale = self.__get_in_events__("sale")
        is_foreclosure = self.__get_in_events__("foreclosure")
        is_ad_litem = self.__get_in_events__("ad litem")
        is_ad__litem = self.__get_in_events__("ad-litem")
        is_litem = self.__get_in_events__("litem")
        case_status = self.__get_case_status__()
        
        nonsult_dismissal = is_nonsuit or is_non_suit or is_non__suit or \
            is_dismissal or is_dismiss
        judgment_trial_sale_foreclosure = is_judgment or is_trial or \
            is_sale or is_foreclosure
        ad_litem = is_ad_litem or is_ad__litem or is_litem
        if ad_litem:
            print(ad_litem)
        
        # Return case data
        return {
            "defendants": defendants,
            "filings": filings,
            "nonsult_dismissal": nonsult_dismissal,
            "judgment_trial_sale_foreclosure": judgment_trial_sale_foreclosure,
            "case_status": case_status,
            "attorneys": attorneys,
            "ad_litem": ad_litem,
        }