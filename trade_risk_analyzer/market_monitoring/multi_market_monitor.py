"""
Multi-Market Monitor

Efficiently monitors all markets on an exchange with intelligent scheduling,
prioritization, and resource management.
"""

import asyncio
from typing import List, Dict, Any, Optional, Set, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass
from collections import defaultdict
import heapq

from trade_risk_analyzer.core.logger import get_logger
from trade_risk_analyzer.core.base import RiskLevel
from trade_risk_analyzer.market_monitoring.mcp_client import MCPClient, MCPConfig
from trade_risk_analyzer.market_monitoring.market_analyzer import MarketAnalyzer, MarketAlert


logger = get_logger(__name__)


@dataclass
class MarketPriority:
    """Market priority for monitoring"""
    market: str
    priority_score: float
    volume_24h: float
    last_alert_time: Optional[datetime] = None
    alert_count: int = 0
    check_interval: int = 60  # seconds
    
    def __lt__(self, other):
        """For priority queue ordering"""
        return self.priority_score > other.priority_score


@dataclass
class MonitoringStats:
    """Statistics for multi-market monitoring"""
    total_markets: int = 0
    active_markets: int = 0
    total_checks: int = 0
    total_alerts: int = 0
    high_risk_markets: int = 0
    medium_risk_markets: int = 0
    start_time: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        uptime = (datetime.now() - self.start_time).total_seconds() if self.start_time else 0
        return {
            'total_markets': self.total_markets,
            'active_markets': self.active_markets,
            'total_checks': self.total_checks,
            'total_alerts': self.total_alerts,
            'high_risk_markets': self.high_risk_markets,
            'medium_risk_markets': self.medium_risk_markets,
            'uptime_seconds': uptime,
            'checks_per_minute': (self.total_checks / uptime * 60) if uptime > 0 else 0
        }


