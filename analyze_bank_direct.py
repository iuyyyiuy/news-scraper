"""
Analyze BANK Spot Market - Direct API Version

Uses CoinEx public REST API directly without requiring MCP server installation.
More secure - no additional dependencies needed.
"""

import requests
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
import statistics


class CoinExDirectAPI:
    """
    Direct CoinEx API client using public REST endpoints
    
    Uses CoinEx's recommended HTTP service for public market data.
    More secure - no local installation required.
    Reference: https://pypi.org/project/coinex-mcp-server/
    """
    
    BASE_URL = "https://api.coinex.com/v2"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'TradeRiskAnalyzer/1.0',
            'Content-Type': 'application/json'
        })
        print("🔒 Using CoinEx HTTP Service (Recommended for public market data)")
        print("📖 Reference: https://pypi.org/project/coinex-mcp-server/\n")
    
    def get_ticker(self, market: str) -> Optional[Dict[str, Any]]:
        """Get ticker data for a market"""
        try:
            url = f"{self.BASE_URL}/spot/ticker"
            params = {"market": market}
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get('code') == 0 and data.get('data'):
                return data['data'][0] if isinstance(data['data'], list) else data['data']
            return None
        except Exception as e:
            print(f"Error fetching ticker: {e}")
            return None
    
    def get_klines(self, market: str, period: str = "1min", limit: int = 100) -> Optional[List[Dict[str, Any]]]:
        """Get K-line data"""
        try:
            url = f"{self.BASE_URL}/spot/kline"
            params = {
                "market": market,
                "period": period,
                "limit": limit
            }
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get('code') == 0 and data.get('data'):
                return data['data']
            return None
        except Exception as e:
            print(f"Error fetching K-lines: {e}")
            return None
    
    def get_orderbook(self, market: str, limit: int = 20) -> Optional[Dict[str, Any]]:
        """Get order book depth"""
        try:
            url = f"{self.BASE_URL}/spot/depth"
            params = {
                "market": market,
                "limit": str(limit),
                "interval": "0"
            }
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get('code') != 0:
                print(f"   API Error Code: {data.get('code')}")
                print(f"   API Message: {data.get('message', 'No message')}")
                print(f"   Note: Order book may not be available for low-liquidity markets")
            
            if data.get('code') == 0 and data.get('data'):
                return data['data']
            return None
        except Exception as e:
            print(f"   Error fetching order book: {e}")
            return None
    
    def get_recent_trades(self, market: str, limit: int = 100) -> Optional[List[Dict[str, Any]]]:
        """Get recent trades"""
        try:
            url = f"{self.BASE_URL}/spot/deals"
            params = {
                "market": market,
                "limit": limit
            }
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get('code') == 0 and data.get('data'):
                return data['data']
            return None
        except Exception as e:
            print(f"Error fetching trades: {e}")
            return None


