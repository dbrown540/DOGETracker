import logging
import math
import os
from typing import List

import pandas as pd

from src.utils.logger import initialize_logger
from src.scrapers.doge_api import DogeAPIScraper
from src.scrapers.fpds_scraper import FPDS_Scraper
from src.models.api_models import IRawDogeContracts
from src.utils.writer import sanitize_contract, write_contracts_to_csv
from src.utils.helpers import count_rows_in_csv
from src.processors.data_cleaner import DOGEApiDataCleaner
from settings import (
    RESULTS_PER_PAGE,
    DOGE_API_FIELDS,
    RAW_DOGE_DATA_CSV_PATH
)

initialize_logger(level="INFO")
logging.getLogger(__name__)

def main():
    logging.info("The DOGE scraper has started!")

    # Create DOGE API Scraper object
    doge_scraper = DogeAPIScraper()

    # Send the pilot request to get the total number of entries
    total_canceled_contracts = doge_scraper.get_total_results()

    # Now let's see if we even need to run the API requests.
    # We can do that by checking to see if our csv file exists.
    # If the csv file exists, let's check if the number of rows equals the total contracts
    # Otherwise, just continue.
    number_of_csv_rows = count_rows_in_csv(RAW_DOGE_DATA_CSV_PATH)
    logging.info("There are %d CSV rows.", number_of_csv_rows)

    if number_of_csv_rows != total_canceled_contracts:
        # Now that we have the total number of canceled contracts, let's figure out
        # how many pages we need to iterate
        if os.path.exists(RAW_DOGE_DATA_CSV_PATH):
            os.remove(RAW_DOGE_DATA_CSV_PATH)
            logging.info("Removed the old DOGE data. Refreshing now...")

        number_of_doge_pages = math.ceil(total_canceled_contracts / RESULTS_PER_PAGE)
        logging.info("We need to scrape %d pages from the DOGE API.", number_of_doge_pages)

        # Now let's loop through the pages, send an API request, and parse the data as we receive it
        processed_contracts = 0
        for page_data in doge_scraper.iter_pages(total_pages=number_of_doge_pages):
            if not page_data:
                continue
            contracts: List[IRawDogeContracts] = page_data.get("result", {}).get("contracts", [])
            logging.info("Retrieved %d contracts from this page!", len(contracts))

            # Parse the contract data and append to a CSV file.
            sanitized_contracts = [
                sanitize_contract(contract, DOGE_API_FIELDS)
                for contract in contracts
            ]

            write_contracts_to_csv(
                sanitized_contracts, 
                file_path=RAW_DOGE_DATA_CSV_PATH,
                fieldnames=DOGE_API_FIELDS
            )
            processed_contracts += len(sanitized_contracts)
            logging.info(
                "Processed %d/%d contracts!", 
                processed_contracts,
                total_canceled_contracts
            )

    else:
        logging.info("DOGE API data is already up to date!")


    # Now we should validate the data
    # So check that the columns match and handle any blanks.
    raw_doge_data_cleaner = DOGEApiDataCleaner()
    cleaned_doge_df = raw_doge_data_cleaner.clean_doge_data()

    # Now we are ready to evaluate the FPDS site
    # We will only scrape FPDS for rows that have a valid link!

    # First we should add columns to the cleaned_doge_df to have it ready for new data
    new_columns = [
        "Buying Org 2",
        "Buying Org 3",
        "NAICS",
        "PSC",
    ]

    # Add the new columns to the DataFrame with empty values
    for column in new_columns:
        cleaned_doge_df[column] = ""
        
    # Create FPDS scraper instance
    fpds_scraper = FPDS_Scraper(cleaned_doge_df)
    
    # Process all rows concurrently (can adjust max_workers as needed)
    logging.info("Starting concurrent processing of FPDS links")
    results = fpds_scraper.process_rows_concurrently(max_workers=20)
    
    # Update the dataframe with the results
    fpds_scraper.update_dataframe_with_results(results)
    
    logging.info("FPDS data extraction completed")
    
    # Reorganize columns before saving
    logging.info("Reorganizing columns for better readability")
    
    # Define logical column order
    column_order = [
        # Contract identification
        "PIID",
        
        # Organization information (grouped together)
        "Buying Org 1",
        "Buying Org 2",
        "Buying Org 3",
        
        # Classification codes (grouped together)
        "NAICS",
        "PSC",
        
        # Financial information (grouped together)
        "Total Contract Value (TCV)",
        "Savings",
        
        # Dates
        "Deleted On"
    ]
    
    # Ensure we only include columns that exist in the dataframe
    existing_columns = cleaned_doge_df.columns.tolist()
    ordered_columns = [col for col in column_order if col in existing_columns]
    
    # Add any remaining columns that weren't in our ordered list
    remaining_columns = [col for col in existing_columns if col not in ordered_columns]
    final_column_order = ordered_columns + remaining_columns
    
    # Reorder the dataframe columns
    cleaned_doge_df = cleaned_doge_df[final_column_order]
    
    # Save the data in both CSV and Excel formats
    csv_path = r"data/processed_doge_data.csv"
    excel_path = r"data/processed_doge_data.xlsx"
    
    # Save as CSV for compatibility
    cleaned_doge_df.to_csv(csv_path, index=False)
    logging.info(f"Data saved to {csv_path}")
    
    # Save as formatted Excel file
    from src.utils.excel_exporter import export_doge_data_to_excel
    export_doge_data_to_excel(cleaned_doge_df, excel_path)
    logging.info(f"Data saved to {excel_path} with enhanced formatting")
    
if __name__ == "__main__":
    main()
