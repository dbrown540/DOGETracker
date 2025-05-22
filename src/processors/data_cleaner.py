"""
Data Cleaner Module
==================

This module provides functionality to clean and process DOGE API data.
It handles column renaming, validation, NaN handling, and type conversions
to prepare the data for analysis.
"""
import logging
import pandas as pd
from typing import List

from settings import RAW_DOGE_DATA_CSV_PATH, RAW_DOGE_FIELDS

class DOGEApiDataCleaner:
    """
    Class for cleaning and processing DOGE API data.
    
    Reads raw data from CSV, performs validation and cleaning operations,
    and returns a processed DataFrame ready for analysis.
    """
    def __init__(self):
        """
        Initialize the data cleaner by loading the raw CSV data.
        """
        self.df = pd.read_csv(RAW_DOGE_DATA_CSV_PATH)

    def _validate_columns(self) -> bool:
        """
        Validate that the DataFrame columns match expected fields.
        
        Returns:
            bool: True if columns match, False otherwise
        """
        return sorted(self.df.columns) == sorted(RAW_DOGE_FIELDS)
    
    def _replace_column_names(self) -> pd.DataFrame:
        """
        Rename DataFrame columns to more descriptive names.
        
        Returns:
            pd.DataFrame: DataFrame with renamed columns
        """
        # Use inplace=False for clarity but this is efficient
        return self.df.rename(columns={
            "piid": "PIID",
            "agency": "Buying Org 1",
            "vendor": "Incumbent",
            "value": "Total Contract Value (TCV)",
            "description": "Description",
            "fpds_status": "Status",
            "fpds_link": "FPDS Link",
            "deleted_date": "Deleted On",
            "savings": "Savings"
        })
        
    def _handle_nan(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Handle missing values in the DataFrame.
        
        Drops rows with missing values in required fields and 
        fills remaining NaN values with empty strings.
        
        Args:
            df: Input DataFrame with potential NaN values
            
        Returns:
            pd.DataFrame: DataFrame with handled NaN values
        """
        # Dropping NaN rows for rows that did not have NA in original dataset
        # These are required and if they are missed, they are not worth evaluating
        required_columns = [
            "PIID",
            "Buying Org 1",
            "Total Contract Value (TCV)",
            "Deleted On",
            "Savings"
        ]
        
        # Chain operations instead of creating intermediate variables
        return df.dropna(subset=required_columns).fillna("")
    
    def _convert_types(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Convert DataFrame columns to appropriate data types.
        
        Args:
            df: Input DataFrame with columns to convert
            
        Returns:
            pd.DataFrame: DataFrame with converted data types
        """
        # Avoid unnecessary copy, modify in place
        df = df.copy()
        df["Deleted On"] = pd.to_datetime(
            df["Deleted On"], errors="coerce"
        )

        logging.info("Converted datatypes for more efficient analysis.")
        return df

    def clean_doge_data(self) -> pd.DataFrame:
        """
        Main method to clean and process DOGE API data.
        
        Validates columns, renames them, handles missing values,
        converts data types, and fixes FPDS links.
        
        Returns:
            pd.DataFrame: Clean, processed DataFrame ready for analysis
            
        Raises:
            ValueError: If column validation fails
        """
        # Validate the expected columns
        received_expected_columns = self._validate_columns()
        if not received_expected_columns:
            difference = [f"From API: {item}" for item in self.df.columns if item not in RAW_DOGE_FIELDS] + \
                         [f"From settings: {item}" for item in RAW_DOGE_FIELDS if item not in self.df.columns]
            logging.error("The API columns do not match up with the expected columns. The difference is %s", difference)
            raise ValueError(f"Column validation failed - differences in expected columns: {difference}")

        logging.info("Input columns have been validated!")
        
        # Process data through the cleaning pipeline
        df_renamed = self._replace_column_names()
        logging.info("Renamed df columns!")

        df_handled_nan = self._handle_nan(df_renamed)
        logging.info("Handled NaN values!")

        df_processed = self._convert_types(df_handled_nan)
        
        # Fix: Replace bad FPDS link in the entire dataframe, not just the column
        df_processed["FPDS Link"] = df_processed["FPDS Link"].replace({
            "https://fpds.gov": ""
        })
        logging.info("Fixed bad FPDS links!")

        return df_processed
