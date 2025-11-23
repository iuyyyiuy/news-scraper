"""
Example: Real-time Market Monitoring

Demonstrates how to use the market monitoring module to detect manipulation
in real-time using CoinEx MCP server.
"""

import asyncio
from datetime import datetime

from trade_risk_analyzer.market_monitoring.mcp_client import MCPClient, SimpleMCPClient
from trade_risk_analyzer.market_monitoring.market_analyzer import MarketAnalyzer, MarketAlert
from trade_risk_analyzer.market_monitoring.kline_monitor import KLineMonitor
from trade_risk_analyzer.market_monitoring.orderbook_monitor import OrderBookMonitor


def alert_callback(alert: MarketAlert):
    """Callback for market alerts"""
    print(f"\n🚨 MARKET ALERT: {alert.title}")
    print(f"   Market: {alert.market}")
    print(f"   Type: {alert.alert_type.value}")
    print(f"   Risk Level: {alert.risk_level.value}")
    print(f"   Severity: {alert.severity:.1f}/100")
    print(f"   Description: {alert.description}")
    print(f"   Action: {alert.recommended_action}")
    print(f"   Timestamp: {alert.timestamp.isoformat()}")


async def example_basic_monitoring():
    """Example 1: Basic market monitoring"""
    print("=" * 60)
    print("Example 1: Basic Market Monitoring")
    print("=" * 60)
    
    print("\n📊 Monitoring BTC/USDT market...")
    
    # Create analyzer
    analyzer = MarketAnalyzer()
    
    # Add alert callback
    analyzer.add_alert_callback(alert_callback)
    
    # Analyze market once
    alerts = await analyzer.analyze_market("BTCUSDT")
    
    print(f"\n✓ Analysis complete: {len(alerts)} alerts generated")
    
    if not alerts:
        print("   No manipulation detected - market appears healthy")


async def example_continuous_monitoring():
    """Example 2: Continuous monitoring"""
    print("\n" + "=" * 60)
    print("Example 2: Continuous Monitoring")
    print("=" * 60)
    
    print("\n📊 Starting continuous monitoring...")
    print("   Markets: BTCUSDT, ETHUSDT")
    print("   Interval: 60 seconds")
    print("   Press Ctrl+C to stop")
    
    # Create analyzer
    analyzer = MarketAnalyzer()
    
    # Add alert callback
    analyzer.add_alert_callback(alert_callback)
    
    try:
        # Start monitoring (will run until interrupted)
        await analyzer.start_monitoring(
            markets=["BTCUSDT", "ETHUSDT"],
            interval_seconds=60
        )
    except KeyboardInterrupt:
        print("\n\n✓ Monitoring stopped")
        analyzer.stop_monitoring()


async def example_kline_analysis():
    """Example 3: K-line analysis"""
    print("\n" + "=" * 60)
    print("Example 3: K-line Analysis")
    print("=" * 60)
    
    print("\n📈 Analyzing K-line data for BTC/USDT...")
    
    # Create MCP client
    async with MCPClient() as client:
        # Get K-line data
        klines = await client.get_kline("BTCUSDT", interval="1min", limit=100)
        
        if klines:
            print(f"   Retrieved {len(klines)} candles")
            
            # Analyze with K-line monitor
            monitor = KLineMonitor()
            anomalies = monitor.analyze_klines(klines, "BTCUSDT")
            
            print(f"\n✓ K-line analysis complete: {len(anomalies)} anomalies detected")
            
            for anomaly in anomalies:
                print(f"\n   Anomaly: {anomaly.anomaly_type.value}")
                print(f"   Severity: {anomaly.severity:.1f}/100")
                print(f"   Description: {anomaly.description}")
            
            # Get market health score
            health = monitor.get_market_health_score(klines, "BTCUSDT")
            print(f"\n   Market Health Score: {health['health_score']:.1f}/100")
            print(f"   Status: {health['status']}")
        else:
            print("   Failed to retrieve K-line data")


