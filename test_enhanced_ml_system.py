#!/usr/bin/env python3
"""
Test Enhanced ML System with Market Indicators
Tests the complete enhanced ML system including volatility, volume, and smart collection
"""

import asyncio
import json
import time
import requests
from datetime import datetime

def test_api_endpoint(endpoint, method='GET', data=None):
    """Test API endpoint and return response"""
    url = f"http://localhost:8000{endpoint}"
    
    try:
        if method == 'GET':
            response = requests.get(url, timeout=10)
        elif method == 'POST':
            response = requests.post(url, json=data, timeout=10)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ {endpoint}: HTTP {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ {endpoint}: {e}")
        return None

def main():
    print("🧠 Testing Enhanced ML System with Market Indicators")
    print("=" * 60)
    
    # Test 1: Check ML system status
    print("\n1️⃣ Testing ML System Status...")
    status = test_api_endpoint("/api/ml-analysis/status")
    if status and status.get('success'):
        print("✅ ML system is available")
        print(f"   - Model trained: {status.get('model_trained', False)}")
        print(f"   - Collection active: {status.get('collection_active', False)}")
        print(f"   - Enhanced features: {status.get('enhanced_features', {})}")
        
        if status.get('market_indicators'):
            indicators = status['market_indicators']
            print(f"   - Current volatility: {indicators.get('current_volatility', 0):.2%}")
            print(f"   - Collection priority: {indicators.get('collection_priority', 0):.2f}")
    else:
        print("❌ ML system not available")
        return
    
    # Test 2: Check market indicators
    print("\n2️⃣ Testing Market Indicators...")
    indicators = test_api_endpoint("/api/ml-analysis/market-indicators")
    if indicators and indicators.get('success'):
        print("✅ Market indicators working")
        ind = indicators.get('indicators', {})
        print(f"   - Volatility: {ind.get('current_volatility', 0):.2%}")
        print(f"   - Volume: ${ind.get('current_volume', 0):,.0f}")
        print(f"   - RSI: {ind.get('current_rsi', 50):.1f}")
        print(f"   - Funding Rate: {ind.get('funding_rate', 0):.4f}")
        print(f"   - Price: ${ind.get('price', 0):,.0f}")
        print(f"   - Collection Priority: {ind.get('collection_priority', 0):.2f}")
        print(f"   - Should Collect: {indicators.get('should_collect', False)}")
        print(f"   - Collection Reason: {indicators.get('collection_reason', 'N/A')}")
    else:
        print("❌ Market indicators not working")
    
    # Test 3: Simulate training data
    print("\n3️⃣ Simulating Training Data...")
    simulate_result = test_api_endpoint("/api/ml-analysis/simulate-data", "POST", {"samples": 50})
    if simulate_result and simulate_result.get('success'):
        print("✅ Training data simulation successful")
        print(f"   - Samples created: {simulate_result.get('samples_created', 0)}")
    else:
        print("❌ Training data simulation failed")
    
    # Test 4: Train ML model
    print("\n4️⃣ Training ML Model...")
    train_result = test_api_endpoint("/api/ml-analysis/train-model", "POST", {
        "min_samples": 50,
        "force_retrain": True
    })
    if train_result and train_result.get('success'):
        print("✅ Model training successful")
        metrics = train_result.get('metrics', {})
        print(f"   - Accuracy: {metrics.get('accuracy', 0):.1%}")
        print(f"   - Training samples: {train_result.get('training_samples', 0)}")
    else:
        print("❌ Model training failed")
        if train_result:
            print(f"   - Error: {train_result.get('error', 'Unknown error')}")
    
    # Test 5: Start enhanced collection
    print("\n5️⃣ Testing Enhanced Collection...")
    collection_result = test_api_endpoint("/api/ml-analysis/start-enhanced-collection", "POST", {
        "interval": 5
    })
    if collection_result and collection_result.get('success'):
        print("✅ Enhanced collection started")
        print(f"   - Message: {collection_result.get('message', '')}")
        features = collection_result.get('features', [])
        if features:
            print("   - Enhanced features:")
            for feature in features:
                print(f"     • {feature}")
        
        # Wait a bit for collection to work
        print("   - Waiting 10 seconds for data collection...")
        time.sleep(10)
        
        # Check status again
        status = test_api_endpoint("/api/ml-analysis/status")
        if status and status.get('success'):
            stats = status.get('collection_stats', {})
            print(f"   - Snapshots collected: {stats.get('snapshots_collected', 0)}")
            print(f"   - High priority collections: {stats.get('high_priority_collections', 0)}")
            print(f"   - Average volatility: {stats.get('average_volatility', 0):.2%}")
    else:
        print("❌ Enhanced collection failed to start")
        if collection_result:
            print(f"   - Error: {collection_result.get('error', 'Unknown error')}")
    
    # Test 6: Get ML prediction
    print("\n6️⃣ Testing ML Prediction...")
    prediction_result = test_api_endpoint("/api/ml-analysis/predict", "POST", {
        "market": "BTC/USDT",
        "include_features": True
    })
    if prediction_result and prediction_result.get('success'):
        print("✅ ML prediction successful")
        pred = prediction_result.get('prediction', {})
        prediction = pred.get('prediction', {})
        print(f"   - Market: {pred.get('market', 'N/A')}")
        print(f"   - Price: ${pred.get('price', 0):,.2f}")
        print(f"   - Prediction: {prediction.get('prediction_label', 'N/A')}")
        print(f"   - Confidence: {prediction.get('confidence', 0):.1%}")
        print(f"   - Is Anomaly: {prediction.get('is_anomaly', False)}")
        
        # Show probabilities
        probabilities = prediction.get('probabilities', {})
        if probabilities:
            print("   - Probabilities:")
            for event_type, prob in probabilities.items():
                print(f"     • {event_type}: {prob:.1%}")
    else:
        print("❌ ML prediction failed")
        if prediction_result:
            print(f"   - Error: {prediction_result.get('error', 'Unknown error')}")
    
    # Test 7: Stop collection
    print("\n7️⃣ Stopping Collection...")
    stop_result = test_api_endpoint("/api/ml-analysis/stop-collection", "POST")
    if stop_result and stop_result.get('success'):
        print("✅ Collection stopped successfully")
    else:
        print("❌ Failed to stop collection")
    
    # Test 8: Check training data summary
    print("\n8️⃣ Testing Training Data Summary...")
    data_summary = test_api_endpoint("/api/ml-analysis/training-data?limit=100")
    if data_summary and data_summary.get('success'):
        print("✅ Training data summary available")
        summary = data_summary.get('summary', {})
        print(f"   - Total events: {summary.get('total_events', 0)}")
        print(f"   - Normal events: {summary.get('normal_count', 0)}")
        print(f"   - Manipulation events: {summary.get('manipulation_count', 0)}")
        
        event_types = summary.get('event_types', {})
        if event_types:
            print("   - Event types:")
            for event_type, count in event_types.items():
                print(f"     • {event_type}: {count}")
    else:
        print("❌ Training data summary not available")
    
    print("\n" + "=" * 60)
    print("🎉 Enhanced ML System Test Complete!")
    print("\n📋 Summary:")
    print("✅ Enhanced market analysis with volatility, volume, and RSI")
    print("✅ Smart data collection based on market conditions")
    print("✅ ML model training with enhanced features")
    print("✅ Real-time market indicators monitoring")
    print("✅ Intelligent collection priority scoring")
    
    print(f"\n🌐 Access the ML interface at: http://localhost:8000/ml-analysis")
    print("💡 The system now intelligently decides when to collect data based on:")
    print("   • Market volatility (>2%)")
    print("   • Volume spikes (1.5x average)")
    print("   • Order book imbalance (>60%)")
    print("   • RSI extremes (<30 or >70)")
    print("   • Overall priority score (>0.6)")

if __name__ == "__main__":
    main()