def analyze_bank():
    """Analyze BANK spot market"""
    
    market = "BANKUSDT"
    
    print(f"\n{'='*70}")
    print(f"BANK Spot Market Analysis (Direct API)")
    print(f"Market: {market}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*70}\n")
    
    # Initialize API client
    api = CoinExDirectAPI()
    
    print("📡 Connecting to CoinEx public REST API...\n")
    
    # Fetch market data
    print("Fetching market data...")
    print("-" * 70)
    
    # 1. Get ticker data
    print("\n1. 📊 Ticker Data:")
    ticker = api.get_ticker(market)
    
    volatility = 0  # Initialize
    volume_24h = 0  # Initialize
    
    if ticker:
        last_price = float(ticker.get('last', 0))
        volume_24h = float(ticker.get('vol', 0))
        change_24h = float(ticker.get('change_percentage', 0))
        high_24h = float(ticker.get('high', 0))
        low_24h = float(ticker.get('low', 0))
        
        print(f"   Last Price: ${last_price:.8f}")
        print(f"   24h Volume: {volume_24h:,.2f} BANK")
        print(f"   24h Change: {change_24h:.2f}%")
        print(f"   24h High: ${high_24h:.8f}")
        print(f"   24h Low: ${low_24h:.8f}")
        
        # Calculate price volatility
        if low_24h > 0:
            volatility = ((high_24h - low_24h) / low_24h) * 100
            print(f"   24h Volatility: {volatility:.2f}%")
            
            if volatility > 20:
                print(f"   ⚠️  HIGH VOLATILITY DETECTED!")
    else:
        print("   ⚠️  No ticker data available - market may not exist or be delisted")
        print("\n❌ Analysis cannot continue without ticker data")
        return
    
    # 2. Get K-line data
    print("\n2. 📈 K-line Data (Last 100 candles, 1min interval):")
    klines = api.get_klines(market, period="1min", limit=100)
    
    if klines and len(klines) > 0:
        print(f"   Retrieved {len(klines)} candles")
        
        # Analyze price movement
        if isinstance(klines[0], list):
            prices = [float(k[2]) for k in klines]  # Close prices
            volumes = [float(k[5]) for k in klines]  # Volumes
        else:
            prices = [float(k.get('close', 0)) for k in klines]
            volumes = [float(k.get('volume', 0)) for k in klines]
        
        if len(prices) > 1:
            price_change = ((prices[-1] - prices[0]) / prices[0]) * 100
            avg_volume = statistics.mean(volumes)
            max_volume = max(volumes)
            
            print(f"   Price Change (100 candles): {price_change:.2f}%")
            print(f"   Average Volume: {avg_volume:,.2f}")
            print(f"   Max Volume: {max_volume:,.2f}")
            
            # Detect volume spikes
            volume_spike_threshold = avg_volume * 3
            volume_spikes = sum(1 for v in volumes if v > volume_spike_threshold)
            
            if volume_spikes > 0:
                print(f"   ⚠️  Volume spikes detected: {volume_spikes} candles (>3x average)")
        
        # Show latest candle
        latest = klines[-1]
        print(f"\n   Latest Candle:")
        if isinstance(latest, list):
            print(f"     Open: ${float(latest[1]):.8f}")
            print(f"     High: ${float(latest[3]):.8f}")
            print(f"     Low: ${float(latest[4]):.8f}")
            print(f"     Close: ${float(latest[2]):.8f}")
            print(f"     Volume: {float(latest[5]):,.2f}")
        else:
            print(f"     Open: ${float(latest.get('open', 0)):.8f}")
            print(f"     High: ${float(latest.get('high', 0)):.8f}")
            print(f"     Low: ${float(latest.get('low', 0)):.8f}")
            print(f"     Close: ${float(latest.get('close', 0)):.8f}")
            print(f"     Volume: {float(latest.get('volume', 0)):,.2f}")
    else:
        print("   ⚠️  No K-line data available")
    
    # 3. Get order book
    print("\n3. 📖 Order Book (Depth: 20):")
    orderbook = api.get_orderbook(market, limit=20)
    imbalance = 0  # Initialize
    spread_pct = 0  # Initialize
    asks = []
    bids = []
    
    if orderbook:
        asks = orderbook.get('asks', [])
        bids = orderbook.get('bids', [])
        
        print(f"   Asks: {len(asks)} levels")
        print(f"   Bids: {len(bids)} levels")
        
        if asks and bids and len(asks) > 0 and len(bids) > 0:
            best_ask = float(asks[0][0])
            best_bid = float(bids[0][0])
            spread = best_ask - best_bid
            spread_pct = (spread / best_bid * 100) if best_bid > 0 else 0
            
            print(f"   Best Bid: ${best_bid:.8f}")
            print(f"   Best Ask: ${best_ask:.8f}")
            print(f"   Spread: ${spread:.8f} ({spread_pct:.3f}%)")
            
            if spread_pct > 1.0:
                print(f"   ⚠️  Wide spread detected (>{spread_pct:.2f}%)")
            
            # Calculate order book imbalance
            total_bid_volume = sum(float(b[1]) for b in bids[:10])
            total_ask_volume = sum(float(a[1]) for a in asks[:10])
            
            if total_bid_volume + total_ask_volume > 0:
                imbalance = (total_bid_volume - total_ask_volume) / (total_bid_volume + total_ask_volume)
                print(f"   Order Book Imbalance (top 10): {imbalance:.3f}")
                
                if abs(imbalance) > 0.3:
                    side = "BUY" if imbalance > 0 else "SELL"
                    print(f"   ⚠️  Significant {side} pressure detected!")
        else:
            print("   ⚠️  Order book is empty - extremely low liquidity!")
    else:
        print("   ⚠️  No order book data available")
    
    # 4. Get recent trades
    print("\n4. 💱 Recent Trades (Last 100):")
    trades = api.get_recent_trades(market, limit=100)
    
    if trades and len(trades) > 0:
        print(f"   Retrieved {len(trades)} trades")
        
        # Analyze trade patterns
        buy_volume = sum(float(t['amount']) for t in trades if t.get('side') == 'buy')
        sell_volume = sum(float(t['amount']) for t in trades if t.get('side') == 'sell')
        total_volume = buy_volume + sell_volume
        
        if total_volume > 0:
            buy_pct = (buy_volume / total_volume) * 100
            sell_pct = (sell_volume / total_volume) * 100
            
            print(f"   Buy Volume: {buy_volume:,.2f} ({buy_pct:.1f}%)")
            print(f"   Sell Volume: {sell_volume:,.2f} ({sell_pct:.1f}%)")
            
            if abs(buy_pct - sell_pct) > 30:
                dominant = "BUY" if buy_pct > sell_pct else "SELL"
                print(f"   ⚠️  Significant {dominant} pressure in recent trades!")
    else:
        print("   ⚠️  No trade data available")
    
    # 5. Manipulation Detection
    print("\n" + "="*70)
    print("🔍 MANIPULATION DETECTION ANALYSIS")
    print("="*70 + "\n")
    
    alerts = []
    
    # Check for pump and dump
    if klines and len(klines) > 10:
        if isinstance(klines[0], list):
            prices = [float(k[2]) for k in klines]
            volumes = [float(k[5]) for k in klines]
        else:
            prices = [float(k.get('close', 0)) for k in klines]
            volumes = [float(k.get('volume', 0)) for k in klines]
        
        recent_price_change = ((prices[-1] - prices[-10]) / prices[-10]) * 100
        avg_volume = statistics.mean(volumes[:-10]) if len(volumes) > 10 else statistics.mean(volumes)
        recent_volume = statistics.mean(volumes[-10:])
        
        volume_spike = (recent_volume / avg_volume) if avg_volume > 0 else 0
        
        if abs(recent_price_change) > 10 and volume_spike > 2:
            alerts.append({
                'type': 'PUMP_AND_DUMP',
                'severity': 'HIGH',
                'score': 85,
                'description': f'Rapid price change ({recent_price_change:.1f}%) with volume spike ({volume_spike:.1f}x)'
            })
    
    # Check for spoofing (order book manipulation)
    if orderbook and asks and bids:
        if abs(imbalance) > 0.5:
            alerts.append({
                'type': 'ORDER_BOOK_MANIPULATION',
                'severity': 'MEDIUM',
                'score': 70,
                'description': f'Extreme order book imbalance ({imbalance:.2f})'
            })
    
    # Check for wash trading indicators
    if trades and len(trades) > 20:
        # Check for repeated similar-sized trades
        trade_sizes = [float(t['amount']) for t in trades]
        if len(set(trade_sizes)) < len(trade_sizes) * 0.3:  # Less than 30% unique sizes
            alerts.append({
                'type': 'WASH_TRADING',
                'severity': 'MEDIUM',
                'score': 65,
                'description': 'Suspicious pattern: Many trades with identical sizes'
            })
    
    if alerts:
        print(f"🚨 ALERTS DETECTED: {len(alerts)} potential issues found\n")
        
        for i, alert in enumerate(alerts, 1):
            print(f"Alert #{i}:")
            print(f"  Pattern: {alert['type']}")
            print(f"  Severity: {alert['severity']}")
            print(f"  Anomaly Score: {alert['score']}/100")
            print(f"  Description: {alert['description']}")
            print()
    else:
        print("✅ No obvious manipulation patterns detected")
        print("   Market appears to be trading normally\n")
    
    # 6. Market Health Summary
    print("="*70)
    print("📋 MARKET HEALTH SUMMARY")
    print("="*70 + "\n")
    
    health_score = 100
    issues = []
    
    # Check volume
    if ticker and volume_24h < 10000:
        health_score -= 20
        issues.append(f"Low 24h volume ({volume_24h:,.0f} BANK)")
    
    # Check spread
    if orderbook and asks and bids and spread_pct > 1.0:
        health_score -= 15
        issues.append(f"Wide spread ({spread_pct:.2f}%)")
    
    # Check volatility
    if ticker and volatility > 20:
        health_score -= 10
        issues.append(f"High volatility ({volatility:.1f}%)")
    
    # Check order book imbalance
    if orderbook and abs(imbalance) > 0.3:
        health_score -= 15
        issues.append(f"Order book imbalance ({imbalance:.2f})")
    
    # Check alerts
    if alerts:
        health_score -= len(alerts) * 15
        issues.append(f"{len(alerts)} manipulation alerts")
    
    health_score = max(0, health_score)
    
    print(f"Overall Health Score: {health_score}/100")
    
    if health_score >= 80:
        print("Status: ✅ HEALTHY - Market trading normally")
    elif health_score >= 60:
        print("Status: ⚠️  CAUTION - Some concerns detected")
    elif health_score >= 40:
        print("Status: 🔶 WARNING - Multiple issues detected")
    else:
        print("Status: 🚨 HIGH RISK - Significant manipulation indicators")
    
    if issues:
        print("\nIssues Detected:")
        for issue in issues:
            print(f"  • {issue}")
    else:
        print("\n✅ No significant issues detected")
    
    print("\n" + "="*70)
    print("Analysis Complete")
    print("="*70 + "\n")
    
    print("💡 Note: This analysis uses public market data only.")
    print("   For deeper analysis, consider reviewing historical patterns")
    print("   and comparing with similar markets.\n")


if __name__ == "__main__":
    try:
        analyze_bank()
    except KeyboardInterrupt:
        print("\n\nAnalysis interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
