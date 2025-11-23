"""
Futures Data Collection and Storage Pipeline

Periodically collects futures market data and stores it in the database.
"""

import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from trade_risk_analyzer.core.logger import get_logger
from trade_risk_analyzer.core.config import get_config
from trade_risk_analyzer.market_monitoring.mcp_client import MCPClient, MCPConfig
from trade_risk_analyzer.data_ingestion.models import (
    FuturesFundingRateModel,
    FuturesLiquidationModel,
    FuturesBasisHistoryModel,
    MarketSnapshotModel
)


logger = get_logger(__name__)


class FuturesDataCollector:
    """
    Collects and stores futures market data
    
    Features:
    - Periodic funding rate collection
    - Liquidation event monitoring
    - Basis history collection
    - Orderbook snapshot storage
    - K-line data archival
    """
    
    def __init__(
        self,
        mcp_client: MCPClient,
        database_url: Optional[str] = None,
        funding_rate_interval: int = 300,  # 5 minutes
        liquidation_check_interval: int = 60,  # 1 minute
        basis_history_interval: int = 3600,  # 1 hour
        orderbook_snapshot_interval: int = 30  # 30 seconds
    ):
        """
        Initialize futures data collector
        
        Args:
            mcp_client: MCP client for fetching data
            database_url: Database connection URL
            funding_rate_interval: Interval for funding rate collection (seconds)
            liquidation_check_interval: Interval for liquidation checks (seconds)
            basis_history_interval: Interval for basis history collection (seconds)
            orderbook_snapshot_interval: Interval for orderbook snapshots (seconds)
        """
        self.mcp_client = mcp_client
        self.funding_rate_interval = funding_rate_interval
        self.liquidation_check_interval = liquidation_check_interval
        self.basis_history_interval = basis_history_interval
        self.orderbook_snapshot_interval = orderbook_snapshot_interval
        self.logger = logger
        
        # Database setup
        if not database_url:
            config = get_config()
            database_url = config.get('database', {}).get('url', 'sqlite:///trade_risk_analyzer.db')
        
        self.engine = create_engine(database_url)
        self.Session = sessionmaker(bind=self.engine)
        
        # Collection state
        self._collecting = False
        self._markets: List[str] = []
    
    async def start_collection(self, markets: List[str]) -> None:
        """
        Start data collection for specified markets
        
        Args:
            markets: List of futures market symbols to monitor
        """
        self.logger.info(f"Starting data collection for {len(markets)} futures markets")
        
        self._markets = markets
        self._collecting = True
        
        # Create collection tasks
        tasks = [
            self._collect_funding_rates_loop(),
            self._collect_liquidations_loop(),
            self._collect_basis_history_loop(),
            self._collect_orderbook_snapshots_loop()
        ]
        
        await asyncio.gather(*tasks)
    
    def stop_collection(self) -> None:
        """Stop data collection"""
        self.logger.info("Stopping data collection")
        self._collecting = False
    
    async def _collect_funding_rates_loop(self) -> None:
        """Periodically collect funding rates"""
        while self._collecting:
            try:
                for market in self._markets:
                    await self._collect_funding_rate(market)
                
                await asyncio.sleep(self.funding_rate_interval)
                
            except Exception as e:
                self.logger.error(f"Error in funding rate collection loop: {e}")
                await asyncio.sleep(60)
    
    async def _collect_funding_rate(self, market: str) -> None:
        """
        Collect and store funding rate for a market
        
        Args:
            market: Futures market symbol
        """
        try:
            funding_data = await self.mcp_client.get_futures_funding_rate(market)
            
            if not funding_data:
                return
            
            # Store in database
            session = self.Session()
            try:
                funding_rate = FuturesFundingRateModel(
                    market=market,
                    funding_rate=float(funding_data.get('funding_rate', 0)),
                    funding_time=datetime.fromisoformat(funding_data.get('funding_time', '').replace('Z', '+00:00')),
                    next_funding_time=datetime.fromisoformat(funding_data.get('next_funding_time', '').replace('Z', '+00:00')) if funding_data.get('next_funding_time') else None,
                    predicted_rate=float(funding_data.get('predicted_rate', 0)) if funding_data.get('predicted_rate') else None
                )
                
                session.add(funding_rate)
                session.commit()
                
                self.logger.debug(f"Stored funding rate for {market}")
                
            finally:
                session.close()
                
        except Exception as e:
            self.logger.error(f"Error collecting funding rate for {market}: {e}")
    
    async def _collect_liquidations_loop(self) -> None:
        """Periodically collect liquidation events"""
        while self._collecting:
            try:
                for market in self._markets:
                    await self._collect_liquidations(market)
                
                await asyncio.sleep(self.liquidation_check_interval)
                
            except Exception as e:
                self.logger.error(f"Error in liquidation collection loop: {e}")
                await asyncio.sleep(60)
    
    async def _collect_liquidations(self, market: str) -> None:
        """
        Collect and store liquidation events for a market
        
        Args:
            market: Futures market symbol
        """
        try:
            liquidations = await self.mcp_client.get_futures_liquidations(market, limit=50)
            
            if not liquidations:
                return
            
            # Store in database
            session = self.Session()
            try:
                for liq in liquidations:
                    # Check if already exists
                    liq_id = liq.get('liquidation_id', f"{market}_{liq.get('timestamp')}")
                    existing = session.query(FuturesLiquidationModel).filter_by(liquidation_id=liq_id).first()
                    
                    if existing:
                        continue
                    
                    liquidation = FuturesLiquidationModel(
                        liquidation_id=liq_id,
                        market=market,
                        side=liq.get('side', 'UNKNOWN'),
                        price=float(liq.get('price', 0)),
                        volume=float(liq.get('volume', 0)),
                        timestamp=datetime.fromisoformat(liq.get('timestamp', '').replace('Z', '+00:00')),
                        liquidation_type=liq.get('type')
                    )
                    
                    session.add(liquidation)
                
                session.commit()
                self.logger.debug(f"Stored liquidations for {market}")
                
            finally:
                session.close()
                
        except Exception as e:
            self.logger.error(f"Error collecting liquidations for {market}: {e}")
    
    async def _collect_basis_history_loop(self) -> None:
        """Periodically collect basis history"""
        while self._collecting:
            try:
                for market in self._markets:
                    await self._collect_basis_history(market)
                
                await asyncio.sleep(self.basis_history_interval)
                
            except Exception as e:
                self.logger.error(f"Error in basis history collection loop: {e}")
                await asyncio.sleep(300)
    
    async def _collect_basis_history(self, market: str) -> None:
        """
        Collect and store basis history for a market
        
        Args:
            market: Futures market symbol
        """
        try:
            basis_history = await self.mcp_client.get_futures_basis_history(market, interval="1hour", limit=24)
            
            if not basis_history:
                return
            
            # Store in database
            session = self.Session()
            try:
                for basis in basis_history:
                    basis_record = FuturesBasisHistoryModel(
                        market=market,
                        timestamp=datetime.fromisoformat(basis.get('timestamp', '').replace('Z', '+00:00')),
                        futures_price=float(basis.get('futures_price', 0)),
                        spot_price=float(basis.get('spot_price', 0)),
                        basis=float(basis.get('basis', 0)),
                        basis_rate=float(basis.get('basis_rate', 0))
                    )
                    
                    session.add(basis_record)
                
                session.commit()
                self.logger.debug(f"Stored basis history for {market}")
                
            finally:
                session.close()
                
        except Exception as e:
            self.logger.error(f"Error collecting basis history for {market}: {e}")
    
    async def _collect_orderbook_snapshots_loop(self) -> None:
        """Periodically collect orderbook snapshots"""
        while self._collecting:
            try:
                for market in self._markets:
                    await self._collect_orderbook_snapshot(market)
                
                await asyncio.sleep(self.orderbook_snapshot_interval)
                
            except Exception as e:
                self.logger.error(f"Error in orderbook snapshot collection loop: {e}")
                await asyncio.sleep(60)
    
    async def _collect_orderbook_snapshot(self, market: str) -> None:
        """
        Collect and store orderbook snapshot for a market
        
        Args:
            market: Futures market symbol
        """
        try:
            orderbook = await self.mcp_client.get_futures_orderbook(market, depth=20)
            ticker = await self.mcp_client.get_futures_ticker(market)
            
            if not orderbook or not ticker:
                return
            
            # Store in database
            session = self.Session()
            try:
                snapshot = MarketSnapshotModel(
                    market=market,
                    market_type='futures',
                    timestamp=datetime.now(),
                    price=float(ticker.get('last_price', 0)),
                    volume_24h=float(ticker.get('volume_24h', 0)),
                    orderbook_data=orderbook,
                    open_interest=float(ticker.get('open_interest', 0))
                )
                
                session.add(snapshot)
                session.commit()
                
                self.logger.debug(f"Stored orderbook snapshot for {market}")
                
            finally:
                session.close()
                
        except Exception as e:
            self.logger.error(f"Error collecting orderbook snapshot for {market}: {e}")
    
    async def cleanup_old_data(self, days_to_keep: int = 30) -> None:
        """
        Clean up old data from database
        
        Args:
            days_to_keep: Number of days of data to keep
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            
            session = self.Session()
            try:
                # Delete old funding rates
                session.query(FuturesFundingRateModel).filter(
                    FuturesFundingRateModel.created_at < cutoff_date
                ).delete()
                
                # Delete old liquidations
                session.query(FuturesLiquidationModel).filter(
                    FuturesLiquidationModel.created_at < cutoff_date
                ).delete()
                
                # Delete old basis history
                session.query(FuturesBasisHistoryModel).filter(
                    FuturesBasisHistoryModel.created_at < cutoff_date
                ).delete()
                
                # Delete old snapshots
                session.query(MarketSnapshotModel).filter(
                    MarketSnapshotModel.created_at < cutoff_date
                ).delete()
                
                session.commit()
                
                self.logger.info(f"Cleaned up data older than {days_to_keep} days")
                
            finally:
                session.close()
                
        except Exception as e:
            self.logger.error(f"Error cleaning up old data: {e}")
