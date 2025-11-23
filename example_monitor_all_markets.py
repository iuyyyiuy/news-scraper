"""
Example: Monitor All Markets

Demonstrates how to monitor ALL markets on the exchange efficiently
with automatic discovery, prioritization, and intelligent scheduling.
"""

import asyncio
from datetime import datetime

from trade_risk_analyzer.market_monitoring import MultiMarketMonitor, MarketAlert


def alert_handler(alert: MarketAlert):
    """Handle market alerts"""
    print(f"\n🚨 ALERT: {alert.market}")
    print(f"   Type: {alert.alert_type.value}")
    print(f"   Risk: {alert.risk_level.value}")
    print(f"   Severity: {alert.severity:.1f}/100")
    print(f"   {alert.description}")
    print(f"   Action: {alert.recommended_action}")


async def example_discover_markets():
    """Example 1: Discover all available markets"""
    print("=" * 60)
    print("Example 1: Discover All Markets")
    print("=" * 60)
    
    monitor = MultiMarketMonitor()
    
    print("\n📊 Discovering all USDT markets...")
    markets = await monitor.discover_markets(quote_currency="USDT")
    
    print(f"\n✓ Found {len(markets)} USDT markets")
    print(f"\nTop 20 markets:")
    for i, market in enumerate(markets[:20], 1):
        print(f"   {i}. {market}")
    
    print(f"\n... and {len(markets) - 20} more markets")


async def example_monitor_all_usdt():
    """Example 2: Monitor all USDT markets"""
    print("\n" + "=" * 60)
    print("Example 2: Monitor All USDT Markets")
    print("=" * 60)
    
    print("\n📊 Starting monitoring of ALL USDT markets...")
    print("   Minimum volume: $10,000 daily")
    print("   Press Ctrl+C to stop\n")
    
    monitor = MultiMarketMonitor(
        min_volume_24h=10000.0,  # $10k minimum
        max_concurrent=5,  # Check 5 markets at once
        base_interval=60,  # Check every 60 seconds
        high_priority_interval=30,  # High priority every 30s
        low_priority_interval=300  # Low priority every 5 min
    )
    
    # Add alert handler
    monitor.add_alert_callback(alert_handler)
    
    try:
        # This will discover and monitor ALL USDT markets
        await monitor.start_monitoring_all(quote_currency="USDT")
    except KeyboardInterrupt:
        print("\n\n✓ Monitoring stopped")
        monitor.stop_monitoring()


async def example_monitor_high_volume():
    """Example 3: Monitor only high-volume markets"""
    print("\n" + "=" * 60)
    print("Example 3: Monitor High-Volume Markets Only")
    print("=" * 60)
    
    print("\n📊 Monitoring high-volume markets (>$1M daily)...")
    
    monitor = MultiMarketMonitor(
        min_volume_24h=1000000.0,  # $1M minimum
        max_concurrent=10,  # More concurrent checks
        base_interval=30  # Check more frequently
    )
    
    # Add alert handler
    monitor.add_alert_callback(alert_handler)
    
    # Discover high-volume markets
    markets = await monitor.discover_markets(
        quote_currency="USDT",
        min_volume=1000000.0
    )
    
    print(f"   Found {len(markets)} high-volume markets")
    
    try:
        await monitor.start_monitoring_markets(markets)
    except KeyboardInterrupt:
        print("\n\n✓ Monitoring stopped")
        monitor.stop_monitoring()


async def example_monitor_specific_and_discover():
    """Example 4: Monitor specific markets + auto-discover others"""
    print("\n" + "=" * 60)
    print("Example 4: Mixed Monitoring Strategy")
    print("=" * 60)
    
    print("\n📊 Monitoring strategy:")
    print("   - High priority: BTC, ETH, BNB")
    print("   - Auto-discover: All other USDT markets")
    
    monitor = MultiMarketMonitor(
        min_volume_24h=50000.0,  # $50k minimum for auto-discovered
        max_concurrent=8
    )
    
    # Add alert handler
    monitor.add_alert_callback(alert_handler)
    
    # Start monitoring all
    try:
        await monitor.start_monitoring_all(quote_currency="USDT")
    except KeyboardInterrupt:
        print("\n\n✓ Monitoring stopped")
        monitor.stop_monitoring()


