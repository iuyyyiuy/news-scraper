"""
Markets Router

Endpoints for market data retrieval (spot and futures).
"""

from fastapi import APIRouter, HTTPException, Query, Request
from typing import Optional, List
import requests


router = APIRouter()


# Direct CoinEx API client (secure, no local installation)
class CoinExAPI:
    BASE_URL = "https://api.coinex.com/v2"
    
    @staticmethod
    def get_ticker(market: str):
        """Get spot ticker"""
        try:
            response = requests.get(
                f"{CoinExAPI.BASE_URL}/spot/ticker",
                params={"market": market},
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            if data.get('code') == 0:
                return data.get('data', [{}])[0] if isinstance(data.get('data'), list) else data.get('data')
            return None
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to fetch ticker: {str(e)}")
    
    @staticmethod
    def get_klines(market: str, period: str = "1min", limit: int = 100):
        """Get K-line data"""
        try:
            response = requests.get(
                f"{CoinExAPI.BASE_URL}/spot/kline",
                params={"market": market, "period": period, "limit": limit},
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            if data.get('code') == 0:
                return data.get('data', [])
            return []
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to fetch K-lines: {str(e)}")
    
    @staticmethod
    def get_orderbook(market: str, limit: int = 20):
        """Get order book"""
        try:
            response = requests.get(
                f"{CoinExAPI.BASE_URL}/spot/depth",
                params={"market": market, "limit": str(limit), "interval": "0"},
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            if data.get('code') == 0:
                return data.get('data')
            return None
        except Exception:
            return None  # Order book may not be available for all markets
    
    @staticmethod
    def get_trades(market: str, limit: int = 100):
        """Get recent trades"""
        try:
            response = requests.get(
                f"{CoinExAPI.BASE_URL}/spot/deals",
                params={"market": market, "limit": limit},
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            if data.get('code') == 0:
                return data.get('data', [])
            return []
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to fetch trades: {str(e)}")


@router.get("/spot/{market}/ticker")
async def get_spot_ticker(market: str):
    """
    Get spot market ticker
    
    - **market**: Market symbol (e.g., BTCUSDT)
    """
    ticker = CoinExAPI.get_ticker(market)
    if not ticker:
        raise HTTPException(status_code=404, detail="Market not found or no data available")
    return {"market": market, "data": ticker}


@router.get("/spot/{market}/kline")
async def get_spot_kline(
    market: str,
    interval: str = Query("1min", description="Time interval (1min, 5min, 15min, 1hour, 1day)"),
    limit: int = Query(100, ge=1, le=1000, description="Number of candles")
):
    """
    Get spot market K-line data
    
    - **market**: Market symbol
    - **interval**: Time interval
    - **limit**: Number of candles (1-1000)
    """
    klines = CoinExAPI.get_klines(market, interval, limit)
    return {"market": market, "interval": interval, "data": klines}


@router.get("/spot/{market}/orderbook")
async def get_spot_orderbook(
    market: str,
    depth: int = Query(20, ge=5, le=50, description="Order book depth")
):
    """
    Get spot market order book
    
    - **market**: Market symbol
    - **depth**: Number of price levels (5-50)
    """
    orderbook = CoinExAPI.get_orderbook(market, depth)
    if not orderbook:
        return {"market": market, "data": None, "message": "Order book not available"}
    return {"market": market, "data": orderbook}


@router.get("/spot/{market}/trades")
async def get_spot_trades(
    market: str,
    limit: int = Query(100, ge=1, le=1000, description="Number of trades")
):
    """
    Get recent spot market trades
    
    - **market**: Market symbol
    - **limit**: Number of trades (1-1000)
    """
    trades = CoinExAPI.get_trades(market, limit)
    return {"market": market, "data": trades}


@router.get("/spot/{market}/analysis")
async def analyze_spot_market(market: str):
    """
    Analyze spot market for abnormal trading behavior
    
    - **market**: Market symbol
    
    Returns comprehensive analysis including:
    - Ticker data
    - Price volatility
    - Volume analysis
    - Order book metrics
    - Trade patterns
    - Manipulation detection
    - Health score
    """
    try:
        # Fetch all data
        ticker = CoinExAPI.get_ticker(market)
        if not ticker:
            raise HTTPException(status_code=404, detail="Market not found")
        
        klines = CoinExAPI.get_klines(market, "1min", 100)
        orderbook = CoinExAPI.get_orderbook(market, 20)
        trades = CoinExAPI.get_trades(market, 100)
        
        # Calculate metrics
        last_price = float(ticker.get('last', 0))
        volume_24h = float(ticker.get('vol', 0))
        change_24h = float(ticker.get('change_percentage', 0))
        high_24h = float(ticker.get('high', 0))
        low_24h = float(ticker.get('low', 0))
        
        # Volatility
        volatility = ((high_24h - low_24h) / low_24h * 100) if low_24h > 0 else 0
        
        # Volume analysis
        volume_spikes = 0
        if klines:
            volumes = [float(k.get('volume', 0)) for k in klines]
            avg_volume = sum(volumes) / len(volumes) if volumes else 0
            volume_spikes = sum(1 for v in volumes if v > avg_volume * 3)
        
        # Trade analysis
        buy_volume = 0
        sell_volume = 0
        if trades:
            buy_volume = sum(float(t.get('amount', 0)) for t in trades if t.get('side') == 'buy')
            sell_volume = sum(float(t.get('amount', 0)) for t in trades if t.get('side') == 'sell')
        
        total_trade_volume = buy_volume + sell_volume
        buy_pct = (buy_volume / total_trade_volume * 100) if total_trade_volume > 0 else 0
        sell_pct = (sell_volume / total_trade_volume * 100) if total_trade_volume > 0 else 0
        
        # Order book analysis
        spread_pct = 0
        imbalance = 0
        if orderbook:
            asks = orderbook.get('asks', [])
            bids = orderbook.get('bids', [])
            if asks and bids:
                best_ask = float(asks[0][0])
                best_bid = float(bids[0][0])
                spread = best_ask - best_bid
                spread_pct = (spread / best_bid * 100) if best_bid > 0 else 0
                
                total_bid_volume = sum(float(b[1]) for b in bids[:10])
                total_ask_volume = sum(float(a[1]) for a in asks[:10])
                if total_bid_volume + total_ask_volume > 0:
                    imbalance = (total_bid_volume - total_ask_volume) / (total_bid_volume + total_ask_volume)
        
        # Alerts
        alerts = []
        if volatility > 20:
            alerts.append({"type": "HIGH_VOLATILITY", "severity": "MEDIUM", "message": f"High volatility: {volatility:.1f}%"})
        if volume_spikes > 5:
            alerts.append({"type": "VOLUME_SPIKE", "severity": "MEDIUM", "message": f"{volume_spikes} volume spikes detected"})
        if abs(buy_pct - sell_pct) > 30:
            alerts.append({"type": "TRADE_IMBALANCE", "severity": "LOW", "message": f"Trade imbalance: {buy_pct:.1f}% buy vs {sell_pct:.1f}% sell"})
        if spread_pct > 1.0:
            alerts.append({"type": "WIDE_SPREAD", "severity": "LOW", "message": f"Wide spread: {spread_pct:.2f}%"})
        
        # Health score
        health_score = 100
        if volume_24h < 10000:
            health_score -= 20
        if volatility > 20:
            health_score -= 10
        if spread_pct > 1.0:
            health_score -= 15
        if abs(imbalance) > 0.3:
            health_score -= 15
        health_score -= len(alerts) * 10
        health_score = max(0, health_score)
        
        return {
            "market": market,
            "ticker": {
                "last_price": last_price,
                "volume_24h": volume_24h,
                "change_24h": change_24h,
                "high_24h": high_24h,
                "low_24h": low_24h,
                "volatility": volatility
            },
            "volume_analysis": {
                "volume_spikes": volume_spikes,
                "avg_volume": avg_volume if klines else 0
            },
            "trade_analysis": {
                "buy_volume": buy_volume,
                "sell_volume": sell_volume,
                "buy_percentage": buy_pct,
                "sell_percentage": sell_pct
            },
            "orderbook_analysis": {
                "spread_percentage": spread_pct,
                "imbalance": imbalance,
                "available": orderbook is not None
            },
            "alerts": alerts,
            "health_score": health_score,
            "health_status": "HEALTHY" if health_score >= 80 else "CAUTION" if health_score >= 60 else "WARNING" if health_score >= 40 else "HIGH_RISK"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")
