import os
from dotenv import load_dotenv
from scraper import Scraper

load_dotenv()
VAR = os.getenv("VAR")


def main():
    scraper = Scraper()
    scraper.get_case_data("2018-79939", "11/21/2018")


if __name__ == "__main__":
    main()
