"""
ML Integration API for Market Analysis System
Integrates BTC ML model with enhanced market indicators (volatility, open interest, volume)
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import asyncio
import json
import logging
import time
import os

# Import ML components
from btc_deep_analyzer import BTCOrderBookMLModel, BTCDataCollector, OrderBookSnapshot, MarketEvent
from btc_live_collector import BTCLiveCollector
from enhanced_market_analyzer import EnhancedDataCollector, MarketIndicators, EnhancedMarketSnapshot

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/ml-analysis", tags=["ml-analysis"])

# Global ML state with enhanced features
ml_state = {
    "btc_collector": None,
    "enhanced_collector": None,  # New enhanced collector
    "ml_model": None,
    "data_collector": None,
    "collection_active": False,
    "model_trained": False,
    "last_prediction": None,
    "training_progress": {
        "samples_collected": 0,
        "last_training": None,
        "model_accuracy": 0.0,
        "training_status": "not_started"
    },
    "live_predictions": [],
    "collection_stats": {
        "start_time": None,
        "snapshots_collected": 0,
        "events_created": 0,
        "anomalies_detected": 0,
        "high_priority_collections": 0,  # New metric
        "average_volatility": 0.0,       # New metric
        "average_volume": 0.0            # New metric
    },
    "market_indicators": {
        "current_volatility": 0.0,
        "current_volume": 0.0,
        "current_rsi": 50.0,
        "funding_rate": 0.0,
        "collection_priority": 0.0
    }
}

class MLTrainingRequest(BaseModel):
    force_retrain: bool = False
    min_samples: int = 100

class MLPredictionRequest(BaseModel):
    market: str = "BTC/USDT"
    include_features: bool = True

@router.get("/status")
async def get_ml_status():
    """Get ML system status with enhanced market indicators"""
    try:
        # Initialize components if needed
        if not ml_state["ml_model"]:
            ml_state["ml_model"] = BTCOrderBookMLModel()
            ml_state["data_collector"] = BTCDataCollector()
            ml_state["enhanced_collector"] = EnhancedDataCollector()
        
        # Check if model is trained
        model_trained = ml_state["ml_model"].load_model()
        ml_state["model_trained"] = model_trained
        
        # Get training data count
        training_events = ml_state["data_collector"].get_training_events(1)
        total_samples = len(ml_state["data_collector"].get_training_events(10000))
        
        # Get enhanced collection summary
        collection_summary = {}
        if ml_state["enhanced_collector"]:
            collection_summary = ml_state["enhanced_collector"].get_collection_summary()
        
        return {
            "success": True,
            "ml_available": True,
            "model_trained": model_trained,
            "collection_active": ml_state["collection_active"],
            "training_progress": {
                **ml_state["training_progress"],
                "total_samples": total_samples
            },
            "collection_stats": ml_state["collection_stats"],
            "market_indicators": ml_state["market_indicators"],
            "enhanced_features": {
                "volatility_tracking": True,
                "volume_analysis": True,
                "open_interest_monitoring": True,
                "smart_collection": True
            },
            "collection_summary": collection_summary,
            "last_prediction": ml_state["last_prediction"],
            "live_predictions_count": len(ml_state["live_predictions"])
        }
    
    except Exception as e:
        logger.error(f"Error getting ML status: {e}")
        return {
            "success": False,
            "error": str(e),
            "ml_available": False
        }

@router.get("/market-indicators")
async def get_current_market_indicators():
    """Get current market indicators (volatility, volume, open interest)"""
    try:
        if not ml_state["enhanced_collector"]:
            ml_state["enhanced_collector"] = EnhancedDataCollector()
        
        # Get current market snapshot
        enhanced_snapshot = await ml_state["enhanced_collector"].collect_enhanced_snapshot()
        
        if enhanced_snapshot:
            # Update global state
            ml_state["market_indicators"] = {
                "current_volatility": enhanced_snapshot.indicators.volatility,
                "current_volume": enhanced_snapshot.indicators.volume_24h,
                "current_rsi": enhanced_snapshot.indicators.rsi or 50.0,
                "funding_rate": enhanced_snapshot.indicators.funding_rate or 0.0,
                "collection_priority": enhanced_snapshot.collection_priority,
                "prediction_confidence": enhanced_snapshot.prediction_confidence,
                "price": enhanced_snapshot.indicators.price,
                "price_momentum": enhanced_snapshot.indicators.price_momentum or 0.0
            }
            
            return {
                "success": True,
                "indicators": ml_state["market_indicators"],
                "should_collect": ml_state["enhanced_collector"].should_collect_data(enhanced_snapshot),
                "collection_reason": get_collection_reason(enhanced_snapshot),
                "timestamp": enhanced_snapshot.indicators.timestamp
            }
        else:
            return {
                "success": False,
                "error": "Failed to collect market indicators"
            }
    
    except Exception as e:
        logger.error(f"Error getting market indicators: {e}")
        return {
            "success": False,
            "error": str(e)
        }

def get_collection_reason(snapshot: EnhancedMarketSnapshot) -> str:
    """Get human-readable reason for data collection decision"""
    reasons = []
    
    if snapshot.collection_priority > 0.6:
        reasons.append(f"High priority score ({snapshot.collection_priority:.2f})")
    
    if snapshot.indicators.volatility > 0.02:
        reasons.append(f"High volatility ({snapshot.indicators.volatility:.1%})")
    
    if abs(snapshot.orderbook.imbalance) > 0.6:
        reasons.append(f"Order book imbalance ({snapshot.orderbook.imbalance:.2f})")
    
    if snapshot.indicators.rsi and (snapshot.indicators.rsi < 30 or snapshot.indicators.rsi > 70):
        reasons.append(f"RSI extreme ({snapshot.indicators.rsi:.1f})")
    
    if not reasons:
        reasons.append("Normal market conditions")
    
    return "; ".join(reasons)

@router.post("/start-enhanced-collection")
async def start_enhanced_collection(background_tasks: BackgroundTasks, interval: int = 10):
    """Start enhanced data collection with market indicators"""
    try:
        if ml_state["collection_active"]:
            return {
                "success": False,
                "error": "数据收集已在运行中"
            }
        
        # Initialize enhanced collector
        if not ml_state["enhanced_collector"]:
            ml_state["enhanced_collector"] = EnhancedDataCollector()
        
        # Start enhanced collection in background
        background_tasks.add_task(run_enhanced_collection, interval)
        
        ml_state["collection_active"] = True
        ml_state["collection_stats"]["start_time"] = datetime.now()
        
        logger.info(f"Started enhanced BTC data collection with {interval}s interval")
        
        return {
            "success": True,
            "message": f"开始增强型BTC数据收集 (间隔: {interval}秒)",
            "features": [
                "实时波动率监控",
                "成交量分析",
                "资金费率跟踪", 
                "智能数据收集策略",
                "RSI和布林带指标",
                "订单簿深度分析"
            ],
            "interval": interval
        }
    
    except Exception as e:
        logger.error(f"Error starting enhanced collection: {e}")
        return {
            "success": False,
            "error": str(e)
        }

async def run_enhanced_collection(interval: int):
    """Run enhanced collection with market indicators"""
    try:
        collector = ml_state["enhanced_collector"]
        if not collector:
            return
        
        logger.info("Starting enhanced BTC collection background task")
        
        collected_count = 0
        high_priority_count = 0
        volatility_sum = 0.0
        volume_sum = 0.0
        
        while ml_state["collection_active"]:
            try:
                # Collect enhanced snapshot
                enhanced_snapshot = await collector.collect_enhanced_snapshot()
                
                if enhanced_snapshot:
                    # Decide whether to collect this data
                    should_collect = collector.should_collect_data(enhanced_snapshot)
                    
                    if should_collect:
                        # Store the order book snapshot
                        ml_state["data_collector"].store_snapshot(enhanced_snapshot.orderbook)
                        
                        # Create market event with enhanced features
                        await create_enhanced_market_event(enhanced_snapshot)
                        
                        collected_count += 1
                        
                        if enhanced_snapshot.collection_priority > 0.6:
                            high_priority_count += 1
                        
                        # Update running averages
                        volatility_sum += enhanced_snapshot.indicators.volatility
                        volume_sum += enhanced_snapshot.indicators.volume_24h
                        
                        # Update stats
                        ml_state["collection_stats"]["snapshots_collected"] = collected_count
                        ml_state["collection_stats"]["high_priority_collections"] = high_priority_count
                        ml_state["collection_stats"]["average_volatility"] = volatility_sum / collected_count
                        ml_state["collection_stats"]["average_volume"] = volume_sum / collected_count
                        
                        logger.info(f"Collected enhanced snapshot (priority: {enhanced_snapshot.collection_priority:.2f}, "
                                  f"volatility: {enhanced_snapshot.indicators.volatility:.1%})")
                    
                    # Update current indicators regardless of collection
                    ml_state["market_indicators"] = {
                        "current_volatility": enhanced_snapshot.indicators.volatility,
                        "current_volume": enhanced_snapshot.indicators.volume_24h,
                        "current_rsi": enhanced_snapshot.indicators.rsi or 50.0,
                        "funding_rate": enhanced_snapshot.indicators.funding_rate or 0.0,
                        "collection_priority": enhanced_snapshot.collection_priority,
                        "prediction_confidence": enhanced_snapshot.prediction_confidence,
                        "price": enhanced_snapshot.indicators.price,
                        "price_momentum": enhanced_snapshot.indicators.price_momentum or 0.0
                    }
                
                await asyncio.sleep(interval)
                
            except Exception as e:
                logger.error(f"Error in enhanced collection loop: {e}")
                await asyncio.sleep(interval)
        
    except Exception as e:
        logger.error(f"Error in enhanced collection: {e}")
    finally:
        ml_state["collection_active"] = False

async def create_enhanced_market_event(enhanced_snapshot: EnhancedMarketSnapshot):
    """Create market event with enhanced features"""
    try:
        # Use enhanced feature extractor for consistent dimensions
        from enhanced_feature_extractor import EnhancedFeatureExtractor
        
        feature_extractor = EnhancedFeatureExtractor()
        
        # Get recent snapshots for temporal features
        recent_snapshots = ml_state["data_collector"].get_recent_snapshots(20)
        
        # Prepare market indicators dictionary
        market_indicators = {
            'current_volatility': enhanced_snapshot.indicators.volatility,
            'current_volume': enhanced_snapshot.indicators.volume_24h,
            'current_rsi': enhanced_snapshot.indicators.rsi or 50.0,
            'funding_rate': enhanced_snapshot.indicators.funding_rate or 0.0,
            'price_momentum': enhanced_snapshot.indicators.price_momentum or 0.0,
            'collection_priority': enhanced_snapshot.collection_priority,
            'prediction_confidence': enhanced_snapshot.prediction_confidence,
            'price': enhanced_snapshot.indicators.price
        }
        
        # Add Bollinger Bands if available
        if enhanced_snapshot.indicators.bollinger_bands:
            bb = enhanced_snapshot.indicators.bollinger_bands
            market_indicators.update({
                'bb_upper': bb["upper"],
                'bb_lower': bb["lower"]
            })
        
        # Extract consistent enhanced features (42 features)
        enhanced_features_array = feature_extractor.extract_features(
            enhanced_snapshot.orderbook, 
            recent_snapshots,
            market_indicators
        )
        
        # Convert array back to dictionary for compatibility
        feature_names = feature_extractor.feature_names
        enhanced_features = {name: float(enhanced_features_array[i]) for i, name in enumerate(feature_names)}
        
        # Determine manipulation based on enhanced criteria
        manipulation_detected = detect_enhanced_manipulation(enhanced_snapshot, enhanced_features)
        
        # Classify event type with enhanced logic
        event_type = classify_enhanced_event(enhanced_snapshot, enhanced_features, manipulation_detected)
        
        # Calculate price changes (simplified for now)
        price_change_1min = 0.0
        price_change_5min = 0.0
        
        if recent_snapshots:
            recent_price = recent_snapshots[-1].mid_price
            price_change_1min = (enhanced_snapshot.orderbook.mid_price - recent_price) / recent_price
        
        # Create enhanced market event
        event = MarketEvent(
            timestamp=enhanced_snapshot.orderbook.timestamp,
            features=enhanced_features,
            price_change_1min=price_change_1min,
            price_change_5min=price_change_5min,
            manipulation_detected=manipulation_detected,
            event_type=event_type
        )
        
        # Store the event
        ml_state["data_collector"].store_market_event(event)
        ml_state["collection_stats"]["events_created"] += 1
        
        if manipulation_detected:
            ml_state["collection_stats"]["anomalies_detected"] += 1
        
    except Exception as e:
        logger.error(f"Error creating enhanced market event: {e}")
        import traceback
        traceback.print_exc()

def detect_enhanced_manipulation(snapshot: EnhancedMarketSnapshot, features: Dict[str, float]) -> bool:
    """Enhanced manipulation detection using market indicators"""
    
    # Original order book based detection
    orderbook_manipulation = (
        abs(snapshot.orderbook.imbalance) > 0.7 or
        (snapshot.orderbook.spread / snapshot.orderbook.mid_price) * 10000 > 50
    )
    
    # Enhanced detection using market indicators
    volatility_spike = snapshot.indicators.volatility > 0.05  # 5% volatility
    volume_spike = False
    
    # Check for volume spikes (need historical data)
    if hasattr(ml_state["enhanced_collector"], "indicator_calculator"):
        calc = ml_state["enhanced_collector"].indicator_calculator
        if calc.volume_history:
            avg_volume = sum(calc.volume_history) / len(calc.volume_history)
            volume_spike = snapshot.indicators.volume_24h > avg_volume * 2
    
    # RSI extremes
    rsi_extreme = False
    if snapshot.indicators.rsi:
        rsi_extreme = snapshot.indicators.rsi < 20 or snapshot.indicators.rsi > 80
    
    # Funding rate extremes
    funding_extreme = False
    if snapshot.indicators.funding_rate:
        funding_extreme = abs(snapshot.indicators.funding_rate) > 0.005  # 0.5%
    
    # High collection priority indicates unusual market conditions
    priority_high = snapshot.collection_priority > 0.8
    
    # Combine all factors
    return (orderbook_manipulation or 
            (volatility_spike and volume_spike) or
            (rsi_extreme and volatility_spike) or
            (funding_extreme and priority_high))

def classify_enhanced_event(snapshot: EnhancedMarketSnapshot, features: Dict[str, float], 
                          manipulation_detected: bool) -> str:
    """Enhanced event classification using market indicators"""
    
    if not manipulation_detected:
        return 'normal'
    
    # Use price momentum and RSI for better classification
    momentum = snapshot.indicators.price_momentum or 0.0
    rsi = snapshot.indicators.rsi or 50.0
    volatility = snapshot.indicators.volatility
    
    # Pump detection (enhanced)
    if momentum > 0.02 and rsi > 70 and volatility > 0.03:
        return 'pump'
    
    # Dump detection (enhanced)  
    if momentum < -0.02 and rsi < 30 and volatility > 0.03:
        return 'dump'
    
    # Spoofing detection (large orders, low volatility)
    if (features.get('large_bid_count', 0) > 2 or features.get('large_ask_count', 0) > 2) and volatility < 0.01:
        return 'spoofing'
    
    # Wash trading (high volume, low price movement)
    if snapshot.indicators.volume_24h > 1500000000 and abs(momentum) < 0.005:  # $1.5B volume, <0.5% movement
        return 'wash_trading'
    
    # Funding rate manipulation
    if snapshot.indicators.funding_rate and abs(snapshot.indicators.funding_rate) > 0.01:
        return 'funding_manipulation'
    
    return 'manipulation'
async def start_btc_collection(background_tasks: BackgroundTasks, interval: int = 10):
    """Start BTC order book data collection"""
    try:
        if ml_state["collection_active"]:
            return {
                "success": False,
                "error": "数据收集已在运行中"
            }
        
        # Initialize collector
        if not ml_state["btc_collector"]:
            ml_state["btc_collector"] = BTCLiveCollector()
        
        # Start collection in background
        background_tasks.add_task(run_btc_collection, interval)
        
        ml_state["collection_active"] = True
        ml_state["collection_stats"]["start_time"] = datetime.now()
        
        logger.info(f"Started BTC data collection with {interval}s interval")
        
        return {
            "success": True,
            "message": f"开始BTC数据收集 (间隔: {interval}秒)",
            "interval": interval
        }
    
    except Exception as e:
        logger.error(f"Error starting BTC collection: {e}")
        return {
            "success": False,
            "error": str(e)
        }

@router.post("/stop-collection")
async def stop_btc_collection():
    """Stop BTC data collection"""
    try:
        if ml_state["btc_collector"]:
            ml_state["btc_collector"].stop_collection()
        
        ml_state["collection_active"] = False
        
        return {
            "success": True,
            "message": "BTC数据收集已停止"
        }
    
    except Exception as e:
        logger.error(f"Error stopping BTC collection: {e}")
        return {
            "success": False,
            "error": str(e)
        }

async def run_btc_collection(interval: int):
    """Run BTC collection in background"""
    try:
        collector = ml_state["btc_collector"]
        if not collector:
            return
        
        logger.info("Starting BTC collection background task")
        
        # Run collection for 1 hour, then auto-stop
        await asyncio.wait_for(
            collector.start_collection(interval),
            timeout=3600  # 1 hour
        )
        
    except asyncio.TimeoutError:
        logger.info("BTC collection completed (1 hour timeout)")
    except Exception as e:
        logger.error(f"Error in BTC collection: {e}")
    finally:
        ml_state["collection_active"] = False

@router.post("/train-model")
async def train_ml_model(request: MLTrainingRequest):
    """Train or retrain the ML model"""
    try:
        # Initialize components
        if not ml_state["ml_model"]:
            ml_state["ml_model"] = BTCOrderBookMLModel()
        if not ml_state["data_collector"]:
            ml_state["data_collector"] = BTCDataCollector()
        
        # Get training data
        training_events = ml_state["data_collector"].get_training_events(1000)
        
        if len(training_events) < request.min_samples:
            return {
                "success": False,
                "error": f"训练数据不足，需要至少 {request.min_samples} 个样本，当前只有 {len(training_events)} 个"
            }
        
        # Update training status
        ml_state["training_progress"]["training_status"] = "training"
        ml_state["training_progress"]["samples_collected"] = len(training_events)
        
        logger.info(f"Training ML model with {len(training_events)} samples")
        
        # Train model
        metrics = ml_state["ml_model"].train(training_events)
        
        # Update training progress
        ml_state["training_progress"].update({
            "training_status": "completed",
            "last_training": datetime.now().isoformat(),
            "model_accuracy": metrics.get("accuracy", 0.0),
            "samples_collected": len(training_events)
        })
        ml_state["model_trained"] = True
        
        logger.info(f"Model training completed - Accuracy: {metrics.get('accuracy', 0):.3f}")
        
        return {
            "success": True,
            "message": "模型训练完成",
            "metrics": metrics,
            "training_samples": len(training_events)
        }
    
    except Exception as e:
        logger.error(f"Error training ML model: {e}")
        ml_state["training_progress"]["training_status"] = "failed"
        return {
            "success": False,
            "error": str(e)
        }

@router.post("/predict")
async def get_ml_prediction(request: MLPredictionRequest):
    """Get ML prediction for current market state"""
    try:
        # Initialize components
        if not ml_state["ml_model"]:
            ml_state["ml_model"] = BTCOrderBookMLModel()
        if not ml_state["data_collector"]:
            ml_state["data_collector"] = BTCDataCollector()
        
        # Check if model is trained
        if not ml_state["model_trained"]:
            if not ml_state["ml_model"].load_model():
                return {
                    "success": False,
                    "error": "模型未训练，请先训练模型"
                }
        
        # Get recent snapshots
        recent_snapshots = ml_state["data_collector"].get_recent_snapshots(20)
        
        if len(recent_snapshots) < 10:
            return {
                "success": False,
                "error": "历史数据不足，需要至少10个快照"
            }
        
        # Get latest snapshot
        latest_snapshot = recent_snapshots[-1]
        
        # Get current market indicators for enhanced prediction
        market_indicators = ml_state.get("market_indicators", {})
        
        # Make prediction with market indicators
        prediction = ml_state["ml_model"].predict(
            latest_snapshot, 
            recent_snapshots[:-1],
            market_indicators
        )
        
        if "error" in prediction:
            return {
                "success": False,
                "error": prediction["error"]
            }
        
        # Store prediction
        prediction_result = {
            "timestamp": datetime.now().isoformat(),
            "market": request.market,
            "prediction": prediction,
            "snapshot_time": datetime.fromtimestamp(latest_snapshot.timestamp).isoformat(),
            "price": latest_snapshot.mid_price
        }
        
        ml_state["last_prediction"] = prediction_result
        ml_state["live_predictions"].append(prediction_result)
        
        # Keep only last 50 predictions
        if len(ml_state["live_predictions"]) > 50:
            ml_state["live_predictions"] = ml_state["live_predictions"][-50:]
        
        # Update anomaly count
        if prediction.get("is_anomaly"):
            ml_state["collection_stats"]["anomalies_detected"] += 1
        
        response = {
            "success": True,
            "prediction": prediction_result
        }
        
        if not request.include_features:
            # Remove detailed features for lighter response
            if "features" in response["prediction"]["prediction"]:
                del response["prediction"]["prediction"]["features"]
        
        return response
    
    except Exception as e:
        logger.error(f"Error getting ML prediction: {e}")
        return {
            "success": False,
            "error": str(e)
        }

@router.get("/predictions")
async def get_recent_predictions(limit: int = 20):
    """Get recent ML predictions"""
    try:
        predictions = ml_state["live_predictions"][-limit:] if ml_state["live_predictions"] else []
        
        return {
            "success": True,
            "predictions": predictions,
            "total": len(ml_state["live_predictions"])
        }
    
    except Exception as e:
        logger.error(f"Error getting predictions: {e}")
        return {
            "success": False,
            "error": str(e),
            "predictions": []
        }

@router.get("/training-data")
async def get_training_data_summary(limit: int = 100):
    """Get training data summary"""
    try:
        if not ml_state["data_collector"]:
            ml_state["data_collector"] = BTCDataCollector()
        
        # Get training events
        training_events = ml_state["data_collector"].get_training_events(limit)
        
        # Summarize data
        summary = {
            "total_events": len(training_events),
            "event_types": {},
            "manipulation_count": 0,
            "normal_count": 0,
            "recent_events": []
        }
        
        for event in training_events:
            # Count event types
            event_type = event.event_type
            summary["event_types"][event_type] = summary["event_types"].get(event_type, 0) + 1
            
            # Count manipulation vs normal
            if event.manipulation_detected:
                summary["manipulation_count"] += 1
            else:
                summary["normal_count"] += 1
            
            # Add to recent events (last 10)
            if len(summary["recent_events"]) < 10:
                summary["recent_events"].append({
                    "timestamp": datetime.fromtimestamp(event.timestamp).isoformat(),
                    "event_type": event.event_type,
                    "manipulation_detected": event.manipulation_detected,
                    "price_change_1min": event.price_change_1min,
                    "price_change_5min": event.price_change_5min
                })
        
        return {
            "success": True,
            "summary": summary
        }
    
    except Exception as e:
        logger.error(f"Error getting training data: {e}")
        return {
            "success": False,
            "error": str(e)
        }

@router.post("/simulate-data")
async def simulate_training_data(samples: int = 50):
    """Simulate training data for testing (development only)"""
    try:
        if not ml_state["data_collector"]:
            ml_state["data_collector"] = BTCDataCollector()
        
        import random
        import time
        
        logger.info(f"Simulating {samples} training samples")
        
        for i in range(samples):
            # Create simulated order book snapshot
            base_price = 88000 + random.uniform(-2000, 2000)
            spread = random.uniform(0.5, 3.0)
            
            bids = [(base_price - spread/2 - j * random.uniform(0.1, 1.0), 
                    random.uniform(0.1, 5.0)) for j in range(20)]
            asks = [(base_price + spread/2 + j * random.uniform(0.1, 1.0), 
                    random.uniform(0.1, 5.0)) for j in range(20)]
            
            bid_volume = sum(vol for _, vol in bids)
            ask_volume = sum(vol for _, vol in asks)
            imbalance = (bid_volume - ask_volume) / (bid_volume + ask_volume) if (bid_volume + ask_volume) > 0 else 0
            
            snapshot = OrderBookSnapshot(
                timestamp=time.time() - (samples - i) * 60,  # 1 minute intervals
                bids=bids,
                asks=asks,
                mid_price=base_price,
                spread=spread,
                bid_volume=bid_volume,
                ask_volume=ask_volume,
                imbalance=imbalance
            )
            
            # Store snapshot
            ml_state["data_collector"].store_snapshot(snapshot)
            
            # Create market event
            price_change_1min = random.uniform(-0.05, 0.05)  # -5% to +5%
            price_change_5min = random.uniform(-0.1, 0.1)    # -10% to +10%
            
            # Simulate manipulation detection
            manipulation_detected = (abs(price_change_1min) > 0.02 or 
                                   abs(imbalance) > 0.6 or 
                                   spread > 2.0)
            
            if manipulation_detected:
                if price_change_1min > 0.02:
                    event_type = "pump"
                elif price_change_1min < -0.02:
                    event_type = "dump"
                elif abs(imbalance) > 0.6:
                    event_type = "spoofing"
                else:
                    event_type = "manipulation"
            else:
                event_type = "normal"
            
            # Extract features using enhanced feature extractor for consistency
            from enhanced_feature_extractor import EnhancedFeatureExtractor
            
            feature_extractor = EnhancedFeatureExtractor()
            
            # Create simulated market indicators
            market_indicators = {
                'current_volatility': abs(price_change_1min) * 2,  # Simulate volatility
                'current_volume': random.uniform(800000000, 1200000000),  # $800M-$1.2B
                'current_rsi': random.uniform(20, 80),  # RSI 20-80
                'funding_rate': random.uniform(-0.01, 0.01),  # -1% to +1%
                'price_momentum': price_change_1min,
                'collection_priority': random.uniform(0.2, 0.8),
                'prediction_confidence': random.uniform(0.5, 0.9),
                'price': base_price
            }
            
            # Extract consistent 42 features
            features_array = feature_extractor.extract_features(
                snapshot, 
                [],  # No historical snapshots for simulation
                market_indicators
            )
            
            # Convert to dictionary
            feature_names = feature_extractor.feature_names
            features = {name: float(features_array[i]) for i, name in enumerate(feature_names)}
            
            event = MarketEvent(
                timestamp=snapshot.timestamp,
                features=features,
                price_change_1min=price_change_1min,
                price_change_5min=price_change_5min,
                manipulation_detected=manipulation_detected,
                event_type=event_type
            )
            
            ml_state["data_collector"].store_market_event(event)
        
        # Update stats
        ml_state["collection_stats"]["snapshots_collected"] += samples
        ml_state["collection_stats"]["events_created"] += samples
        
        return {
            "success": True,
            "message": f"成功模拟 {samples} 个训练样本",
            "samples_created": samples
        }
    
    except Exception as e:
        logger.error(f"Error simulating training data: {e}")
        return {
            "success": False,
            "error": str(e)
        }

@router.delete("/clear-data")
async def clear_training_data():
    """Clear all training data (development only)"""
    try:
        if ml_state["data_collector"]:
            # Clear database
            import sqlite3
            conn = sqlite3.connect(ml_state["data_collector"].db_path)
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM orderbook_snapshots")
            cursor.execute("DELETE FROM market_events")
            
            conn.commit()
            conn.close()
        
        # Reset state
        ml_state["live_predictions"] = []
        ml_state["last_prediction"] = None
        ml_state["collection_stats"] = {
            "start_time": None,
            "snapshots_collected": 0,
            "events_created": 0,
            "anomalies_detected": 0
        }
        ml_state["training_progress"] = {
            "samples_collected": 0,
            "last_training": None,
            "model_accuracy": 0.0,
            "training_status": "not_started"
        }
        
        return {
            "success": True,
            "message": "训练数据已清除"
        }
    
    except Exception as e:
        logger.error(f"Error clearing training data: {e}")
        return {
            "success": False,
            "error": str(e)
        }

@router.get("/export-predictions")
async def export_predictions():
    """Export predictions as CSV"""
    try:
        import csv
        import io
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            "时间戳", "市场", "预测类型", "置信度", "异常检测", 
            "价格", "概率_正常", "概率_操纵", "概率_拉盘", "概率_砸盘", "概率_欺骗"
        ])
        
        # Write predictions
        for pred in ml_state["live_predictions"]:
            prediction = pred["prediction"]
            probabilities = prediction.get("probabilities", {})
            
            writer.writerow([
                pred["timestamp"],
                pred["market"],
                prediction.get("prediction_label", ""),
                prediction.get("confidence", 0),
                prediction.get("is_anomaly", False),
                pred["price"],
                probabilities.get("normal", 0),
                probabilities.get("manipulation", 0),
                probabilities.get("pump", 0),
                probabilities.get("dump", 0),
                probabilities.get("spoofing", 0)
            ])
        
        output.seek(0)
        content = output.getvalue()
        output.close()
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"ml_predictions_{timestamp}.csv"
        
        return StreamingResponse(
            io.BytesIO(content.encode('utf-8-sig')),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))