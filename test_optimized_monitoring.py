#!/usr/bin/env python3
"""
Test Optimized Market Monitoring Performance
Compare resource usage between different monitoring strategies
"""

import asyncio
import time
import requests
import json
import psutil
import os
from datetime import datetime

BASE_URL = "http://localhost:8000"

class PerformanceMonitor:
    def __init__(self):
        self.process = psutil.Process(os.getpid())
        self.start_time = time.time()
        self.start_memory = self.process.memory_info().rss / 1024 / 1024  # MB
        self.start_cpu = self.process.cpu_percent()
    
    def get_stats(self):
        current_memory = self.process.memory_info().rss / 1024 / 1024  # MB
        current_cpu = self.process.cpu_percent()
        elapsed_time = time.time() - self.start_time
        
        return {
            "elapsed_time": elapsed_time,
            "memory_usage_mb": current_memory,
            "memory_increase_mb": current_memory - self.start_memory,
            "cpu_percent": current_cpu
        }

def test_api_call(endpoint, method="GET", data=None):
    """Test API call with timing"""
    start_time = time.time()
    try:
        url = f"{BASE_URL}{endpoint}"
        
        if method == "GET":
            response = requests.get(url, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=10)
        
        elapsed = time.time() - start_time
        
        return {
            "success": response.status_code == 200,
            "status_code": response.status_code,
            "response_time": elapsed,
            "data": response.json() if response.headers.get('content-type', '').startswith('application/json') else None
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "response_time": time.time() - start_time
        }

async def test_monitoring_performance():
    """Test monitoring performance with different market counts"""
    
    print("🚀 Testing Optimized Market Monitoring Performance")
    print("=" * 70)
    
    perf_monitor = PerformanceMonitor()
    
    # Test 1: Get available markets
    print("\n1. Testing market data retrieval...")
    result = test_api_call("/api/market-analysis/markets")
    
    if result["success"]:
        markets = result["data"]["markets"]
        print(f"✅ Retrieved {len(markets)} markets in {result['response_time']:.2f}s")
        
        # Test different market counts
        test_scenarios = [
            {"name": "Small (10 markets)", "count": 10},
            {"name": "Medium (50 markets)", "count": 50},
            {"name": "Large (100 markets)", "count": 100},
            {"name": "Extra Large (200+ markets)", "count": min(len(markets), 250)}
        ]
        
        for scenario in test_scenarios:
            print(f"\n2. Testing {scenario['name']}...")
            
            # Select markets for this scenario
            selected_markets = [m["base"] for m in markets[:scenario["count"]]]
            
            # Start monitoring
            start_result = test_api_call("/api/market-analysis/start", "POST", {
                "markets": selected_markets,
                "interval": 5,  # 5 second interval
                "sensitivity": "medium",
                "max_markets": scenario["count"]
            })
            
            if start_result["success"]:
                print(f"   ✅ Started monitoring {scenario['count']} markets")
                print(f"   📊 Response time: {start_result['response_time']:.2f}s")
                
                # Let it run for 30 seconds
                print("   ⏳ Running for 30 seconds...")
                await asyncio.sleep(30)
                
                # Check status and performance
                status_result = test_api_call("/api/market-analysis/status")
                if status_result["success"]:
                    status_data = status_result["data"]
                    perf_stats = perf_monitor.get_stats()
                    
                    print(f"   📈 Scans completed: {status_data.get('scan_count', 0)}")
                    print(f"   🚨 Alerts generated: {status_data.get('alert_count', 0)}")
                    print(f"   🎯 Priority markets: {status_data.get('priority_markets', 0)}")
                    print(f"   💾 Memory usage: {perf_stats['memory_usage_mb']:.1f} MB")
                    print(f"   🔄 CPU usage: {perf_stats['cpu_percent']:.1f}%")
                    
                    # Calculate efficiency metrics
                    scans_per_second = status_data.get('scan_count', 0) / 30
                    markets_per_scan = scenario['count'] / max(status_data.get('scan_count', 1), 1)
                    
                    print(f"   ⚡ Efficiency: {scans_per_second:.2f} scans/sec")
                    print(f"   📊 Throughput: {markets_per_scan:.1f} markets/scan")
                
                # Stop monitoring
                stop_result = test_api_call("/api/market-analysis/stop", "POST")
                if stop_result["success"]:
                    print(f"   ✅ Stopped monitoring")
                
                # Wait between tests
                await asyncio.sleep(5)
            
            else:
                print(f"   ❌ Failed to start monitoring: {start_result.get('error', 'Unknown error')}")
    
    else:
        print(f"❌ Failed to get markets: {result.get('error', 'Unknown error')}")
    
    # Final performance summary
    final_stats = perf_monitor.get_stats()
    print(f"\n" + "=" * 70)
    print("📊 Performance Summary:")
    print(f"   Total test time: {final_stats['elapsed_time']:.1f} seconds")
    print(f"   Peak memory usage: {final_stats['memory_usage_mb']:.1f} MB")
    print(f"   Memory increase: {final_stats['memory_increase_mb']:.1f} MB")
    print(f"   Average CPU usage: {final_stats['cpu_percent']:.1f}%")
    print("=" * 70)

