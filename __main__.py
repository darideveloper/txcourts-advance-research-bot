import os
from time import sleep

from dotenv import load_dotenv

from libs.scraper import Scraper
# from libs.data_manager import DataManager

# Env variables
load_dotenv()
GOOGLE_SHEET_LINK = os.getenv("GOOGLE_SHEET_LINK")
SHEET_OUTPUT = os.getenv("SHEET_OUTPUT")
USER_EMAIL = os.getenv("USER_EMAIL")
USER_PASSWORD = os.getenv("USER_PASSWORD")
WAIT_MINUTES = int(os.getenv("WAIT_MINUTES"))
SHOW_BROWSER = os.getenv("SHOW_BROWSER") == "True"
START_DATE = os.getenv("START_DATE")
END_DATE = os.getenv("END_DATE")

# Paths
current_path = os.path.dirname(os.path.abspath(__file__))
creds_path = os.path.join(current_path, "credentials.json")


def main():
    # Main workflow: scrape each ready case from the input sheet,
    # update the output sheet with the scraped data, and update the status

    # Header
    print("\n----------------------------------")
    print("TXCourts Research Bot")
    print("----------------------------------\n")

    # data_manager = DataManager(GOOGLE_SHEET_LINK, creds_path, SHEET_OUTPUT)

    # Start scraper
    scraper = Scraper(USER_EMAIL, USER_PASSWORD, not SHOW_BROWSER)
        
    print(f"Waiting {WAIT_MINUTES} minutes...")
    sleep(WAIT_MINUTES * 60)


if __name__ == "__main__":
    main()
