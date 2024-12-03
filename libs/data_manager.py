import os
from libs.google_sheets import SheetsManager


class DataManager(SheetsManager):

    def __init__(self, google_sheet_link: str, creds_path: os.PathLike,
                 sheet_output: str):
        """ Class to manage data from google sheet

        Args:
            google_sheet_link (str): editable google sheet link
            creds_path (os.PathLike): path to google json credentials file
            sheet_output (str): name of the output sheet
        """

        # Connect to google sheet
        super().__init__(google_sheet_link, creds_path)
        
        # Save output sheet name
        self.sheet_output = sheet_output

        # Move to output sheet
        self.set_sheet(self.sheet_output)

    def write_output_data(self, cases_data: list[dict]):
        """ Write case row in output sheet

        Args:
            list[dict]: list of cases data
                description (str): case description
                number (str): case number
                location (str): case location
                type (str): case type
                filed_date (str): case filed date
        """
        
        print("\tWriting data in output sheet...")

        rows = []
        for case_data in cases_data:
            row = [
                case_data["description"],
                case_data["number"],
                case_data["location"],
                case_data["type"],
                case_data["filed_date"],
            ]
            rows.append(row)

        # Write row in output sheet
        last_row = self.get_rows_num()
        self.write_data(rows, row=last_row + 1)
