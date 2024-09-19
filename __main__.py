import os
from dotenv import load_dotenv
from scraper import Scraper

load_dotenv()
VAR = os.getenv("VAR")


def main():
    scraper = Scraper()
    scraper.get_case_data("017-355108-24", "7/31/2024")
    

if __name__ == "__main__":
    main()
