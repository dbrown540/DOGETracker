from typing import Dict, List, Tuple, Optional
import concurrent.futures
import logging

import requests
from bs4 import BeautifulSoup
import pandas as pd

from src.utils.decorators import api_retry
from settings import REQUEST_TIMEOUT

class FPDS_Scraper:
    def __init__(self, df):
        self.df = df

    @property
    def headers(self) -> Dict[str, str]:
        """
        Constructs and returns the headers required for making API requests.
        Returns:
            Dict[str, str]: A dictionary containing the headers, including the 
            "Content-Type" set to "application/json".
        """
        return {
            "Content-Type": "application/json"
        }

    @api_retry
    def get_fpds_html(self, link):
        """
        Sends a GET request to the specified FPDS link and returns the response details
        including the source HTML.
        Args:
            link (str): The URL to send the GET request to.
        Returns:
            dict: A dictionary containing the following keys:
                - "ok" (bool): Indicates whether the request was successful (True) or not (False).
                - "status" (int): The HTTP status code of the response.
                - "data" (str): The HTML content of the response as a string.
                - "headers" (dict): A dictionary of the response headers.
        """
        response = requests.get(
            url=link,
            headers=self.headers,
            timeout=REQUEST_TIMEOUT
        )
        return {
            "ok": response.ok,
            "status": response.status_code,
            "data": response.text,
            "headers": dict(response.headers)
        }

    def extract_contracting_office_agency_name(self, html_content: str) -> str:
        """
        Extracts the Contracting Office Agency Name from the FPDS HTML content.
        
        Args:
            html_content (str): The HTML content of the FPDS page.
            
        Returns:
            str: The extracted Contracting Office Agency Name, or an empty string if not found.
        """
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            # Find the input with title "Contracting Office Agency Name"
            agency_input = soup.find('input', {'title': 'Contracting Office Agency Name'})
            
            # Check if the element exists and has a value attribute
            if agency_input and agency_input.get('value'):
                return agency_input.get('value')
            return ""
        except Exception as e:
            # Log the error and return empty string in case of any exception
            print(f"Error extracting contracting office agency name: {e}")
            return ""
    
    def extract_contracting_office_name(self, html_content: str) -> str:
        """
        Extracts the Contracting Office Name from the FPDS HTML content.
        
        Args:
            html_content (str): The HTML content of the FPDS page.
            
        Returns:
            str: The extracted Contracting Office Name, or an empty string if not found.
        """
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            # Find the input with title "Contracting Office Name"
            office_input = soup.find('input', {'title': 'Contracting Office Name'})
            
            # Check if the element exists and has a value attribute
            if office_input and office_input.get('value'):
                return office_input.get('value')
            return ""
        except Exception as e:
            # Log the error and return empty string in case of any exception
            print(f"Error extracting contracting office name: {e}")
            return ""
    
    def extract_naics_code(self, html_content: str) -> str:
        """
        Extracts the NAICS (North American Industry Classification System) Code 
        from the FPDS HTML content.
        
        Args:
            html_content (str): The HTML content of the FPDS page.
            
        Returns:
            str: The extracted NAICS Code, or an empty string if not found.
        """
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            # Find the input with title "Principal North American Industry Classification System Code"
            naics_input = soup.find('input', {
                'title': 'Principal North American Industry Classification System Code'
            })
            
            # Check if the element exists and has a value attribute
            if naics_input and naics_input.get('value'):
                return naics_input.get('value')
            return ""
        except Exception as e:
            # Log the error and return empty string in case of any exception
            print(f"Error extracting NAICS code: {e}")
            return ""
    
    def extract_psc_code(self, html_content: str) -> str:
        """
        Extracts the PSC (Product or Service Code) from the FPDS HTML content.
        
        Args:
            html_content (str): The HTML content of the FPDS page.
            
        Returns:
            str: The extracted PSC Code, or an empty string if not found.
        """
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            # Find the input with title "Product Or Service Code"
            psc_input = soup.find('input', {'title': 'Product Or Service Code'})
            
            # Check if the element exists and has a value attribute
            if psc_input and psc_input.get('value'):
                return psc_input.get('value')
            return ""
        except Exception as e:
            # Log the error and return empty string in case of any exception
            print(f"Error extracting PSC code: {e}")
            return ""

    def process_row(self, row_data: Tuple[int, pd.Series]) -> Dict:
        """
        Process a single dataframe row to extract FPDS data.
        
        Args:
            row_data: Tuple containing (index, row) from DataFrame
            
        Returns:
            Dict containing the extracted data and row index
        """
        index, row = row_data
        result = {
            "index": index,
            "buying_org_2": "",
            "buying_org_3": "",
            "naics": "",
            "psc": ""
        }
        
        fpds_link = row.get("FPDS Link")
        if not fpds_link:
            return result
            
        try:
            response = self.get_fpds_html(fpds_link)
            
            if not response["ok"]:
                logging.warning(f"Failed to retrieve data from FPDS link: {fpds_link}")
                return result
                
            html_content = response["data"]
            
            # Extract all required fields
            result["buying_org_2"] = self.extract_contracting_office_agency_name(html_content)
            result["buying_org_3"] = self.extract_contracting_office_name(html_content)
            result["naics"] = self.extract_naics_code(html_content)
            result["psc"] = self.extract_psc_code(html_content)
            
            logging.info(f"Successfully processed row {index}")
            return result
            
        except Exception as e:
            logging.error(f"Error processing row {index}: {e}")
            return result
            
    def process_rows_concurrently(self, max_workers: int = 10) -> List[Dict]:
        """
        Process multiple rows concurrently to extract FPDS data.
        
        Args:
            max_workers: Maximum number of worker threads to use
            
        Returns:
            List of dictionaries containing the extracted data
        """
        results = []
        
        # Get rows with FPDS links
        rows_with_links = [(i, row) for i, row in self.df.iterrows() if row.get("FPDS Link")]
        
        if not rows_with_links:
            logging.info("No FPDS links found in the dataframe")
            return results
            
        logging.info(f"Processing {len(rows_with_links)} FPDS links with {max_workers} workers")
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_row = {executor.submit(self.process_row, row_data): row_data for row_data in rows_with_links}
            
            for future in concurrent.futures.as_completed(future_to_row):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    row_data = future_to_row[future]
                    logging.error(f"Exception processing row {row_data[0]}: {e}")
        
        return results
        
    def update_dataframe_with_results(self, results: List[Dict]) -> None:
        """
        Update the dataframe with the results from concurrent processing.
        
        Args:
            results: List of dictionaries containing the extracted data
        """
        for result in results:
            index = result["index"]
            self.df.at[index, "Buying Org 2"] = result["buying_org_2"]
            self.df.at[index, "Buying Org 3"] = result["buying_org_3"]
            self.df.at[index, "NAICS"] = result["naics"]
            self.df.at[index, "PSC"] = result["psc"]
