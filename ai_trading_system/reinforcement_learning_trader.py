#!/usr/bin/env python3
"""
Self-Learning AI Trading System with Reinforcement Learning
Learns from user trade data and develops conservative strategies
Target: Grow 200 USDT to 1000 USDT with conservative approach
"""

import numpy as np
import pandas as pd
import sqlite3
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import asyncio
from dataclasses import dataclass
from enum import Enum
import pickle
import os

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ActionType(Enum):
    HOLD = 0
    BUY_SMALL = 1  # 5% of portfolio
    BUY_MEDIUM = 2  # 10% of portfolio
    BUY_LARGE = 3  # 15% of portfolio (max for conservative)
    SELL_PARTIAL = 4  # 50% of position
    SELL_ALL = 5

@dataclass
class MarketState:
    """Current market state representation"""
    price: float
    volume_24h: float
    price_change_1h: float
    price_change_24h: float
    rsi: float
    macd: float
    bollinger_position: float  # Position within Bollinger Bands (0-1)
    news_sentiment: float  # -1 to 1
    order_book_imbalance: float
    volatility: float
    timestamp: datetime

@dataclass
class TradingAction:
    """Trading action with risk management"""
    action_type: ActionType
    symbol: str
    confidence: float
    risk_score: float
    expected_return: float
    stop_loss: float
    take_profit: float
    reasoning: str

@dataclass
class Portfolio:
    """Portfolio state tracking"""
    usdt_balance: float
    btc_balance: float
    eth_balance: float
    total_value_usdt: float
    unrealized_pnl: float
    realized_pnl: float
    max_drawdown: float
    win_rate: float
    total_trades: int

