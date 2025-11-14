"""
Database Migration: Add Futures Tables

Adds futures-specific tables and updates existing tables for futures support.
"""

from sqlalchemy import create_engine, text
from trade_risk_analyzer.core.config import get_config
from trade_risk_analyzer.core.logger import get_logger
from trade_risk_analyzer.data_ingestion.models import (
    Base,
    FuturesFundingRateModel,
    FuturesLiquidationModel,
    FuturesBasisHistoryModel,
    MarketSnapshotModel
)


logger = get_logger(__name__)


def run_migration(database_url: str = None):
    """
    Run database migration to add futures tables
    
    Args:
        database_url: Database connection URL (uses config if not provided)
    """
    try:
        # Get database URL
        if not database_url:
            config = get_config()
            database_url = config.get('database', {}).get('url', 'sqlite:///trade_risk_analyzer.db')
        
        logger.info(f"Running futures tables migration on: {database_url}")
        
        # Create engine
        engine = create_engine(database_url)
        
        # Create all futures tables
        logger.info("Creating futures tables...")
        Base.metadata.create_all(engine, tables=[
            FuturesFundingRateModel.__table__,
            FuturesLiquidationModel.__table__,
            FuturesBasisHistoryModel.__table__,
            MarketSnapshotModel.__table__
        ])
        
        # Add market_type column to trades table if it doesn't exist
        logger.info("Adding market_type column to trades table...")
        with engine.connect() as conn:
            try:
                # Check if column exists
                result = conn.execute(text("SELECT market_type FROM trades LIMIT 1"))
                logger.info("market_type column already exists")
            except Exception:
                # Column doesn't exist, add it
                conn.execute(text("ALTER TABLE trades ADD COLUMN market_type VARCHAR(10) DEFAULT 'spot'"))
                conn.execute(text("CREATE INDEX idx_market_type ON trades(market_type)"))
                conn.commit()
                logger.info("Added market_type column to trades table")
        
        logger.info("Migration completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Migration failed: {e}", exc_info=True)
        return False


if __name__ == "__main__":
    import sys
    
    # Get database URL from command line or use default
    db_url = sys.argv[1] if len(sys.argv) > 1 else None
    
    success = run_migration(db_url)
    sys.exit(0 if success else 1)
