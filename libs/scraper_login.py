import os
import pickle
from time import sleep

from libs.web_scraping import WebScraping
from libs.decorators import save_screnshot


# Paths
current_path = os.path.dirname(os.path.abspath(__file__))
cookies_path = os.path.join(current_path, "cookies.pkl")


class ScraperLogin(WebScraping):

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
        self.user_email = user_email
        self.user_password = user_password

        # Setup
        self.__load_cookies__()
        self.__accept_close_session__()
        sleep(3)
        
        # Constrol variables
        self.filters_applied_num = 0

    @save_screnshot
    def __set_home_page__(self):
        """ Load home page and refresh """

        self.set_page(self.home_page)
        sleep(4)
        self.refresh_selenium()

    @save_screnshot
    def __load_cookies__(self):
        """ Load cookies from local file """

        if not os.path.exists(cookies_path):
            return

        with open(cookies_path, "rb") as file:
            cookies = pickle.load(file)
        self.set_cookies(cookies)
        self.driver.refresh()
        self.refresh_selenium()

    @save_screnshot
    def __validate_login__(self) -> bool:
        """ Validate if user is logged in

        Args:
            bool: True if the user is logged in, False otherwise
        """

        print("\tValidating login...")

        self.__set_home_page__()

        btn_login_btn = self.get_elems(self.global_selectors["btn_login"])
        if btn_login_btn:
            return False
        return True

    @save_screnshot
    def __accept_close_session__(self):
        """ Accept message for closing session (if exists) """

        selectors = {
            "btn_close": '[ng-click="endOtherSessions()"]'
        }

        print("\tLooking for close session message")

        btn_close_elem = self.get_elems(selectors["btn_close"])
        if btn_close_elem:
            self.click(selectors["btn_close"])
            self.refresh_selenium()
            
    @save_screnshot
    def login(self):
        """ Login with user credentials """

        selectors = {
            "email": '#UserName',
            "password": '#Password',
            "btn_submit": '#sign-in-btn',
        }

        is_logged = self.__validate_login__()

        # sKip if the user is already logged in
        if is_logged:
            print("\tUser is already logged in")
            return

        # Login if the user is not logged in
        print("\tUser is not logged in")
        print(f"\tLogin with email '{self.user_email}'...")

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
            print("\tERROR: Login failed. Check credentials and try again.")
            self.kill()
            quit()

        # Save cookies in local file
        cookies = self.driver.get_cookies()
        with open(cookies_path, "wb") as file:
            pickle.dump(cookies, file)

            