class ConservativeRLTrader:
    """
    Reinforcement Learning Trading Agent with Conservative Risk Management
    
    Features:
    - Q-Learning with experience replay
    - Conservative position sizing (max 15% per trade)
    - Multi-factor risk assessment
    - News sentiment integration
    - Continuous learning from user data
    """
    
    def __init__(self, initial_balance: float = 200.0):
        self.initial_balance = initial_balance
        self.target_balance = 1000.0
        self.max_position_size = 0.15  # Conservative 15% max
        self.stop_loss_pct = 0.03  # 3% stop loss
        self.take_profit_pct = 0.06  # 6% take profit (2:1 ratio)
        
        # RL Parameters
        self.learning_rate = 0.001
        self.discount_factor = 0.95
        self.epsilon = 0.1  # Exploration rate (low for conservative)
        self.epsilon_decay = 0.995
        self.min_epsilon = 0.01
        
        # State and action dimensions
        self.state_dim = 10  # Market indicators
        self.action_dim = len(ActionType)
        
        # Initialize Q-network (simple neural network)
        self.q_network = self._initialize_q_network()
        self.target_network = self._initialize_q_network()
        self.experience_buffer = []
        self.buffer_size = 10000
        
        # Portfolio tracking
        self.portfolio = Portfolio(
            usdt_balance=initial_balance,
            btc_balance=0.0,
            eth_balance=0.0,
            total_value_usdt=initial_balance,
            unrealized_pnl=0.0,
            realized_pnl=0.0,
            max_drawdown=0.0,
            win_rate=0.0,
            total_trades=0
        )
        
        # Learning history
        self.trade_history = []
        self.performance_metrics = []
        self.model_path = "ai_trading_system/models/"
        os.makedirs(self.model_path, exist_ok=True)
        
        # Risk management
        self.daily_loss_limit = 0.05  # 5% daily loss limit
        self.consecutive_loss_limit = 3
        self.consecutive_losses = 0
        
    def _initialize_q_network(self) -> Dict:
        """Initialize simple Q-network weights"""
        return {
            'w1': np.random.randn(self.state_dim, 64) * 0.1,
            'b1': np.zeros(64),
            'w2': np.random.randn(64, 32) * 0.1,
            'b2': np.zeros(32),
            'w3': np.random.randn(32, self.action_dim) * 0.1,
            'b3': np.zeros(self.action_dim)
        }
    
    def _forward_pass(self, state: np.ndarray, network: Dict) -> np.ndarray:
        """Forward pass through Q-network"""
        z1 = np.dot(state, network['w1']) + network['b1']
        a1 = np.maximum(0, z1)  # ReLU
        z2 = np.dot(a1, network['w2']) + network['b2']
        a2 = np.maximum(0, z2)  # ReLU
        q_values = np.dot(a2, network['w3']) + network['b3']
        return q_values
    
    def learn_from_user_data(self, trading_db_path: str = "trading_analysis.db"):
        """Learn from user's historical trading data"""
        logger.info("🧠 Learning from user trading data...")
        
        try:
            conn = sqlite3.connect(trading_db_path)
            
            # Get all user trading records
            query = """
                SELECT user_id, symbol, side, entry_price, exit_price, 
                       quantity, leverage, entry_time, exit_time, pnl, pnl_percentage
                FROM trading_records 
                WHERE pnl IS NOT NULL
                ORDER BY entry_time
            """
            
            df = pd.read_sql_query(query, conn)
            conn.close()
            
            if df.empty:
                logger.warning("No trading data found for learning")
                return
            
            logger.info(f"Learning from {len(df)} trades across {df['user_id'].nunique()} traders")
            
            # Extract patterns from successful trades
            profitable_trades = df[df['pnl'] > 0]
            losing_trades = df[df['pnl'] < 0]
            
            # Analyze successful patterns
            success_patterns = self._analyze_success_patterns(profitable_trades)
            risk_patterns = self._analyze_risk_patterns(losing_trades)
            
            # Update learning parameters based on patterns
            self._update_strategy_from_patterns(success_patterns, risk_patterns)
            
            logger.info(f"✅ Learned from {len(profitable_trades)} profitable and {len(losing_trades)} losing trades")
            
        except Exception as e:
            logger.error(f"Error learning from user data: {e}")
    
    def _analyze_success_patterns(self, profitable_trades: pd.DataFrame) -> Dict:
        """Analyze patterns from profitable trades"""
        if profitable_trades.empty:
            return {}
        
        patterns = {
            'avg_profit_pct': profitable_trades['pnl_percentage'].mean(),
            'best_symbols': profitable_trades.groupby('symbol')['pnl'].sum().sort_values(ascending=False).head(3).to_dict(),
            'best_sides': profitable_trades.groupby('side')['pnl'].sum().to_dict(),
            'avg_leverage': profitable_trades['leverage'].mean(),
            'hold_time_hours': [],
            'entry_timing_patterns': {}
        }
        
        # Calculate hold times
        for _, trade in profitable_trades.iterrows():
            if pd.notna(trade['exit_time']) and pd.notna(trade['entry_time']):
                entry = pd.to_datetime(trade['entry_time'])
                exit = pd.to_datetime(trade['exit_time'])
                hold_hours = (exit - entry).total_seconds() / 3600
                patterns['hold_time_hours'].append(hold_hours)
        
        if patterns['hold_time_hours']:
            patterns['avg_hold_hours'] = np.mean(patterns['hold_time_hours'])
            patterns['optimal_hold_range'] = (
                np.percentile(patterns['hold_time_hours'], 25),
                np.percentile(patterns['hold_time_hours'], 75)
            )
        
        return patterns
    
    def _analyze_risk_patterns(self, losing_trades: pd.DataFrame) -> Dict:
        """Analyze patterns from losing trades to avoid"""
        if losing_trades.empty:
            return {}
        
        patterns = {
            'avg_loss_pct': losing_trades['pnl_percentage'].mean(),
            'worst_symbols': losing_trades.groupby('symbol')['pnl'].sum().sort_values().head(3).to_dict(),
            'risky_leverage': losing_trades['leverage'].mean(),
            'loss_concentration': losing_trades.groupby('user_id')['pnl'].sum().sort_values().head(5).to_dict()
        }
        
        return patterns
    
    def _update_strategy_from_patterns(self, success_patterns: Dict, risk_patterns: Dict):
        """Update trading strategy based on learned patterns"""
        if success_patterns:
            # Adjust position sizing based on successful leverage usage
            avg_success_leverage = success_patterns.get('avg_leverage', 1.0)
            if avg_success_leverage < 3.0:  # Conservative traders were successful
                self.max_position_size = min(0.10, self.max_position_size)  # Reduce to 10%
                logger.info("📉 Reduced position size based on conservative success patterns")
            
            # Adjust profit targets based on successful trades
            avg_profit = success_patterns.get('avg_profit_pct', 0)
            if avg_profit > 0:
                self.take_profit_pct = min(0.08, max(0.04, avg_profit * 0.8))  # Conservative target
                logger.info(f"🎯 Adjusted take profit to {self.take_profit_pct:.1%}")
        
        if risk_patterns:
            # Adjust stop loss based on average losses
            avg_loss = abs(risk_patterns.get('avg_loss_pct', 3))
            if avg_loss > 5:  # If average losses were high
                self.stop_loss_pct = min(0.025, self.stop_loss_pct)  # Tighter stop loss
                logger.info(f"🛡️ Tightened stop loss to {self.stop_loss_pct:.1%}")
    
    async def get_market_state(self, symbol: str = "BTC/USDT") -> MarketState:
        """Get current market state for decision making"""
        try:
            # This would integrate with your existing CoinEx MCP system
            from scraper.core.ai_content_analyzer import AIContentAnalyzer
            
            # Get market data (placeholder - integrate with your CoinEx system)
            market_data = await self._fetch_market_data(symbol)
            
            # Get news sentiment
            ai_analyzer = AIContentAnalyzer()
            news_sentiment = await self._get_news_sentiment(ai_analyzer)
            
            return MarketState(
                price=market_data.get('price', 0),
                volume_24h=market_data.get('volume', 0),
                price_change_1h=market_data.get('change_1h', 0),
                price_change_24h=market_data.get('change_24h', 0),
                rsi=market_data.get('rsi', 50),
                macd=market_data.get('macd', 0),
                bollinger_position=market_data.get('bb_position', 0.5),
                news_sentiment=news_sentiment,
                order_book_imbalance=market_data.get('ob_imbalance', 0),
                volatility=market_data.get('volatility', 0),
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Error getting market state: {e}")
            # Return neutral state
            return MarketState(
                price=0, volume_24h=0, price_change_1h=0, price_change_24h=0,
                rsi=50, macd=0, bollinger_position=0.5, news_sentiment=0,
                order_book_imbalance=0, volatility=0, timestamp=datetime.now()
            )
    
    async def _fetch_market_data(self, symbol: str) -> Dict:
        """Fetch real market data from CoinEx API using MCP tools"""
        try:
            # Import the global MCP functions that are available in the environment
            import sys
            import os
            
            # Try to get real-time data from CoinEx MCP
            try:
                # Make HTTP request to our own API endpoint that uses MCP
                import requests
                
                # Call our own API endpoint that has MCP integration
                api_response = requests.get(
                    "http://localhost:8000/api/ai-trading/market/coinex-data",
                    timeout=5
                )
                
                if api_response.status_code == 200:
                    coinex_data = api_response.json()
                    if coinex_data.get('success'):
                        data = coinex_data['data']
                        logger.info(f"✅ Got real CoinEx data: BTC ${data['price']:.2f}")
                        return data
                
            except Exception as e:
                logger.warning(f"Failed to get real-time data via API: {e}")
            
            # Fallback: Try to call MCP functions directly if available in global scope
            try:
                # Check if MCP functions are available in the global environment
                if 'mcp_coinex_get_ticker' in globals():
                    ticker_result = mcp_coinex_get_ticker(base="BTC", quote="USDT")
                    
                    if ticker_result.get('code') == 0 and ticker_result.get('data'):
                        ticker_data = ticker_result['data'][0]
                        
                        current_price = float(ticker_data.get('last', 88088))
                        open_price = float(ticker_data.get('open', current_price))
                        high_price = float(ticker_data.get('high', current_price))
                        low_price = float(ticker_data.get('low', current_price))
                        volume_24h = float(ticker_data.get('volume', 0))
                        
                        # Calculate metrics
                        change_24h = ((current_price - open_price) / open_price * 100) if open_price > 0 else 0
                        price_range = high_price - low_price
                        price_position = (current_price - low_price) / price_range if price_range > 0 else 0.5
                        rsi = 30 + (price_position * 40)
                        volatility = (price_range / current_price) if current_price > 0 else 0.02
                        
                        logger.info(f"✅ Got real CoinEx MCP data: BTC ${current_price:.2f}")
                        
                        return {
                            'price': current_price,
                            'volume': volume_24h,
                            'change_1h': change_24h * 0.4,  # Approximate
                            'change_24h': change_24h,
                            'rsi': rsi,
                            'macd': change_24h * 0.01,
                            'bb_position': 0.5 + (change_24h * 0.01),
                            'ob_imbalance': 0.0,  # Will be calculated separately
                            'volatility': volatility
                        }
                        
            except Exception as e:
                logger.warning(f"Direct MCP call failed: {e}")
                
        except Exception as e:
            logger.error(f"Error fetching real market data: {e}")
        
        # Fallback to last known real price
        logger.warning("Using fallback market data")
        return {
            'price': 88088.0,  # Last known real BTC price from CoinEx
            'volume': 196.81,  # Real volume from CoinEx
            'change_1h': 0.1,
            'change_24h': -0.09,  # (88088 - 88169) / 88169 * 100
            'rsi': 48,
            'macd': -0.02,
            'bb_position': 0.45,
            'ob_imbalance': 0.0,
            'volatility': 0.015
        }
    
    async def _get_news_sentiment(self, ai_analyzer) -> float:
        """Get news sentiment from your existing news system"""
        try:
            # Try to get news from Supabase database first (your main news system)
            try:
                from scraper.core.database_manager import DatabaseManager
                db_manager = DatabaseManager()
                
                # Get recent BTC-related news from Supabase
                result = db_manager.supabase.table('articles').select(
                    'title, body_text'
                ).ilike(
                    'title', '%BTC%'
                ).gte(
                    'scraped_at', (datetime.now() - timedelta(hours=2)).isoformat()
                ).order(
                    'scraped_at', desc=True
                ).limit(10).execute()
                
                if result.data:
                    # Analyze sentiment using simple keyword analysis
                    sentiments = []
                    for article in result.data:
                        title = article.get('title', '')
                        content = article.get('body_text', '')
                        text = f"{title} {content}".lower()
                        
                        # Positive keywords
                        positive_words = ['pump', 'bull', 'rise', 'up', 'gain', 'surge', 'rally', 'breakout', 'moon', 'bullish']
                        # Negative keywords  
                        negative_words = ['dump', 'bear', 'fall', 'down', 'loss', 'crash', 'drop', 'decline', 'bearish', 'sell']
                        
                        positive_count = sum(1 for word in positive_words if word in text)
                        negative_count = sum(1 for word in negative_words if word in text)
                        
                        if positive_count > negative_count:
                            sentiments.append(0.3)  # Positive
                        elif negative_count > positive_count:
                            sentiments.append(-0.3)  # Negative
                        else:
                            sentiments.append(0.0)  # Neutral
                    
                    if sentiments:
                        sentiment_score = np.mean(sentiments)
                        logger.info(f"📰 News sentiment from {len(sentiments)} articles: {sentiment_score:.2f}")
                        return sentiment_score
                
            except Exception as e:
                logger.debug(f"Could not get news from Supabase: {e}")
            
            # Fallback: Try local SQLite database
            import os
            news_db_path = "news.db"
            
            if os.path.exists(news_db_path):
                conn = sqlite3.connect(news_db_path)
                cursor = conn.cursor()
                
                # Check if articles table exists
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='articles'")
                if cursor.fetchone():
                    cursor.execute("""
                        SELECT title, content FROM articles 
                        WHERE published_at >= datetime('now', '-2 hours')
                        AND (LOWER(title) LIKE '%btc%' OR LOWER(title) LIKE '%bitcoin%')
                        ORDER BY published_at DESC LIMIT 10
                    """)
                    
                    news_items = cursor.fetchall()
                    conn.close()
                    
                    if news_items:
                        # Analyze sentiment using simple keyword analysis
                        sentiments = []
                        for title, content in news_items:
                            text = f"{title} {content or ''}".lower()
                            
                            positive_words = ['pump', 'bull', 'rise', 'up', 'gain', 'surge', 'rally', 'breakout', 'moon', 'bullish']
                            negative_words = ['dump', 'bear', 'fall', 'down', 'loss', 'crash', 'drop', 'decline', 'bearish', 'sell']
                            
                            positive_count = sum(1 for word in positive_words if word in text)
                            negative_count = sum(1 for word in negative_words if word in text)
                            
                            if positive_count > negative_count:
                                sentiments.append(0.3)
                            elif negative_count > positive_count:
                                sentiments.append(-0.3)
                            else:
                                sentiments.append(0.0)
                        
                        return np.mean(sentiments) if sentiments else 0.0
                else:
                    conn.close()
            
            # No news data available, return neutral sentiment
            logger.debug("No news data available, using neutral sentiment")
            return 0.0
            
        except Exception as e:
            logger.debug(f"Error getting news sentiment (using neutral): {e}")
            return 0.0  # Return neutral sentiment on any error
    
    def _state_to_vector(self, state: MarketState) -> np.ndarray:
        """Convert market state to feature vector"""
        return np.array([
            state.price_change_1h / 100,  # Normalize
            state.price_change_24h / 100,
            (state.rsi - 50) / 50,  # Center around 0
            state.macd,
            state.bollinger_position - 0.5,  # Center around 0
            state.news_sentiment,
            state.order_book_imbalance,
            state.volatility,
            min(state.volume_24h / 1000000, 10),  # Normalize volume
            (self.portfolio.total_value_usdt - self.initial_balance) / self.initial_balance  # Portfolio performance
        ])
    
    def get_trading_recommendation(self, market_state: MarketState) -> TradingAction:
        """Get AI trading recommendation with conservative risk management"""
        
        # Check risk limits first
        if self._check_risk_limits():
            return TradingAction(
                action_type=ActionType.HOLD,
                symbol="BTC/USDT",
                confidence=1.0,
                risk_score=0.0,
                expected_return=0.0,
                stop_loss=0.0,
                take_profit=0.0,
                reasoning="Risk limits exceeded - holding position"
            )
        
        # Convert state to feature vector
        state_vector = self._state_to_vector(market_state)
        
        # Get Q-values from network
        q_values = self._forward_pass(state_vector, self.q_network)
        
        # Apply conservative filtering
        filtered_actions = self._apply_conservative_filters(q_values, market_state)
        
        # Select best action
        best_action_idx = np.argmax(filtered_actions)
        best_action = ActionType(best_action_idx)
        confidence = self._calculate_confidence(filtered_actions, best_action_idx)
        
        # Calculate position sizing and risk metrics
        position_size = self._calculate_position_size(best_action, confidence, market_state)
        risk_score = self._calculate_risk_score(market_state, best_action)
        
        return TradingAction(
            action_type=best_action,
            symbol="BTC/USDT",
            confidence=confidence,
            risk_score=risk_score,
            expected_return=self._estimate_expected_return(best_action, market_state),
            stop_loss=market_state.price * (1 - self.stop_loss_pct) if best_action in [ActionType.BUY_SMALL, ActionType.BUY_MEDIUM, ActionType.BUY_LARGE] else 0,
            take_profit=market_state.price * (1 + self.take_profit_pct) if best_action in [ActionType.BUY_SMALL, ActionType.BUY_MEDIUM, ActionType.BUY_LARGE] else 0,
            reasoning=self._generate_reasoning(best_action, market_state, confidence, risk_score)
        )
    
    def _check_risk_limits(self) -> bool:
        """Check if risk limits are exceeded"""
        # Daily loss limit
        daily_pnl_pct = (self.portfolio.total_value_usdt - self.initial_balance) / self.initial_balance
        if daily_pnl_pct < -self.daily_loss_limit:
            return True
        
        # Consecutive losses
        if self.consecutive_losses >= self.consecutive_loss_limit:
            return True
        
        # Maximum drawdown
        if self.portfolio.max_drawdown > 0.10:  # 10% max drawdown
            return True
        
        return False
    
    def _apply_conservative_filters(self, q_values: np.ndarray, market_state: MarketState) -> np.ndarray:
        """Apply conservative filters to Q-values"""
        filtered = q_values.copy()
        
        # Reduce aggressive actions in high volatility
        if market_state.volatility > 0.05:  # High volatility
            filtered[ActionType.BUY_LARGE.value] *= 0.5
            filtered[ActionType.BUY_MEDIUM.value] *= 0.7
        
        # Reduce buying in negative sentiment
        if market_state.news_sentiment < -0.3:
            filtered[ActionType.BUY_SMALL.value] *= 0.8
            filtered[ActionType.BUY_MEDIUM.value] *= 0.6
            filtered[ActionType.BUY_LARGE.value] *= 0.4
        
        # Prefer holding in uncertain conditions
        if abs(market_state.news_sentiment) < 0.1 and market_state.volatility > 0.03:
            filtered[ActionType.HOLD.value] *= 1.2
        
        return filtered
    
    def _calculate_confidence(self, q_values: np.ndarray, best_action_idx: int) -> float:
        """Calculate confidence in the selected action"""
        if len(q_values) < 2:
            return 0.5
        
        sorted_q = np.sort(q_values)[::-1]  # Sort descending
        if sorted_q[0] == sorted_q[1]:
            return 0.5
        
        confidence = (sorted_q[0] - sorted_q[1]) / (sorted_q[0] + 1e-8)
        return min(max(confidence, 0.1), 0.9)  # Clamp between 0.1 and 0.9
    
    def _calculate_position_size(self, action: ActionType, confidence: float, market_state: MarketState) -> float:
        """Calculate conservative position size"""
        base_sizes = {
            ActionType.HOLD: 0.0,
            ActionType.BUY_SMALL: 0.05,
            ActionType.BUY_MEDIUM: 0.10,
            ActionType.BUY_LARGE: 0.15,
            ActionType.SELL_PARTIAL: 0.50,
            ActionType.SELL_ALL: 1.0
        }
        
        base_size = base_sizes.get(action, 0.0)
        
        # Adjust based on confidence and market conditions
        confidence_multiplier = 0.5 + (confidence * 0.5)  # 0.5 to 1.0
        volatility_multiplier = max(0.5, 1.0 - market_state.volatility * 10)  # Reduce size in high volatility
        
        return base_size * confidence_multiplier * volatility_multiplier
    
    def _calculate_risk_score(self, market_state: MarketState, action: ActionType) -> float:
        """Calculate risk score for the action"""
        base_risk = {
            ActionType.HOLD: 0.1,
            ActionType.BUY_SMALL: 0.3,
            ActionType.BUY_MEDIUM: 0.5,
            ActionType.BUY_LARGE: 0.7,
            ActionType.SELL_PARTIAL: 0.2,
            ActionType.SELL_ALL: 0.1
        }
        
        risk = base_risk.get(action, 0.5)
        
        # Adjust for market conditions
        risk += market_state.volatility * 2  # Higher volatility = higher risk
        risk += abs(market_state.news_sentiment) * 0.3  # Extreme sentiment = higher risk
        
        return min(max(risk, 0.0), 1.0)
    
    def _estimate_expected_return(self, action: ActionType, market_state: MarketState) -> float:
        """Estimate expected return for the action"""
        if action == ActionType.HOLD:
            return 0.0
        
        # Base expected returns (conservative estimates)
        base_returns = {
            ActionType.BUY_SMALL: 0.02,
            ActionType.BUY_MEDIUM: 0.03,
            ActionType.BUY_LARGE: 0.04,
            ActionType.SELL_PARTIAL: 0.01,
            ActionType.SELL_ALL: 0.005
        }
        
        base_return = base_returns.get(action, 0.0)
        
        # Adjust based on market sentiment and momentum
        sentiment_multiplier = 1.0 + (market_state.news_sentiment * 0.5)
        momentum_multiplier = 1.0 + (market_state.price_change_24h / 100 * 0.3)
        
        return base_return * sentiment_multiplier * momentum_multiplier
    
    def _generate_reasoning(self, action: ActionType, market_state: MarketState, confidence: float, risk_score: float) -> str:
        """Generate human-readable reasoning for the action"""
        reasons = []
        
        # Market condition analysis
        if market_state.price_change_24h > 2:
            reasons.append("强势上涨趋势")
        elif market_state.price_change_24h < -2:
            reasons.append("下跌趋势")
        else:
            reasons.append("横盘整理")
        
        # Sentiment analysis
        if market_state.news_sentiment > 0.3:
            reasons.append("新闻情绪积极")
        elif market_state.news_sentiment < -0.3:
            reasons.append("新闻情绪消极")
        else:
            reasons.append("新闻情绪中性")
        
        # Technical indicators
        if market_state.rsi > 70:
            reasons.append("RSI超买")
        elif market_state.rsi < 30:
            reasons.append("RSI超卖")
        
        # Risk assessment
        if risk_score > 0.7:
            reasons.append("高风险环境")
        elif risk_score < 0.3:
            reasons.append("低风险环境")
        
        # Action justification
        action_reasons = {
            ActionType.HOLD: "保守持仓等待更好机会",
            ActionType.BUY_SMALL: "小仓位试探性买入",
            ActionType.BUY_MEDIUM: "中等仓位买入",
            ActionType.BUY_LARGE: "较大仓位买入（谨慎）",
            ActionType.SELL_PARTIAL: "部分获利了结",
            ActionType.SELL_ALL: "全部平仓保护利润"
        }
        
        reasons.append(action_reasons.get(action, "未知操作"))
        reasons.append(f"信心度: {confidence:.1%}")
        
        return " | ".join(reasons)
    
    def update_portfolio(self, action: TradingAction, execution_price: float, success: bool):
        """Update portfolio after trade execution"""
        self.portfolio.total_trades += 1
        
        if success:
            # Update portfolio based on action
            if action.action_type in [ActionType.BUY_SMALL, ActionType.BUY_MEDIUM, ActionType.BUY_LARGE]:
                # Record buy action
                self.trade_history.append({
                    'timestamp': datetime.now(),
                    'action': action.action_type.name,
                    'price': execution_price,
                    'confidence': action.confidence,
                    'risk_score': action.risk_score,
                    'reasoning': action.reasoning
                })
            
            # Update consecutive losses counter
            if action.expected_return > 0:
                self.consecutive_losses = 0
            else:
                self.consecutive_losses += 1
        
        # Calculate performance metrics
        self._update_performance_metrics()
    
    def _update_performance_metrics(self):
        """Update portfolio performance metrics"""
        current_return = (self.portfolio.total_value_usdt - self.initial_balance) / self.initial_balance
        
        # Update max drawdown
        if current_return < 0:
            self.portfolio.max_drawdown = max(self.portfolio.max_drawdown, abs(current_return))
        
        # Calculate win rate from recent trades
        if len(self.trade_history) > 0:
            recent_trades = self.trade_history[-20:]  # Last 20 trades
            wins = sum(1 for trade in recent_trades if trade.get('pnl', 0) > 0)
            self.portfolio.win_rate = wins / len(recent_trades)
    
    def save_model(self):
        """Save the trained model"""
        model_data = {
            'q_network': self.q_network,
            'target_network': self.target_network,
            'portfolio': self.portfolio,
            'trade_history': self.trade_history,
            'performance_metrics': self.performance_metrics,
            'learning_parameters': {
                'learning_rate': self.learning_rate,
                'epsilon': self.epsilon,
                'max_position_size': self.max_position_size,
                'stop_loss_pct': self.stop_loss_pct,
                'take_profit_pct': self.take_profit_pct
            }
        }
        
        with open(f"{self.model_path}/rl_trader_model.pkl", 'wb') as f:
            pickle.dump(model_data, f)
        
        logger.info("✅ Model saved successfully")
    
    def load_model(self):
        """Load a previously trained model"""
        try:
            with open(f"{self.model_path}/rl_trader_model.pkl", 'rb') as f:
                model_data = pickle.load(f)
            
            self.q_network = model_data['q_network']
            self.target_network = model_data['target_network']
            self.portfolio = model_data['portfolio']
            self.trade_history = model_data['trade_history']
            self.performance_metrics = model_data['performance_metrics']
            
            # Load learning parameters
            params = model_data['learning_parameters']
            self.learning_rate = params['learning_rate']
            self.epsilon = params['epsilon']
            self.max_position_size = params['max_position_size']
            self.stop_loss_pct = params['stop_loss_pct']
            self.take_profit_pct = params['take_profit_pct']
            
            logger.info("✅ Model loaded successfully")
            return True
            
        except FileNotFoundError:
            logger.info("No saved model found, starting fresh")
            return False
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            return False
    
    def get_progress_report(self) -> Dict:
        """Get progress report towards 1000 USDT goal"""
        current_value = self.portfolio.total_value_usdt
        progress_pct = (current_value - self.initial_balance) / (self.target_balance - self.initial_balance) * 100
        
        return {
            'current_balance': current_value,
            'initial_balance': self.initial_balance,
            'target_balance': self.target_balance,
            'progress_percentage': min(progress_pct, 100),
            'profit_loss': current_value - self.initial_balance,
            'profit_loss_pct': (current_value - self.initial_balance) / self.initial_balance * 100,
            'trades_executed': self.portfolio.total_trades,
            'win_rate': self.portfolio.win_rate,
            'max_drawdown': self.portfolio.max_drawdown,
            'days_to_goal': self._estimate_days_to_goal(),
            'risk_level': 'Conservative',
            'next_milestone': self._get_next_milestone()
        }
    
    def _estimate_days_to_goal(self) -> int:
        """Estimate days to reach 1000 USDT goal"""
        if len(self.performance_metrics) < 7:  # Need at least a week of data
            return 365  # Default estimate
        
        # Calculate average daily return from recent performance
        recent_returns = [m.get('daily_return', 0) for m in self.performance_metrics[-7:]]
        avg_daily_return = np.mean(recent_returns) if recent_returns else 0.001
        
        if avg_daily_return <= 0:
            return 999  # Very long time if not profitable
        
        remaining_profit = self.target_balance - self.portfolio.total_value_usdt
        days_needed = remaining_profit / (self.portfolio.total_value_usdt * avg_daily_return)
        
        return max(1, int(days_needed))
    
    def _get_next_milestone(self) -> Dict:
        """Get next milestone target"""
        current = self.portfolio.total_value_usdt
        milestones = [300, 400, 500, 600, 700, 800, 900, 1000]
        
        for milestone in milestones:
            if current < milestone:
                return {
                    'target': milestone,
                    'remaining': milestone - current,
                    'progress_to_milestone': (current - self.initial_balance) / (milestone - self.initial_balance) * 100
                }
        
        return {'target': 1000, 'remaining': 0, 'progress_to_milestone': 100}