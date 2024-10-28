import os
from datetime import datetime
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
    
    def write_output_row(self, case_data: dict, case_id: str, case_date: str,
                         case_description: str, case_location: str):
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
            case_id (str): case id
            case_date (str): case date
            case_description (str): case description
            case_location (str): case location
        """
        
        print("Writing output data in output sheet...")
        
        # Initial data
        run_date = datetime.now().strftime("%m/%d/%Y")
        row_data = [
            case_description,
            case_id,
            case_location,
            case_date,
            run_date,
        ]
        
        # Fix data
        if case_data:
        
            # None to empty string
            if case_data["case_status"] is None:
                case_data["case_status"] = ""
                
            # Bool values to string
            bool_columns = [
                "nonsult_dismissal",
                "judgment_trial_sale_foreclosure",
                "ad_litem",
            ]
            for column in bool_columns:
                if case_data[column]:
                    case_data[column] = "Yes"
                else:
                    case_data[column] = "No"
                
            # Create row data: case_id, case_date, defendants, num_defendants,
            row_data.append("\n".join(case_data["defendants"]))
            row_data.append(len(case_data["defendants"]))
            row_data.append("\n".join(case_data["filings"]))
            row_data.append(case_data["nonsult_dismissal"])
            row_data.append(case_data["judgment_trial_sale_foreclosure"])
            row_data.append(case_data["ad_litem"])
            row_data.append(case_data["case_status"])
            row_data.append("\n".join(case_data["defendants_attorneys"]))
            row_data.append("\n".join(case_data["plaintiffs_attorneys"]))
            
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

    