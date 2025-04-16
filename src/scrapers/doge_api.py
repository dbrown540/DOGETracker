"""
DogeAPIScraper is a class designed to interact with the DOGE API.

This class provides methods to send HTTP GET requests to the DOGE API, handle
response data, and extract useful information such as the total number of
results available. It includes functionality for retrying API requests and
converting response data to JSON format.

Attributes:
    headers (Dict[str, str]): Default headers to include in API requests.
    params (IParams): Default query parameters for API requests.

Methods:
    __init__():
        Initializes the DogeAPIScraper instance with default headers and parameters.
    request_doge_api(reformatted_params: IParams) -> IDogeAPI:
        Sends a GET request to the DOGE API endpoint with the specified parameters.
    try_converting_to_json(response_text: str):
        Attempts to parse the provided response text as JSON. Returns the parsed
        JSON data if successful, otherwise returns the original response text.
    get_total_results() -> int:
        Fetches the total number of results available from the DOGE API by sending
        a minimal request. Returns the total count or 0 if the information couldn't
        be retrieved.
"""
import json
from json import JSONDecodeError
import logging
from typing import Dict, Union, Any, Generator, Optional

import requests

from settings import (
    DOGE_CONTRACTS_API_ENDPOINT,
    REQUEST_TIMEOUT,
    RESULTS_PER_PAGE
)
from src.models.api_models import (
    IDogeAPI,
    IParams
)
from src.utils.decorators import api_retry

logging.getLogger(__name__)

class DogeAPIScraper:
    """
    DogeAPIScraper is a class designed to interact with the DOGE API.
    This class provides methods to send HTTP GET requests to the DOGE API, handle
    response data, and extract useful information such as the total number of
    results available. It includes functionality for retrying API requests and
    converting response data to JSON format.
    Attributes:
        headers (Dict[str, str]): Default headers to include in API requests.
        params (IParams): Default query parameters for API requests.
    Methods:
        __init__():
            Initializes the DogeAPIScraper instance with default headers and parameters.
        request_doge_api(reformatted_params: IParams) -> IDogeAPI:
            Sends a GET request to the DOGE API endpoint with the specified parameters.
        try_converting_to_json(response_text: str):
            Attempts to parse the provided response text as JSON. Returns the parsed
            JSON data if successful, otherwise returns the original response text.
        get_total_results() -> int:
            Fetches the total number of results available from the DOGE API by sending
            a minimal request. Returns the total count or 0 if the information couldn't
            be retrieved.
    """

    def __init__(self):
        self.params: IParams = {
            "sort_by": "savings",
            "sort_order": "desc",
            "page": None,
            "per_page": None
        }

    @property
    def headers(self) -> Dict[str, str]:
        """
        Constructs and returns the headers required for making API requests.
        Returns:
            Dict[str, str]: A dictionary containing the headers, including the 
            "Content-Type" set to "application/json".
        """
        return {
            "Content-Type": "appication/json"
        }

    @api_retry
    def request_doge_api(self, reformatted_params: IParams) -> IDogeAPI:
        """
        Sends a GET request to the DOGE_API endpoint with the specified parameters.
        Args:
            reformatted_params (IParams): The query parameters to include in the request.
        Returns:
            IDogeAPI: A dictionary containing the following keys:
                - "ok" (bool): Indicates whether the request was successful.
                - "status" (int): The HTTP status code of the response.
                - "data" (dict or None): The JSON-decoded response data, or None if decoding fails.
                - "headers" (dict): The headers returned in the response.
        Raises:
            requests.exceptions.RequestException: If an error occurs during the HTTP request.
        """
        response = requests.get(
            url=DOGE_CONTRACTS_API_ENDPOINT,
            headers=self.headers,
            params=reformatted_params,
            timeout=REQUEST_TIMEOUT
        )
        return {
            "ok": response.ok,
            "status": response.status_code,
            "data": self.try_converting_to_json(response.text),
            "headers": dict(response.headers)
        }

    def try_converting_to_json(self, response_text: str) -> Union[Dict[str, Any], str]:
        """
        Converts a given response text to JSON format.
        
        This function attempts to parse the provided response text as JSON. 
        If the conversion is successful, it logs an informational message and returns 
        the parsed JSON data. If the conversion fails due to a TypeError or JSONDecodeError, 
        it logs a warning and returns the original response text.
        
        Args:
            response_text (str): The response text to be converted to JSON.
        
        Returns:
            dict or str: The parsed JSON data if successful, otherwise the original response text.
        """
        try:
            json_data = json.loads(response_text)
            logging.info("Successfully converted the request data into JSON format!")
            return json_data
        except (TypeError, JSONDecodeError) as e:
            logging.warning(
                "Could not convert the response data into JSON format... "
                "returning the response.text instead. %s", str(e)
            )
            return response_text

    def get_total_results(self) -> int:
        """
        Fetches the total number of results available from the DOGE API.
        
        This method sends a minimal request (1 item on page 1) to determine
        the total count of available results without fetching all the data.
        
        Returns:
            int: The total number of results available, or 0 if the information
                couldn't be retrieved.
                
        Raises:
            Any exceptions from request_doge_api may propagate up.
        """
        # Create a copy of params to avoid side effects
        pilot_params = self.params.copy()

        # Set minimal pagination values
        pilot_params["page"] = 1
        pilot_params["per_page"] = 1

        # Make the request
        response: IDogeAPI = self.request_doge_api(reformatted_params=pilot_params)

        # Handle potential errors
        if not response["ok"] or not isinstance(response["data"], dict):
            logging.warning("Failed to get total results count from API")
            return 0

        # Extract the total results
        total = response["data"].get("meta", {}).get("total_results", 0)
        logging.info("API reports %d total results available", total)
        return total

    def iter_pages(self, total_pages: int) -> Generator[Optional[Dict[str, Any]], None, None]:
        """
        Iterates through pages of data from the Doge API.
        This generator method fetches data from the Doge API for each page
        up to the specified total number of pages. It yields the data for
        each page if the response is successful, or `None` if the request
        fails.
        Args:
            total_pages (int): The total number of pages to iterate through.
        Yields:
            dict or None: The data for each page if the response is successful,
            otherwise `None` if the request fails.
        Logs:
            A warning message if a page fails to fetch.
        """

        for page in range(1, total_pages + 1):
            page_params = self.params.copy()
            page_params["page"] = page
            page_params["per_page"] = RESULTS_PER_PAGE

            response = self.request_doge_api(reformatted_params=page_params)

            if response["ok"] and isinstance(response["data"], dict):
                yield response["data"]

            else:
                logging.warning("Failed to fetch page: %d", page)
                yield None
