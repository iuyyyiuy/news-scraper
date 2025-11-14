"""
Market Monitoring Module - Real-time market surveillance via MCP services
"""

from trade_risk_analyzer.market_monitoring.mcp_client import (
    MCPClient,
    MarketDataType,
    MCPConfig
)
from trade_risk_analyzer.market_monitoring.market_analyzer import (
    MarketAnalyzer,
    MarketAlert,
    MarketAlertType,
    MarketRiskIndicators
)
from trade_risk_analyzer.market_monitoring.orderbook_monitor import (
    OrderBookMonitor,
    OrderBookSnapshot,
    OrderBookAnomaly
)
from trade_risk_analyzer.market_monitoring.kline_monitor import (
    KLineMonitor,
    KLineData,
    PriceAnomaly
)
from trade_risk_analyzer.market_monitoring.multi_market_monitor import (
    MultiMarketMonitor,
    MarketPriority,
    MonitoringStats
)

__all__ = [
    "MCPClient",
    "MarketDataType",
    "MCPConfig",
    "MarketAnalyzer",
    "MarketAlert",
    "MarketAlertType",
    "MarketRiskIndicators",
    "OrderBookMonitor",
    "OrderBookSnapshot",
    "OrderBookAnomaly",
    "KLineMonitor",
    "KLineData",
    "PriceAnomaly",
    "MultiMarketMonitor",
    "MarketPriority",
    "MonitoringStats",
]
