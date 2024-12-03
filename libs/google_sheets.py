import os
from time import sleep

import gspread
from oauth2client.service_account import ServiceAccountCredentials


class SheetsManager ():
    """ Class to conect to google shets and upload data"""

    def __init__(self, google_sheet_link, creds_path, sheet_name=None):
        """ Construtor of the class"""

        # Read credentials
        if not os.path.isfile(creds_path):
            raise FileNotFoundError("The credential file path is not correct")

        scope = ['https://spreadsheets.google.com/feeds',
                 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name(
            creds_path, scope)
        client = gspread.authorize(creds)

        # Conect to google sheet
        self.sheet = client.open_by_url(google_sheet_link)

        # Set the sheet 1 as worksheet
        if sheet_name:
            self.worksheet = self.sheet.worksheet(sheet_name)
        else:
            self.worksheet = self.sheet.sheet1

    def set_sheet(self, sheet_name: str):
        """ Change current working sheet

        Args:
            sheet_name (str): sheet name
        """

        self.worksheet = self.sheet.worksheet(sheet_name)

    def write_cell(self, value, row=1, column=1):
        """ Write data in specific cell
        """
        
        for _ in range(3):
            try:
                self.worksheet.update_cell(row, column, value)
            except Exception:
                print("\tError writing cell. Retrying in 1 minute seconds...")
                sleep(60)
            else:
                break

    def write_data(self, data, row=1, column=1):
        """ Write list of data in the worksheet"""

        # check if data exist
        if not data:
            print("THERE IS NO NEW INFORMATION TO WRITE IN THE FILE.")
        else:
            
            # Loop for each row of data
            for row_data in data:

                # Set the position of the next row. Omit the header
                row_index = data.index(row_data) + row
                
                cell_range = self.get_range(row_index, column, len(row_data))
                self.worksheet.update(cell_range, [row_data])

    def get_data(self):
        """ Read all records of the sheet"""

        records = self.worksheet.get_all_records()
        return records

    def get_rows_num(self) -> int:
        """ Get number of the rows in use """

        return len(self.worksheet.col_values(1))

    def get_cols_num(self) -> int:
        """ Get number of the columns in use """

        return len(self.worksheet.rows_values(1))

    def delete_row(self, row: int):
        """ Delete a row of the sheet """

        self.worksheet.delete_row(row)

    def get_range(self, row, start_col, end_col) -> str:
        """ Return the range of the cells
        
        Args:
            row (int): row number
            start_col (int): start column number
            end_col (int): end column number
            
        Returns:
            str: range of the cells
        """
        
        start_cell = gspread.utils.rowcol_to_a1(row, start_col)
        end_cell = gspread.utils.rowcol_to_a1(row, end_col)
        return f"{start_cell}:{end_cell}"