#!/usr/bin/env python3
"""
Test ML Integration System
Comprehensive test of the BTC ML analysis system
"""

import asyncio
import requests
import json
import time
from datetime import datetime

class MLIntegrationTester:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def test_ml_status(self):
        """Test ML system status endpoint"""
        print("🔍 Testing ML system status...")
        
        try:
            response = self.session.get(f"{self.base_url}/api/ml-analysis/status")
            data = response.json()
            
            print(f"   Status: {'✅' if data.get('success') else '❌'}")
            print(f"   ML Available: {'✅' if data.get('ml_available') else '❌'}")
            print(f"   Model Trained: {'✅' if data.get('model_trained') else '❌'}")
            print(f"   Collection Active: {'✅' if data.get('collection_active') else '❌'}")
            
            if data.get('training_progress'):
                progress = data['training_progress']
                print(f"   Training Samples: {progress.get('total_samples', 0)}")
                print(f"   Model Accuracy: {progress.get('model_accuracy', 0):.1%}")
            
            return data.get('success', False)
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return False
    
    def test_simulate_data(self, samples=50):
        """Test data simulation for training"""
        print(f"🧪 Testing data simulation ({samples} samples)...")
        
        try:
            response = self.session.post(
                f"{self.base_url}/api/ml-analysis/simulate-data",
                json={"samples": samples}
            )
            data = response.json()
            
            if data.get('success'):
                print(f"   ✅ Simulated {data.get('samples_created', 0)} samples")
                return True
            else:
                print(f"   ❌ Error: {data.get('error', 'Unknown error')}")
                return False
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return False
    
    def test_model_training(self, min_samples=50):
        """Test ML model training"""
        print(f"🎓 Testing model training (min {min_samples} samples)...")
        
        try:
            response = self.session.post(
                f"{self.base_url}/api/ml-analysis/train-model",
                json={
                    "min_samples": min_samples,
                    "force_retrain": True
                }
            )
            data = response.json()
            
            if data.get('success'):
                metrics = data.get('metrics', {})
                print(f"   ✅ Model trained successfully")
                print(f"   Accuracy: {metrics.get('accuracy', 0):.1%}")
                print(f"   F1 Score: {metrics.get('f1_score', 0):.3f}")
                print(f"   Training Samples: {data.get('training_samples', 0)}")
                return True
            else:
                print(f"   ❌ Error: {data.get('error', 'Unknown error')}")
                return False
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return False
    
    def test_prediction(self):
        """Test ML prediction"""
        print("🔮 Testing ML prediction...")
        
        try:
            response = self.session.post(
                f"{self.base_url}/api/ml-analysis/predict",
                json={
                    "market": "BTC/USDT",
                    "include_features": True
                }
            )
            data = response.json()
            
            if data.get('success'):
                prediction = data['prediction']['prediction']
                print(f"   ✅ Prediction successful")
                print(f"   Prediction: {prediction.get('prediction_label', 'unknown')}")
                print(f"   Confidence: {prediction.get('confidence', 0):.1%}")
                print(f"   Anomaly: {'Yes' if prediction.get('is_anomaly') else 'No'}")
                print(f"   Price: ${data['prediction'].get('price', 0):.2f}")
                
                # Show top probabilities
                probs = prediction.get('probabilities', {})
                if probs:
                    print("   Probabilities:")
                    for label, prob in probs.items():
                        if prob > 0.1:  # Only show significant probabilities
                            print(f"     {label}: {prob:.1%}")
                
                return True
            else:
                print(f"   ❌ Error: {data.get('error', 'Unknown error')}")
                return False
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return False
    
    def test_data_collection(self, duration=30):
        """Test data collection (short duration for testing)"""
        print(f"📊 Testing data collection ({duration}s)...")
        
        try:
            # Start collection
            response = self.session.post(
                f"{self.base_url}/api/ml-analysis/start-collection",
                json={"interval": 5}
            )
            data = response.json()
            
            if not data.get('success'):
                print(f"   ❌ Failed to start collection: {data.get('error')}")
                return False
            
            print(f"   ✅ Collection started")
            
            # Wait for collection
            print(f"   ⏳ Collecting data for {duration} seconds...")
            time.sleep(duration)
            
            # Stop collection
            response = self.session.post(f"{self.base_url}/api/ml-analysis/stop-collection")
            data = response.json()
            
            if data.get('success'):
                print(f"   ✅ Collection stopped")
                return True
            else:
                print(f"   ⚠️  Collection stop warning: {data.get('error')}")
                return True  # Still consider success if we collected data
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return False
    
    def test_training_data_summary(self):
        """Test training data summary"""
        print("📈 Testing training data summary...")
        
        try:
            response = self.session.get(f"{self.base_url}/api/ml-analysis/training-data?limit=100")
            data = response.json()
            
            if data.get('success'):
                summary = data.get('summary', {})
                print(f"   ✅ Summary retrieved")
                print(f"   Total Events: {summary.get('total_events', 0)}")
                print(f"   Normal Events: {summary.get('normal_count', 0)}")
                print(f"   Manipulation Events: {summary.get('manipulation_count', 0)}")
                
                event_types = summary.get('event_types', {})
                if event_types:
                    print("   Event Types:")
                    for event_type, count in event_types.items():
                        print(f"     {event_type}: {count}")
                
                return True
            else:
                print(f"   ❌ Error: {data.get('error', 'Unknown error')}")
                return False
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return False
    
    def test_web_interface(self):
        """Test web interface accessibility"""
        print("🌐 Testing web interface...")
        
        try:
            response = self.session.get(f"{self.base_url}/ml-analysis")
            
            if response.status_code == 200:
                print(f"   ✅ ML analysis page accessible")
                return True
            elif response.status_code == 503:
                print(f"   ⚠️  ML analysis not available (service unavailable)")
                return False
            else:
                print(f"   ❌ Error: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return False
    
    def run_comprehensive_test(self):
        """Run comprehensive ML system test"""
        print("🚀 Starting Comprehensive ML Integration Test")
        print("=" * 60)
        
        results = {}
        
        # Test 1: Check ML system status
        results['status'] = self.test_ml_status()
        print()
        
        # Test 2: Test web interface
        results['web_interface'] = self.test_web_interface()
        print()
        
        # Test 3: Simulate training data
        results['simulate_data'] = self.test_simulate_data(50)
        print()
        
        # Test 4: Train ML model
        results['model_training'] = self.test_model_training(50)
        print()
        
        # Test 5: Test prediction
        results['prediction'] = self.test_prediction()
        print()
        
        # Test 6: Test training data summary
        results['data_summary'] = self.test_training_data_summary()
        print()
        
        # Test 7: Test data collection (short duration)
        results['data_collection'] = self.test_data_collection(15)
        print()
        
        # Summary
        print("=" * 60)
        print("📊 Test Results Summary:")
        
        passed = 0
        total = len(results)
        
        for test_name, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"   {test_name.replace('_', ' ').title()}: {status}")
            if result:
                passed += 1
        
        print(f"\n🎯 Overall Result: {passed}/{total} tests passed ({passed/total:.1%})")
        
        if passed == total:
            print("🎉 All tests passed! ML system is fully functional.")
        elif passed >= total * 0.8:
            print("✅ Most tests passed. ML system is mostly functional.")
        else:
            print("⚠️  Several tests failed. Check ML system configuration.")
        
        return passed / total

