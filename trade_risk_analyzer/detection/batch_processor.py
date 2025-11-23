"""
Batch Processing Module

Handles batch analysis of historical trade data with progress tracking,
parallel processing, and memory optimization.
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional, Callable
from datetime import datetime, timedelta
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from dataclasses import dataclass
import time

from trade_risk_analyzer.core.base import Alert, DetectionResult
from trade_risk_analyzer.core.logger import get_logger
from trade_risk_analyzer.detection.engine import DetectionEngine, DetectionConfig
from trade_risk_analyzer.data_ingestion.storage import DatabaseStorage


logger = get_logger(__name__)


@dataclass
class BatchProgress:
    """
    Batch processing progress information
    """
    total_batches: int
    completed_batches: int
    total_trades: int
    processed_trades: int
    total_alerts: int
    start_time: datetime
    estimated_completion: Optional[datetime] = None
    current_batch: int = 0
    errors: int = 0
    
    @property
    def progress_percentage(self) -> float:
        """Calculate progress percentage"""
        if self.total_batches == 0:
            return 0.0
        return (self.completed_batches / self.total_batches) * 100
    
    @property
    def elapsed_time(self) -> float:
        """Calculate elapsed time in seconds"""
        return (datetime.now() - self.start_time).total_seconds()
    
    @property
    def processing_rate(self) -> float:
        """Calculate trades per second"""
        if self.elapsed_time == 0:
            return 0.0
        return self.processed_trades / self.elapsed_time
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'total_batches': self.total_batches,
            'completed_batches': self.completed_batches,
            'total_trades': self.total_trades,
            'processed_trades': self.processed_trades,
            'total_alerts': self.total_alerts,
            'progress_percentage': self.progress_percentage,
            'elapsed_time': self.elapsed_time,
            'processing_rate': self.processing_rate,
            'estimated_completion': self.estimated_completion.isoformat() if self.estimated_completion else None,
            'current_batch': self.current_batch,
            'errors': self.errors
        }


class BatchProcessor:
    """
    Batch processor for historical trade data analysis
    """
    
    def __init__(
        self,
        detection_engine: DetectionEngine,
        storage: Optional[DatabaseStorage] = None,
        batch_size: int = 10000,
        max_workers: Optional[int] = None,
        use_parallel: bool = False
    ):
        """
        Initialize batch processor
        
        Args:
            detection_engine: Detection engine instance
            storage: Database storage for saving results
            batch_size: Number of trades per batch
            max_workers: Maximum number of parallel workers (None = CPU count)
            use_parallel: Whether to use parallel processing
        """
        self.detection_engine = detection_engine
        self.storage = storage
        self.batch_size = batch_size
        self.max_workers = max_workers
        self.use_parallel = use_parallel
        self.logger = logger
        
        # Progress tracking
        self.progress: Optional[BatchProgress] = None
        self.progress_callbacks: List[Callable[[BatchProgress], None]] = []
    
    def add_progress_callback(self, callback: Callable[[BatchProgress], None]) -> None:
        """
        Add callback function for progress updates
        
        Args:
            callback: Function to call with progress updates
        """
        self.progress_callbacks.append(callback)
    
    def process_dataframe(
        self,
        trades_df: pd.DataFrame,
        group_by: str = 'user_id',
        save_alerts: bool = True,
        check_duplicates: bool = True
    ) -> Dict[str, Any]:
        """
        Process trades from DataFrame in batches
        
        Args:
            trades_df: DataFrame with trade data
            group_by: Column to group by for analysis
            save_alerts: Whether to save alerts to database
            check_duplicates: Whether to check for duplicate alerts
            
        Returns:
            Dictionary with processing results
        """
        self.logger.info(f"Starting batch processing of {len(trades_df)} trades")
        
        # Initialize progress tracking
        num_batches = int(np.ceil(len(trades_df) / self.batch_size))
        self.progress = BatchProgress(
            total_batches=num_batches,
            completed_batches=0,
            total_trades=len(trades_df),
            processed_trades=0,
            total_alerts=0,
            start_time=datetime.now()
        )
        
        # Split into batches
        batches = self._split_into_batches(trades_df)
        
        # Process batches
        if self.use_parallel and num_batches > 1:
            results = self._process_parallel(batches, group_by)
        else:
            results = self._process_sequential(batches, group_by)
        
        # Aggregate results
        all_alerts = []
        total_anomaly_scores = []
        
        for result in results:
            if result:
                all_alerts.extend(result.alerts)
                total_anomaly_scores.extend(result.anomaly_scores)
        
        # Save alerts if requested
        save_results = {'saved': 0, 'duplicates': 0, 'errors': 0}
        if save_alerts and all_alerts:
            save_results = self.detection_engine.save_alerts(
                all_alerts,
                check_duplicates=check_duplicates
            )
        
        # Calculate final statistics
        processing_time = self.progress.elapsed_time
        
        summary = {
            'total_trades': len(trades_df),
            'total_batches': num_batches,
            'total_alerts': len(all_alerts),
            'alerts_saved': save_results['saved'],
            'alerts_duplicates': save_results['duplicates'],
            'alerts_errors': save_results['errors'],
            'processing_time_seconds': processing_time,
            'trades_per_second': len(trades_df) / processing_time if processing_time > 0 else 0,
            'errors': self.progress.errors,
            'progress': self.progress.to_dict()
        }
        
        self.logger.info(
            f"Batch processing complete: {len(all_alerts)} alerts generated "
            f"in {processing_time:.2f} seconds"
        )
        
        return summary
    
    def process_from_database(
        self,
        filters: Optional[Dict[str, Any]] = None,
        group_by: str = 'user_id',
        save_alerts: bool = True,
        check_duplicates: bool = True
    ) -> Dict[str, Any]:
        """
        Process trades from database in batches
        
        Args:
            filters: Filters for retrieving trades
            group_by: Column to group by for analysis
            save_alerts: Whether to save alerts to database
            check_duplicates: Whether to check for duplicate alerts
            
        Returns:
            Dictionary with processing results
        """
        if not self.storage:
            raise ValueError("Storage not configured for database processing")
        
        self.logger.info("Loading trades from database...")
        
        # Load trades from database
        trades_df = self.storage.get_trades_as_dataframe(filters)
        
        if trades_df.empty:
            self.logger.warning("No trades found in database")
            return {
                'total_trades': 0,
                'total_batches': 0,
                'total_alerts': 0,
                'processing_time_seconds': 0,
                'errors': 0
            }
        
        self.logger.info(f"Loaded {len(trades_df)} trades from database")
        
        # Process the DataFrame
        return self.process_dataframe(
            trades_df,
            group_by=group_by,
            save_alerts=save_alerts,
            check_duplicates=check_duplicates
        )
    
    def process_date_range(
        self,
        start_date: datetime,
        end_date: datetime,
        group_by: str = 'user_id',
        save_alerts: bool = True,
        check_duplicates: bool = True
    ) -> Dict[str, Any]:
        """
        Process trades for a specific date range
        
        Args:
            start_date: Start date
            end_date: End date
            group_by: Column to group by for analysis
            save_alerts: Whether to save alerts to database
            check_duplicates: Whether to check for duplicate alerts
            
        Returns:
            Dictionary with processing results
        """
        filters = {
            'start_date': start_date,
            'end_date': end_date
        }
        
        return self.process_from_database(
            filters=filters,
            group_by=group_by,
            save_alerts=save_alerts,
            check_duplicates=check_duplicates
        )
    
    def _split_into_batches(self, df: pd.DataFrame) -> List[pd.DataFrame]:
        """
        Split DataFrame into batches
        
        Args:
            df: DataFrame to split
            
        Returns:
            List of DataFrame batches
        """
        batches = []
        num_batches = int(np.ceil(len(df) / self.batch_size))
        
        for i in range(num_batches):
            start_idx = i * self.batch_size
            end_idx = min((i + 1) * self.batch_size, len(df))
            batch = df.iloc[start_idx:end_idx].copy()
            batches.append(batch)
        
        self.logger.info(f"Split data into {len(batches)} batches of size {self.batch_size}")
        
        return batches
    
    def _process_sequential(
        self,
        batches: List[pd.DataFrame],
        group_by: str
    ) -> List[DetectionResult]:
        """
        Process batches sequentially
        
        Args:
            batches: List of DataFrame batches
            group_by: Column to group by
            
        Returns:
            List of detection results
        """
        results = []
        
        for i, batch in enumerate(batches):
            self.progress.current_batch = i + 1
            
            try:
                # Process batch
                result = self.detection_engine.detect(batch, group_by=group_by)
                results.append(result)
                
                # Update progress
                self.progress.completed_batches += 1
                self.progress.processed_trades += len(batch)
                self.progress.total_alerts += len(result.alerts)
                
                # Estimate completion time
                if self.progress.completed_batches > 0:
                    avg_time_per_batch = self.progress.elapsed_time / self.progress.completed_batches
                    remaining_batches = self.progress.total_batches - self.progress.completed_batches
                    remaining_seconds = avg_time_per_batch * remaining_batches
                    self.progress.estimated_completion = datetime.now() + timedelta(seconds=remaining_seconds)
                
                # Call progress callbacks
                self._notify_progress()
                
                self.logger.info(
                    f"Batch {i+1}/{len(batches)} complete: "
                    f"{len(result.alerts)} alerts, "
                    f"{self.progress.progress_percentage:.1f}% done"
                )
                
            except Exception as e:
                self.logger.error(f"Error processing batch {i+1}: {str(e)}", exc_info=True)
                self.progress.errors += 1
                results.append(None)
        
        return results
    
    def _process_parallel(
        self,
        batches: List[pd.DataFrame],
        group_by: str
    ) -> List[DetectionResult]:
        """
        Process batches in parallel
        
        Args:
            batches: List of DataFrame batches
            group_by: Column to group by
            
        Returns:
            List of detection results
        """
        self.logger.info(f"Processing {len(batches)} batches in parallel with {self.max_workers} workers")
        
        results = [None] * len(batches)
        
        # Use ThreadPoolExecutor for I/O-bound tasks
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all batches
            future_to_idx = {
                executor.submit(self._process_batch, batch, group_by): i
                for i, batch in enumerate(batches)
            }
            
            # Process completed batches
            for future in as_completed(future_to_idx):
                idx = future_to_idx[future]
                
                try:
                    result = future.result()
                    results[idx] = result
                    
                    # Update progress
                    self.progress.completed_batches += 1
                    self.progress.processed_trades += len(batches[idx])
                    if result:
                        self.progress.total_alerts += len(result.alerts)
                    
                    # Estimate completion time
                    if self.progress.completed_batches > 0:
                        avg_time_per_batch = self.progress.elapsed_time / self.progress.completed_batches
                        remaining_batches = self.progress.total_batches - self.progress.completed_batches
                        remaining_seconds = avg_time_per_batch * remaining_batches
                        self.progress.estimated_completion = datetime.now() + timedelta(seconds=remaining_seconds)
                    
                    # Call progress callbacks
                    self._notify_progress()
                    
                    self.logger.info(
                        f"Batch {idx+1}/{len(batches)} complete: "
                        f"{self.progress.progress_percentage:.1f}% done"
                    )
                    
                except Exception as e:
                    self.logger.error(f"Error processing batch {idx+1}: {str(e)}", exc_info=True)
                    self.progress.errors += 1
                    results[idx] = None
        
        return results
    
    def _process_batch(self, batch: pd.DataFrame, group_by: str) -> DetectionResult:
        """
        Process a single batch
        
        Args:
            batch: DataFrame batch
            group_by: Column to group by
            
        Returns:
            Detection result
        """
        return self.detection_engine.detect(batch, group_by=group_by)
    
    def _notify_progress(self) -> None:
        """Notify all progress callbacks"""
        for callback in self.progress_callbacks:
            try:
                callback(self.progress)
            except Exception as e:
                self.logger.error(f"Error in progress callback: {str(e)}")
    
    def get_progress(self) -> Optional[BatchProgress]:
        """
        Get current progress
        
        Returns:
            Current BatchProgress or None
        """
        return self.progress
