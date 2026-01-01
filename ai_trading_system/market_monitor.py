#!/usr/bin/env python3
"""
Real-time Market Monitoring and Entry Signal System
Monitors market conditions and provides entry recommendations
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json
import sqlite3
from dataclasses import dataclass, asdict
from enum import Enum
import numpy as np

from reinforcement_learning_trader import ConservativeRLTrader, MarketState, TradingAction

logger = logging.getLogger(__name__)

class SignalStrength(Enum):
    VERY_WEAK = 1
    WEAK = 2
    MODERATE = 3
    STRONG = 4
    VERY_STRONG = 5

class MarketCondition(Enum):
    BULL_MARKET = "bull"
    BEAR_MARKET = "bear"
    SIDEWAYS = "sideways"
    VOLATILE = "volatile"

@dataclass
class EntrySignal:
    """Market entry signal with detailed analysis"""
    timestamp: datetime
    signal_strength: SignalStrength
    market_condition: MarketCondition
    recommended_action: str
    entry_price: float
    stop_loss: float
    take_profit: float
    position_size_pct: float
    confidence: float
    risk_reward_ratio: float
    reasoning: List[str]
    technical_indicators: Dict
    news_sentiment: float
    market_momentum: float
    volatility_score: float

class MarketMonitor:
    """
    Real-time market monitoring system that:
    1. Continuously monitors market conditions
    2. Integrates with RL trader for recommendations
    3. Provides entry/exit signals
    4. Tracks performance and learns
    """
    
    def __init__(self, rl_trader: ConservativeRLTrader):
        self.rl_trader = rl_trader
        self.monitoring = False
        self.signals_history = []
        self.market_data_buffer = []
        self.buffer_size = 100
        
        # Signal generation parameters
        self.min_signal_interval = 900  # 15 minutes between signals (15 * 60 = 900 seconds)
        self.analysis_interval = 900     # 15 minutes between analysis updates
        self.last_signal_time = None
        self.last_analysis_time = None
        
        # Market condition tracking
        self.current_trend = MarketCondition.SIDEWAYS
        self.trend_strength = 0.0
        self.volatility_window = 24  # Hours
        
        # Performance tracking
        self.signal_performance = []
        self.accuracy_metrics = {
            'total_signals': 0,
            'successful_signals': 0,
            'accuracy_rate': 0.0,
            'avg_return': 0.0
        }
    
    async def start_monitoring(self):
        """Start continuous market monitoring"""
        logger.info("🔍 Starting market monitoring system...")
        self.monitoring = True
        
        # Load previous model if available
        self.rl_trader.load_model()
        
        # Learn from existing user data
        self.rl_trader.learn_from_user_data()
        
        # Start monitoring loop
        while self.monitoring:
            try:
                await self._monitoring_cycle()
                await asyncio.sleep(300)  # Check every 5 minutes, but generate signals every 15 minutes
                
            except Exception as e:
                logger.error(f"Error in monitoring cycle: {e}")
                await asyncio.sleep(300)
    
    async def _monitoring_cycle(self):
        """Single monitoring cycle"""
        current_time = datetime.now()
        
        # Get current market state
        market_state = await self.rl_trader.get_market_state()
        
        # Update market data buffer
        self._update_market_buffer(market_state)
        
        # Analyze market conditions
        market_condition = self._analyze_market_condition()
        
        # ALWAYS log analysis every 15 minutes (regardless of signals)
        if self._should_log_analysis():
            await self._log_market_analysis(market_state, market_condition)
            self.last_analysis_time = current_time
        
        # Check for IMMEDIATE trading signals (can happen anytime)
        signal = await self._generate_entry_signal(market_state, market_condition)
        
        if signal:
            # For STRONG signals, send immediate alert
            if signal.signal_strength.value >= 4:  # STRONG or VERY_STRONG
                await self._send_immediate_trading_alert(signal)
                await self._process_signal(signal)
            
            # For MODERATE signals, only if enough time has passed
            elif signal.signal_strength.value >= 3 and self._should_generate_signal():
                await self._process_signal(signal)
        
        # Update learning from recent performance
        await self._update_learning()
    
    def _update_market_buffer(self, market_state: MarketState):
        """Update market data buffer for trend analysis"""
        self.market_data_buffer.append({
            'timestamp': market_state.timestamp,
            'price': market_state.price,
            'volume': market_state.volume_24h,
            'price_change_1h': market_state.price_change_1h,
            'price_change_24h': market_state.price_change_24h,
            'rsi': market_state.rsi,
            'volatility': market_state.volatility,
            'news_sentiment': market_state.news_sentiment
        })
        
        # Keep buffer size manageable
        if len(self.market_data_buffer) > self.buffer_size:
            self.market_data_buffer.pop(0)
    
    def _analyze_market_condition(self) -> MarketCondition:
        """Analyze current market condition based on recent data"""
        if len(self.market_data_buffer) < 10:
            return MarketCondition.SIDEWAYS
        
        recent_data = self.market_data_buffer[-24:]  # Last 24 data points
        
        # Calculate trend metrics
        prices = [d['price'] for d in recent_data if d['price'] > 0]
        if not prices:
            return MarketCondition.SIDEWAYS
        
        price_changes = [d['price_change_1h'] for d in recent_data]
        volatilities = [d['volatility'] for d in recent_data]
        
        # Trend analysis
        avg_change = np.mean(price_changes)
        volatility_avg = np.mean(volatilities)
        
        # Determine market condition
        if volatility_avg > 0.05:  # High volatility
            return MarketCondition.VOLATILE
        elif avg_change > 1.0:  # Consistent upward movement
            return MarketCondition.BULL_MARKET
        elif avg_change < -1.0:  # Consistent downward movement
            return MarketCondition.BEAR_MARKET
        else:
            return MarketCondition.SIDEWAYS
    
    def _should_generate_signal(self) -> bool:
        """Check if enough time has passed to generate a new signal"""
        if self.last_signal_time is None:
            return True
        
        time_since_last = (datetime.now() - self.last_signal_time).total_seconds()
        return time_since_last >= self.min_signal_interval
    
    def _should_log_analysis(self) -> bool:
        """Check if enough time has passed to log market analysis"""
        if self.last_analysis_time is None:
            return True
        
        time_since_last = (datetime.now() - self.last_analysis_time).total_seconds()
        return time_since_last >= self.analysis_interval
    
    async def _send_immediate_trading_alert(self, signal: EntrySignal):
        """Send immediate trading alert for strong signals"""
        try:
            # Log immediate alert
            logger.warning("🚨🚨🚨 IMMEDIATE TRADING ALERT 🚨🚨🚨")
            logger.warning(f"⚡ {signal.signal_strength.name} SIGNAL: {signal.recommended_action}")
            logger.warning(f"💰 BTC: ${signal.entry_price:.2f}")
            logger.warning(f"📊 Entry: ${signal.entry_price:.2f} | SL: ${signal.stop_loss:.2f} | TP: ${signal.take_profit:.2f}")
            logger.warning(f"📏 Position Size: {signal.position_size_pct:.1%}")
            logger.warning(f"🎯 Confidence: {signal.confidence:.1%} | R:R = {signal.risk_reward_ratio:.1f}")
            logger.warning(f"💡 {signal.reasoning[0] if signal.reasoning else 'Strong market signal detected'}")
            logger.warning("🚨🚨🚨 TAKE ACTION NOW 🚨🚨🚨")
            
            # Store as high-priority alert
            await self._store_trading_alert(signal)
            
        except Exception as e:
            logger.error(f"Error sending immediate alert: {e}")
    
    async def _store_trading_alert(self, signal: EntrySignal):
        """Store high-priority trading alert"""
        try:
            conn = sqlite3.connect("trading_analysis.db")
            cursor = conn.cursor()
            
            # Create alerts table if not exists
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS trading_alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TIMESTAMP NOT NULL,
                    alert_type TEXT NOT NULL,
                    signal_strength TEXT NOT NULL,
                    recommended_action TEXT NOT NULL,
                    entry_price REAL NOT NULL,
                    stop_loss REAL NOT NULL,
                    take_profit REAL NOT NULL,
                    position_size_pct REAL NOT NULL,
                    confidence REAL NOT NULL,
                    risk_reward_ratio REAL NOT NULL,
                    reasoning TEXT NOT NULL,
                    market_condition TEXT NOT NULL,
                    urgency_level INTEGER NOT NULL,
                    acknowledged BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Insert alert
            cursor.execute('''
                INSERT INTO trading_alerts (
                    timestamp, alert_type, signal_strength, recommended_action,
                    entry_price, stop_loss, take_profit, position_size_pct,
                    confidence, risk_reward_ratio, reasoning, market_condition,
                    urgency_level
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                signal.timestamp,
                'IMMEDIATE_TRADE',
                signal.signal_strength.name,
                signal.recommended_action,
                signal.entry_price,
                signal.stop_loss,
                signal.take_profit,
                signal.position_size_pct,
                signal.confidence,
                signal.risk_reward_ratio,
                json.dumps(signal.reasoning, ensure_ascii=False),
                signal.market_condition.value,
                5 if signal.signal_strength.value >= 5 else 4  # Urgency level
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
    async def _log_market_analysis(self, market_state: MarketState, market_condition: MarketCondition):
        """Log current market analysis every 15 minutes"""
        try:
            # Get RL trader recommendation
            trading_action = self.rl_trader.get_trading_recommendation(market_state)
            
            # Calculate technical indicators
            technical_indicators = self._calculate_technical_indicators()
            
            # Create analysis log
            analysis = {
                'timestamp': datetime.now().isoformat(),
                'btc_price': market_state.price,
                'price_change_1h': market_state.price_change_1h,
                'price_change_24h': market_state.price_change_24h,
                'volume_24h': market_state.volume_24h,
                'rsi': market_state.rsi,
                'volatility': market_state.volatility,
                'news_sentiment': market_state.news_sentiment,
                'market_condition': market_condition.value,
                'ai_recommendation': trading_action.action_type.name,
                'ai_confidence': trading_action.confidence,
                'risk_score': trading_action.risk_score,
                'reasoning': trading_action.reasoning,
                'technical_indicators': technical_indicators
            }
            
            # Determine if this is just analysis or also a signal
            signal_strength = "ANALYSIS_ONLY"
            if trading_action.action_type.name != 'HOLD':
                signal = await self._generate_entry_signal(market_state, market_condition)
                if signal:
                    signal_strength = signal.signal_strength.name
            
            # Log to console with different formatting based on signal strength
            if signal_strength in ['STRONG', 'VERY_STRONG']:
                logger.warning("🚨 === 15-MINUTE ANALYSIS + STRONG SIGNAL ===")
            else:
                logger.info("📊 === 15-MINUTE MARKET ANALYSIS ===")
            
            logger.info(f"🪙 BTC Price: ${market_state.price:.2f} ({market_state.price_change_24h:+.2f}% 24h)")
            logger.info(f"📈 Market Condition: {market_condition.value.upper()}")
            logger.info(f"🤖 AI Recommendation: {trading_action.action_type.name} (Confidence: {trading_action.confidence:.1%})")
            
            if signal_strength != "ANALYSIS_ONLY":
                logger.info(f"⚡ Signal Strength: {signal_strength}")
            
            logger.info(f"📊 RSI: {market_state.rsi:.1f} | Volatility: {market_state.volatility:.3f}")
            logger.info(f"📰 News Sentiment: {market_state.news_sentiment:+.2f}")
            logger.info(f"💡 Reasoning: {trading_action.reasoning}")
            
            # Add technical indicators summary
            if technical_indicators:
                sma_status = "Above" if technical_indicators.get('price_vs_sma20', 0) > 0 else "Below"
                logger.info(f"📈 Technical: Price {sma_status} SMA20, Momentum: {technical_indicators.get('momentum_5', 0):+.2f}%")
            
            logger.info("=" * 50)
            
            # Store analysis in database
            await self._store_analysis(analysis)
            
            # Store as regular analysis alert (lower priority)
            await self._store_analysis_alert(analysis, signal_strength)
            
        except Exception as e:
            logger.error(f"Error logging market analysis: {e}")
    
    async def _store_analysis_alert(self, analysis: Dict, signal_strength: str):
        """Store regular analysis as a notification"""
        try:
            conn = sqlite3.connect("trading_analysis.db")
            cursor = conn.cursor()
            
            # Create notifications table if not exists
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS analysis_notifications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TIMESTAMP NOT NULL,
                    notification_type TEXT NOT NULL,
                    btc_price REAL NOT NULL,
                    price_change_24h REAL NOT NULL,
                    market_condition TEXT NOT NULL,
                    ai_recommendation TEXT NOT NULL,
                    ai_confidence REAL NOT NULL,
                    signal_strength TEXT NOT NULL,
                    summary TEXT NOT NULL,
                    read_status BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create summary
            price_trend = "📈" if analysis['price_change_24h'] > 0 else "📉" if analysis['price_change_24h'] < 0 else "➡️"
            summary = f"{price_trend} BTC ${analysis['btc_price']:.0f} ({analysis['price_change_24h']:+.1f}%) | {analysis['market_condition'].upper()} | AI: {analysis['ai_recommendation']} ({analysis['ai_confidence']:.0%})"
            
            # Insert notification
            cursor.execute('''
                INSERT INTO analysis_notifications (
                    timestamp, notification_type, btc_price, price_change_24h,
                    market_condition, ai_recommendation, ai_confidence,
                    signal_strength, summary
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                analysis['timestamp'],
                'REGULAR_ANALYSIS',
                analysis['btc_price'],
                analysis['price_change_24h'],
                analysis['market_condition'],
                analysis['ai_recommendation'],
                analysis['ai_confidence'],
                signal_strength,
                summary
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error storing analysis notification: {e}")
        """Log current market analysis every 15 minutes"""
        try:
            # Get RL trader recommendation
            trading_action = self.rl_trader.get_trading_recommendation(market_state)
            
            # Calculate technical indicators
            technical_indicators = self._calculate_technical_indicators()
            
            # Create analysis log
            analysis = {
                'timestamp': datetime.now().isoformat(),
                'btc_price': market_state.price,
                'price_change_1h': market_state.price_change_1h,
                'price_change_24h': market_state.price_change_24h,
                'volume_24h': market_state.volume_24h,
                'rsi': market_state.rsi,
                'volatility': market_state.volatility,
                'news_sentiment': market_state.news_sentiment,
                'market_condition': market_condition.value,
                'ai_recommendation': trading_action.action_type.name,
                'ai_confidence': trading_action.confidence,
                'risk_score': trading_action.risk_score,
                'reasoning': trading_action.reasoning,
                'technical_indicators': technical_indicators
            }
            
            # Log to console
            logger.info("📊 === 15-MINUTE MARKET ANALYSIS ===")
            logger.info(f"🪙 BTC Price: ${market_state.price:.2f} ({market_state.price_change_24h:+.2f}% 24h)")
            logger.info(f"📈 Market Condition: {market_condition.value.upper()}")
            logger.info(f"🤖 AI Recommendation: {trading_action.action_type.name} (Confidence: {trading_action.confidence:.1%})")
            logger.info(f"📊 RSI: {market_state.rsi:.1f} | Volatility: {market_state.volatility:.3f}")
            logger.info(f"📰 News Sentiment: {market_state.news_sentiment:+.2f}")
            logger.info(f"💡 Reasoning: {trading_action.reasoning}")
            logger.info("=" * 50)
            
            # Store analysis in database
            await self._store_analysis(analysis)
            
        except Exception as e:
            logger.error(f"Error logging market analysis: {e}")
    
    async def _store_analysis(self, analysis: Dict):
        """Store market analysis in database"""
        try:
            conn = sqlite3.connect("trading_analysis.db")
            cursor = conn.cursor()
            
            # Create analysis table if not exists
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS market_analysis (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TIMESTAMP NOT NULL,
                    btc_price REAL NOT NULL,
                    price_change_1h REAL NOT NULL,
                    price_change_24h REAL NOT NULL,
                    volume_24h REAL NOT NULL,
                    rsi REAL NOT NULL,
                    volatility REAL NOT NULL,
                    news_sentiment REAL NOT NULL,
                    market_condition TEXT NOT NULL,
                    ai_recommendation TEXT NOT NULL,
                    ai_confidence REAL NOT NULL,
                    risk_score REAL NOT NULL,
                    reasoning TEXT NOT NULL,
                    technical_indicators TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Insert analysis
            cursor.execute('''
                INSERT INTO market_analysis (
                    timestamp, btc_price, price_change_1h, price_change_24h,
                    volume_24h, rsi, volatility, news_sentiment,
                    market_condition, ai_recommendation, ai_confidence,
                    risk_score, reasoning, technical_indicators
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                analysis['timestamp'],
                analysis['btc_price'],
                analysis['price_change_1h'],
                analysis['price_change_24h'],
                analysis['volume_24h'],
                analysis['rsi'],
                analysis['volatility'],
                analysis['news_sentiment'],
                analysis['market_condition'],
                analysis['ai_recommendation'],
                analysis['ai_confidence'],
                analysis['risk_score'],
                analysis['reasoning'],
                json.dumps(analysis['technical_indicators'], ensure_ascii=False)
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error storing analysis: {e}")
    
    async def _generate_entry_signal(self, market_state: MarketState, market_condition: MarketCondition) -> Optional[EntrySignal]:
        """Generate entry signal using RL trader and market analysis"""
        
        # Get RL trader recommendation
        trading_action = self.rl_trader.get_trading_recommendation(market_state)
        
        # Skip if recommendation is to hold
        if trading_action.action_type.name == 'HOLD':
            return None
        
        # Calculate technical indicators
        technical_indicators = self._calculate_technical_indicators()
        
        # Determine signal strength
        signal_strength = self._calculate_signal_strength(
            trading_action, market_state, technical_indicators
        )
        
        # Calculate position sizing
        position_size = self._calculate_conservative_position_size(
            trading_action, signal_strength, market_state
        )
        
        # Generate reasoning
        reasoning = self._generate_signal_reasoning(
            trading_action, market_state, market_condition, technical_indicators
        )
        
        # Calculate risk-reward ratio
        risk_reward = self._calculate_risk_reward_ratio(
            market_state.price, trading_action.stop_loss, trading_action.take_profit
        )
        
        return EntrySignal(
            timestamp=datetime.now(),
            signal_strength=signal_strength,
            market_condition=market_condition,
            recommended_action=trading_action.action_type.name,
            entry_price=market_state.price,
            stop_loss=trading_action.stop_loss,
            take_profit=trading_action.take_profit,
            position_size_pct=position_size,
            confidence=trading_action.confidence,
            risk_reward_ratio=risk_reward,
            reasoning=reasoning,
            technical_indicators=technical_indicators,
            news_sentiment=market_state.news_sentiment,
            market_momentum=market_state.price_change_24h,
            volatility_score=market_state.volatility
        )
    
    def _calculate_technical_indicators(self) -> Dict:
        """Calculate technical indicators from market buffer"""
        if len(self.market_data_buffer) < 20:
            return {}
        
        recent_data = self.market_data_buffer[-20:]
        prices = [d['price'] for d in recent_data if d['price'] > 0]
        
        if not prices:
            return {}
        
        # Simple moving averages
        sma_5 = np.mean(prices[-5:]) if len(prices) >= 5 else prices[-1]
        sma_10 = np.mean(prices[-10:]) if len(prices) >= 10 else prices[-1]
        sma_20 = np.mean(prices[-20:]) if len(prices) >= 20 else prices[-1]
        
        current_price = prices[-1]
        
        # Price position relative to SMAs
        price_vs_sma5 = (current_price - sma_5) / sma_5 * 100
        price_vs_sma10 = (current_price - sma_10) / sma_10 * 100
        price_vs_sma20 = (current_price - sma_20) / sma_20 * 100
        
        # Momentum indicators
        momentum_5 = (prices[-1] - prices[-5]) / prices[-5] * 100 if len(prices) >= 5 else 0
        momentum_10 = (prices[-1] - prices[-10]) / prices[-10] * 100 if len(prices) >= 10 else 0
        
        return {
            'sma_5': sma_5,
            'sma_10': sma_10,
            'sma_20': sma_20,
            'price_vs_sma5': price_vs_sma5,
            'price_vs_sma10': price_vs_sma10,
            'price_vs_sma20': price_vs_sma20,
            'momentum_5': momentum_5,
            'momentum_10': momentum_10,
            'current_price': current_price
        }
    
    def _calculate_signal_strength(self, trading_action: TradingAction, market_state: MarketState, technical_indicators: Dict) -> SignalStrength:
        """Calculate signal strength based on multiple factors"""
        score = 0
        
        # Base score from RL trader confidence
        score += trading_action.confidence * 2  # 0-2 points
        
        # Technical alignment
        if technical_indicators:
            # Price above moving averages (bullish)
            if technical_indicators.get('price_vs_sma5', 0) > 0:
                score += 0.5
            if technical_indicators.get('price_vs_sma10', 0) > 0:
                score += 0.5
            if technical_indicators.get('price_vs_sma20', 0) > 0:
                score += 0.5
            
            # Momentum alignment
            if technical_indicators.get('momentum_5', 0) > 1:
                score += 0.5
        
        # News sentiment alignment
        if market_state.news_sentiment > 0.2:
            score += 0.5
        elif market_state.news_sentiment < -0.2:
            score -= 0.5
        
        # RSI conditions
        if 30 < market_state.rsi < 70:  # Not overbought/oversold
            score += 0.5
        
        # Volume confirmation
        if market_state.volume_24h > 1000000:  # Good volume
            score += 0.5
        
        # Risk-reward ratio
        if trading_action.expected_return > trading_action.risk_score:
            score += 0.5
        
        # Convert score to signal strength
        if score >= 4.5:
            return SignalStrength.VERY_STRONG
        elif score >= 3.5:
            return SignalStrength.STRONG
        elif score >= 2.5:
            return SignalStrength.MODERATE
        elif score >= 1.5:
            return SignalStrength.WEAK
        else:
            return SignalStrength.VERY_WEAK
    
    def _calculate_conservative_position_size(self, trading_action: TradingAction, signal_strength: SignalStrength, market_state: MarketState) -> float:
        """Calculate conservative position size"""
        base_size = {
            SignalStrength.VERY_WEAK: 0.02,    # 2%
            SignalStrength.WEAK: 0.03,         # 3%
            SignalStrength.MODERATE: 0.05,     # 5%
            SignalStrength.STRONG: 0.08,       # 8%
            SignalStrength.VERY_STRONG: 0.10   # 10% (conservative max)
        }
        
        size = base_size.get(signal_strength, 0.05)
        
        # Reduce size in high volatility
        if market_state.volatility > 0.05:
            size *= 0.7
        
        # Reduce size if portfolio is already at risk
        current_risk = self.rl_trader.portfolio.max_drawdown
        if current_risk > 0.05:  # 5% drawdown
            size *= 0.5
        
        return min(size, 0.10)  # Never exceed 10%
    
    def _generate_signal_reasoning(self, trading_action: TradingAction, market_state: MarketState, market_condition: MarketCondition, technical_indicators: Dict) -> List[str]:
        """Generate human-readable reasoning for the signal"""
        reasoning = []
        
        # Market condition
        condition_descriptions = {
            MarketCondition.BULL_MARKET: "市场处于上升趋势",
            MarketCondition.BEAR_MARKET: "市场处于下降趋势",
            MarketCondition.SIDEWAYS: "市场横盘整理",
            MarketCondition.VOLATILE: "市场波动较大"
        }
        reasoning.append(condition_descriptions.get(market_condition, "市场状态不明"))
        
        # Technical analysis
        if technical_indicators:
            if technical_indicators.get('price_vs_sma5', 0) > 2:
                reasoning.append("价格强势突破短期均线")
            elif technical_indicators.get('momentum_5', 0) > 3:
                reasoning.append("短期动量强劲")
        
        # News sentiment
        if market_state.news_sentiment > 0.3:
            reasoning.append("新闻情绪非常积极")
        elif market_state.news_sentiment > 0.1:
            reasoning.append("新闻情绪偏向积极")
        elif market_state.news_sentiment < -0.3:
            reasoning.append("新闻情绪非常消极")
        elif market_state.news_sentiment < -0.1:
            reasoning.append("新闻情绪偏向消极")
        
        # RSI analysis
        if market_state.rsi < 30:
            reasoning.append("RSI显示超卖，可能反弹")
        elif market_state.rsi > 70:
            reasoning.append("RSI显示超买，需要谨慎")
        elif 40 < market_state.rsi < 60:
            reasoning.append("RSI处于中性区域")
        
        # Volume analysis
        if market_state.volume_24h > 2000000:
            reasoning.append("成交量充足，支持价格走势")
        elif market_state.volume_24h < 500000:
            reasoning.append("成交量偏低，需要确认")
        
        # Risk management
        reasoning.append(f"AI信心度: {trading_action.confidence:.1%}")
        reasoning.append(f"风险评分: {trading_action.risk_score:.1f}/1.0")
        
        return reasoning
    
    def _calculate_risk_reward_ratio(self, entry_price: float, stop_loss: float, take_profit: float) -> float:
        """Calculate risk-reward ratio"""
        if stop_loss == 0 or take_profit == 0:
            return 0.0
        
        risk = abs(entry_price - stop_loss)
        reward = abs(take_profit - entry_price)
        
        if risk == 0:
            return 0.0
        
        return reward / risk
    
    async def _process_signal(self, signal: EntrySignal):
        """Process and store the generated signal"""
        self.last_signal_time = signal.timestamp
        self.signals_history.append(signal)
        
        # Store in database
        await self._store_signal(signal)
        
        # Log the signal
        logger.info(f"🚨 New {signal.signal_strength.name} signal: {signal.recommended_action}")
        logger.info(f"   Entry: ${signal.entry_price:.2f} | SL: ${signal.stop_loss:.2f} | TP: ${signal.take_profit:.2f}")
        logger.info(f"   Position Size: {signal.position_size_pct:.1%} | R:R = {signal.risk_reward_ratio:.1f}")
        logger.info(f"   Reasoning: {' | '.join(signal.reasoning[:3])}")
        
        # Keep history manageable
        if len(self.signals_history) > 100:
            self.signals_history.pop(0)
    
    async def _store_signal(self, signal: EntrySignal):
        """Store signal in database"""
        try:
            conn = sqlite3.connect("trading_analysis.db")
            cursor = conn.cursor()
            
            # Create signals table if not exists
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS trading_signals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TIMESTAMP NOT NULL,
                    signal_strength TEXT NOT NULL,
                    market_condition TEXT NOT NULL,
                    recommended_action TEXT NOT NULL,
                    entry_price REAL NOT NULL,
                    stop_loss REAL NOT NULL,
                    take_profit REAL NOT NULL,
                    position_size_pct REAL NOT NULL,
                    confidence REAL NOT NULL,
                    risk_reward_ratio REAL NOT NULL,
                    reasoning TEXT NOT NULL,
                    technical_indicators TEXT NOT NULL,
                    news_sentiment REAL NOT NULL,
                    market_momentum REAL NOT NULL,
                    volatility_score REAL NOT NULL,
                    executed BOOLEAN DEFAULT FALSE,
                    result_pnl REAL DEFAULT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Insert signal
            cursor.execute('''
                INSERT INTO trading_signals (
                    timestamp, signal_strength, market_condition, recommended_action,
                    entry_price, stop_loss, take_profit, position_size_pct,
                    confidence, risk_reward_ratio, reasoning, technical_indicators,
                    news_sentiment, market_momentum, volatility_score
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                signal.timestamp,
                signal.signal_strength.name,
                signal.market_condition.value,
                signal.recommended_action,
                signal.entry_price,
                signal.stop_loss,
                signal.take_profit,
                signal.position_size_pct,
                signal.confidence,
                signal.risk_reward_ratio,
                json.dumps(signal.reasoning, ensure_ascii=False),
                json.dumps(signal.technical_indicators, ensure_ascii=False),
                signal.news_sentiment,
                signal.market_momentum,
                signal.volatility_score
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error storing signal: {e}")
    
    async def _update_learning(self):
        """Update RL trader learning based on recent performance"""
        # This would be called periodically to update the model
        # based on how well recent signals performed
        
        # Check if we have enough recent signals to evaluate
        recent_signals = [s for s in self.signals_history if 
                         (datetime.now() - s.timestamp).total_seconds() < 86400]  # Last 24 hours
        
        if len(recent_signals) >= 5:
            # Evaluate performance and update learning
            await self._evaluate_signal_performance(recent_signals)
    
    async def _evaluate_signal_performance(self, signals: List[EntrySignal]):
        """Evaluate how well recent signals performed"""
        # This would check actual market outcomes vs predictions
        # and update the RL model accordingly
        
        performance_data = []
        
        for signal in signals:
            # Calculate how the signal would have performed
            # (This is simplified - in practice you'd track actual executions)
            
            time_elapsed = (datetime.now() - signal.timestamp).total_seconds() / 3600  # Hours
            
            if time_elapsed >= 1:  # At least 1 hour has passed
                # Get current price and calculate theoretical performance
                current_market = await self.rl_trader.get_market_state()
                
                if current_market.price > 0:
                    price_change = (current_market.price - signal.entry_price) / signal.entry_price
                    
                    # Determine if signal was successful
                    if signal.recommended_action in ['BUY_SMALL', 'BUY_MEDIUM', 'BUY_LARGE']:
                        success = price_change > 0.01  # 1% profit threshold
                    else:
                        success = price_change < -0.01  # Successful short
                    
                    performance_data.append({
                        'signal_strength': signal.signal_strength.value,
                        'success': success,
                        'return': price_change,
                        'confidence': signal.confidence
                    })
        
        # Update accuracy metrics
        if performance_data:
            successful = sum(1 for p in performance_data if p['success'])
            total = len(performance_data)
            
            self.accuracy_metrics['total_signals'] += total
            self.accuracy_metrics['successful_signals'] += successful
            self.accuracy_metrics['accuracy_rate'] = (
                self.accuracy_metrics['successful_signals'] / 
                max(self.accuracy_metrics['total_signals'], 1)
            )
            
            avg_return = np.mean([p['return'] for p in performance_data])
            self.accuracy_metrics['avg_return'] = avg_return
            
            logger.info(f"📊 Signal Performance: {successful}/{total} successful ({self.accuracy_metrics['accuracy_rate']:.1%})")
    
    def get_current_signals(self, limit: int = 10) -> List[Dict]:
        """Get recent signals for display"""
        recent_signals = sorted(self.signals_history, key=lambda x: x.timestamp, reverse=True)[:limit]
        
        return [asdict(signal) for signal in recent_signals]
    
    def get_performance_summary(self) -> Dict:
        """Get performance summary"""
        return {
            'monitoring_active': self.monitoring,
            'total_signals_generated': len(self.signals_history),
            'accuracy_metrics': self.accuracy_metrics,
            'current_market_condition': self.current_trend.value if self.current_trend else 'unknown',
            'rl_trader_progress': self.rl_trader.get_progress_report(),
            'last_signal_time': self.last_signal_time.isoformat() if self.last_signal_time else None,
            'signals_today': len([s for s in self.signals_history if 
                                (datetime.now() - s.timestamp).days == 0])
        }
    
    def stop_monitoring(self):
        """Stop market monitoring"""
        logger.info("⏹️ Stopping market monitoring...")
        self.monitoring = False
        
        # Save the model
        self.rl_trader.save_model()
        
        logger.info("✅ Market monitoring stopped and model saved")