class MultiMarketMonitor:
    """
    Monitors all markets on an exchange efficiently
    
    Features:
    - Auto-discovery of all markets
    - Priority-based scheduling
    - Volume-based filtering
    - Adaptive check intervals
    - Resource management
    """
    
    def __init__(
        self,
        mcp_config: Optional[MCPConfig] = None,
        min_volume_24h: float = 10000.0,  # Min $10k daily volume
        max_concurrent: int = 5,  # Max concurrent market checks
        base_interval: int = 60,  # Base check interval (seconds)
        high_priority_interval: int = 30,  # High priority interval
        low_priority_interval: int = 300  # Low priority interval (5 min)
    ):
        """
        Initialize multi-market monitor
        
        Args:
            mcp_config: MCP client configuration
            min_volume_24h: Minimum 24h volume to monitor
            max_concurrent: Maximum concurrent market checks
            base_interval: Base check interval in seconds
            high_priority_interval: Interval for high priority markets
            low_priority_interval: Interval for low priority markets
        """
        self.mcp_client = MCPClient(mcp_config or MCPConfig())
        self.min_volume_24h = min_volume_24h
        self.max_concurrent = max_concurrent
        self.base_interval = base_interval
        self.high_priority_interval = high_priority_interval
        self.low_priority_interval = low_priority_interval
        self.logger = logger
        
        # Market analyzers (one per market for efficiency)
        self._analyzers: Dict[str, MarketAnalyzer] = {}
        
        # Market priorities
        self._market_priorities: Dict[str, MarketPriority] = {}
        
        # Market types (spot or futures)
        self._market_types: Dict[str, str] = {}
        
        # Monitoring state
        self._monitoring = False
        self._stats = MonitoringStats()
        
        # Alert callbacks
        self._alert_callbacks: List[Callable[[MarketAlert], None]] = []
        
        # Market risk levels
        self._market_risks: Dict[str, RiskLevel] = {}
    
    async def discover_markets(
        self,
        quote_currency: Optional[str] = "USDT",
        min_volume: Optional[float] = None
    ) -> List[str]:
        """
        Discover all available spot markets
        
        Args:
            quote_currency: Filter by quote currency (e.g., "USDT")
            min_volume: Minimum 24h volume filter
            
        Returns:
            List of market symbols
        """
        self.logger.info("Discovering spot markets...")
        
        try:
            # Get all tickers
            all_tickers = await self.mcp_client.get_all_tickers()
            
            if not all_tickers:
                self.logger.warning("No tickers retrieved")
                return []
            
            markets = []
            min_vol = min_volume or self.min_volume_24h
            
            for ticker in all_tickers:
                market = ticker.get('market', '')
                volume_24h = float(ticker.get('volume_24h', 0))
                
                # Apply filters
                if quote_currency and not market.endswith(quote_currency):
                    continue
                
                if volume_24h < min_vol:
                    continue
                
                markets.append(market)
            
            self.logger.info(f"Discovered {len(markets)} spot markets (filtered from {len(all_tickers)} total)")
            
            return sorted(markets)
            
        except Exception as e:
            self.logger.error(f"Failed to discover spot markets: {e}", exc_info=True)
            return []
    
    async def discover_futures_markets(
        self,
        quote_currency: Optional[str] = "USDT",
        min_volume: Optional[float] = None
    ) -> List[str]:
        """
        Discover all available futures markets
        
        Args:
            quote_currency: Filter by quote currency (e.g., "USDT")
            min_volume: Minimum 24h volume filter
            
        Returns:
            List of futures market symbols
        """
        self.logger.info("Discovering futures markets...")
        
        try:
            # Get all futures tickers
            all_tickers = await self.mcp_client.get_all_futures_tickers()
            
            if not all_tickers:
                self.logger.warning("No futures tickers retrieved")
                return []
            
            markets = []
            min_vol = min_volume or self.min_volume_24h
            
            for ticker in all_tickers:
                market = ticker.get('market', '')
                volume_24h = float(ticker.get('volume_24h', 0))
                
                # Apply filters
                if quote_currency and not market.endswith(quote_currency):
                    continue
                
                if volume_24h < min_vol:
                    continue
                
                markets.append(market)
            
            self.logger.info(f"Discovered {len(markets)} futures markets (filtered from {len(all_tickers)} total)")
            
            return sorted(markets)
            
        except Exception as e:
            self.logger.error(f"Failed to discover futures markets: {e}", exc_info=True)
            return []
    
    async def start_monitoring_all(
        self,
        quote_currency: str = "USDT",
        min_volume: Optional[float] = None,
        market_type: str = "both"  # "spot", "futures", or "both"
    ) -> None:
        """
        Start monitoring all markets
        
        Args:
            quote_currency: Quote currency filter
            min_volume: Minimum volume filter
            market_type: Type of markets to monitor ("spot", "futures", or "both")
        """
        self.logger.info(f"Starting multi-market monitoring ({market_type})...")
        
        # Connect to MCP
        connected = await self.mcp_client.connect()
        if not connected:
            self.logger.error("Failed to connect to MCP server")
            return
        
        try:
            # Discover markets based on type
            markets = []
            if market_type in ["spot", "both"]:
                spot_markets = await self.discover_markets(quote_currency, min_volume)
                markets.extend([(m, "spot") for m in spot_markets])
            
            if market_type in ["futures", "both"]:
                futures_markets = await self.discover_futures_markets(quote_currency, min_volume)
                markets.extend([(m, "futures") for m in futures_markets])
            
            if not markets:
                self.logger.error("No markets to monitor")
                return
            
            # Initialize priorities
            await self._initialize_priorities([m[0] for m in markets])
            
            # Store market types
            self._market_types = {m[0]: m[1] for m in markets}
            
            # Start monitoring
            self._monitoring = True
            self._stats = MonitoringStats(
                total_markets=len(markets),
                active_markets=len(markets),
                start_time=datetime.now()
            )
            
            self.logger.info(f"Monitoring {len(markets)} markets ({market_type})")
            
            # Create monitoring tasks
            tasks = []
            
            # Priority-based monitoring
            tasks.append(self._priority_monitoring_loop())
            
            # Periodic priority updates
            tasks.append(self._priority_update_loop())
            
            # Stats reporting
            tasks.append(self._stats_reporting_loop())
            
            # Run all tasks
            await asyncio.gather(*tasks)
            
        finally:
            await self.mcp_client.disconnect()
            self._monitoring = False
    
    async def start_monitoring_markets(
        self,
        markets: List[str]
    ) -> None:
        """
        Start monitoring specific markets
        
        Args:
            markets: List of market symbols to monitor
        """
        self.logger.info(f"Starting monitoring for {len(markets)} specific markets...")
        
        # Connect to MCP
        connected = await self.mcp_client.connect()
        if not connected:
            self.logger.error("Failed to connect to MCP server")
            return
        
        try:
            # Initialize priorities
            await self._initialize_priorities(markets)
            
            # Start monitoring
            self._monitoring = True
            self._stats = MonitoringStats(
                total_markets=len(markets),
                active_markets=len(markets),
                start_time=datetime.now()
            )
            
            # Create monitoring tasks
            tasks = [
                self._priority_monitoring_loop(),
                self._priority_update_loop(),
                self._stats_reporting_loop()
            ]
            
            await asyncio.gather(*tasks)
            
        finally:
            await self.mcp_client.disconnect()
            self._monitoring = False
    
    def stop_monitoring(self) -> None:
        """Stop monitoring"""
        self.logger.info("Stopping multi-market monitoring")
        self._monitoring = False
    
    def add_alert_callback(self, callback: Callable[[MarketAlert], None]) -> None:
        """Add alert callback"""
        self._alert_callbacks.append(callback)
    
    async def _initialize_priorities(self, markets: List[str]) -> None:
        """Initialize market priorities based on volume"""
        self.logger.info("Initializing market priorities...")
        
        # Get tickers for all markets
        all_tickers = await self.mcp_client.get_all_tickers()
        
        if not all_tickers:
            # Fallback: equal priority
            for market in markets:
                self._market_priorities[market] = MarketPriority(
                    market=market,
                    priority_score=1.0,
                    volume_24h=0,
                    check_interval=self.base_interval
                )
            return
        
        # Create ticker lookup
        ticker_map = {t.get('market'): t for t in all_tickers}
        
        # Calculate priorities
        volumes = []
        for market in markets:
            ticker = ticker_map.get(market, {})
            volume = float(ticker.get('volume_24h', 0))
            volumes.append(volume)
        
        # Normalize volumes to priority scores (0-1)
        max_volume = max(volumes) if volumes else 1
        
        for market, volume in zip(markets, volumes):
            # Priority score based on volume
            priority_score = volume / max_volume if max_volume > 0 else 0.5
            
            # Determine check interval based on priority
            if priority_score > 0.7:
                interval = self.high_priority_interval
            elif priority_score > 0.3:
                interval = self.base_interval
            else:
                interval = self.low_priority_interval
            
            self._market_priorities[market] = MarketPriority(
                market=market,
                priority_score=priority_score,
                volume_24h=volume,
                check_interval=interval
            )
        
        self.logger.info(
            f"Initialized {len(self._market_priorities)} market priorities "
            f"(high: {sum(1 for p in self._market_priorities.values() if p.check_interval == self.high_priority_interval)}, "
            f"medium: {sum(1 for p in self._market_priorities.values() if p.check_interval == self.base_interval)}, "
            f"low: {sum(1 for p in self._market_priorities.values() if p.check_interval == self.low_priority_interval)})"
        )
    
    async def _priority_monitoring_loop(self) -> None:
        """Main monitoring loop with priority scheduling"""
        # Create priority queue
        next_check_times: List[Tuple[float, str]] = []
        
        # Initialize with current time
        now = datetime.now().timestamp()
        for market, priority in self._market_priorities.items():
            heapq.heappush(next_check_times, (now, market))
        
        # Semaphore for concurrent checks
        semaphore = asyncio.Semaphore(self.max_concurrent)
        
        while self._monitoring:
            try:
                # Get next market to check
                if not next_check_times:
                    await asyncio.sleep(1)
                    continue
                
                next_time, market = heapq.heappop(next_check_times)
                
                # Wait until it's time to check
                now = datetime.now().timestamp()
                if next_time > now:
                    # Put it back and wait
                    heapq.heappush(next_check_times, (next_time, market))
                    await asyncio.sleep(min(1, next_time - now))
                    continue
                
                # Check market (with concurrency limit)
                async with semaphore:
                    await self._check_market(market)
                
                # Schedule next check
                priority = self._market_priorities.get(market)
                if priority:
                    next_time = datetime.now().timestamp() + priority.check_interval
                    heapq.heappush(next_check_times, (next_time, market))
                
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}", exc_info=True)
                await asyncio.sleep(1)
    
    async def _check_market(self, market: str) -> None:
        """Check a single market"""
        try:
            # Get or create analyzer
            if market not in self._analyzers:
                self._analyzers[market] = MarketAnalyzer()
                
                # Add alert callback
                def market_alert_callback(alert: MarketAlert):
                    self._handle_alert(alert)
                
                self._analyzers[market].add_alert_callback(market_alert_callback)
            
            analyzer = self._analyzers[market]
            
            # Analyze market
            alerts = await analyzer.analyze_market(market)
            
            # Update stats
            self._stats.total_checks += 1
            
            # Update priority based on alerts
            if alerts:
                priority = self._market_priorities.get(market)
                if priority:
                    priority.alert_count += len(alerts)
                    priority.last_alert_time = datetime.now()
                    
                    # Increase priority if alerts detected
                    priority.priority_score = min(1.0, priority.priority_score + 0.1)
                    
                    # Decrease check interval for high-alert markets
                    if priority.alert_count > 3:
                        priority.check_interval = max(
                            self.high_priority_interval,
                            priority.check_interval // 2
                        )
            
            # Update market risk level
            if alerts:
                max_risk = max(alert.risk_level for alert in alerts)
                self._market_risks[market] = max_risk
            
        except Exception as e:
            self.logger.error(f"Error checking market {market}: {e}")
    
    async def _priority_update_loop(self) -> None:
        """Periodically update market priorities"""
        while self._monitoring:
            try:
                await asyncio.sleep(300)  # Update every 5 minutes
                
                # Get fresh ticker data
                all_tickers = await self.mcp_client.get_all_tickers()
                
                if all_tickers:
                    ticker_map = {t.get('market'): t for t in all_tickers}
                    
                    # Update volumes and priorities
                    for market, priority in self._market_priorities.items():
                        ticker = ticker_map.get(market, {})
                        new_volume = float(ticker.get('volume_24h', 0))
                        
                        # Update volume
                        priority.volume_24h = new_volume
                        
                        # Decay alert count over time
                        if priority.last_alert_time:
                            hours_since = (datetime.now() - priority.last_alert_time).total_seconds() / 3600
                            if hours_since > 1:
                                priority.alert_count = max(0, priority.alert_count - 1)
                    
                    self.logger.info("Updated market priorities")
                
            except Exception as e:
                self.logger.error(f"Error updating priorities: {e}")
    
    async def _stats_reporting_loop(self) -> None:
        """Periodically report statistics"""
        while self._monitoring:
            try:
                await asyncio.sleep(60)  # Report every minute
                
                # Update risk counts
                self._stats.high_risk_markets = sum(
                    1 for risk in self._market_risks.values()
                    if risk == RiskLevel.HIGH
                )
                self._stats.medium_risk_markets = sum(
                    1 for risk in self._market_risks.values()
                    if risk == RiskLevel.MEDIUM
                )
                
                # Log stats
                stats = self._stats.to_dict()
                self.logger.info(
                    f"Monitoring stats: {stats['active_markets']} markets, "
                    f"{stats['total_checks']} checks, {stats['total_alerts']} alerts, "
                    f"{stats['checks_per_minute']:.1f} checks/min"
                )
                
            except Exception as e:
                self.logger.error(f"Error reporting stats: {e}")
    
    def _handle_alert(self, alert: MarketAlert) -> None:
        """Handle generated alert"""
        self._stats.total_alerts += 1
        
        # Call all callbacks
        for callback in self._alert_callbacks:
            try:
                callback(alert)
            except Exception as e:
                self.logger.error(f"Error in alert callback: {e}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get monitoring statistics"""
        return self._stats.to_dict()
    
    def get_high_risk_markets(self) -> List[str]:
        """Get list of high-risk markets"""
        return [
            market for market, risk in self._market_risks.items()
            if risk == RiskLevel.HIGH
        ]
    
    def get_market_priorities(self) -> List[MarketPriority]:
        """Get market priorities sorted by score"""
        return sorted(
            self._market_priorities.values(),
            key=lambda p: p.priority_score,
            reverse=True
        )
