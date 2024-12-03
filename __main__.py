import os
from time import sleep

from dotenv import load_dotenv

from libs.scraper_extractor import Scraper
from libs.data_manager import DataManager

# Env variables
load_dotenv()
GOOGLE_SHEET_LINK = os.getenv("GOOGLE_SHEET_LINK")
SHEET_OUTPUT = os.getenv("SHEET_OUTPUT")
USER_EMAIL = os.getenv("USER_EMAIL")
USER_PASSWORD = os.getenv("USER_PASSWORD")
SHOW_BROWSER = os.getenv("SHOW_BROWSER") == "True"
START_DATE = os.getenv("START_DATE")
END_DATE = os.getenv("END_DATE")
DEBUG = os.getenv("DEBUG") == "True"

# Paths
current_path = os.path.dirname(os.path.abspath(__file__))
creds_path = os.path.join(current_path, "credentials.json")


def main():
    # Main workflow: scrape each ready case from the input sheet,
    # update the output sheet with the scraped data, and update the status

    # Header
    print("\n----------------------------------")
    print("TXCourts (Advance) Research Bot")
    print("----------------------------------\n")

    data_manager = DataManager(GOOGLE_SHEET_LINK, creds_path, SHEET_OUTPUT)

    # Start scraper
    scraper = Scraper(USER_EMAIL, USER_PASSWORD, not SHOW_BROWSER, debug=DEBUG)
    scraper.login()
    scraper.open_advanced_search()
    
    # Filter cases and submit search
    scraper.filter(START_DATE, END_DATE)
    scraper.submit()
    
    # Get cases data and save to excel
    while True:
        
        # Get cases data
        cases_data = scraper.get_current_cases_data()
        if not cases_data:
            break
        
        # Save data to excel
        data_manager.write_output_data(cases_data)
        sleep(2)
        
        # Go to the next
        has_next_page = scraper.go_next_page()
        if not has_next_page:
            print("No more pages to scrape.")
            break


if __name__ == "__main__":
    main()