async def example_get_statistics():
    """Example 5: Get monitoring statistics"""
    print("\n" + "=" * 60)
    print("Example 5: Monitoring Statistics")
    print("=" * 60)
    
    monitor = MultiMarketMonitor()
    
    # Add alert handler
    def stats_alert_handler(alert: MarketAlert):
        print(f"   Alert: {alert.market} - {alert.alert_type.value}")
    
    monitor.add_alert_callback(stats_alert_handler)
    
    print("\n📊 Monitoring for 2 minutes to collect statistics...")
    
    # Start monitoring in background
    monitor_task = asyncio.create_task(
        monitor.start_monitoring_all(quote_currency="USDT")
    )
    
    try:
        # Wait 2 minutes
        await asyncio.sleep(120)
        
        # Get statistics
        stats = monitor.get_statistics()
        
        print(f"\n📈 Monitoring Statistics:")
        print(f"   Total Markets: {stats['total_markets']}")
        print(f"   Active Markets: {stats['active_markets']}")
        print(f"   Total Checks: {stats['total_checks']}")
        print(f"   Total Alerts: {stats['total_alerts']}")
        print(f"   High Risk Markets: {stats['high_risk_markets']}")
        print(f"   Medium Risk Markets: {stats['medium_risk_markets']}")
        print(f"   Uptime: {stats['uptime_seconds']:.0f} seconds")
        print(f"   Checks per Minute: {stats['checks_per_minute']:.1f}")
        
        # Get high-risk markets
        high_risk = monitor.get_high_risk_markets()
        if high_risk:
            print(f"\n⚠️  High Risk Markets:")
            for market in high_risk:
                print(f"   - {market}")
        
        # Get market priorities
        priorities = monitor.get_market_priorities()
        print(f"\n🎯 Top 10 Priority Markets:")
        for i, priority in enumerate(priorities[:10], 1):
            print(f"   {i}. {priority.market}")
            print(f"      Priority: {priority.priority_score:.2f}")
            print(f"      Volume: ${priority.volume_24h:,.0f}")
            print(f"      Check Interval: {priority.check_interval}s")
            print(f"      Alerts: {priority.alert_count}")
        
    finally:
        monitor.stop_monitoring()
        monitor_task.cancel()
        try:
            await monitor_task
        except asyncio.CancelledError:
            pass


async def example_adaptive_monitoring():
    """Example 6: Adaptive monitoring with dynamic priorities"""
    print("\n" + "=" * 60)
    print("Example 6: Adaptive Monitoring")
    print("=" * 60)
    
    print("\n📊 Adaptive monitoring features:")
    print("   - Markets with alerts get higher priority")
    print("   - Check intervals adapt based on risk")
    print("   - High-volume markets checked more frequently")
    print("   - Low-activity markets checked less often")
    
    monitor = MultiMarketMonitor(
        min_volume_24h=10000.0,
        max_concurrent=5,
        base_interval=60,
        high_priority_interval=30,  # High risk: every 30s
        low_priority_interval=300   # Low risk: every 5 min
    )
    
    # Enhanced alert handler
    def adaptive_alert_handler(alert: MarketAlert):
        print(f"\n🚨 {alert.market} - {alert.risk_level.value} RISK")
        print(f"   {alert.description}")
        
        if alert.risk_level.value == "HIGH":
            print(f"   ⚡ Priority increased - will check more frequently")
    
    monitor.add_alert_callback(adaptive_alert_handler)
    
    print("\n   Starting adaptive monitoring...")
    print("   Watch how check intervals adapt to market conditions\n")
    
    try:
        await monitor.start_monitoring_all(quote_currency="USDT")
    except KeyboardInterrupt:
        print("\n\n✓ Monitoring stopped")
        monitor.stop_monitoring()


def main():
    """Run examples"""
    print("\n" + "=" * 60)
    print("MONITOR ALL MARKETS - EXAMPLES")
    print("=" * 60)
    print("\nNote: Requires 'uv' and 'coinex-mcp-server'")
    print("Install: pip install uv && uvx coinex-mcp-server")
    
    try:
        # Run discovery example
        asyncio.run(example_discover_markets())
        
        # Run statistics example (2 minutes)
        # asyncio.run(example_get_statistics())
        
        # Uncomment to run continuous monitoring
        # asyncio.run(example_monitor_all_usdt())
        # asyncio.run(example_monitor_high_volume())
        # asyncio.run(example_adaptive_monitoring())
        
        print("\n" + "=" * 60)
        print("✅ Examples completed!")
        print("=" * 60)
        print("\nTo run continuous monitoring:")
        print("  - Uncomment the monitoring examples in main()")
        print("  - Press Ctrl+C to stop monitoring")
        print("\nFeatures:")
        print("  ✓ Auto-discovers all markets")
        print("  ✓ Filters by volume and quote currency")
        print("  ✓ Priority-based scheduling")
        print("  ✓ Adaptive check intervals")
        print("  ✓ Efficient resource usage")
        print("  ✓ Real-time statistics")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
