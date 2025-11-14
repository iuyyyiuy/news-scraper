"""
Analyze ZEROLEND Spot Market for Abnormal Trading Behavior

Uses the market monitoring system to fetch real-time data and detect
manipulation patterns.
"""

import asyncio
from datetime import datetime
from trade_risk_analyzer.market_monitoring.mcp_client import MCPClient, MCPConfig
from trade_risk_analyzer.market_monitoring.market_analyzer import MarketAnalyzer


async def analyze_zerolend():
    """Analyze ZEROLEND spot market"""
    
    market = "ZEROLENDUSDT"
    
    print(f"\n{'='*60}")
    print(f"ZEROLEND Spot Market Analysis")
    print(f"Market: {market}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")
    
    # Initialize MCP client
    mcp_client = MCPClient(MCPConfig())
    
    try:
        # Connect to MCP server
        print("Connecting to CoinEx MCP server...")
        connected = await mcp_client.connect()
        
        if not connected:
            print("❌ Failed to connect to MCP server")
            return
        
        print("✅ Connected to MCP server\n")
        
        # Fetch market data
        print("Fetching market data...")
        print("-" * 60)
        
        # 1. Get ticker data
        print("\n1. Ticker Data:")
        ticker = await mcp_client.get_ticker(market)
        if ticker:
            print(f"   Last Price: ${float(ticker.get('last_price', 0)):.6f}")
            print(f"   24h Volume: ${float(ticker.get('volume_24h', 0)):,.2f}")
            print(f"   24h Change: {float(ticker.get('change_24h', 0)):.2f}%")
            print(f"   24h High: ${float(ticker.get('high_24h', 0)):.6f}")
            print(f"   24h Low: ${float(ticker.get('low_24h', 0)):.6f}")
        else:
            print("   ⚠️  No ticker data available")
        
        # 2. Get K-line data
        print("\n2. K-line Data (Last 100 candles, 1min interval):")
        klines = await mcp_client.get_kline(market, interval="1min", limit=100)
        if klines:
            print(f"   Retrieved {len(klines)} candles")
            if len(klines) > 0:
                latest = klines[-1]
                print(f"   Latest Candle:")
                print(f"     Open: ${float(latest.get('open', 0)):.6f}")
                print(f"     High: ${float(latest.get('high', 0)):.6f}")
                print(f"     Low: ${float(latest.get('low', 0)):.6f}")
                print(f"     Close: ${float(latest.get('close', 0)):.6f}")
                print(f"     Volume: {float(latest.get('volume', 0)):,.2f}")
        else:
            print("   ⚠️  No K-line data available")
        
        # 3. Get order book
        print("\n3. Order Book (Depth: 20):")
        orderbook = await mcp_client.get_orderbook(market, depth=20)
        if orderbook:
            bids = orderbook.get('bids', [])
            asks = orderbook.get('asks', [])
            print(f"   Bids: {len(bids)} levels")
            print(f"   Asks: {len(asks)} levels")
            
            if bids and asks:
                best_bid = float(bids[0][0]) if bids else 0
                best_ask = float(asks[0][0]) if asks else 0
                spread = best_ask - best_bid
                spread_pct = (spread / best_bid * 100) if best_bid > 0 else 0
                
                print(f"   Best Bid: ${best_bid:.6f}")
                print(f"   Best Ask: ${best_ask:.6f}")
                print(f"   Spread: ${spread:.6f} ({spread_pct:.3f}%)")
                
                # Calculate order book imbalance
                total_bid_volume = sum(float(b[1]) for b in bids[:10])
                total_ask_volume = sum(float(a[1]) for a in asks[:10])
                imbalance = (total_bid_volume - total_ask_volume) / (total_bid_volume + total_ask_volume) if (total_bid_volume + total_ask_volume) > 0 else 0
                
                print(f"   Order Book Imbalance (top 10): {imbalance:.3f}")
                if abs(imbalance) > 0.3:
                    print(f"   ⚠️  Significant imbalance detected!")
        else:
            print("   ⚠️  No order book data available")
        
        # 4. Get recent trades
        print("\n4. Recent Trades (Last 100):")
        trades = await mcp_client.get_recent_trades(market, limit=100)
        if trades:
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
                    print(f"   ⚠️  Significant buy/sell imbalance!")
        else:
            print("   ⚠️  No trade data available")
        
        # 5. Run market analyzer for manipulation detection
        print("\n" + "="*60)
        print("MANIPULATION DETECTION ANALYSIS")
        print("="*60 + "\n")
        
        analyzer = MarketAnalyzer()
        alerts = await analyzer.analyze_market(market)
        
        if alerts:
            print(f"🚨 ALERTS DETECTED: {len(alerts)} potential issues found\n")
            
            for i, alert in enumerate(alerts, 1):
                print(f"Alert #{i}:")
                print(f"  Pattern: {alert.pattern_type}")
                print(f"  Risk Level: {alert.risk_level.value}")
                print(f"  Anomaly Score: {alert.anomaly_score:.2f}/100")
                print(f"  Explanation: {alert.explanation}")
                print(f"  Timestamp: {alert.timestamp}")
                print()
        else:
            print("✅ No manipulation patterns detected")
            print("   Market appears to be trading normally")
        
        # 6. Market health summary
        print("\n" + "="*60)
        print("MARKET HEALTH SUMMARY")
        print("="*60 + "\n")
        
        health_score = 100
        issues = []
        
        # Check volume
        if ticker:
            volume_24h = float(ticker.get('volume_24h', 0))
            if volume_24h < 10000:
                health_score -= 20
                issues.append("Low 24h volume (< $10k)")
        
        # Check spread
        if orderbook and bids and asks:
            if spread_pct > 1.0:
                health_score -= 15
                issues.append(f"Wide spread ({spread_pct:.2f}%)")
        
        # Check order book imbalance
        if orderbook and abs(imbalance) > 0.3:
            health_score -= 15
            issues.append(f"Order book imbalance ({imbalance:.2f})")
        
        # Check alerts
        if alerts:
            health_score -= len(alerts) * 10
            issues.append(f"{len(alerts)} manipulation alerts")
        
        health_score = max(0, health_score)
        
        print(f"Overall Health Score: {health_score}/100")
        
        if health_score >= 80:
            print("Status: ✅ HEALTHY")
        elif health_score >= 60:
            print("Status: ⚠️  CAUTION")
        else:
            print("Status: 🚨 HIGH RISK")
        
        if issues:
            print("\nIssues Detected:")
            for issue in issues:
                print(f"  • {issue}")
        else:
            print("\n✅ No significant issues detected")
        
    except Exception as e:
        print(f"\n❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Disconnect
        await mcp_client.disconnect()
        print(f"\n{'='*60}")
        print("Analysis Complete")
        print(f"{'='*60}\n")


if __name__ == "__main__":
    asyncio.run(analyze_zerolend())
