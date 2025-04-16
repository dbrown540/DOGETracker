"""
settings.py
============
Settings module for misc. values.
"""

# URLs
DOGE_SITE_URL = "https://doge.gov/savings"
DOGE_CONTRACTS_API_ENDPOINT = "https://api.doge.gov/savings/contracts"

# Retries and timeouts
MAX_RETRIES = 3
RETRY_TIMEOUT = 10
REQUEST_TIMEOUT = 10

# API settings
RESULTS_PER_PAGE = 100

# API Fields
DOGE_API_FIELDS = [
    "piid", "agency", "vendor", "value", "description",
    "fpds_status", "fpds_link", "deleted_date", "savings"
]

# Filepaths
RAW_DOGE_DATA_CSV_PATH = "data/doge_raw_api_data.csv"

# Datafields
RAW_DOGE_FIELDS = [
    'piid', 'agency', 'vendor', 'value', 
    'description', 'fpds_status', 'fpds_link', 
    'deleted_date', 'savings'
]