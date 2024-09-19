import os
from libs.google_sheets import SheetsManager


class DataManager(SheetsManager):
    
    def __init__(self, google_sheet_link: str, creds_path: os.PathLike,
                 sheet_input: str, sheet_output: str):
        """ Class to manage data from google sheet

        Args:
            google_sheet_link (str): editable google sheet link
            creds_path (os.PathLike): path to google json credentials file
            sheet_input (str): name of the input sheet
            sheet_output (str): name of the output sheet
        """
        
        # Save sheets and columns
        self.sheet_input = sheet_input
        self.sheet_output = sheet_output
        self.input_data = []
        
        super().__init__(google_sheet_link, creds_path)
        
    def get_input_data(self) -> list[dict[str, str]]:
        """ Get cases data from input sheet

        Returns:
            list[dict[str, str]]: list of cases data
        """
        
        print("Getting input data...")
    
        # Activate input sheet
        self.set_sheet(self.sheet_input)
        
        # Get all values from the sheet
        data = self.get_data()
        self.input_data = data
        data_ready = list(filter(lambda row: row["Status"] == "ready", data))
        
        # Filter only ready registers and required columns
        return data_ready
    
    def write_output_row(self, row_data: list[str]):
        """ Write case row in output sheet

        Args:
            row_data (list[str]): row data
        """
        pass
    
    def update_input_status(self, case_id: int, status: str):
        """ Update status of case input row

        Args:
            row (int): row number
            status (str): status
        """
        pass

    