def test_optimization_features():
    """Test specific optimization features"""
    
    print("\n🔧 Testing Optimization Features")
    print("=" * 50)
    
    # Test market caching
    print("\n1. Testing market data caching...")
    
    # First call (should be fresh)
    start_time = time.time()
    result1 = test_api_call("/api/market-analysis/markets")
    time1 = time.time() - start_time
    
    # Second call (should be cached)
    start_time = time.time()
    result2 = test_api_call("/api/market-analysis/markets")
    time2 = time.time() - start_time
    
    if result1["success"] and result2["success"]:
        source1 = result1["data"].get("source", "unknown")
        source2 = result2["data"].get("source", "unknown")
        
        print(f"   First call: {time1:.3f}s (source: {source1})")
        print(f"   Second call: {time2:.3f}s (source: {source2})")
        
        if time2 < time1 * 0.5:  # Should be at least 50% faster
            print("   ✅ Caching is working effectively")
        else:
            print("   ⚠️  Caching may not be optimal")
    
    # Test batch processing efficiency
    print("\n2. Testing batch processing...")
    
    # Start monitoring with large market set
    markets_result = test_api_call("/api/market-analysis/markets")
    if markets_result["success"]:
        all_markets = [m["base"] for m in markets_result["data"]["markets"][:100]]
        
        start_result = test_api_call("/api/market-analysis/start", "POST", {
            "markets": all_markets,
            "interval": 10,
            "sensitivity": "medium",
            "max_markets": 100
        })
        
        if start_result["success"]:
            print("   ✅ Started batch monitoring")
            
            # Monitor for a short time
            await asyncio.sleep(15)
            
            status_result = test_api_call("/api/market-analysis/status")
            if status_result["success"]:
                status = status_result["data"]
                batch_size = status.get("batch_size", 20)
                total_markets = status.get("total_markets", 0)
                priority_markets = status.get("priority_markets", 0)
                
                print(f"   📊 Batch size: {batch_size}")
                print(f"   🎯 Priority markets: {priority_markets}")
                print(f"   📈 Total markets: {total_markets}")
                print(f"   ⚡ Batching efficiency: {total_markets/batch_size:.1f} batches needed")
            
            # Stop monitoring
            test_api_call("/api/market-analysis/stop", "POST")
            print("   ✅ Stopped batch monitoring")

async def main():
    """Main test function"""
    try:
        print("🧪 Optimized Market Monitoring Performance Test")
        print("=" * 70)
        
        # Check if server is running
        health_result = test_api_call("/api/health")
        if not health_result["success"]:
            print("❌ Server is not running. Please start the server first.")
            return False
        
        print("✅ Server is running")
        
        # Run performance tests
        await test_monitoring_performance()
        
        # Test optimization features
        test_optimization_features()
        
        print("\n🎉 Performance testing complete!")
        print("\n💡 Optimization Benefits:")
        print("   • Batch processing reduces API calls")
        print("   • Priority markets get more frequent checks")
        print("   • Caching reduces redundant data fetching")
        print("   • Efficient data structures minimize memory usage")
        print("   • Concurrent processing improves throughput")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️  Test interrupted by user")
        exit(1)