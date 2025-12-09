"""
Database Storage Layer

Handles database connection management, connection pooling, and CRUD operations
for trade data with batch insert optimization.
"""

from sqlalchemy import create_engine, and_, or_
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from contextlib import contextmanager
from typing import List, Dict, Any, Optional
from datetime import datetime
import pandas as pd

from trade_risk_analyzer.core.base import BaseStorage, Trade, Alert, TradeType, RiskLevel, PatternType
from trade_risk_analyzer.core.logger import get_logger
from trade_risk_analyzer.data_ingestion.models import Base, TradeModel, AlertModel, FeedbackModel, ModelVersionModel


logger = get_logger(__name__)


class DatabaseStorage(BaseStorage):
    """
    Database storage implementation using SQLAlchemy
    """
    
    def __init__(self, database_url: str, pool_size: int = 10, max_overflow: int = 20):
        """
        Initialize database storage
        
        Args:
            database_url: Database connection URL
            pool_size: Connection pool size
            max_overflow: Maximum overflow connections
        """
        self.database_url = database_url
        self.pool_size = pool_size
        self.max_overflow = max_overflow
        self.engine = None
        self.SessionLocal = None
        self.logger = logger
    
    def connect(self) -> None:
        """
        Establish database connection with connection pooling
        """
        self.logger.info(f"Connecting to database: {self.database_url}")
        
        try:
            # Create engine with connection pooling
            self.engine = create_engine(
                self.database_url,
                poolclass=QueuePool,
                pool_size=self.pool_size,
                max_overflow=self.max_overflow,
                pool_pre_ping=True,  # Verify connections before using
                echo=False  # Set to True for SQL debugging
            )
            
            # Create session factory
            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )
            
            # Create tables if they don't exist
            Base.metadata.create_all(bind=self.engine)
            
            self.logger.info("Database connection established successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to connect to database: {str(e)}")
            raise
    
    def disconnect(self) -> None:
        """
        Close database connection
        """
        if self.engine:
            self.engine.dispose()
            self.logger.info("Database connection closed")
    
    @contextmanager
    def get_session(self) -> Session:
        """
        Get database session context manager
        
        Yields:
            SQLAlchemy session
        """
        if self.SessionLocal is None:
            raise RuntimeError("Database not connected. Call connect() first.")
        
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            self.logger.error(f"Session error: {str(e)}")
            raise
        finally:
            session.close()
    
    def save_trades(self, trades: List[Trade]) -> bool:
        """
        Save trades to database with batch insert optimization
        
        Args:
            trades: List of Trade objects
            
        Returns:
            Success status
        """
        if not trades:
            self.logger.warning("No trades to save")
            return True
        
        self.logger.info(f"Saving {len(trades)} trades to database")
        
        try:
            with self.get_session() as session:
                # Convert Trade objects to TradeModel objects
                trade_models = []
                for trade in trades:
                    trade_model = TradeModel(
                        trade_id=trade.trade_id,
                        user_id=trade.user_id,
                        timestamp=trade.timestamp,
                        symbol=trade.symbol,
                        price=trade.price,
                        volume=trade.volume,
                        trade_type=trade.trade_type.value if isinstance(trade.trade_type, TradeType) else trade.trade_type,
                        order_id=trade.order_id
                    )
                    trade_models.append(trade_model)
                
                # Batch insert
                session.bulk_save_objects(trade_models)
                
            self.logger.info(f"Successfully saved {len(trades)} trades")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save trades: {str(e)}")
            return False
    
    def save_trades_from_dataframe(self, df: pd.DataFrame) -> bool:
        """
        Save trades from DataFrame with batch insert optimization
        
        Args:
            df: DataFrame containing trade data
            
        Returns:
            Success status
        """
        if df.empty:
            self.logger.warning("Empty DataFrame, nothing to save")
            return True
        
        self.logger.info(f"Saving {len(df)} trades from DataFrame")
        
        try:
            with self.get_session() as session:
                # Convert DataFrame to list of dictionaries
                records = df.to_dict('records')
                
                # Prepare records for bulk insert
                trade_records = []
                for record in records:
                    trade_record = {
                        'trade_id': record.get('trade_id'),
                        'user_id': record.get('user_id'),
                        'timestamp': record.get('timestamp'),
                        'symbol': record.get('symbol'),
                        'price': float(record.get('price')),
                        'volume': float(record.get('volume')),
                        'trade_type': str(record.get('trade_type')).upper(),
                        'order_id': record.get('order_id'),
                    }
                    trade_records.append(trade_record)
                
                # Batch insert using bulk_insert_mappings for better performance
                session.bulk_insert_mappings(TradeModel, trade_records)
                
            self.logger.info(f"Successfully saved {len(df)} trades from DataFrame")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save trades from DataFrame: {str(e)}")
            return False
    
    def get_trades(self, filters: Optional[Dict[str, Any]] = None) -> List[Trade]:
        """
        Retrieve trades from database
        
        Args:
            filters: Optional filters (user_id, symbol, start_date, end_date, limit)
            
        Returns:
            List of Trade objects
        """
        filters = filters or {}
        
        self.logger.info(f"Retrieving trades with filters: {filters}")
        
        try:
            with self.get_session() as session:
                query = session.query(TradeModel)
                
                # Apply filters
                if 'user_id' in filters:
                    query = query.filter(TradeModel.user_id == filters['user_id'])
                
                if 'symbol' in filters:
                    query = query.filter(TradeModel.symbol == filters['symbol'])
                
                if 'start_date' in filters:
                    query = query.filter(TradeModel.timestamp >= filters['start_date'])
                
                if 'end_date' in filters:
                    query = query.filter(TradeModel.timestamp <= filters['end_date'])
                
                if 'trade_type' in filters:
                    query = query.filter(TradeModel.trade_type == filters['trade_type'])
                
                # Apply ordering
                query = query.order_by(TradeModel.timestamp.desc())
                
                # Apply limit
                if 'limit' in filters:
                    query = query.limit(filters['limit'])
                
                # Execute query
                trade_models = query.all()
                
                # Convert to Trade objects
                trades = []
                for tm in trade_models:
                    trade = Trade(
                        trade_id=tm.trade_id,
                        user_id=tm.user_id,
                        timestamp=tm.timestamp,
                        symbol=tm.symbol,
                        price=tm.price,
                        volume=tm.volume,
                        trade_type=TradeType[tm.trade_type],
                        order_id=tm.order_id
                    )
                    trades.append(trade)
                
                self.logger.info(f"Retrieved {len(trades)} trades")
                return trades
                
        except Exception as e:
            self.logger.error(f"Failed to retrieve trades: {str(e)}")
            return []
    
    def get_trades_as_dataframe(self, filters: Optional[Dict[str, Any]] = None) -> pd.DataFrame:
        """
        Retrieve trades as DataFrame
        
        Args:
            filters: Optional filters
            
        Returns:
            DataFrame containing trade data
        """
        filters = filters or {}
        
        try:
            with self.get_session() as session:
                query = session.query(TradeModel)
                
                # Apply filters (same as get_trades)
                if 'user_id' in filters:
                    query = query.filter(TradeModel.user_id == filters['user_id'])
                
                if 'symbol' in filters:
                    query = query.filter(TradeModel.symbol == filters['symbol'])
                
                if 'start_date' in filters:
                    query = query.filter(TradeModel.timestamp >= filters['start_date'])
                
                if 'end_date' in filters:
                    query = query.filter(TradeModel.timestamp <= filters['end_date'])
                
                if 'trade_type' in filters:
                    query = query.filter(TradeModel.trade_type == filters['trade_type'])
                
                query = query.order_by(TradeModel.timestamp.desc())
                
                if 'limit' in filters:
                    query = query.limit(filters['limit'])
                
                # Convert to DataFrame using pandas
                df = pd.read_sql(query.statement, session.bind)
                
                self.logger.info(f"Retrieved {len(df)} trades as DataFrame")
                return df
                
        except Exception as e:
            self.logger.error(f"Failed to retrieve trades as DataFrame: {str(e)}")
            return pd.DataFrame()
    
    def save_alert(self, alert: Alert) -> bool:
        """
        Save or update alert in database
        
        Args:
            alert: Alert object
            
        Returns:
            Success status
        """
        self.logger.info(f"Saving alert: {alert.alert_id}")
        
        try:
            with self.get_session() as session:
                # Check if alert already exists
                existing_alert = session.query(AlertModel).filter(
                    AlertModel.alert_id == alert.alert_id
                ).first()
                
                if existing_alert:
                    # Update existing alert
                    existing_alert.user_id = alert.user_id
                    existing_alert.timestamp = alert.timestamp
                    existing_alert.anomaly_score = alert.anomaly_score
                    existing_alert.risk_level = alert.risk_level.value if isinstance(alert.risk_level, RiskLevel) else alert.risk_level
                    existing_alert.pattern_type = alert.pattern_type.value if isinstance(alert.pattern_type, PatternType) else alert.pattern_type
                    existing_alert.explanation = alert.explanation
                    existing_alert.trade_ids = alert.trade_ids
                    existing_alert.recommended_action = alert.recommended_action
                    existing_alert.is_reviewed = alert.is_reviewed
                    existing_alert.is_true_positive = alert.is_true_positive
                    existing_alert.reviewer_notes = alert.reviewer_notes
                    self.logger.info(f"Updated existing alert: {alert.alert_id}")
                else:
                    # Create new alert
                    alert_model = AlertModel(
                        alert_id=alert.alert_id,
                        user_id=alert.user_id,
                        timestamp=alert.timestamp,
                        anomaly_score=alert.anomaly_score,
                        risk_level=alert.risk_level.value if isinstance(alert.risk_level, RiskLevel) else alert.risk_level,
                        pattern_type=alert.pattern_type.value if isinstance(alert.pattern_type, PatternType) else alert.pattern_type,
                        explanation=alert.explanation,
                        trade_ids=alert.trade_ids,
                        recommended_action=alert.recommended_action,
                        is_reviewed=alert.is_reviewed,
                        is_true_positive=alert.is_true_positive,
                        reviewer_notes=alert.reviewer_notes
                    )
                    session.add(alert_model)
                    self.logger.info(f"Created new alert: {alert.alert_id}")
                
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save alert: {str(e)}")
            return False
    
    def save_alerts_batch(self, alerts: List[Alert]) -> bool:
        """
        Save multiple alerts to database with batch optimization
        
        Args:
            alerts: List of Alert objects
            
        Returns:
            Success status
        """
        if not alerts:
            self.logger.warning("No alerts to save")
            return True
        
        self.logger.info(f"Saving {len(alerts)} alerts to database")
        
        try:
            with self.get_session() as session:
                # Prepare alert records for bulk insert
                alert_records = []
                for alert in alerts:
                    alert_record = {
                        'alert_id': alert.alert_id,
                        'user_id': alert.user_id,
                        'timestamp': alert.timestamp,
                        'anomaly_score': alert.anomaly_score,
                        'risk_level': alert.risk_level.value if isinstance(alert.risk_level, RiskLevel) else alert.risk_level,
                        'pattern_type': alert.pattern_type.value if isinstance(alert.pattern_type, PatternType) else alert.pattern_type,
                        'explanation': alert.explanation,
                        'trade_ids': alert.trade_ids,
                        'recommended_action': alert.recommended_action,
                        'is_reviewed': alert.is_reviewed,
                        'is_true_positive': alert.is_true_positive,
                        'reviewer_notes': alert.reviewer_notes
                    }
                    alert_records.append(alert_record)
                
                # Batch insert using bulk_insert_mappings
                session.bulk_insert_mappings(AlertModel, alert_records)
                
            self.logger.info(f"Successfully saved {len(alerts)} alerts")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save alerts batch: {str(e)}")
            return False
    
    def get_alerts(self, filters: Optional[Dict[str, Any]] = None) -> List[Alert]:
        """
        Retrieve alerts from database
        
        Args:
            filters: Optional filters (user_id, risk_level, start_date, end_date, is_reviewed, limit)
            
        Returns:
            List of Alert objects
        """
        filters = filters or {}
        
        self.logger.info(f"Retrieving alerts with filters: {filters}")
        
        try:
            with self.get_session() as session:
                query = session.query(AlertModel)
                
                # Apply filters
                if 'user_id' in filters:
                    query = query.filter(AlertModel.user_id == filters['user_id'])
                
                if 'risk_level' in filters:
                    query = query.filter(AlertModel.risk_level == filters['risk_level'])
                
                if 'pattern_type' in filters:
                    query = query.filter(AlertModel.pattern_type == filters['pattern_type'])
                
                if 'start_date' in filters:
                    query = query.filter(AlertModel.timestamp >= filters['start_date'])
                
                if 'end_date' in filters:
                    query = query.filter(AlertModel.timestamp <= filters['end_date'])
                
                if 'is_reviewed' in filters:
                    query = query.filter(AlertModel.is_reviewed == filters['is_reviewed'])
                
                # Apply ordering
                query = query.order_by(AlertModel.timestamp.desc())
                
                # Apply limit
                if 'limit' in filters:
                    query = query.limit(filters['limit'])
                
                # Execute query
                alert_models = query.all()
                
                # Convert to Alert objects
                alerts = []
                for am in alert_models:
                    alert = Alert(
                        alert_id=am.alert_id,
                        timestamp=am.timestamp,
                        user_id=am.user_id,
                        trade_ids=am.trade_ids or [],
                        anomaly_score=am.anomaly_score,
                        risk_level=RiskLevel[am.risk_level],
                        pattern_type=PatternType[am.pattern_type],
                        explanation=am.explanation or "",
                        recommended_action=am.recommended_action or "",
                        is_reviewed=am.is_reviewed,
                        is_true_positive=am.is_true_positive,
                        reviewer_notes=am.reviewer_notes
                    )
                    alerts.append(alert)
                
                self.logger.info(f"Retrieved {len(alerts)} alerts")
                return alerts
                
        except Exception as e:
            self.logger.error(f"Failed to retrieve alerts: {str(e)}")
            return []
    
    def delete_trades(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """
        Delete trades from database
        
        Args:
            filters: Filters to identify trades to delete
            
        Returns:
            Number of deleted records
        """
        filters = filters or {}
        
        self.logger.info(f"Deleting trades with filters: {filters}")
        
        try:
            with self.get_session() as session:
                query = session.query(TradeModel)
                
                # Apply filters
                if 'user_id' in filters:
                    query = query.filter(TradeModel.user_id == filters['user_id'])
                
                if 'symbol' in filters:
                    query = query.filter(TradeModel.symbol == filters['symbol'])
                
                if 'start_date' in filters:
                    query = query.filter(TradeModel.timestamp >= filters['start_date'])
                
                if 'end_date' in filters:
                    query = query.filter(TradeModel.timestamp <= filters['end_date'])
                
                # Delete
                count = query.delete()
                
                self.logger.info(f"Deleted {count} trades")
                return count
                
        except Exception as e:
            self.logger.error(f"Failed to delete trades: {str(e)}")
            return 0
    
    def get_trade_count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """
        Get count of trades matching filters
        
        Args:
            filters: Optional filters
            
        Returns:
            Count of matching trades
        """
        filters = filters or {}
        
        try:
            with self.get_session() as session:
                query = session.query(TradeModel)
                
                # Apply filters
                if 'user_id' in filters:
                    query = query.filter(TradeModel.user_id == filters['user_id'])
                
                if 'symbol' in filters:
                    query = query.filter(TradeModel.symbol == filters['symbol'])
                
                if 'start_date' in filters:
                    query = query.filter(TradeModel.timestamp >= filters['start_date'])
                
                if 'end_date' in filters:
                    query = query.filter(TradeModel.timestamp <= filters['end_date'])
                
                count = query.count()
                return count
                
        except Exception as e:
            self.logger.error(f"Failed to get trade count: {str(e)}")
            return 0
