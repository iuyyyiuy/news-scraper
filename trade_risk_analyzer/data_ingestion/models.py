"""
SQLAlchemy Database Models

Defines database schema for trades, alerts, feedback, and model_versions tables.
"""

from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime, Text, JSON, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime


Base = declarative_base()


class TradeModel(Base):
    """
    Trade data model
    """
    __tablename__ = 'trades'
    
    trade_id = Column(String(255), primary_key=True)
    user_id = Column(String(255), nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    symbol = Column(String(50), nullable=False, index=True)
    price = Column(Float, nullable=False)
    volume = Column(Float, nullable=False)
    trade_type = Column(String(10), nullable=False)
    order_id = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=func.now())
    
    # Composite indices for common queries
    __table_args__ = (
        Index('idx_user_timestamp', 'user_id', 'timestamp'),
        Index('idx_symbol_timestamp', 'symbol', 'timestamp'),
    )
    
    def __repr__(self):
        return f"<Trade(trade_id='{self.trade_id}', user_id='{self.user_id}', symbol='{self.symbol}')>"


class AlertModel(Base):
    """
    Alert data model
    """
    __tablename__ = 'alerts'
    
    alert_id = Column(String(255), primary_key=True)
    user_id = Column(String(255), nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    anomaly_score = Column(Float, nullable=False)
    risk_level = Column(String(10), nullable=False, index=True)
    pattern_type = Column(String(50), nullable=False)
    explanation = Column(Text, nullable=True)
    trade_ids = Column(JSON, nullable=True)
    recommended_action = Column(Text, nullable=True)
    is_reviewed = Column(Boolean, default=False, index=True)
    is_true_positive = Column(Boolean, nullable=True)
    reviewer_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.now())
    
    def __repr__(self):
        return f"<Alert(alert_id='{self.alert_id}', user_id='{self.user_id}', risk_level='{self.risk_level}')>"


class FeedbackModel(Base):
    """
    Feedback data model
    """
    __tablename__ = 'feedback'
    
    feedback_id = Column(String(255), primary_key=True)
    alert_id = Column(String(255), ForeignKey('alerts.alert_id'), nullable=False, index=True)
    is_true_positive = Column(Boolean, nullable=False)
    notes = Column(Text, nullable=True)
    submitted_by = Column(String(255), nullable=True)
    submitted_at = Column(DateTime, default=func.now())
    
    def __repr__(self):
        return f"<Feedback(feedback_id='{self.feedback_id}', alert_id='{self.alert_id}')>"


class ModelVersionModel(Base):
    """
    Model version data model
    """
    __tablename__ = 'model_versions'
    
    version_id = Column(String(255), primary_key=True)
    model_type = Column(String(50), nullable=False, index=True)
    trained_at = Column(DateTime, nullable=False)
    training_samples = Column(Integer, nullable=True)
    performance_metrics = Column(JSON, nullable=True)
    model_path = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=False, index=True)
    created_at = Column(DateTime, default=func.now())
    
    def __repr__(self):
        return f"<ModelVersion(version_id='{self.version_id}', model_type='{self.model_type}')>"


# Futures Market Models

class FuturesFundingRateModel(Base):
    """
    Futures funding rate data model
    """
    __tablename__ = 'futures_funding_rates'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    market = Column(String(50), nullable=False, index=True)
    funding_rate = Column(Float, nullable=False)
    funding_time = Column(DateTime, nullable=False, index=True)
    next_funding_time = Column(DateTime, nullable=True)
    predicted_rate = Column(Float, nullable=True)
    created_at = Column(DateTime, default=func.now())
    
    __table_args__ = (
        Index('idx_market_funding_time', 'market', 'funding_time'),
    )
    
    def __repr__(self):
        return f"<FuturesFundingRate(market='{self.market}', rate={self.funding_rate})>"


class FuturesLiquidationModel(Base):
    """
    Futures liquidation data model
    """
    __tablename__ = 'futures_liquidations'
    
    liquidation_id = Column(String(255), primary_key=True)
    market = Column(String(50), nullable=False, index=True)
    side = Column(String(10), nullable=False)  # LONG or SHORT
    price = Column(Float, nullable=False)
    volume = Column(Float, nullable=False)
    timestamp = Column(DateTime, nullable=False, index=True)
    liquidation_type = Column(String(20), nullable=True)  # ADL or FORCED
    created_at = Column(DateTime, default=func.now())
    
    __table_args__ = (
        Index('idx_market_timestamp', 'market', 'timestamp'),
    )
    
    def __repr__(self):
        return f"<FuturesLiquidation(market='{self.market}', side='{self.side}', volume={self.volume})>"


class FuturesBasisHistoryModel(Base):
    """
    Futures basis history data model
    """
    __tablename__ = 'futures_basis_history'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    market = Column(String(50), nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    futures_price = Column(Float, nullable=False)
    spot_price = Column(Float, nullable=False)
    basis = Column(Float, nullable=False)
    basis_rate = Column(Float, nullable=False)
    created_at = Column(DateTime, default=func.now())
    
    __table_args__ = (
        Index('idx_market_timestamp_basis', 'market', 'timestamp'),
    )
    
    def __repr__(self):
        return f"<FuturesBasisHistory(market='{self.market}', basis_rate={self.basis_rate})>"


class MarketSnapshotModel(Base):
    """
    Market snapshot data model for orderbook and kline storage
    """
    __tablename__ = 'market_snapshots'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    market = Column(String(50), nullable=False, index=True)
    market_type = Column(String(10), nullable=False, index=True)  # spot or futures
    timestamp = Column(DateTime, nullable=False, index=True)
    price = Column(Float, nullable=False)
    volume_24h = Column(Float, nullable=True)
    orderbook_data = Column(JSON, nullable=True)
    kline_data = Column(JSON, nullable=True)
    open_interest = Column(Float, nullable=True)  # For futures only
    created_at = Column(DateTime, default=func.now())
    
    __table_args__ = (
        Index('idx_market_type_timestamp', 'market', 'market_type', 'timestamp'),
    )
    
    def __repr__(self):
        return f"<MarketSnapshot(market='{self.market}', type='{self.market_type}', price={self.price})>"


# Update TradeModel to include market_type
def add_market_type_to_trades():
    """
    Migration function to add market_type column to trades table
    This should be run as a database migration
    """
    # ALTER TABLE trades ADD COLUMN market_type VARCHAR(10) DEFAULT 'spot';
    # CREATE INDEX idx_market_type ON trades(market_type);
    pass
