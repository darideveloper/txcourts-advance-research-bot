import os
from dotenv import load_dotenv
from scraper import Scraper

load_dotenv()
VAR = os.getenv("VAR")


def main():
    scraper = Scraper()
    scraper.search_case("sample case 1", "2021-01-01")


if __name__ == "__main__":
    main()
