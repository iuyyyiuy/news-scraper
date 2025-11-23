"""
Analyze ZEROLEND Spot Market - Using CoinEx Hosted MCP Service

Uses CoinEx's hosted MCP service at https://mcp.coinex.com/mcp
✅ No local installation required
✅ Most secure option - official CoinEx service
✅ Full order book and market data access

Reference: https://pypi.org/project/coinex-mcp-server/
"""

import requests
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
import statistics


class CoinExMCPHosted:
    """
    CoinEx Hosted MCP Service Client
    
    Uses the official hosted MCP service - no installation needed.
    Service URL: https://mcp.coinex.com/mcp
    """
    
    MCP_URL = "https://mcp.coinex.com/mcp"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'User-Agent': 'TradeRiskAnalyzer-MCP/1.0'
        })
        print("🔒 Using CoinEx Hosted MCP Service (Official)")
        print("🌐 Service: https://mcp.coinex.com/mcp")
        print("✅ No local installation required\n")
    
    def _call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Optional[Any]:
        """Call MCP tool via hosted service"""
        try:
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {
                    "name": tool_name,
                    "arguments": arguments
                }
            }
            
            response = self.session.post(
                self.MCP_URL,
                json=payload,
                timeout=15
            )
            response.raise_for_status()
            data = response.json()
            
            if "error" in data:
                print(f"   MCP Error: {data['error'].get('message', 'Unknown error')}")
                return None
            
            if "result" in data:
                # Extract content from MCP response
                result = data["result"]
                if isinstance(result, list) and len(result) > 0:
                    content = result[0].get("content", [])
                    if content and len(content) > 0:
                        text = content[0].get("text", "")
                        if text:
                            return json.loads(text)
                return result
            
            return None
            
        except requests.exceptions.Timeout:
            print(f"   Timeout calling {tool_name}")
            return None
        except Exception as e:
            print(f"   Error calling {tool_name}: {e}")
            return None
    
    def get_ticker(self, market: str) -> Optional[Dict[str, Any]]:
        """Get ticker data"""
        return self._call_tool("get_ticker", {"market": market})
    
    def get_kline(self, market: str, interval: str = "1min", limit: int = 100) -> Optional[List[Dict[str, Any]]]:
        """Get K-line data"""
        return self._call_tool("get_kline", {
            "market": market,
            "interval": interval,
            "limit": limit
        })
    
    def get_orderbook(self, market: str, depth: int = 20) -> Optional[Dict[str, Any]]:
        """Get order book depth"""
        return self._call_tool("get_orderbook", {
            "market": market,
            "depth": depth
        })
    
    def get_recent_trades(self, market: str, limit: int = 100) -> Optional[List[Dict[str, Any]]]:
        """Get recent trades"""
        return self._call_tool("get_recent_trades", {
            "market": market,
            "limit": limit
        })


def analyze_zerolend():
    """Analyze ZEROLEND spot market using hosted MCP service"""
    
    market = "ZEROLENDUSDT"
    
    print(f"\n{'='*70}")
    print(f"ZEROLEND Spot Market Analysis")
    print(f"Using CoinEx Hosted MCP Service")
    print(f"Market: {market}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*70}\n")
    
    # Initialize MCP client
    mcp = CoinExMCPHosted()
    
    print("Fetching market data...")
    print("-" * 70)
    
    # 1. Get ticker data
    print("\n1. 📊 Ticker Data:")
    ticker = mcp.get_ticker(market)
    
    if ticker:
        last_price = float(ticker.get('last_price', 0))
        volume_24h = float(ticker.get('volume_24h', 0))
        change_24h = float(ticker.get('change_24h', 0))
        high_24h = float(ticker.get('high_24h', 0))
        low_24h = float(ticker.get('low_24h', 0))
        
        print(f"   Last Price: ${last_price:.8f}")
        print(f"   24h Volume: ${volume_24h:,.2f}")
        print(f"   24h Change: {change_24h:.2f}%")
        print(f"   24h High: ${high_24h:.8f}")
        print(f"   24h Low: ${low_24h:.8f}")
        
        # Calculate volatility
        if low_24h > 0:
            volatility = ((high_24h - low_24h) / low_24h) * 100
            print(f"   24h Volatility: {volatility:.2f}%")
            
            if volatility > 20:
                print(f"   ⚠️  HIGH VOLATILITY DETECTED!")
    else:
        print("   ⚠️  No ticker data available")
        return
    
    # 2. Get K-line data
    print("\n2. 📈 K-line Data (Last 100 candles, 1min interval):")
    klines = mcp.get_kline(market, interval="1min", limit=100)
    
    if klines and len(klines) > 0:
        print(f"   Retrieved {len(klines)} candles")
        
        # Extract prices and volumes
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
        print(f"     Open: ${float(latest.get('open', 0)):.8f}")
        print(f"     High: ${float(latest.get('high', 0)):.8f}")
        print(f"     Low: ${float(latest.get('low', 0)):.8f}")
        print(f"     Close: ${float(latest.get('close', 0)):.8f}")
        print(f"     Volume: {float(latest.get('volume', 0)):,.2f}")
    else:
        print("   ⚠️  No K-line data available")
    
    # 3. Get order book
    print("\n3. 📖 Order Book (Depth: 20):")
    orderbook = mcp.get_orderbook(market, depth=20)
    
    if orderbook:
        asks = orderbook.get('asks', [])
        bids = orderbook.get('bids', [])
        
        print(f"   ✅ Order book retrieved successfully!")
        print(f"   Asks: {len(asks)} levels")
        print(f"   Bids: {len(bids)} levels")
        
        if asks and bids:
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
        print("   ⚠️  No order book data available")
    
    # 4. Get recent trades
    print("\n4. 💱 Recent Trades (Last 100):")
    trades = mcp.get_recent_trades(market, limit=100)
    
    if trades and len(trades) > 0:
        print(f"   Retrieved {len(trades)} trades")
        
        # Analyze trade patterns
        buy_volume = sum(float(t.get('volume', 0)) for t in trades if t.get('side') == 'buy')
        sell_volume = sum(float(t.get('volume', 0)) for t in trades if t.get('side') == 'sell')
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
        trade_sizes = [float(t.get('volume', 0)) for t in trades]
        if len(set(trade_sizes)) < len(trade_sizes) * 0.3:
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
        issues.append(f"Low 24h volume (${volume_24h:,.0f})")
    
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
    
    print("💡 Using CoinEx Hosted MCP Service")
    print("   ✅ Most secure option - official CoinEx service")
    print("   ✅ No local installation required")
    print("   🌐 https://mcp.coinex.com/mcp\n")


if __name__ == "__main__":
    try:
        analyze_zerolend()
    except KeyboardInterrupt:
        print("\n\nAnalysis interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
