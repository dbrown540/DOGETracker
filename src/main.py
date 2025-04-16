import logging
import math
import os
from typing import List

from src.utils.logger import initialize_logger
from src.scrapers.doge_api import DogeAPIScraper
from src.models.api_models import IContracts
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
            contracts: List[IContracts] = page_data.get("result", {}).get("contracts", [])
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
    raw_doge_data_cleaner.clean_doge_data()

if __name__ == "__main__":
    main()
