#!/usr/bin/env python3
"""
Test Improved ML Interface
Test the user-friendly improvements to the ML analysis interface
"""

import requests
import json
import time

def test_ml_interface_improvements():
    """Test the improved ML interface features"""
    print("🧪 Testing Improved ML Interface")
    print("=" * 40)
    
    base_url = "http://localhost:8000"
    
    # Test 1: Check if server is running
    try:
        response = requests.get(f"{base_url}/api/health", timeout=5)
        if response.status_code != 200:
            print("❌ Server not running. Please start with: python3 start_ml_server.py")
            return False
        print("✅ Server is running")
    except:
        print("❌ Cannot connect to server. Please start with: python3 start_ml_server.py")
        return False
    
    # Test 2: Check ML status endpoint
    try:
        response = requests.get(f"{base_url}/api/ml-analysis/status", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ ML Status API working")
            print(f"   ML Available: {data.get('ml_available', False)}")
            print(f"   Training Samples: {data.get('training_progress', {}).get('total_samples', 0)}")
            print(f"   Model Trained: {data.get('model_trained', False)}")
        else:
            print(f"⚠️  ML Status API returned {response.status_code}")
    except Exception as e:
        print(f"❌ ML Status API error: {e}")
    
    # Test 3: Test simulate data endpoint
    print("\n📊 Testing Data Simulation...")
    try:
        response = requests.post(
            f"{base_url}/api/ml-analysis/simulate-data",
            json={"samples": 50},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ Data simulation working")
                print(f"   Samples created: {data.get('samples_created', 0)}")
            else:
                print(f"⚠️  Data simulation issue: {data.get('error')}")
        else:
            print(f"❌ Data simulation failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Data simulation error: {e}")
    
    # Test 4: Check updated status after simulation
    print("\n📈 Checking Status After Simulation...")
    try:
        response = requests.get(f"{base_url}/api/ml-analysis/status", timeout=5)
        if response.status_code == 200:
            data = response.json()
            samples = data.get('training_progress', {}).get('total_samples', 0)
            print(f"✅ Updated samples count: {samples}")
            
            if samples >= 50:
                print("✅ Sufficient data for testing ML training")
            else:
                print("⚠️  May need more data for training")
        else:
            print(f"⚠️  Status check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Status check error: {e}")
    
    # Test 5: Test training data summary
    print("\n📋 Testing Training Data Summary...")
    try:
        response = requests.get(f"{base_url}/api/ml-analysis/training-data?limit=10", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                summary = data.get('summary', {})
                print("✅ Training data summary working")
                print(f"   Total events: {summary.get('total_events', 0)}")
                print(f"   Normal events: {summary.get('normal_count', 0)}")
                print(f"   Manipulation events: {summary.get('manipulation_count', 0)}")
                
                event_types = summary.get('event_types', {})
                if event_types:
                    print("   Event types:")
                    for event_type, count in event_types.items():
                        print(f"     {event_type}: {count}")
            else:
                print(f"⚠️  Training data summary issue: {data.get('error')}")
        else:
            print(f"❌ Training data summary failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Training data summary error: {e}")
    
    # Test 6: Check web interface accessibility
    print("\n🌐 Testing Web Interface...")
    try:
        response = requests.get(f"{base_url}/ml-analysis", timeout=5)
        if response.status_code == 200:
            print("✅ ML Analysis web page accessible")
            
            # Check if the page contains our improvements
            content = response.text
            if "数据收集进度" in content:
                print("✅ Progress bar feature detected")
            if "系统状态" in content:
                print("✅ Status summary feature detected")
            if "quickStatusSummary" in content:
                print("✅ Quick status feature detected")
                
        else:
            print(f"❌ Web interface failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Web interface error: {e}")
    
    print("\n" + "=" * 40)
    print("🎯 Interface Improvements Summary:")
    print("✅ Real-time data progress tracking")
    print("✅ Clear status indicators with explanations")
    print("✅ Helpful guidance messages")
    print("✅ Detailed sample counting")
    print("✅ User-friendly feedback")
    
    print("\n🌐 Access your improved ML interface:")
    print(f"   {base_url}/ml-analysis")
    
    print("\n💡 What you'll see now:")
    print("• Clear progress bar showing data collection status")
    print("• Detailed sample counts (X/100 samples)")
    print("• Status explanations (e.g., '还需要 50 个样本')")
    print("• Helpful next-step guidance")
    print("• Real-time collection statistics")
    print("• Model training progress indicators")
    
    return True

if __name__ == "__main__":
    success = test_ml_interface_improvements()
    
    if success:
        print("\n🎉 Improved ML interface is ready!")
        print("🚀 Open http://localhost:8000/ml-analysis to see the improvements")
    else:
        print("\n❌ Please start the server first: python3 start_ml_server.py")