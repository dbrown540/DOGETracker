from datetime import datetime
from typing import TypedDict, Union, Dict, Any

class IDogeAPI(TypedDict):
    """
    A TypedDict representing the structure of a response from the Doge API.
    Attributes:
        ok (bool): Indicates whether the API request was successful.
        status (int): The HTTP status code of the API response.
        data (Union[str, Dict[str, Any]]): The data returned by the API, 
        which can be a string or a dictionary.
        headers (Dict[str, str]): A dictionary containing the headers of the 
        API response.
    """
    ok: bool
    status: int
    data: Union[str, Dict[str, Any]]
    headers: Dict[str, str]

class IParams(TypedDict):
    """
    IParams is a TypedDict that defines the structure of parameters used for API requests.
    Attributes:
        sort_by (str): The field by which the data should be sorted (e.g., "name", "date").
        sort_order (str): The order of sorting, either "asc" for ascending or "desc" for descending.
        page (Union[None, int]): The page number for paginated results. Can be None if 
        pagination is not used.
        per_page (Union[None, int]): The number of items per page for paginated results. 
        Can be None if pagination is not used.
    """
    sort_by: str
    sort_order: str
    page: Union[None, int]
    per_page: Union[None, int]

class IRawDogeContracts(TypedDict):
    """
    IContracts: A TypedDict representing the structure of contract data.
    Attributes:
        piid (str): The Procurement Instrument Identifier (PIID) of the contract.
        agency (str): The name of the agency associated with the contract.
        vendor (str): The name of the vendor awarded the contract.
        value (int): The monetary value of the contract.
        description (str): A brief description of the contract.
        fpds_status (str): The status of the contract in the Federal Procurement Data System (FPDS).
        fpds_link (str): A URL link to the contract details in FPDS.
        deleted_date (str): The date the contract was marked as deleted, if applicable.
        savings (Union[int, float]): The amount of savings associated with the contract, as an integer or float.
    """
    piid: str
    agency: str
    vendor: str
    value: int
    description: str
    fpds_status: str
    fpds_link: str
    deleted_date: str
    savings: Union[int, float]
