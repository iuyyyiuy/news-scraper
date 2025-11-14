"""
MCP Client for CoinEx Exchange

Connects to CoinEx MCP server for real-time market data monitoring.
No API credentials required - uses public market data.
"""

import asyncio
import json
from typing import List, Dict, Any, Optional, Callable
from datetime import datetime
from enum import Enum
from dataclasses import dataclass
import subprocess
import sys

from trade_risk_analyzer.core.logger import get_logger


logger = get_logger(__name__)


class MarketDataType(Enum):
    """Types of market data available"""
    TICKER = "ticker"
    KLINE = "kline"
    ORDERBOOK = "orderbook"
    TRADES = "trades"
    MARKET_INFO = "market_info"
    # Futures-specific data types
    FUTURES_TICKER = "futures_ticker"
    FUTURES_KLINE = "futures_kline"
    FUTURES_ORDERBOOK = "futures_orderbook"
    FUNDING_RATE = "funding_rate"
    PREMIUM_INDEX = "premium_index"
    BASIS_HISTORY = "basis_history"
    LIQUIDATIONS = "liquidations"
    POSITION_TIERS = "position_tiers"


@dataclass
class MCPConfig:
    """Configuration for MCP client"""
    server_command: str = "uvx"
    server_args: List[str] = None
    reconnect_attempts: int = 3
    reconnect_delay: int = 5
    timeout: int = 30
    
    def __post_init__(self):
        if self.server_args is None:
            self.server_args = ["coinex-mcp-server"]


