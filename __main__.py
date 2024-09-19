import os
from dotenv import load_dotenv

from scraper import Scraper
from data_manager import DataManager

# Env variables
load_dotenv()
GOOGLE_SHEET_LINK = os.getenv("GOOGLE_SHEET_LINK")
SHEET_INPUT = os.getenv("SHEET_INPUT")
SHEET_OUTPUT = os.getenv("SHEET_OUTPUT")
USER_EMAIL = os.getenv("USER_EMAIL")
USER_PASSWORD = os.getenv("USER_PASSWORD")

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
    # scraper = Scraper(USER_EMAIL, USER_PASSWORD)

    # Scrape each case
    for case_data in input_data:

        case_number = case_data["Case Number"]
        case_date = case_data["Case Filed Date"]
        print("\n------------------")
        # case_data = scraper.get_case_data(case_number, case_date)
        case_data = {
            'defendants': ['HEIRS Of SARA ALICIA P CRUZ', 'HEIRS Of ROBERTO CRUZ'],
            'filings': [
                'Petition-----ORIGINAL PETITION TO COLLECT DELINQUENT TAXES'
            ],
            'is_judgment': False,
            'is_trial': False,
            'is_sale': False,
            'case_status': None,
            'attorneys': ['']
        }

        # Save case data in output sheet
        data_manager.write_output_row(case_data, case_number, case_date)

        # Update status in input sheet
        data_manager.update_input_status(case_data["Case Number"], "scraped")

    print("All cases have been scraped.")


if __name__ == "__main__":
    main()
