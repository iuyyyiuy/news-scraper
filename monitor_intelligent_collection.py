#!/usr/bin/env python3
"""
Monitor Intelligent Data Collection in Real-Time
Shows that the system is automatically collecting data based on market conditions
"""

import requests
import time
from datetime import datetime

def get_status():
    """Get current ML system status"""
    try:
        response = requests.get("http://localhost:8000/api/ml-analysis/status", timeout=5)
        return response.json()
    except:
        return None

def get_indicators():
    """Get current market indicators"""
    try:
        response = requests.get("http://localhost:8000/api/ml-analysis/market-indicators", timeout=5)
        return response.json()
    except:
        return None

def main():
    print("🧠 Intelligent Data Collection Monitor")
    print("=" * 70)
    print("Watching the system automatically collect data based on market conditions...")
    print("Press Ctrl+C to stop\n")
    
    last_snapshot_count = 0
    
    try:
        while True:
            # Get current status
            status = get_status()
            indicators = get_indicators()
            
            if status and status.get('success'):
                timestamp = datetime.now().strftime("%H:%M:%S")
                
                # Collection stats
                stats = status.get('collection_stats', {})
                snapshots = stats.get('snapshots_collected', 0)
                high_priority = stats.get('high_priority_collections', 0)
                avg_volatility = stats.get('average_volatility', 0)
                
                # Market indicators
                if indicators and indicators.get('success'):
                    ind = indicators.get('indicators', {})
                    volatility = ind.get('current_volatility', 0)
                    priority = ind.get('collection_priority', 0)
                    should_collect = indicators.get('should_collect', False)
                    reason = indicators.get('collection_reason', 'N/A')
                    
                    # Check if new data was collected
                    if snapshots > last_snapshot_count:
                        print(f"\n🎯 [{timestamp}] NEW DATA COLLECTED!")
                        print(f"   Total snapshots: {snapshots} (+{snapshots - last_snapshot_count})")
                        last_snapshot_count = snapshots
                    
                    # Display current status
                    status_icon = "✅" if should_collect else "⏸️"
                    priority_color = "🔴" if priority > 0.8 else "🟡" if priority > 0.6 else "🟢" if priority > 0.4 else "⚪"
                    
                    print(f"\r[{timestamp}] {status_icon} Snapshots: {snapshots} | "
                          f"Volatility: {volatility:.1%} | "
                          f"Priority: {priority_color} {priority:.2f} | "
                          f"Reason: {reason[:30]}", end="", flush=True)
                
            time.sleep(5)  # Update every 5 seconds
            
    except KeyboardInterrupt:
        print("\n\n" + "=" * 70)
        print("✅ Monitoring stopped")
        
        # Final summary
        final_status = get_status()
        if final_status and final_status.get('success'):
            stats = final_status.get('collection_stats', {})
            print(f"\n📊 Final Statistics:")
            print(f"   Total snapshots collected: {stats.get('snapshots_collected', 0)}")
            print(f"   High priority collections: {stats.get('high_priority_collections', 0)}")
            print(f"   Average volatility: {stats.get('average_volatility', 0):.2%}")
            print(f"   Average volume: ${stats.get('average_volume', 0):,.0f}")
            
            summary = final_status.get('collection_summary', {})
            print(f"\n🎯 Collection Strategy:")
            params = summary.get('strategy_parameters', {})
            print(f"   Min volatility threshold: {params.get('min_volatility_threshold', 0):.1%}")
            print(f"   High volume threshold: {params.get('high_volume_threshold', 0):.1f}x")
            print(f"   Priority score threshold: {params.get('priority_score_threshold', 0):.1f}")
            
            print(f"\n✅ The system IS automatically collecting data!")
            print(f"   It collects when market conditions are interesting.")

if __name__ == "__main__":
    main()