import os
import pickle
from time import sleep
from datetime import datetime

from libs.scraper_login import ScraperLogin
from libs.decorators import save_screnshot


# Paths
current_path = os.path.dirname(os.path.abspath(__file__))
cookies_path = os.path.join(current_path, "cookies.pkl")




class Scraper(ScraperLogin):

    def __init__(self, user_email: str, user_password: str, headless: bool = False):
        """ Initialize the scraper.

        Args:
            user_email (str): user email
            user_password (str): user password
            headless (bool): run the browser in headless mode
        """

        print("Starting scraper...")

        super().__init__(
            user_email=user_email,
            user_password=user_password,
            headless=headless
        )
                
        # Constrol variables
        self.filters_applied_num = 0
            
    @save_screnshot
    def __add_filter_condition__(self, value: str):
        """ Add new filter condition to the search

        Args:
            value (str): search by value (Case Type, Case Filed Date, etc.)
        """

        index = self.filters_applied_num + 1
        selector_wrapper = f'#conditions [ng-repeat]:nth-child({index + 1})'
        selectors = {
            "search_by_dropdown": f'{selector_wrapper} #advSearchFieldDropdown_0',
            "search_by_btn": f'{selector_wrapper} #selectionButton_0',
            "add_btn": '#addCondition',
        }
        
        # Click in "add" button is its not first condition
        if index == 0:
            self.click_js(selectors["add_btn"])
            self.refresh_selenium()
        
        # Select search by
        self.select_drop_down_text(selectors["search_by_dropdown"], value)
        self.click_js(selectors["search_by_btn"])
        sleep(3)
        self.refresh_selenium()
        
        # Update filters counter
        self.filters_applied_num += 1

    def __search_by_case_type__(self):
        """ Filter by specific case type
        """
        
        selectors = {
            'input': '#searchText',
            'search_btn': '#searchSelectionButton',
            'option': '#selectAllResults + div label',
            'accept_btn': '#selectAllResults',
        }
        
        # Request case type to user
        case_types = [
            "TAX DELINQUENCY",
            "QUIET TITLE",
            "FORECLOSURE - OTHER",
            "FORECLOSURE - HOME EQUITY-EXPEDITED",
            "DEBT/CONTRACT - OTHER",
            "OTHER CIVIL",
            "OTHER PROPERTY",
        ]
        
        while True:
            print("Case types: ")
            for case_type in case_types:
                case_type_index = case_types.index(case_type)
                print(f"{case_type_index + 1}. {case_type}")
                
            try:
                case_type_input = int(input("Enter the number of the case type: "))
                case_type = case_types[case_type_input - 1]
            except (ValueError, IndexError):
                print("ERROR: Invalid case type")
                continue
            break
        
        # Select search by "Case Type"
        self.__add_filter_condition__("Case Type")
        
        # Type value in search bar and submit
        self.send_data(selectors["input"], case_type)
        self.click_js(selectors["search_btn"])
        sleep(5)
        
        # Select first option and accept
        self.refresh_selenium()
        self.click_js(selectors["option"])
        sleep(1)
        self.click_js(selectors["case_type_accept_btn"])
        
    @save_screnshot
    def __search_by_dates__(self, start_date: datetime, end_date: datetime):
        """ Apply date range filter to the search

        Args:
            start_date (datetime): start date value
            end_date (datetime): end date value
        """
        
        # Convert dates to datetime and validate
        try:
            start_date_value = datetime.strptime(start_date, "%m/%d/%Y")
            end_date_value = datetime.strptime(end_date, "%m/%d/%Y")
        except ValueError:
            print("ERROR: Invalid dates format. Use 'mm/dd/yyyy'")
            self.kill()
            quit()
        
        self.__add_filter_condition__("Case Filed Date")

    @save_screnshot
    def open_advanced_search(self):
        """ Open advanced search """

        selectors = {
            "advanced_search": '#btnAdvancedSearch',
        }

        print("Opening advanced search...")

        self.click_js(selectors["advanced_search"])
        sleep(3)
        self.refresh_selenium()

    @save_screnshot
    def filter(self, start_date: str, end_date: str):
        """ Filter cases applying the given date range and search term

        Args:
            start_date (str): start date in format "mm/dd/yyyy"
            end_date (str): end date in format "mm/dd/yyyy"
        """

        self.__search_by_case_type__()
        self.__search_by_dates__(start_date, end_date)
        
            
            