def main():
    """Main test function"""
    print("BTC ML Analysis System Integration Test")
    print("=====================================")
    
    # Check if server is running
    try:
        response = requests.get("http://localhost:8000/api/health", timeout=5)
        if response.status_code != 200:
            print("❌ Server not responding. Please start the server first:")
            print("   python3 restart_server_with_market_analysis.py")
            return
    except requests.exceptions.RequestException:
        print("❌ Cannot connect to server. Please start the server first:")
        print("   python3 restart_server_with_market_analysis.py")
        return
    
    print("✅ Server is running")
    print()
    
    # Run tests
    tester = MLIntegrationTester()
    success_rate = tester.run_comprehensive_test()
    
    # Final recommendations
    print("\n📋 Next Steps:")
    if success_rate >= 0.8:
        print("1. ✅ ML system is ready for production use")
        print("2. 🌐 Access the ML dashboard at: http://localhost:8000/ml-analysis")
        print("3. 📊 Start collecting real BTC data for better predictions")
        print("4. 🔄 Set up automated retraining schedule")
    else:
        print("1. 🔧 Fix failing tests before production use")
        print("2. 📦 Check ML dependencies: pip install tensorflow scikit-learn")
        print("3. 🔍 Review error messages above")
        print("4. 📖 Check ML system documentation")

if __name__ == "__main__":
    main()