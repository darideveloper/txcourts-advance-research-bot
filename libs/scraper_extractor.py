import os
from time import sleep
from datetime import datetime

from libs.scraper_login import ScraperLogin
from libs.decorators import save_screnshot


# Paths
current_path = os.path.dirname(os.path.abspath(__file__))
cookies_path = os.path.join(current_path, "cookies.pkl")


class Scraper(ScraperLogin):

    def __init__(self, user_email: str, user_password: str, headless: bool = False,
                 debug: bool = False):
        """ Initialize the scraper.

        Args:
            user_email (str): user email
            user_password (str): user password
            headless (bool): run the browser in headless mode
            debug (bool): run the scraper in debug mode
        """

        super().__init__(
            user_email=user_email,
            user_password=user_password,
            headless=headless
        )

        # Constrol variables
        self.filters_applied_num = 0
        self.case_type = ""

        # Debug mode
        self.debug = debug

    @save_screnshot
    def __wait_loading__(self):
        """ Wait until the loading spinner is gone """
        
        selectors = {
            "loading": '[ng-if="IsLoading"]',
        }
        
        self.refresh_selenium()
        self.wait_die(selectors["loading"])

    @save_screnshot
    def __add_filter_condition__(self, value: str):
        """ Add new filter condition to the search

        Args:
            value (str): search by value (Case Type, Case Filed Date, etc.)
        """

        index = self.filters_applied_num + 1
        selector_wrapper = f'#conditions [ng-repeat]:nth-child({index + 1})'
        selectors = {
            "search_by_dropdown": f'{selector_wrapper} '
                                  'select[ng-model="condition.fieldOption"]',
            "add_btn": '#btnAddCondition',
        }

        # Click in "add" button is its not first condition
        if index > 1:
            self.click_js(selectors["add_btn"])
            self.refresh_selenium()

        # Select search by
        self.select_drop_down_text(selectors["search_by_dropdown"], value)
        self.refresh_selenium()

        # Update filters counter
        self.filters_applied_num += 1

    def __search_by_case_type__(self):
        """ Filter by specific case type
        """
        
        print("\tSearching by case type...")

        selectors = {
            "select_btn": '#selectionButton_0',
            'input': '#searchText',
            'search_btn': '#searchSelectionButton',
            'option': '#selectAllResults + div label',
            'accept_btn': '#doneSelectionButton',
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

        if self.debug:
            print("\t\tDEBUG: Using first case type")
            self.case_type = case_types[0]
        else:
            while True:
                print("Case types: ")
                for case_type_nmame in case_types:
                    case_type_index = case_types.index(case_type_nmame)
                    print(f"{case_type_index + 1}. {case_type_nmame}")

                try:
                    case_type_input = int(
                        input("Enter the number of the case type: "))
                    self.case_type = case_types[case_type_input - 1]
                except (ValueError, IndexError):
                    print("ERROR: Invalid case type")
                    continue
                break

        # Select search by "Case Type"
        self.__add_filter_condition__("Case Type")
        
        # Click in "select" button
        self.click_js(selectors["select_btn"])
        sleep(3)
        self.refresh_selenium()

        # Type value in search bar and submit
        self.send_data(selectors["input"], self.case_type)
        self.click_js(selectors["search_btn"])
        sleep(5)

        # Select first option and accept
        self.refresh_selenium()
        self.click_js(selectors["option"])
        sleep(1)
        self.click_js(selectors["accept_btn"])
        self.refresh_selenium()

    @save_screnshot
    def __search_by_dates__(self, start_date: str, end_date: str):
        """ Apply date range filter to the search

        Args:
            start_date (str): start date value in format "mm/dd/yyyy"
            end_date (str): end date value in format "mm/dd/yyyy"
        """
        
        print(f"\tSearching by dates: {start_date} - {end_date}...")
        
        selectors = {
            "start_date": 'input[ng-model="condition.fromValue"]',
            "end_date": 'input[ng-model="condition.toValue"]',
        }

        # Select search by "Case Filed Date"
        self.__add_filter_condition__("Case Filed Date")
        
        # Set values to date inputs
        self.send_data(selectors["start_date"], start_date)
        self.send_data(selectors["end_date"], end_date)
        self.refresh_selenium()

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
    def submit(self):
        """ Submit the search """

        selectors = {
            "submit_btn": '#btnSearch',
        }

        print("\tSubmitting search...")

        self.click_js(selectors["submit_btn"])
        self.__wait_loading__()

    @save_screnshot
    def filter(self, start_date: str, end_date: str):
        """ Filter cases applying the given date range and search term

        Args:
            start_date (str): start date in format "mm/dd/yyyy"
            end_date (str): end date in format "mm/dd/yyyy"
        """
        
        print("Applying filters...")

        self.__search_by_case_type__()
        self.__search_by_dates__(start_date, end_date)
        
    @save_screnshot
    def get_current_cases_data(self) -> list[dict]:
        """ Return the data of the current cases in the current results page
        
        Returns:
            list[dict]: list of cases data
                description (str): case description
                number (str): case number
                location (str): case location
                type (str): case type
                filed_date (str): case filed date
        """
        
        selectors = {
            "row": '.list-group > div',
            "active_page": '.page-item.active',
            "data": {
                "description": '.card-title',
                "number": '.card-sub-header',
                "location": '.row:last-child .col-md-2:first-child span',
                "filed_date": '.row:last-child .col-md-2:last-child > [ng-bind]',
            }
        }
        
        # Get current page and rows
        current_page = self.get_text(selectors["active_page"])
        rows_num = len(self.get_elems(selectors["row"]))
        
        # Validate rows
        if rows_num == 0:
            print("No cases found for this search.")
            return []
        
        print(f"Scraping results from page {current_page}...")
        print("\tGetting cases data...")
        
        # Get data from each row
        cases_data = []
        for index in range(rows_num):
            case_data = {}
            for selector_name, selector_value in selectors["data"].items():
                selector = f'{selectors["row"]}:nth-child({index + 1}) {selector_value}'
                case_data[selector_name] = self.get_text(selector)
            cases_data.append(case_data)
        
        return cases_data
    
    def go_next_page(self) -> bool:
        """ Go to next results page
        
        Returns:
            bool: True if there is a next page, False otherwise
        """
        
        selectors = {
            "next": 'li:not(.disabled) [ng-click="selectPage(page + 1, $event)"]'
        }
        
        print("\tGoing to next page...")
        
        # Go next page
        self.click_js(selectors["next"])
        self.__wait_loading__()
        
        # Validate if there is a next page
        next_page_btn = self.get_elems(selectors["next"])
        return bool(next_page_btn)