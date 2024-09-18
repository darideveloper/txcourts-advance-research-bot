from libs.web_scraping import WebScraping


class Scraper(WebScraping):
    
    def __init__(self, headless: bool = False):
        super().__init__(
            auto_chrome_folder_windows=True,
            headless=headless,
            start_killing=True,
        )
        
    def __search_case__(self, case_id: str, date: str):
        """ Search case in the website.

        Args:
            case_id (str): case identifier
            date (str): case date (to filter if there are multiple cases
                with the same identifier)
        """
    
    def __get_defendants__(self) -> list[str]:
        """ Get defendants of the case.

        Returns:
            list: list of defendants (usually two)
        """
    
    def __get_filings__(self) -> list[str]:
        """ Get last three filings of the case.
        
        returns:
            list[str]: list of filings for the case
        """
    
    def __get_is_judgment__(self) -> bool:
        """ Validate if there is a judgment in the case.

        Returns:
            bool: True if there is a judgment, False otherwise
        """
    
    def __get_is_trial__(self) -> bool:
        """ Validate if there is a trial in the case.

        Returns:
            bool: True if there is a trial, False otherwise
        """
    
    def __get_is_sale__(self) -> bool:
        """ Validate if there is a sale in the case.

        Returns:
            bool: True if there is a sale, False otherwise
        """
    
    def __get_case_status__(self) -> str:
        """ Return case status.

        Returns:
            str: Case status value. Return None if the status is not
                found.
        """
    
    def __get_defendants_attorneys__(self) -> list:
        """ Get defendants' attorneys.

        Returns:
            list: list of attorneys for the defendants
        """
    
    def get_case_data(self, case_id: str, date: str) -> dict:
        
        # Search case
        self.__search_case__(case_id, date)
        
        # Get case data
        defendants = self.__get_defendants__()
        filings = self.__get_filings__()
        is_judgment = self.__get_is_judgment__()
        is_trial = self.__get_is_trial__()
        is_sale = self.__get_is_sale__()
        case_status = self.__get_case_status__()
        defendants_attorneys = self.__get_defendants_attorneys__()
        
        # Return case data
        return {
            "defendants": defendants,
            "filings": filings,
            "is_judgment": is_judgment,
            "is_trial": is_trial,
            "is_sale": is_sale,
            "case_status": case_status,
            "defendants_attorneys": defendants_attorneys,
        }