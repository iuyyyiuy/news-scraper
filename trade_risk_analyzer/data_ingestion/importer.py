"""
Trade Data Importer Module

Handles importing trade data from CSV, JSON, and Excel formats with proper
type conversion and date/time normalization.
"""

import pandas as pd
from typing import Optional, Union
from pathlib import Path
from datetime import datetime
import json

from trade_risk_analyzer.core.base import BaseDataImporter, ValidationResult, Trade, TradeType
from trade_risk_analyzer.core.logger import get_logger


logger = get_logger(__name__)


class TradeDataImporter(BaseDataImporter):
    """
    Handles importing trade data from various file formats
    """
    
    # Required columns for trade data
    REQUIRED_COLUMNS = ['user_id', 'timestamp', 'symbol', 'price', 'volume', 'trade_type']
    
    # Optional columns
    OPTIONAL_COLUMNS = ['order_id', 'trade_id']
    
    # Date/time format patterns to try
    DATETIME_FORMATS = [
        '%Y-%m-%d %H:%M:%S',
        '%Y-%m-%dT%H:%M:%S',
        '%Y-%m-%dT%H:%M:%S.%f',
        '%Y-%m-%dT%H:%M:%SZ',
        '%Y-%m-%dT%H:%M:%S.%fZ',
        '%Y/%m/%d %H:%M:%S',
        '%d-%m-%Y %H:%M:%S',
        '%d/%m/%Y %H:%M:%S',
        '%m-%d-%Y %H:%M:%S',
        '%m/%d/%Y %H:%M:%S',
    ]
    
    def __init__(self):
        """Initialize the importer"""
        self.logger = logger
    
    def import_csv(self, file_path: str) -> pd.DataFrame:
        """
        Import trade data from CSV file
        
        Args:
            file_path: Path to CSV file
            
        Returns:
            DataFrame containing trade data
            
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file cannot be parsed
        """
        self.logger.info(f"Importing CSV file: {file_path}")
        
        if not Path(file_path).exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        try:
            # Read CSV with pandas
            df = pd.read_csv(file_path)
            
            self.logger.info(f"Successfully read CSV with {len(df)} records")
            
            # Normalize the data
            df = self._normalize_dataframe(df)
            
            return df
            
        except Exception as e:
            self.logger.error(f"Error reading CSV file: {str(e)}")
            raise ValueError(f"Failed to parse CSV file: {str(e)}")
    
    def import_json(self, file_path: str) -> pd.DataFrame:
        """
        Import trade data from JSON file
        
        Args:
            file_path: Path to JSON file
            
        Returns:
            DataFrame containing trade data
            
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file cannot be parsed
        """
        self.logger.info(f"Importing JSON file: {file_path}")
        
        if not Path(file_path).exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        try:
            # Read JSON file
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            # Handle both array of objects and object with array
            if isinstance(data, dict):
                # Try common keys for trade data
                for key in ['trades', 'data', 'records']:
                    if key in data and isinstance(data[key], list):
                        data = data[key]
                        break
                else:
                    # If no array found, wrap single object
                    if not isinstance(data, list):
                        data = [data]
            
            # Convert to DataFrame
            df = pd.DataFrame(data)
            
            self.logger.info(f"Successfully read JSON with {len(df)} records")
            
            # Normalize the data
            df = self._normalize_dataframe(df)
            
            return df
            
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON format: {str(e)}")
            raise ValueError(f"Failed to parse JSON file: {str(e)}")
        except Exception as e:
            self.logger.error(f"Error reading JSON file: {str(e)}")
            raise ValueError(f"Failed to parse JSON file: {str(e)}")
    
    def import_excel(self, file_path: str, sheet_name: Union[str, int] = 0) -> pd.DataFrame:
        """
        Import trade data from Excel file
        
        Args:
            file_path: Path to Excel file
            sheet_name: Sheet name or index to read (default: 0)
            
        Returns:
            DataFrame containing trade data
            
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file cannot be parsed
        """
        self.logger.info(f"Importing Excel file: {file_path}, sheet: {sheet_name}")
        
        if not Path(file_path).exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        try:
            # Read Excel with pandas
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            
            self.logger.info(f"Successfully read Excel with {len(df)} records")
            
            # Normalize the data
            df = self._normalize_dataframe(df)
            
            return df
            
        except Exception as e:
            self.logger.error(f"Error reading Excel file: {str(e)}")
            raise ValueError(f"Failed to parse Excel file: {str(e)}")
    
    def import_data(self, file_path: str) -> pd.DataFrame:
        """
        Import data from file (auto-detect format)
        
        Args:
            file_path: Path to data file
            
        Returns:
            DataFrame containing trade data
        """
        file_path_obj = Path(file_path)
        extension = file_path_obj.suffix.lower()
        
        if extension == '.csv':
            return self.import_csv(file_path)
        elif extension == '.json':
            return self.import_json(file_path)
        elif extension in ['.xlsx', '.xls']:
            return self.import_excel(file_path)
        else:
            raise ValueError(f"Unsupported file format: {extension}")
    
    def _normalize_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Normalize DataFrame with proper type conversion and date handling
        
        Args:
            df: Input DataFrame
            
        Returns:
            Normalized DataFrame
        """
        # Make a copy to avoid modifying original
        df = df.copy()
        
        # Normalize column names (lowercase, strip whitespace)
        df.columns = df.columns.str.strip().str.lower()
        
        # Handle timestamp conversion
        if 'timestamp' in df.columns:
            df['timestamp'] = self._normalize_timestamp(df['timestamp'])
        
        # Handle trade_type conversion
        if 'trade_type' in df.columns:
            df['trade_type'] = df['trade_type'].str.upper()
        
        # Convert numeric columns
        numeric_columns = ['price', 'volume']
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Convert string columns
        string_columns = ['user_id', 'symbol', 'order_id', 'trade_id']
        for col in string_columns:
            if col in df.columns:
                df[col] = df[col].astype(str)
        
        # Generate trade_id if not present
        if 'trade_id' not in df.columns:
            df['trade_id'] = [f"trade_{i}_{int(datetime.now().timestamp())}" 
                             for i in range(len(df))]
        
        return df
    
    def _normalize_timestamp(self, timestamp_series: pd.Series) -> pd.Series:
        """
        Normalize timestamp to ISO8601 format
        
        Args:
            timestamp_series: Series containing timestamps
            
        Returns:
            Series with normalized timestamps
        """
        # Try pandas to_datetime first (handles many formats)
        try:
            return pd.to_datetime(timestamp_series, errors='coerce')
        except Exception:
            pass
        
        # Try each format pattern
        for fmt in self.DATETIME_FORMATS:
            try:
                return pd.to_datetime(timestamp_series, format=fmt, errors='coerce')
            except Exception:
                continue
        
        # If all else fails, try to parse as Unix timestamp
        try:
            return pd.to_datetime(timestamp_series, unit='s', errors='coerce')
        except Exception:
            pass
        
        # Last resort: return as-is and let validation catch it
        self.logger.warning("Could not parse timestamp format, returning as-is")
        return timestamp_series
    
    def validate_data(self, data: pd.DataFrame) -> ValidationResult:
        """
        Validate imported data (placeholder - implemented in validator module)
        
        Args:
            data: DataFrame to validate
            
        Returns:
            ValidationResult
        """
        # This is a placeholder - actual validation is in the validator module
        from trade_risk_analyzer.data_ingestion.validator import TradeDataValidator
        validator = TradeDataValidator()
        return validator.validate(data)
