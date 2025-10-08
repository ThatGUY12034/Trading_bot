# enhanced_ml_trader_expert.py
import pandas as pd
import numpy as np
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import warnings
from datetime import datetime, timedelta

warnings.filterwarnings('ignore')

# Add this function at the MODULE level (not inside the class)
def fetch_historical_data(token, exchange, interval, days):
    """Fetch historical data - placeholder function"""
    try:
        # This should be implemented to fetch real historical data
        # For now, return simulated data
        print(f"📊 Fetching historical data for token {token}")
        
        # Generate simulated historical data
        base_price = 1000  # Default base price
        df = pd.DataFrame()
        
        # Create date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        date_range = pd.date_range(start=start_date, end=end_date, freq='1H')
        
        # Generate price data
        prices = [base_price]
        for i in range(1, len(date_range)):
            change = np.random.normal(0, 10)  # Random walk
            new_price = prices[-1] + change
            prices.append(max(new_price, 1))  # Ensure positive price
        
        df['datetime'] = date_range
        df['open'] = prices
        df['high'] = [p + abs(np.random.normal(0, 5)) for p in prices]
        df['low'] = [p - abs(np.random.normal(0, 5)) for p in prices]
        df['close'] = [p + np.random.normal(0, 2) for p in prices]
        df['volume'] = np.random.randint(1000, 10000, len(date_range))
        
        return df
        
    except Exception as e:
        print(f"❌ Error in fetch_historical_data: {e}")
        return None

