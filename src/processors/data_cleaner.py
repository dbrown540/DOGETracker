import logging
import pandas as pd

from settings import RAW_DOGE_DATA_CSV_PATH, RAW_DOGE_FIELDS

class DOGEApiDataCleaner:
    def __init__(self):
        self.df = pd.read_csv(RAW_DOGE_DATA_CSV_PATH)

    def _validate_columns(self):
        return sorted(self.df.columns) == sorted(RAW_DOGE_FIELDS)
        
    def clean_doge_data(self):
        received_expected_columns = self._validate_columns()
        if not received_expected_columns:
            difference = [f"From API: {item}" for item in self.df.columns if item not in RAW_DOGE_FIELDS] + [f"From settings: {item}" for item in RAW_DOGE_FIELDS if item not in self.df.columns]
            logging.error("The API columns do not match up with the expected columns. The difference is %s", difference)
            raise ValueError("")
