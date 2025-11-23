"""
Trade Data Validator Module

Validates imported trade data for required fields, data types, and value ranges.
Provides detailed error reporting and supports partial imports.
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional
from datetime import datetime

from trade_risk_analyzer.core.base import ValidationResult, ValidationError, TradeType
from trade_risk_analyzer.core.logger import get_logger


logger = get_logger(__name__)


class TradeDataValidator:
    """
    Validates trade data and provides detailed error reporting
    """
    
    # Required columns
    REQUIRED_COLUMNS = ['user_id', 'timestamp', 'symbol', 'price', 'volume', 'trade_type']
    
    # Valid trade types
    VALID_TRADE_TYPES = ['BUY', 'SELL']
    
    # Value constraints
    MIN_PRICE = 0.0
    MAX_PRICE = 1e10  # 10 billion
    MIN_VOLUME = 0.0
    MAX_VOLUME = 1e12  # 1 trillion
    
    def __init__(self):
        """Initialize the validator"""
        self.logger = logger
    
    def validate(self, df: pd.DataFrame, strict: bool = False) -> ValidationResult:
        """
        Validate trade data DataFrame
        
        Args:
            df: DataFrame to validate
            strict: If True, any error makes entire dataset invalid
                   If False, allows partial imports (skip invalid records)
            
        Returns:
            ValidationResult with validation details
        """
        self.logger.info(f"Validating {len(df)} trade records (strict={strict})")
        
        errors: List[ValidationError] = []
        warnings: List[str] = []
        
        # Check if DataFrame is empty
        if df.empty:
            errors.append(ValidationError(
                field='dataframe',
                message='DataFrame is empty',
                value=None
            ))
            return ValidationResult(
                is_valid=False,
                errors=errors,
                warnings=warnings,
                valid_records=0,
                invalid_records=0
            )
        
        # Validate required columns
        missing_columns = self._validate_required_columns(df)
        if missing_columns:
            for col in missing_columns:
                errors.append(ValidationError(
                    field=col,
                    message=f'Required column missing: {col}',
                    value=None
                ))
            
            # Cannot continue without required columns
            return ValidationResult(
                is_valid=False,
                errors=errors,
                warnings=warnings,
                valid_records=0,
                invalid_records=len(df)
            )
        
        # Track valid/invalid record indices
        valid_indices = set(range(len(df)))
        
        # Validate each field
        errors.extend(self._validate_user_ids(df, valid_indices))
        errors.extend(self._validate_timestamps(df, valid_indices))
        errors.extend(self._validate_symbols(df, valid_indices))
        errors.extend(self._validate_prices(df, valid_indices))
        errors.extend(self._validate_volumes(df, valid_indices))
        errors.extend(self._validate_trade_types(df, valid_indices))
        
        # Check for warnings
        warnings.extend(self._check_warnings(df))
        
        # Calculate valid/invalid counts
        invalid_records = len(df) - len(valid_indices)
        valid_records = len(valid_indices)
        
        # Determine if validation passed
        if strict:
            is_valid = len(errors) == 0
        else:
            # In non-strict mode, valid if at least some records are valid
            is_valid = valid_records > 0
        
        self.logger.info(
            f"Validation complete: {valid_records} valid, {invalid_records} invalid"
        )
        
        return ValidationResult(
            is_valid=is_valid,
            errors=errors,
            warnings=warnings,
            valid_records=valid_records,
            invalid_records=invalid_records
        )
    
    def _validate_required_columns(self, df: pd.DataFrame) -> List[str]:
        """
        Check if all required columns are present
        
        Args:
            df: DataFrame to check
            
        Returns:
            List of missing column names
        """
        df_columns = set(df.columns.str.lower())
        required = set(col.lower() for col in self.REQUIRED_COLUMNS)
        missing = required - df_columns
        return list(missing)
    
    def _validate_user_ids(self, df: pd.DataFrame, valid_indices: set) -> List[ValidationError]:
        """
        Validate user_id field
        
        Args:
            df: DataFrame to validate
            valid_indices: Set of valid record indices (modified in place)
            
        Returns:
            List of validation errors
        """
        errors = []
        
        # Check for null/empty user_ids
        null_mask = df['user_id'].isna() | (df['user_id'] == '') | (df['user_id'] == 'nan')
        null_indices = df[null_mask].index.tolist()
        
        for idx in null_indices:
            errors.append(ValidationError(
                field='user_id',
                message=f'Row {idx}: user_id is null or empty',
                value=None
            ))
            valid_indices.discard(idx)
        
        return errors
    
    def _validate_timestamps(self, df: pd.DataFrame, valid_indices: set) -> List[ValidationError]:
        """
        Validate timestamp field
        
        Args:
            df: DataFrame to validate
            valid_indices: Set of valid record indices (modified in place)
            
        Returns:
            List of validation errors
        """
        errors = []
        
        # Check for null timestamps
        null_mask = df['timestamp'].isna()
        null_indices = df[null_mask].index.tolist()
        
        for idx in null_indices:
            errors.append(ValidationError(
                field='timestamp',
                message=f'Row {idx}: timestamp is null',
                value=None
            ))
            valid_indices.discard(idx)
        
        # Check for invalid datetime objects
        for idx in df.index:
            if idx in null_indices:
                continue
            
            ts = df.loc[idx, 'timestamp']
            
            # Check if it's a valid datetime
            if not isinstance(ts, (pd.Timestamp, datetime)):
                try:
                    pd.to_datetime(ts)
                except Exception:
                    errors.append(ValidationError(
                        field='timestamp',
                        message=f'Row {idx}: invalid timestamp format',
                        value=str(ts)
                    ))
                    valid_indices.discard(idx)
        
        return errors
    
    def _validate_symbols(self, df: pd.DataFrame, valid_indices: set) -> List[ValidationError]:
        """
        Validate symbol field
        
        Args:
            df: DataFrame to validate
            valid_indices: Set of valid record indices (modified in place)
            
        Returns:
            List of validation errors
        """
        errors = []
        
        # Check for null/empty symbols
        null_mask = df['symbol'].isna() | (df['symbol'] == '') | (df['symbol'] == 'nan')
        null_indices = df[null_mask].index.tolist()
        
        for idx in null_indices:
            errors.append(ValidationError(
                field='symbol',
                message=f'Row {idx}: symbol is null or empty',
                value=None
            ))
            valid_indices.discard(idx)
        
        return errors
    
    def _validate_prices(self, df: pd.DataFrame, valid_indices: set) -> List[ValidationError]:
        """
        Validate price field
        
        Args:
            df: DataFrame to validate
            valid_indices: Set of valid record indices (modified in place)
            
        Returns:
            List of validation errors
        """
        errors = []
        
        # Check for null prices
        null_mask = df['price'].isna()
        null_indices = df[null_mask].index.tolist()
        
        for idx in null_indices:
            errors.append(ValidationError(
                field='price',
                message=f'Row {idx}: price is null',
                value=None
            ))
            valid_indices.discard(idx)
        
        # Check for non-numeric prices
        for idx in df.index:
            if idx in null_indices:
                continue
            
            price = df.loc[idx, 'price']
            
            # Check if numeric
            if not isinstance(price, (int, float, np.number)):
                errors.append(ValidationError(
                    field='price',
                    message=f'Row {idx}: price is not numeric',
                    value=str(price)
                ))
                valid_indices.discard(idx)
                continue
            
            # Check range
            if price < self.MIN_PRICE:
                errors.append(ValidationError(
                    field='price',
                    message=f'Row {idx}: price is negative',
                    value=price
                ))
                valid_indices.discard(idx)
            elif price > self.MAX_PRICE:
                errors.append(ValidationError(
                    field='price',
                    message=f'Row {idx}: price exceeds maximum allowed value',
                    value=price
                ))
                valid_indices.discard(idx)
        
        return errors
    
    def _validate_volumes(self, df: pd.DataFrame, valid_indices: set) -> List[ValidationError]:
        """
        Validate volume field
        
        Args:
            df: DataFrame to validate
            valid_indices: Set of valid record indices (modified in place)
            
        Returns:
            List of validation errors
        """
        errors = []
        
        # Check for null volumes
        null_mask = df['volume'].isna()
        null_indices = df[null_mask].index.tolist()
        
        for idx in null_indices:
            errors.append(ValidationError(
                field='volume',
                message=f'Row {idx}: volume is null',
                value=None
            ))
            valid_indices.discard(idx)
        
        # Check for non-numeric volumes
        for idx in df.index:
            if idx in null_indices:
                continue
            
            volume = df.loc[idx, 'volume']
            
            # Check if numeric
            if not isinstance(volume, (int, float, np.number)):
                errors.append(ValidationError(
                    field='volume',
                    message=f'Row {idx}: volume is not numeric',
                    value=str(volume)
                ))
                valid_indices.discard(idx)
                continue
            
            # Check range
            if volume <= self.MIN_VOLUME:
                errors.append(ValidationError(
                    field='volume',
                    message=f'Row {idx}: volume must be greater than zero',
                    value=volume
                ))
                valid_indices.discard(idx)
            elif volume > self.MAX_VOLUME:
                errors.append(ValidationError(
                    field='volume',
                    message=f'Row {idx}: volume exceeds maximum allowed value',
                    value=volume
                ))
                valid_indices.discard(idx)
        
        return errors
    
    def _validate_trade_types(self, df: pd.DataFrame, valid_indices: set) -> List[ValidationError]:
        """
        Validate trade_type field
        
        Args:
            df: DataFrame to validate
            valid_indices: Set of valid record indices (modified in place)
            
        Returns:
            List of validation errors
        """
        errors = []
        
        # Check for null trade_types
        null_mask = df['trade_type'].isna() | (df['trade_type'] == '')
        null_indices = df[null_mask].index.tolist()
        
        for idx in null_indices:
            errors.append(ValidationError(
                field='trade_type',
                message=f'Row {idx}: trade_type is null or empty',
                value=None
            ))
            valid_indices.discard(idx)
        
        # Check for invalid trade_types
        for idx in df.index:
            if idx in null_indices:
                continue
            
            trade_type = str(df.loc[idx, 'trade_type']).upper()
            
            if trade_type not in self.VALID_TRADE_TYPES:
                errors.append(ValidationError(
                    field='trade_type',
                    message=f'Row {idx}: invalid trade_type (must be BUY or SELL)',
                    value=trade_type
                ))
                valid_indices.discard(idx)
        
        return errors
    
    def _check_warnings(self, df: pd.DataFrame) -> List[str]:
        """
        Check for potential issues that don't invalidate data
        
        Args:
            df: DataFrame to check
            
        Returns:
            List of warning messages
        """
        warnings = []
        
        # Check for duplicate trade_ids if present
        if 'trade_id' in df.columns:
            duplicates = df['trade_id'].duplicated().sum()
            if duplicates > 0:
                warnings.append(f'Found {duplicates} duplicate trade_ids')
        
        # Check for very old timestamps
        if 'timestamp' in df.columns:
            try:
                min_date = pd.to_datetime(df['timestamp']).min()
                if min_date < pd.Timestamp('2010-01-01'):
                    warnings.append(f'Found timestamps before 2010: {min_date}')
            except Exception:
                pass
        
        # Check for unusual price/volume combinations
        if 'price' in df.columns and 'volume' in df.columns:
            zero_price_count = (df['price'] == 0).sum()
            if zero_price_count > 0:
                warnings.append(f'Found {zero_price_count} trades with zero price')
        
        return warnings
    
    def get_valid_records(self, df: pd.DataFrame, validation_result: ValidationResult) -> pd.DataFrame:
        """
        Extract only valid records from DataFrame
        
        Args:
            df: Original DataFrame
            validation_result: Result from validate()
            
        Returns:
            DataFrame containing only valid records
        """
        if validation_result.valid_records == len(df):
            return df.copy()
        
        # Re-run validation to get valid indices
        valid_indices = set(range(len(df)))
        
        # Apply same validation logic
        self._validate_user_ids(df, valid_indices)
        self._validate_timestamps(df, valid_indices)
        self._validate_symbols(df, valid_indices)
        self._validate_prices(df, valid_indices)
        self._validate_volumes(df, valid_indices)
        self._validate_trade_types(df, valid_indices)
        
        # Return only valid rows
        valid_df = df.iloc[list(valid_indices)].copy()
        
        self.logger.info(f"Extracted {len(valid_df)} valid records from {len(df)} total")
        
        return valid_df