class ExpertAdvisorMLTrader:
    def __init__(self):
        self.model = None
        self.feature_importance = None
        self.accuracy_threshold = 0.60
        
        # Expert Advisor Parameters (from your MQL5 code)
        self.bars_lookback = 5  # BarsN
        self.order_distance_points = 100
        self.tp_points = 200
        self.sl_points = 200
        self.tsl_points = 10
        self.tsl_trigger_points = 15
    
    def expert_breakout_features(self, df):
        """Create features based on the Expert Advisor's breakout strategy"""
        df = df.copy()
        
        # 1. BREAKOUT DETECTION (Core EA Logic)
        df['high_breakout'] = self.detect_high_breakouts(df)
        df['low_breakout'] = self.detect_low_breakouts(df)
        
        # 2. SUPPORT/RESISTANCE LEVELS (EA's findHigh/findLow logic)
        df['resistance_level'] = self.calculate_resistance_levels(df)
        df['support_level'] = self.calculate_support_levels(df)
        
        # 3. BREAKOUT STRENGTH INDICATORS
        df['breakout_strength_high'] = (df['close'] - df['resistance_level']) / df['resistance_level']
        df['breakout_strength_low'] = (df['support_level'] - df['close']) / df['support_level']
        
        # 4. VOLUME CONFIRMATION (EA doesn't use volume, but we can enhance)
        if 'volume' in df.columns:
            df['volume_sma'] = df['volume'].rolling(20).mean()
            df['volume_breakout_ratio'] = df['volume'] / df['volume_sma']
        else:
            df['volume_breakout_ratio'] = 1.0
        
        # 5. PRICE POSITION RELATIVE TO LEVELS
        df['price_to_resistance'] = (df['close'] - df['support_level']) / (df['resistance_level'] - df['support_level'])
        df['distance_to_resistance'] = (df['resistance_level'] - df['close']) / df['close']
        df['distance_to_support'] = (df['close'] - df['support_level']) / df['close']
        
        # 6. BREAKOUT MOMENTUM (Enhanced EA logic)
        df['breakout_momentum'] = self.calculate_breakout_momentum(df)
        df['consolidation_ratio'] = self.calculate_consolidation_ratio(df)
        
        # 7. TIME-BASED FEATURES (EA's time filtering)
        if 'datetime' in df.columns:
            df['hour'] = pd.to_datetime(df['datetime']).dt.hour
            df['is_trading_hours'] = self.is_in_trading_hours(df)
        else:
            df['hour'] = 12
            df['is_trading_hours'] = 1
        
        # 8. RISK MANAGEMENT FEATURES (EA's position sizing)
        df['potential_risk_reward'] = self.calculate_risk_reward(df)
        df['volatility_adjusted_sl'] = self.volatility_adjusted_stop_loss(df)
        
        # TARGET: Predict if breakout will be successful (price moves TP distance)
        if len(df) > 5:
            future_price = df['close'].shift(-5)  # Look 5 periods ahead
            df['target_breakout_success'] = (
                ((future_price - df['close']) / df['close'] > 0.02) |  # 2% up move
                ((df['close'] - future_price) / df['close'] > 0.02)    # 2% down move
            ).astype(int)
        else:
            df['target_breakout_success'] = 0
        
        return df.dropna()
    
    def detect_high_breakouts(self, df, lookback=5):
        """Detect high breakouts like EA's findHigh logic"""
        breakouts = []
        for i in range(len(df)):
            if i < lookback * 2:
                breakouts.append(0)
                continue
                
            current_high = df['high'].iloc[i]
            # Check if current bar is the highest in lookback window
            lookback_highs = df['high'].iloc[i-lookback:i]
            if len(lookback_highs) > 0 and current_high > lookback_highs.max():
                breakouts.append(1)
            else:
                breakouts.append(0)
        return breakouts
    
    def detect_low_breakouts(self, df, lookback=5):
        """Detect low breakouts like EA's findLow logic"""
        breakouts = []
        for i in range(len(df)):
            if i < lookback * 2:
                breakouts.append(0)
                continue
                
            current_low = df['low'].iloc[i]
            # Check if current bar is the lowest in lookback window
            lookback_lows = df['low'].iloc[i-lookback:i]
            if len(lookback_lows) > 0 and current_low < lookback_lows.min():
                breakouts.append(1)
            else:
                breakouts.append(0)
        return breakouts
    
    def calculate_resistance_levels(self, df, lookback=5):
        """Calculate resistance levels like EA's findHigh function"""
        resistance = []
        for i in range(len(df)):
            if i < lookback:
                resistance.append(df['high'].iloc[i])
                continue
                
            # Find recent highs within lookback period
            recent_highs = df['high'].iloc[i-lookback:i+1]
            resistance_level = recent_highs.max()
            resistance.append(resistance_level)
        return resistance
    
    def calculate_support_levels(self, df, lookback=5):
        """Calculate support levels like EA's findLow function"""
        support = []
        for i in range(len(df)):
            if i < lookback:
                support.append(df['low'].iloc[i])
                continue
                
            # Find recent lows within lookback period
            recent_lows = df['low'].iloc[i-lookback:i+1]
            support_level = recent_lows.min()
            support.append(support_level)
        return support
    
    def calculate_breakout_momentum(self, df):
        """Calculate momentum after breakout detection"""
        # Price acceleration after breakout
        price_change = df['close'].pct_change()
        volatility = price_change.rolling(10).std()
        momentum = price_change / (volatility + 1e-8)  # Avoid division by zero
        return momentum.fillna(0)
    
    def calculate_consolidation_ratio(self, df, lookback=10):
        """Measure how consolidated the market is before breakout"""
        consolidation = []
        for i in range(len(df)):
            if i < lookback:
                consolidation.append(0)
                continue
                
            recent_prices = df['close'].iloc[i-lookback:i]
            price_range = recent_prices.max() - recent_prices.min()
            avg_price = recent_prices.mean()
            consolidation_ratio = price_range / (avg_price + 1e-8)
            consolidation.append(consolidation_ratio)
        return consolidation
    
    def is_in_trading_hours(self, df, start_hour=1, end_hour=23):
        """Simulate EA's time filtering logic"""
        return ((df['hour'] >= start_hour) & (df['hour'] <= end_hour)).astype(int)
    
    def calculate_risk_reward(self, df):
        """Calculate potential risk-reward ratio for each breakout"""
        risk_reward = []
        for i in range(len(df)):
            if i < len(df) and df['high_breakout'].iloc[i] == 1:
                entry = df['resistance_level'].iloc[i]
                sl = entry - (self.sl_points * 0.0001)  # Approximate point value
                tp = entry + (self.tp_points * 0.0001)
                risk = entry - sl
                reward = tp - entry
                rr_ratio = reward / risk if risk > 0 else 0
            elif i < len(df) and df['low_breakout'].iloc[i] == 1:
                entry = df['support_level'].iloc[i]
                sl = entry + (self.sl_points * 0.0001)
                tp = entry - (self.tp_points * 0.0001)
                risk = sl - entry
                reward = entry - tp
                rr_ratio = reward / risk if risk > 0 else 0
            else:
                rr_ratio = 0
            risk_reward.append(rr_ratio)
        return risk_reward
    
    def volatility_adjusted_stop_loss(self, df):
        """Calculate volatility-adjusted stop loss like EA's trailing stop"""
        atr = self.calculate_atr(df)
        return (df['close'] * 0.01) / (atr + 1e-8)  # Normalized by volatility
    
    def calculate_atr(self, df, period=14):
        """Calculate Average True Range"""
        high_low = df['high'] - df['low']
        high_close = np.abs(df['high'] - df['close'].shift())
        low_close = np.abs(df['low'] - df['close'].shift())
        true_range = np.maximum(high_low, np.maximum(high_close, low_close))
        return true_range.rolling(period).mean().fillna(0)
    
    def train_expert_ml_model(self, df):
        """Train ML model using Expert Advisor logic features"""
        print("🧠 Creating Expert Advisor-based features...")
        df_featured = self.expert_breakout_features(df)
        
        if len(df_featured) < 100:
            print("❌ Not enough data for training")
            return False
        
        # Select only Expert Advisor-based features
        feature_cols = [
            'high_breakout', 'low_breakout', 'resistance_level', 'support_level',
            'breakout_strength_high', 'breakout_strength_low', 'volume_breakout_ratio',
            'price_to_resistance', 'distance_to_resistance', 'distance_to_support',
            'breakout_momentum', 'consolidation_ratio', 'is_trading_hours',
            'potential_risk_reward', 'volatility_adjusted_sl'
        ]
        
        # Filter existing columns
        feature_cols = [col for col in feature_cols if col in df_featured.columns]
        
        X = df_featured[feature_cols]
        y = df_featured['target_breakout_success']
        
        print(f"📊 Using {len(feature_cols)} Expert Advisor features with {len(X)} samples")
        
        # Time-based split (more realistic for trading)
        split_idx = int(0.7 * len(X))
        X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
        y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]
        
        # Use ensemble model
        from sklearn.ensemble import VotingClassifier
        
        rf = RandomForestClassifier(n_estimators=150, max_depth=10, random_state=42, min_samples_split=10)
        gb = GradientBoostingClassifier(n_estimators=150, learning_rate=0.1, max_depth=6, random_state=42)
        
        self.model = VotingClassifier(
            estimators=[('rf', rf), ('gb', gb)],
            voting='soft'
        )
        
        print("🔄 Training Expert Advisor ML model...")
        self.model.fit(X_train, y_train)
        
        # Evaluate model
        y_pred_train = self.model.predict(X_train)
        y_pred_test = self.model.predict(X_test)
        
        train_accuracy = accuracy_score(y_train, y_pred_train)
        test_accuracy = accuracy_score(y_test, y_pred_test)
        
        print(f"✅ Expert ML Model Training Complete:")
        print(f"   Training Accuracy: {train_accuracy:.3f}")
        print(f"   Testing Accuracy:  {test_accuracy:.3f}")
        
        # Feature importance
        if hasattr(self.model.estimators_[0], 'feature_importances_'):
            self.feature_importance = pd.DataFrame({
                'feature': X.columns,
                'importance': self.model.estimators_[0].feature_importances_
            }).sort_values('importance', ascending=False)
            
            print("📊 Most Important Breakout Features:")
            print(self.feature_importance.head(8))
        
        model_is_usable = test_accuracy > self.accuracy_threshold
        if model_is_usable:
            print(f"🎯 Model meets accuracy threshold ({self.accuracy_threshold}) - READY FOR TRADING")
        else:
            print(f"⚠️ Model below accuracy threshold - USING CONSERVATIVE MODE")
        
        return model_is_usable
    
    def predict_expert_signal(self, df):
        """Generate trading signals using Expert Advisor + ML logic"""
        if self.model is None:
            return "HOLD", 0.0, "Model Not Trained"
        
        try:
            df_featured = self.expert_breakout_features(df)
            if len(df_featured) == 0:
                return "HOLD", 0.0, "No Features"
            
            # Get latest features
            feature_cols = [
                'high_breakout', 'low_breakout', 'resistance_level', 'support_level',
                'breakout_strength_high', 'breakout_strength_low', 'volume_breakout_ratio',
                'price_to_resistance', 'distance_to_resistance', 'distance_to_support',
                'breakout_momentum', 'consolidation_ratio', 'is_trading_hours',
                'potential_risk_reward', 'volatility_adjusted_sl'
            ]
            feature_cols = [col for col in feature_cols if col in df_featured.columns]
            
            latest_features = df_featured[feature_cols].iloc[-1:].values
            
            # Get prediction
            probabilities = self.model.predict_proba(latest_features)[0]
            prediction = self.model.predict(latest_features)[0]
            confidence = max(probabilities)
            
            # Expert Advisor + ML combined logic
            current_high_breakout = df_featured['high_breakout'].iloc[-1]
            current_low_breakout = df_featured['low_breakout'].iloc[-1]
            
            # Combined signal generation
            if prediction == 1 and confidence > 0.65:
                if current_high_breakout == 1:
                    return "BUY", confidence, "High Breakout Confirmed"
                elif current_low_breakout == 1:
                    return "SELL", confidence, "Low Breakout Confirmed"
                else:
                    return "HOLD", confidence, "No Clear Breakout"
            else:
                return "HOLD", confidence, "Low Confidence"
                
        except Exception as e:
            print(f"❌ Expert prediction error: {e}")
            return "HOLD", 0.0, f"Error: {str(e)}"
    
    def get_expert_trading_levels(self, df):
        """Get Expert Advisor trading levels for current market"""
        try:
            df_featured = self.expert_breakout_features(df)
            
            if len(df_featured) == 0:
                return None
            
            current_data = df_featured.iloc[-1]
            
            buy_entry = current_data['resistance_level'] if current_data['high_breakout'] == 1 else None
            sell_entry = current_data['support_level'] if current_data['low_breakout'] == 1 else None
            
            buy_sl = buy_entry - (self.sl_points * 0.0001) if buy_entry else None
            buy_tp = buy_entry + (self.tp_points * 0.0001) if buy_entry else None
            
            sell_sl = sell_entry + (self.sl_points * 0.0001) if sell_entry else None
            sell_tp = sell_entry - (self.tp_points * 0.0001) if sell_entry else None
            
            return {
                'buy_entry': buy_entry,
                'buy_sl': buy_sl,
                'buy_tp': buy_tp,
                'sell_entry': sell_entry,
                'sell_sl': sell_sl,
                'sell_tp': sell_tp,
                'current_resistance': current_data['resistance_level'],
                'current_support': current_data['support_level']
            }
        except Exception as e:
            print(f"❌ Error getting trading levels: {e}")
            return None