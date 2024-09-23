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
    
    def write_output_row(self, case_data: dict, case_id: str, case_date: str):
        """ Write case row in output sheet

        Args:
            case_data (dict): case data
                defendants (list): list of defendants
                filings (list): list of filings
                is_judgment (bool): is judgment
                is_trial (bool): is trial
                is_sale (bool): is sale
                case_status (str): case status
                attorneys (list): list of attorneys
        """
        
        print("Writing output data in output sheet...")
        
        # Fix data
        
        # None to empty string
        if case_data["case_status"] is None:
            case_data["case_status"] = ""
        
        # Fill filings with empty strings
        if len(case_data["filings"]) < 3:
            case_data["filings"] += [""] * (3 - len(case_data["filings"]))
            
        # Bool values to string
        bool_columns = ["is_judgment", "is_trial", "is_sale"]
        for column in bool_columns:
            if case_data[column]:
                case_data[column] = "Yes"
            else:
                case_data[column] = "No"
            
        # Create row data: case_id, case_date, defendants, num_defendants,
        # filing_1, filing_2, filing_3, is_judgment, is_trial, is_sale, case_status,
        # attorneys
        row_data = []
        row_data.append(case_id)
        row_data.append(case_date)
        row_data.append("\n".join(case_data["defendants"]))
        row_data.append(len(case_data["defendants"]))
        row_data += case_data["filings"]
        row_data.append(case_data["is_judgment"])
        row_data.append(case_data["is_trial"])
        row_data.append(case_data["is_sale"])
        row_data.append(case_data["case_status"])
        row_data.append("\n".join(case_data["attorneys"]))
        
        # Move to output sheet
        self.set_sheet(self.sheet_output)
        
        # Write row in output sheet
        last_row = self.get_rows_num()
        self.write_data([row_data], row=last_row + 1)
            
    def update_input_status(self, case_id: int, status: str = "scraped"):
        """ Update status of case input row

        Args:
            row (int): row number
            status (str): status
        """
        
        print(f"Updating status to '{status}'...")
        
        # Move to input sheet
        self.set_sheet(self.sheet_input)
        
        # Calculate row and write status
        cases_ids = [row["Case Number"] for row in self.input_data]
        row = cases_ids.index(case_id) + 2
        self.write_cell(status, row=row, column=6)

    