import os
from dotenv import load_dotenv

from scraper import Scraper
from data_manager import DataManager

# Env variables
load_dotenv()
GOOGLE_SHEET_LINK = os.getenv("GOOGLE_SHEET_LINK")
SHEET_INPUT = os.getenv("SHEET_INPUT")
SHEET_OUTPUT = os.getenv("SHEET_OUTPUT")

# Paths
current_path = os.path.dirname(os.path.abspath(__file__))
creds_path = os.path.join(current_path, "credentials.json")


def main():
    # Main workflow
    
    # scraper = Scraper()
    # scraper.get_case_data("017-355108-24", "7/31/2024")
    
    data_manager = DataManager(GOOGLE_SHEET_LINK, creds_path,
                               SHEET_INPUT, SHEET_OUTPUT)
    input_data = data_manager.get_input_data()
    print()
    

if __name__ == "__main__":
    main()
