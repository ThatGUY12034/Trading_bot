from SmartApi import SmartConnect
import pyotp
from config import SmartAPIConfig
import pandas as pd
from datetime import datetime, timedelta
import time
import json
import logging
import threading
from typing import Dict, List, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RealTimeDataFetcher:
    def __init__(self):
        self.api = None
        self.connected = False
        self.token = None
        self.cache = {}
        self.cache_duration = 5  # seconds
        self.active_symbols = set()
        self.price_callbacks = []
        self.websocket_feed = None
        
    def add_price_callback(self, callback):
        """Add callback function to receive real-time price updates"""
        self.price_callbacks.append(callback)
    
    def notify_price_update(self, symbol: str, data: Dict):
        """Notify all registered callbacks of price updates"""
        for callback in self.price_callbacks:
            try:
                callback(symbol, data)
            except Exception as e:
                logger.error(f"Error in price callback: {e}")
    
    def connect(self):
        """Connect to SmartAPI"""
        try:
            logger.info("🔗 Connecting to SmartAPI for real-time data...")
            self.api = SmartConnect(api_key=SmartAPIConfig.API_KEY)
            
            # Generate TOTP
            totp = pyotp.TOTP(SmartAPIConfig.TOTP).now()
            logger.info(f"🔑 Generated TOTP: {totp}")
            
            # Login
            login_data = self.api.generateSession(
                SmartAPIConfig.CLIENT_ID, 
                SmartAPIConfig.PIN, 
                totp
            )
            
            if login_data['status']:
                self.connected = True
                self.token = login_data['data']['jwtToken']
                self.api.setRefreshToken(login_data['data']['refreshToken'])
                
                logger.info("✅ SmartAPI Connected Successfully!")
                logger.info(f"📊 Token: {self.token[:50]}...")
                
                # Start WebSocket connection for real-time data
                self.start_websocket()
                return True
            else:
                logger.error(f"❌ Login failed: {login_data['message']}")
                return False
                
        except Exception as e:
            logger.error(f"💥 Connection error: {e}")
            return False
    
    def start_websocket(self):
        """Start WebSocket connection for real-time data"""
        try:
            if self.connected:
                # Start WebSocket feed
                self.websocket_feed = self.api.getWebSocket()
                logger.info("📡 WebSocket connection initialized")
                
                # Start WebSocket in a separate thread
                ws_thread = threading.Thread(target=self._websocket_listener)
                ws_thread.daemon = True
                ws_thread.start()
                
        except Exception as e:
            logger.error(f"Error starting WebSocket: {e}")
    
    def _websocket_listener(self):
        """Listen to WebSocket messages"""
        try:
            while self.connected:
                # Check for new WebSocket messages
                # Note: SmartAPI WebSocket implementation might vary
                # Adjust based on actual SmartAPI WebSocket documentation
                time.sleep(1)
                
        except Exception as e:
            logger.error(f"WebSocket listener error: {e}")
    
    def subscribe_symbol(self, symbol: str):
        """Subscribe to real-time updates for a symbol"""
        try:
            if self.connected and self.websocket_feed:
                token = self._get_token(symbol)
                if token:
                    # Subscribe to WebSocket feed
                    subscription_data = {
                        "action": 1,  # Subscribe
                        "mode": 1,    # LTP mode
                        "tokenList": [
                            {
                                "exchangeType": 1,  # NSE
                                "tokens": [token]
                            }
                        ]
                    }
                    self.websocket_feed.send(json.dumps(subscription_data))
                    self.active_symbols.add(symbol)
                    logger.info(f"📡 Subscribed to real-time data for {symbol}")
                    
        except Exception as e:
            logger.error(f"Error subscribing to {symbol}: {e}")
    
    def _get_token(self, symbol: str) -> Optional[str]:
        """Get token for symbol"""
        token_map = {
            "SBIN": "3045",
            "RELIANCE": "2885", 
            "TATASTEEL": "3499",
            "INFY": "1594",
            "TCS": "2951",
            "HDFCBANK": "1330",
            "ICICIBANK": "4963",
            "HINDUNILVR": "1394",
            "ITC": "1660",
            "LT": "11536",
            "BHARTIARTL": "10604",
            "KOTAKBANK": "1922",
            "AXISBANK": "5900",
            "ASIANPAINT": "694",
            "MARUTI": "10999",
            "SUNPHARMA": "857",
            "TATAMOTORS": "3456",
            "TITAN": "8994",
            "ULTRACEMCO": "11532",
            "WIPRO": "3787"
        }
        return token_map.get(symbol)
    
    def get_live_quote(self, symbol="SBIN"):
        """Get live market quote for a symbol"""
        try:
            if not self.connected:
                if not self.connect():
                    return self._generate_fallback_data(symbol)
            
            token = self._get_token(symbol)
            if not token:
                logger.warning(f"Token not found for {symbol}, using fallback")
                return self._generate_fallback_data(symbol)
            
            logger.info(f"📡 Fetching live data for {symbol} (Token: {token})...")
            
            # Get LTP (Last Traded Price)
            quote = self.api.ltpData(
                exchange="NSE",
                tradingsymbol=f"{symbol}-EQ",
                symboltoken=token
            )
            
            if quote and quote.get('status'):
                data = quote['data']
                
                # Calculate change and percentage
                close_price = data.get('close', data['ltp'])
                change = data['ltp'] - close_price
                change_percent = (change / close_price) * 100 if close_price != 0 else 0
                
                result = {
                    'symbol': symbol,
                    'price': round(data['ltp'], 2),
                    'change': round(change, 2),
                    'change_percent': round(change_percent, 2),
                    'open': round(data.get('open', 0), 2),
                    'high': round(data.get('high', 0), 2),
                    'low': round(data.get('low', 0), 2),
                    'close': round(close_price, 2),
                    'volume': data.get('volume', 0),
                    'timestamp': datetime.now().isoformat(),
                    'source': 'smartapi'
                }
                
                # Update cache
                self.cache[symbol] = {
                    'data': result,
                    'timestamp': datetime.now()
                }
                
                # Subscribe for real-time updates
                self.subscribe_symbol(symbol)
                
                logger.info(f"✅ {symbol}: ₹{result['price']} ({result['change_percent']:+.2f}%)")
                return result
            else:
                logger.warning(f"❌ Quote error for {symbol}, using fallback")
                return self._generate_fallback_data(symbol)
                
        except Exception as e:
            logger.error(f"💥 Error getting live quote for {symbol}: {e}")
            return self._generate_fallback_data(symbol)
    
    def _generate_fallback_data(self, symbol: str) -> Dict:
        """Generate fallback data when API fails"""
        base_prices = {
            "SBIN": 650, "RELIANCE": 2850, "INFY": 1850, 
            "TCS": 3850, "HDFCBANK": 1650, "TATAMOTORS": 780,
            "ICICIBANK": 1050, "HINDUNILVR": 2500, "ITC": 450,
            "LT": 3500
        }
        
        base_price = base_prices.get(symbol, 1000)
        variation = (hash(symbol + datetime.now().strftime("%H")) % 20) - 10
        current_price = base_price + variation
        
        return {
            'symbol': symbol,
            'price': round(current_price, 2),
            'change': round(variation, 2),
            'change_percent': round((variation / base_price) * 100, 2),
            'open': round(base_price, 2),
            'high': round(current_price + 5, 2),
            'low': round(current_price - 5, 2),
            'close': round(base_price, 2),
            'volume': 100000,
            'timestamp': datetime.now().isoformat(),
            'source': 'fallback'
        }
    
    def get_historical_data(self, symbol: str, days: int = 30) -> Optional[pd.DataFrame]:
        """Get historical data for technical analysis"""
        try:
            if not self.connected:
                if not self.connect():
                    return None
            
            token = self._get_token(symbol)
            if not token:
                return None
            
            # Get historical data (adjust based on SmartAPI historical data endpoint)
            from_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
            to_date = datetime.now().strftime("%Y-%m-%d")
            
            historical_data = self.api.getCandleData({
                "exchange": "NSE",
                "symboltoken": token,
                "interval": "ONE_HOUR",
                "fromdate": from_date,
                "todate": to_date
            })
            
            if historical_data and historical_data.get('status'):
                data = historical_data['data']
                df = pd.DataFrame(data)
                
                # Convert timestamp and calculate technical indicators
                df['datetime'] = pd.to_datetime(df['timestamp'], unit='s')
                df.set_index('datetime', inplace=True)
                
                # Calculate technical indicators
                df = self._calculate_technical_indicators(df)
                
                return df
                
        except Exception as e:
            logger.error(f"Error fetching historical data for {symbol}: {e}")
        
        return None
    
    def _calculate_technical_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate technical indicators"""
        try:
            df['SMA_20'] = df['close'].rolling(window=20).mean()
            df['SMA_50'] = df['close'].rolling(window=50).mean()
            df['RSI'] = self._calculate_rsi(df['close'])
        except Exception as e:
            logger.error(f"Error calculating technical indicators: {e}")
        
        return df
    
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """Calculate RSI indicator"""
        try:
            delta = prices.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            return rsi
        except:
            return pd.Series([50] * len(prices), index=prices.index)
    
    def get_multiple_quotes(self, symbols: List[str]) -> Dict:
        """Get live quotes for multiple symbols"""
        quotes = {}
        for symbol in symbols:
            quote = self.get_live_quote(symbol)
            if quote:
                quotes[symbol] = quote
            time.sleep(0.5)  # Rate limiting
        return quotes
    
    def generate_trading_signals(self, symbol: str, price_data: Dict, historical_data: pd.DataFrame = None) -> Dict:
        """Generate trading signals based on real data"""
        if historical_data is None or historical_data.empty:
            return {
                'type': 'HOLD',
                'confidence': 50,
                'reason': 'Insufficient data for analysis'
            }
        
        try:
            current_price = price_data['price']
            
            # Get latest technical indicators
            rsi = historical_data['RSI'].iloc[-1] if 'RSI' in historical_data.columns else 50
            sma_20 = historical_data['SMA_20'].iloc[-1] if 'SMA_20' in historical_data.columns else current_price
            sma_50 = historical_data['SMA_50'].iloc[-1] if 'SMA_50' in historical_data.columns else current_price
            
            # Technical analysis logic
            signals = []
            confidence_factors = []
            
            # RSI based signals
            if rsi < 30:
                signals.append('OVERSOLD')
                confidence_factors.append(25)
            elif rsi > 70:
                signals.append('OVERBOUGHT') 
                confidence_factors.append(25)
            else:
                signals.append('NEUTRAL_RSI')
                confidence_factors.append(10)
            
            # Moving average signals
            if current_price > sma_20 > sma_50:
                signals.append('UPTREND')
                confidence_factors.append(30)
            elif current_price < sma_20 < sma_50:
                signals.append('DOWNTREND')
                confidence_factors.append(30)
            else:
                signals.append('SIDEWAYS')
                confidence_factors.append(15)
            
            # Price momentum
            price_change = price_data['change_percent']
            if abs(price_change) > 2:
                signals.append('HIGH_VOLATILITY')
                confidence_factors.append(20)
            
            # Determine final signal
            confidence = min(95, max(60, sum(confidence_factors)))
            
            if 'UPTREND' in signals and 'OVERSOLD' in signals:
                signal_type = 'BUY'
                reason = 'Strong bullish trend with oversold conditions'
            elif 'DOWNTREND' in signals and 'OVERBOUGHT' in signals:
                signal_type = 'SELL'
                reason = 'Strong bearish trend with overbought conditions'
            elif 'UPTREND' in signals:
                signal_type = 'BUY'
                reason = 'Bullish trend identified'
            elif 'DOWNTREND' in signals:
                signal_type = 'SELL'
                reason = 'Bearish trend identified'
            else:
                signal_type = 'HOLD'
                reason = 'Market in consolidation phase'
            
            return {
                'type': signal_type,
                'confidence': round(confidence, 1),
                'reason': reason,
                'indicators': {
                    'rsi': round(rsi, 2),
                    'sma_20': round(sma_20, 2),
                    'sma_50': round(sma_50, 2),
                    'trend': 'Bullish' if signal_type == 'BUY' else 'Bearish' if signal_type == 'SELL' else 'Neutral'
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating trading signals: {e}")
            return {
                'type': 'HOLD',
                'confidence': 50,
                'reason': 'Error in signal generation'
            }
    
    def get_market_status(self):
        """Get current market status"""
        try:
            current_time = datetime.now().time()
            market_open = datetime.strptime("09:15", "%H:%M").time()
            market_close = datetime.strptime("15:30", "%H:%M").time()
            
            is_market_open = market_open <= current_time <= market_close
            
            return {
                'is_open': is_market_open,
                'current_time': current_time.strftime("%H:%M:%S"),
                'market_hours': "09:15 - 15:30",
                'message': "Market is OPEN" if is_market_open else "Market is CLOSED"
            }
            
        except Exception as e:
            logger.error(f"Error getting market status: {e}")
            return None

# Global instance
realtime_fetcher = RealTimeDataFetcher()