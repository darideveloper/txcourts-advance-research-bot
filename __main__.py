import os
from time import sleep

from dotenv import load_dotenv

from libs.scraper import Scraper
from libs.data_manager import DataManager

# Env variables
load_dotenv()
GOOGLE_SHEET_LINK = os.getenv("GOOGLE_SHEET_LINK")
SHEET_INPUT = os.getenv("SHEET_INPUT")
SHEET_OUTPUT = os.getenv("SHEET_OUTPUT")
USER_EMAIL = os.getenv("USER_EMAIL")
USER_PASSWORD = os.getenv("USER_PASSWORD")
WAIT_MINUTES = int(os.getenv("WAIT_MINUTES"))

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

    data_manager = DataManager(GOOGLE_SHEET_LINK, creds_path,
                               SHEET_INPUT, SHEET_OUTPUT)
    input_data = data_manager.get_input_data()

    # Start scraper
    scraper = Scraper(USER_EMAIL, USER_PASSWORD)

    # Scrape each case
    for case_data in input_data:

        case_number = case_data["Case Number"]
        case_date = case_data["Case Filed Date"]
        case_description = case_data["Case Description"]
        case_location = case_data["Case Location"]
        
        print("\n------------------")
        
        try:
            case_data = scraper.get_case_data(case_number, case_date)
        except Exception as e:
            print("Error scraping case. Check logs for more info.")
            
            # Save error log
            error_log_path = os.path.join(current_path, "error.txt")
            with open(error_log_path, "w") as f:
                f.write(f"Error scraping case '{case_number}': {e}\n")
                
            # Save chrome screenshot
            screenshot_path = os.path.join(current_path, "error.png")
            scraper.screenshot(screenshot_path)
            
            case_data = None
        
        # Catch no data
        if case_data:
            status = "scraped"
            
            # Save case data in output sheet
            data_manager.write_output_row(case_data, case_number, case_date,
                                          case_description, case_location)
        else:
            status = "no data"
            print(f"No data found for case '{case_number}'.")
            
            # Save only case number and date
            data_manager.write_output_row({}, case_number, case_date,
                                          case_description, case_location)

        # Update status in input sheet
        data_manager.update_input_status(case_number, status=status)
        print(f"Case '{case_number}' done.")
        
        # Wait time
        print(f"Waiting {WAIT_MINUTES} minutes...")
        sleep(WAIT_MINUTES * 60)

    print("All cases have been scraped.")


if __name__ == "__main__":
    main()