async def example_orderbook_analysis():
    """Example 4: Order book analysis"""
    print("\n" + "=" * 60)
    print("Example 4: Order Book Analysis")
    print("=" * 60)
    
    print("\n📊 Analyzing order book for BTC/USDT...")
    
    # Create MCP client
    async with MCPClient() as client:
        # Get order book
        orderbook = await client.get_orderbook("BTCUSDT", depth=20)
        
        if orderbook:
            print(f"   Retrieved order book with {len(orderbook.get('bids', []))} bids and {len(orderbook.get('asks', []))} asks")
            
            # Analyze with order book monitor
            monitor = OrderBookMonitor()
            anomalies = monitor.analyze_orderbook(orderbook, "BTCUSDT")
            
            print(f"\n✓ Order book analysis complete: {len(anomalies)} anomalies detected")
            
            for anomaly in anomalies:
                print(f"\n   Anomaly: {anomaly.anomaly_type.value}")
                print(f"   Severity: {anomaly.severity:.1f}/100")
                print(f"   Description: {anomaly.description}")
            
            # Get liquidity metrics
            snapshot = monitor._parse_orderbook(orderbook, "BTCUSDT")
            if snapshot:
                metrics = monitor.get_liquidity_metrics(snapshot)
                print(f"\n   Liquidity Metrics:")
                print(f"   Total Liquidity: ${metrics['total_liquidity']:.2f}")
                print(f"   Spread: {metrics['spread_pct']:.3f}%")
                print(f"   Imbalance: {metrics['imbalance_ratio']:.2%}")
        else:
            print("   Failed to retrieve order book data")


async def example_simple_client():
    """Example 5: Simple synchronous client"""
    print("\n" + "=" * 60)
    print("Example 5: Simple Synchronous Client")
    print("=" * 60)
    
    print("\n📊 Using simple MCP client...")
    
    # Create simple client (synchronous)
    client = SimpleMCPClient()
    
    # Get ticker
    print("\n   Getting ticker for BTC/USDT...")
    ticker = client.get_ticker("BTCUSDT")
    
    if ticker:
        print(f"   ✓ Price: ${ticker.get('last', 0)}")
        print(f"   ✓ 24h Change: {ticker.get('change_24h', 0)}%")
        print(f"   ✓ Volume: {ticker.get('volume_24h', 0)}")
    
    # Get K-line
    print("\n   Getting K-line data...")
    klines = client.get_kline("BTCUSDT", interval="1min", limit=10)
    
    if klines:
        print(f"   ✓ Retrieved {len(klines)} candles")
        latest = klines[-1]
        print(f"   ✓ Latest close: ${latest.get('close', 0)}")
    
    # Get order book
    print("\n   Getting order book...")
    orderbook = client.get_orderbook("BTCUSDT", depth=5)
    
    if orderbook:
        bids = orderbook.get('bids', [])
        asks = orderbook.get('asks', [])
        print(f"   ✓ Best bid: ${bids[0][0] if bids else 0}")
        print(f"   ✓ Best ask: ${asks[0][0] if asks else 0}")


async def example_multi_market_monitoring():
    """Example 6: Multi-market monitoring"""
    print("\n" + "=" * 60)
    print("Example 6: Multi-Market Monitoring")
    print("=" * 60)
    
    print("\n📊 Monitoring multiple markets...")
    
    markets = ["BTCUSDT", "ETHUSDT", "BNBUSDT"]
    
    # Create analyzer
    analyzer = MarketAnalyzer()
    
    # Analyze all markets
    all_alerts = []
    
    for market in markets:
        print(f"\n   Analyzing {market}...")
        alerts = await analyzer.analyze_market(market)
        all_alerts.extend(alerts)
        
        if alerts:
            print(f"   ⚠️  {len(alerts)} alerts generated")
        else:
            print(f"   ✓ No issues detected")
    
    print(f"\n✓ Multi-market analysis complete")
    print(f"   Total alerts: {len(all_alerts)}")
    
    # Summary by risk level
    high_risk = sum(1 for a in all_alerts if a.risk_level.value == "HIGH")
    medium_risk = sum(1 for a in all_alerts if a.risk_level.value == "MEDIUM")
    low_risk = sum(1 for a in all_alerts if a.risk_level.value == "LOW")
    
    print(f"   High risk: {high_risk}")
    print(f"   Medium risk: {medium_risk}")
    print(f"   Low risk: {low_risk}")


def main():
    """Run examples"""
    print("\n" + "=" * 60)
    print("MARKET MONITORING EXAMPLES")
    print("=" * 60)
    print("\nNote: Requires 'uv' and 'coinex-mcp-server' to be installed")
    print("Install with: pip install uv && uv tool install coinex-mcp-server")
    
    try:
        # Run async examples
        asyncio.run(example_basic_monitoring())
        asyncio.run(example_kline_analysis())
        asyncio.run(example_orderbook_analysis())
        # asyncio.run(example_simple_client())  # Uncomment if you want to test
        asyncio.run(example_multi_market_monitoring())
        
        # Uncomment to run continuous monitoring
        # asyncio.run(example_continuous_monitoring())
        
        print("\n" + "=" * 60)
        print("✅ Examples completed successfully!")
        print("=" * 60)
        print("\nTo run continuous monitoring, uncomment the line in main()")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
