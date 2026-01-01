#!/usr/bin/env python3
"""
Test Live Article Count Filter
Tests the complete workflow with the running web server
"""

import requests
import json
import time
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_live_article_count_filter():
    """Test the article count filter with the live server"""
    
    print("🌐 Testing Live Article Count Filter")
    print("=" * 60)
    
    # Test with a small number first (300 articles per source)
    test_value = 300
    
    print(f"📊 Testing manual update with {test_value} articles per source")
    print("-" * 40)
    
    try:
        # Test API endpoint
        api_url = "http://localhost:5000/api/manual-update"
        
        payload = {
            "max_articles": test_value
        }
        
        headers = {
            "Content-Type": "application/json"
        }
        
        print(f"📡 Sending POST request to {api_url}")
        print(f"📦 Payload: {json.dumps(payload, indent=2)}")
        
        # Make the request
        response = requests.post(api_url, json=payload, headers=headers, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ API Response: {json.dumps(result, indent=2)}")
            
            # Check if max_articles is properly reflected in response
            if result.get('success'):
                print("✅ Manual update started successfully")
                
                # Check parameters in response
                if 'parameters' in result:
                    params = result['parameters']
                    max_articles_per_source = params.get('max_articles_per_source')
                    
                    if max_articles_per_source == test_value:
                        print(f"✅ Article count parameter correctly set to {test_value}")
                        print("✅ Complete workflow test PASSED")
                        
                        # Show the process details
                        if 'process' in result:
                            print("\n📋 Process steps:")
                            for i, step in enumerate(result['process'], 1):
                                print(f"   {i}. {step}")
                        
                        return True
                    else:
                        print(f"❌ Article count mismatch: expected {test_value}, got {max_articles_per_source}")
                        return False
                else:
                    print("⚠️  Response missing parameters section")
                    return False
            else:
                print(f"❌ API returned success=False: {result.get('message', 'Unknown error')}")
                return False
        else:
            print(f"❌ API Error: {response.status_code} - {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection error - is the server running on localhost:5000?")
        return False
    except requests.exceptions.Timeout:
        print("⏰ Request timeout")
        return False
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False

def test_dashboard_access():
    """Test dashboard accessibility"""
    
    print("\n🌐 Testing Dashboard Access")
    print("-" * 40)
    
    try:
        dashboard_url = "http://localhost:5000/dashboard"
        
        print(f"📡 Accessing dashboard at {dashboard_url}")
        
        response = requests.get(dashboard_url, timeout=5)
        
        if response.status_code == 200:
            print("✅ Dashboard accessible")
            
            # Check if the HTML contains our article count select
            if 'article-count-select' in response.text:
                print("✅ Dashboard contains article count filter")
                
                # Check for specific options
                options_found = 0
                test_options = ['100篇/源', '300篇/源', '500篇/源', '1000篇/源', '2000篇/源']
                
                for option in test_options:
                    if option in response.text:
                        options_found += 1
                
                print(f"✅ Found {options_found}/{len(test_options)} article count options")
                
                if options_found == len(test_options):
                    print("✅ All article count options present")
                    return True
                else:
                    print("⚠️  Some article count options missing")
                    return False
            else:
                print("❌ Dashboard missing article count filter")
                return False
        else:
            print(f"❌ Dashboard error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Dashboard test error: {e}")
        return False

def test_api_health():
    """Test API health endpoint"""
    
    print("\n🔍 Testing API Health")
    print("-" * 40)
    
    try:
        health_url = "http://localhost:5000/api/health"
        
        response = requests.get(health_url, timeout=5)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Health check passed: {result.get('status', 'unknown')}")
            
            # Check database connection
            if 'database' in result:
                db_status = result['database']
                if 'connected' in db_status:
                    print(f"✅ Database connected: {db_status}")
                else:
                    print(f"⚠️  Database status: {db_status}")
            
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def main():
    """Run all live tests"""
    print("🚀 Starting Live Article Count Filter Tests")
    print("=" * 60)
    
    # Test API health first
    health_ok = test_api_health()
    
    # Test dashboard access
    dashboard_ok = test_dashboard_access()
    
    # Test article count filter functionality
    filter_ok = test_live_article_count_filter()
    
    print("\n" + "=" * 60)
    print("🏁 Live Tests Complete")
    print("=" * 60)
    
    print(f"\n📊 Test Results:")
    print(f"   API Health: {'✅ PASS' if health_ok else '❌ FAIL'}")
    print(f"   Dashboard Access: {'✅ PASS' if dashboard_ok else '❌ FAIL'}")
    print(f"   Article Count Filter: {'✅ PASS' if filter_ok else '❌ FAIL'}")
    
    if health_ok and dashboard_ok and filter_ok:
        print(f"\n🎉 ALL TESTS PASSED!")
        print(f"✅ Article count filter is working correctly")
        print(f"🌐 Dashboard: http://localhost:5000/dashboard")
        print(f"📚 API Docs: http://localhost:5000/docs")
    else:
        print(f"\n⚠️  Some tests failed - check the output above")
    
    return health_ok and dashboard_ok and filter_ok

if __name__ == "__main__":
    main()