class MCPClient:
    """
    Client for CoinEx MCP server
    
    Provides access to real-time market data including:
    - Market tickers (price, volume, 24h change)
    - K-line/candlestick data
    - Order book depth
    - Recent trades
    - Market information
    """
    
    def __init__(self, config: Optional[MCPConfig] = None):
        """
        Initialize MCP client
        
        Args:
            config: MCP configuration
        """
        self.config = config or MCPConfig()
        self.logger = logger
        self._process = None
        self._connected = False
        self._callbacks: Dict[MarketDataType, List[Callable]] = {
            data_type: [] for data_type in MarketDataType
        }
    
    async def connect(self) -> bool:
        """
        Connect to CoinEx MCP server
        
        Returns:
            Success status
        """
        try:
            self.logger.info("Connecting to CoinEx MCP server...")
            
            # Start MCP server process
            self._process = await asyncio.create_subprocess_exec(
                self.config.server_command,
                *self.config.server_args,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                stdin=asyncio.subprocess.PIPE
            )
            
            self._connected = True
            self.logger.info("Connected to CoinEx MCP server")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to connect to MCP server: {e}", exc_info=True)
            return False
    
    async def disconnect(self) -> None:
        """Disconnect from MCP server"""
        if self._process:
            try:
                self._process.terminate()
                await self._process.wait()
                self.logger.info("Disconnected from MCP server")
            except Exception as e:
                self.logger.error(f"Error disconnecting: {e}")
        
        self._connected = False
    
    async def get_ticker(self, market: str) -> Optional[Dict[str, Any]]:
        """
        Get ticker data for a market
        
        Args:
            market: Market symbol (e.g., "BTCUSDT")
            
        Returns:
            Ticker data with price, volume, change, etc.
        """
        try:
            result = await self._call_tool("get_ticker", {"market": market})
            return result
        except Exception as e:
            self.logger.error(f"Failed to get ticker for {market}: {e}")
            return None
    
    async def get_kline(
        self,
        market: str,
        interval: str = "1min",
        limit: int = 100
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Get K-line (candlestick) data
        
        Args:
            market: Market symbol (e.g., "BTCUSDT")
            interval: Time interval (1min, 5min, 15min, 1hour, 1day, etc.)
            limit: Number of candles to retrieve
            
        Returns:
            List of K-line data points
        """
        try:
            result = await self._call_tool("get_kline", {
                "market": market,
                "interval": interval,
                "limit": limit
            })
            return result
        except Exception as e:
            self.logger.error(f"Failed to get K-line for {market}: {e}")
            return None
    
    async def get_orderbook(
        self,
        market: str,
        depth: int = 20
    ) -> Optional[Dict[str, Any]]:
        """
        Get order book depth
        
        Args:
            market: Market symbol (e.g., "BTCUSDT")
            depth: Number of price levels (default: 20)
            
        Returns:
            Order book with bids and asks
        """
        try:
            result = await self._call_tool("get_orderbook", {
                "market": market,
                "depth": depth
            })
            return result
        except Exception as e:
            self.logger.error(f"Failed to get order book for {market}: {e}")
            return None
    
    async def get_recent_trades(
        self,
        market: str,
        limit: int = 100
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Get recent trades
        
        Args:
            market: Market symbol (e.g., "BTCUSDT")
            limit: Number of trades to retrieve
            
        Returns:
            List of recent trades
        """
        try:
            result = await self._call_tool("get_recent_trades", {
                "market": market,
                "limit": limit
            })
            return result
        except Exception as e:
            self.logger.error(f"Failed to get recent trades for {market}: {e}")
            return None
    
    async def get_market_info(self, market: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Get market information
        
        Args:
            market: Market symbol (optional, returns all markets if None)
            
        Returns:
            Market information
        """
        try:
            params = {"market": market} if market else {}
            result = await self._call_tool("get_market_info", params)
            return result
        except Exception as e:
            self.logger.error(f"Failed to get market info: {e}")
            return None
    
    async def get_all_tickers(self) -> Optional[List[Dict[str, Any]]]:
        """
        Get tickers for all markets
        
        Returns:
            List of all market tickers
        """
        try:
            result = await self._call_tool("get_all_tickers", {})
            return result
        except Exception as e:
            self.logger.error(f"Failed to get all tickers: {e}")
            return None
    
    # Futures Market Methods
    
    async def get_futures_ticker(self, market: str) -> Optional[Dict[str, Any]]:
        """
        Get futures ticker data for a market
        
        Args:
            market: Futures market symbol (e.g., "BTCUSDT")
            
        Returns:
            Futures ticker data with price, volume, open interest, etc.
        """
        try:
            result = await self._call_tool("get_futures_ticker", {"market": market})
            return result
        except Exception as e:
            self.logger.error(f"Failed to get futures ticker for {market}: {e}")
            return None
    
    async def get_futures_kline(
        self,
        market: str,
        interval: str = "1min",
        limit: int = 100
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Get futures K-line (candlestick) data
        
        Args:
            market: Futures market symbol (e.g., "BTCUSDT")
            interval: Time interval (1min, 5min, 15min, 1hour, 1day, etc.)
            limit: Number of candles to retrieve
            
        Returns:
            List of futures K-line data points with open interest
        """
        try:
            result = await self._call_tool("get_futures_kline", {
                "market": market,
                "interval": interval,
                "limit": limit
            })
            return result
        except Exception as e:
            self.logger.error(f"Failed to get futures K-line for {market}: {e}")
            return None
    
    async def get_futures_orderbook(
        self,
        market: str,
        depth: int = 20
    ) -> Optional[Dict[str, Any]]:
        """
        Get futures order book depth
        
        Args:
            market: Futures market symbol (e.g., "BTCUSDT")
            depth: Number of price levels (default: 20)
            
        Returns:
            Futures order book with bids and asks
        """
        try:
            result = await self._call_tool("get_futures_orderbook", {
                "market": market,
                "depth": depth
            })
            return result
        except Exception as e:
            self.logger.error(f"Failed to get futures order book for {market}: {e}")
            return None
    
    async def get_futures_funding_rate(self, market: str) -> Optional[Dict[str, Any]]:
        """
        Get current funding rate for a futures market
        
        Args:
            market: Futures market symbol (e.g., "BTCUSDT")
            
        Returns:
            Funding rate data including current rate, next funding time, predicted rate
        """
        try:
            result = await self._call_tool("get_futures_funding_rate", {"market": market})
            return result
        except Exception as e:
            self.logger.error(f"Failed to get funding rate for {market}: {e}")
            return None
    
    async def get_futures_funding_rate_history(
        self,
        market: str,
        limit: int = 100
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Get historical funding rates for a futures market
        
        Args:
            market: Futures market symbol (e.g., "BTCUSDT")
            limit: Number of historical records to retrieve
            
        Returns:
            List of historical funding rate data
        """
        try:
            result = await self._call_tool("get_futures_funding_rate_history", {
                "market": market,
                "limit": limit
            })
            return result
        except Exception as e:
            self.logger.error(f"Failed to get funding rate history for {market}: {e}")
            return None
    
    async def get_futures_premium_index(self, market: str) -> Optional[Dict[str, Any]]:
        """
        Get premium index (mark price vs index price) for a futures market
        
        Args:
            market: Futures market symbol (e.g., "BTCUSDT")
            
        Returns:
            Premium index data with mark price, index price, premium rate
        """
        try:
            result = await self._call_tool("get_futures_premium_index", {"market": market})
            return result
        except Exception as e:
            self.logger.error(f"Failed to get premium index for {market}: {e}")
            return None
    
    async def get_futures_basis_history(
        self,
        market: str,
        interval: str = "1hour",
        limit: int = 100
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Get basis history (futures-spot price spread) for a market
        
        Args:
            market: Futures market symbol (e.g., "BTCUSDT")
            interval: Time interval for basis data
            limit: Number of historical records to retrieve
            
        Returns:
            List of basis history data with futures price, spot price, basis, basis rate
        """
        try:
            result = await self._call_tool("get_futures_basis_history", {
                "market": market,
                "interval": interval,
                "limit": limit
            })
            return result
        except Exception as e:
            self.logger.error(f"Failed to get basis history for {market}: {e}")
            return None
    
    async def get_futures_liquidations(
        self,
        market: str,
        limit: int = 100
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Get recent liquidation events for a futures market
        
        Args:
            market: Futures market symbol (e.g., "BTCUSDT")
            limit: Number of liquidation events to retrieve
            
        Returns:
            List of liquidation events with side, price, volume, timestamp
        """
        try:
            result = await self._call_tool("get_futures_liquidations", {
                "market": market,
                "limit": limit
            })
            return result
        except Exception as e:
            self.logger.error(f"Failed to get liquidations for {market}: {e}")
            return None
    
    async def get_futures_position_tiers(self, market: str) -> Optional[List[Dict[str, Any]]]:
        """
        Get position tiers (margin tiers) for a futures market
        
        Args:
            market: Futures market symbol (e.g., "BTCUSDT")
            
        Returns:
            List of position tiers with max position, margin rates, max leverage
        """
        try:
            result = await self._call_tool("get_futures_position_tiers", {"market": market})
            return result
        except Exception as e:
            self.logger.error(f"Failed to get position tiers for {market}: {e}")
            return None
    
    async def get_futures_market_info(self, market: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Get futures market information
        
        Args:
            market: Futures market symbol (optional, returns all futures markets if None)
            
        Returns:
            Futures market information
        """
        try:
            params = {"market": market} if market else {}
            result = await self._call_tool("get_futures_market_info", params)
            return result
        except Exception as e:
            self.logger.error(f"Failed to get futures market info: {e}")
            return None
    
    async def get_all_futures_tickers(self) -> Optional[List[Dict[str, Any]]]:
        """
        Get tickers for all futures markets
        
        Returns:
            List of all futures market tickers
        """
        try:
            result = await self._call_tool("get_all_futures_tickers", {})
            return result
        except Exception as e:
            self.logger.error(f"Failed to get all futures tickers: {e}")
            return None
    
    def add_callback(
        self,
        data_type: MarketDataType,
        callback: Callable[[Dict[str, Any]], None]
    ) -> None:
        """
        Add callback for market data updates
        
        Args:
            data_type: Type of market data
            callback: Callback function
        """
        self._callbacks[data_type].append(callback)
        self.logger.info(f"Added callback for {data_type.value}")
    
    def remove_callback(
        self,
        data_type: MarketDataType,
        callback: Callable[[Dict[str, Any]], None]
    ) -> None:
        """
        Remove callback
        
        Args:
            data_type: Type of market data
            callback: Callback function to remove
        """
        if callback in self._callbacks[data_type]:
            self._callbacks[data_type].remove(callback)
            self.logger.info(f"Removed callback for {data_type.value}")
    
    async def _call_tool(self, tool_name: str, params: Dict[str, Any]) -> Any:
        """
        Call MCP tool
        
        Args:
            tool_name: Name of the tool
            params: Tool parameters
            
        Returns:
            Tool result
        """
        if not self._connected:
            raise RuntimeError("Not connected to MCP server")
        
        # Prepare MCP request
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": params
            }
        }
        
        # Send request
        request_json = json.dumps(request) + "\n"
        self._process.stdin.write(request_json.encode())
        await self._process.stdin.drain()
        
        # Read response
        response_line = await asyncio.wait_for(
            self._process.stdout.readline(),
            timeout=self.config.timeout
        )
        
        response = json.loads(response_line.decode())
        
        if "error" in response:
            raise RuntimeError(f"MCP error: {response['error']}")
        
        return response.get("result")
    
    def is_connected(self) -> bool:
        """Check if connected to MCP server"""
        return self._connected
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.disconnect()


class SimpleMCPClient:
    """
    Simplified synchronous MCP client for basic usage
    
    Uses subprocess to call coinex-mcp-server tools directly
    """
    
    def __init__(self):
        """Initialize simple MCP client"""
        self.logger = logger
    
    def get_ticker(self, market: str) -> Optional[Dict[str, Any]]:
        """
        Get ticker data synchronously
        
        Args:
            market: Market symbol (e.g., "BTCUSDT")
            
        Returns:
            Ticker data
        """
        try:
            # Call MCP server via subprocess
            result = subprocess.run(
                ["uvx", "coinex-mcp-server", "get_ticker", market],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                return json.loads(result.stdout)
            else:
                self.logger.error(f"MCP error: {result.stderr}")
                return None
                
        except Exception as e:
            self.logger.error(f"Failed to get ticker: {e}")
            return None
    
    def get_kline(
        self,
        market: str,
        interval: str = "1min",
        limit: int = 100
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Get K-line data synchronously
        
        Args:
            market: Market symbol
            interval: Time interval
            limit: Number of candles
            
        Returns:
            K-line data
        """
        try:
            result = subprocess.run(
                ["uvx", "coinex-mcp-server", "get_kline", market, interval, str(limit)],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                return json.loads(result.stdout)
            else:
                self.logger.error(f"MCP error: {result.stderr}")
                return None
                
        except Exception as e:
            self.logger.error(f"Failed to get K-line: {e}")
            return None
    
    def get_orderbook(
        self,
        market: str,
        depth: int = 20
    ) -> Optional[Dict[str, Any]]:
        """
        Get order book synchronously
        
        Args:
            market: Market symbol
            depth: Order book depth
            
        Returns:
            Order book data
        """
        try:
            result = subprocess.run(
                ["uvx", "coinex-mcp-server", "get_orderbook", market, str(depth)],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                return json.loads(result.stdout)
            else:
                self.logger.error(f"MCP error: {result.stderr}")
                return None
                
        except Exception as e:
            self.logger.error(f"Failed to get order book: {e}")
            return None
