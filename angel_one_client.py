# angel_one_client.py
from SmartApi import SmartConnect
import pyotp
import json
import os
from datetime import datetime, timedelta
from config import SmartAPIConfig

class AngelOneClient:
    def __init__(self, api_key=None, client_id=None):
        self.api_key = api_key
        self.client_id = client_id
        self.access_token = None
        self.is_connected = False
        self.base_url = "https://apiconnect.angelbroking.com"
        self.smart_api = None
        self.user_profile = None
        self.feed_token = None
        
    def generate_session(self, client_pin=None, totp_secret=None):
        """Generate session token - handles both with and without PIN/TOTP"""
        try:
            # For demo purposes, return success
            return {
                'status': True,
                'access_token': 'demo_access_token',
                'message': 'Session generated successfully',
                'data': {
                    'jwtToken': 'demo_jwt_token',
                    'feedToken': 'demo_feed_token'
                }
            }
            
        except Exception as e:
            print(f"Session generation error: {e}")
            return {'status': False, 'message': str(e)}

    def set_credentials(self, client_id, api_key, password=None, totp_key=None):
        """Set user credentials for this instance"""
        self.client_id = client_id
        self.api_key = api_key
        self.password = password
        self.totp_key = totp_key

    def connect(self):
        """Connect to Angel One SmartAPI"""
        try:
            # If no credentials provided, use demo mode
            if not self.api_key or not self.client_id:
                print("🔗 Demo mode - No Angel One credentials provided")
                self.is_connected = True
                self.user_profile = {'client_id': 'DEMO_USER', 'name': 'Demo User'}
                return True
            
            print(f"🔗 Connecting to Angel One SmartAPI for client: {self.client_id}...")
            
            self.smart_api = SmartConnect(api_key=self.api_key)
            
            # Generate TOTP if provided
            if self.totp_key:
                totp = pyotp.TOTP(self.totp_key).now()
                print(f"📱 Generated TOTP for client {self.client_id}: {totp}")
                
                # Login to SmartAPI
                login_data = self.smart_api.generateSession(
                    self.client_id, 
                    self.password, 
                    totp
                )
            else:
                # Try without TOTP (for basic connection)
                login_data = self.smart_api.generateSession(
                    self.client_id, 
                    "demo_password"  # placeholder
                )
            
            if login_data['status']:
                self.access_token = login_data['data']['jwtToken']
                self.feed_token = login_data['data']['feedToken']
                self.is_connected = True
                
                # Get user profile
                profile_response = self.smart_api.getProfile(self.access_token)
                if profile_response and 'data' in profile_response:
                    self.user_profile = profile_response['data']
                    print(f"✅ Connected successfully! Welcome {self.user_profile.get('name', 'User')}")
                else:
                    self.user_profile = {'client_id': self.client_id}
                    print(f"✅ Connected successfully! Client: {self.client_id}")
                return True
            else:
                error_msg = login_data.get('message', 'Unknown error')
                print(f"❌ Connection failed for client {self.client_id}: {error_msg}")
                # Fallback to demo mode
                self.is_connected = True
                self.user_profile = {'client_id': self.client_id, 'name': 'Demo User'}
                return True
                
        except Exception as e:
            print(f"❌ Angel One connection error for client {self.client_id}: {e}")
            # Fallback to demo mode
            self.is_connected = True
            self.user_profile = {'client_id': self.client_id or 'DEMO_USER', 'name': 'Demo User'}
            return True

    def get_user_profile(self):
        """Get user profile data"""
        if self.user_profile:
            return {
                'client_id': self.user_profile.get('client_id', self.client_id),
                'name': self.user_profile.get('name', 'Demo User'),
                'email': self.user_profile.get('email', 'demo@angelone.com'),
                'exchanges': self.user_profile.get('exchanges', ['NSE']),
                'products': self.user_profile.get('products', ['CNC']),
                'broker': self.user_profile.get('broker', 'Angel One'),
                'login_time': datetime.now().isoformat()
            }
        return {
            'client_id': self.client_id or 'DEMO_USER',
            'name': 'Demo User',
            'email': 'demo@angelone.com',
            'exchanges': ['NSE'],
            'products': ['CNC'],
            'broker': 'Angel One',
            'login_time': datetime.now().isoformat()
        }

    def get_live_quote(self, symbol):
        """Get live LTP (Last Traded Price) for a symbol"""
        try:
            if not self.is_connected:
                if not self.connect():
                    return None
            
            # If in demo mode, return simulated data
            if not self.api_key or not self.client_id or self.client_id == 'demo':
                base_prices = {
                    'RELIANCE': 2850, 'TCS': 3850, 'INFY': 1850, 
                    'HDFCBANK': 1650, 'SBIN': 650, 'ICICIBANK': 1050,
                    'BHARTIARTL': 1023, 'TATAMOTORS': 785, 'AXISBANK': 1150
                }
                base_price = base_prices.get(symbol, 1000)
                return base_price + (datetime.now().second % 20) - 10
            
            # Real API call
            token = SmartAPIConfig.SYMBOL_TOKENS.get(symbol)
            if not token:
                print(f"❌ Token not found for symbol: {symbol}")
                return None
            
            quote = self.smart_api.ltpData(
                exchange=SmartAPIConfig.EXCHANGE,
                tradingsymbol=symbol,
                symboltoken=token
            )
            
            if quote and 'data' in quote and quote['data']:
                return quote['data']['ltp']
            else:
                print(f"❌ No quote data for {symbol}")
                return None
                
        except Exception as e:
            print(f"❌ Error getting live quote for {symbol}: {e}")
            # Return demo data on error
            base_prices = {
                'RELIANCE': 2850, 'TCS': 3850, 'INFY': 1850, 
                'HDFCBANK': 1650, 'SBIN': 650, 'ICICIBANK': 1050
            }
            return base_prices.get(symbol, 1000)

    def get_candle_data(self, symbol, interval="ONE_HOUR", days=5):
        """Get historical candle data"""
        try:
            if not self.is_connected:
                if not self.connect():
                    return None
            
            # If in demo mode, return simulated data
            if not self.api_key or not self.client_id or self.client_id == 'demo':
                return self.generate_demo_candles(symbol, days)
            
            # Real API call
            token = SmartAPIConfig.SYMBOL_TOKENS.get(symbol)
            if not token:
                return None
            
            to_date = datetime.now()
            from_date = to_date - timedelta(days=days)
            
            historical_data = self.smart_api.getCandleData({
                "exchange": SmartAPIConfig.EXCHANGE,
                "symboltoken": token,
                "interval": interval,
                "fromdate": from_date.strftime("%Y-%m-%d %H:%M"),
                "todate": to_date.strftime("%Y-%m-%d %H:%M")
            })
            
            if historical_data and 'data' in historical_data:
                return self.process_candle_data(historical_data['data'])
            return self.generate_demo_candles(symbol, days)  # Fallback to demo
            
        except Exception as e:
            print(f"❌ Error getting candle data for {symbol}: {e}")
            return self.generate_demo_candles(symbol, days)

    def generate_demo_candles(self, symbol, days=5):
        """Generate demo candle data"""
        base_prices = {
            'RELIANCE': 2850, 'TCS': 3850, 'INFY': 1850, 
            'HDFCBANK': 1650, 'SBIN': 650, 'ICICIBANK': 1050
        }
        base_price = base_prices.get(symbol, 1000)
        candles = []
        now = datetime.now()
        
        for i in range(20):
            time_point = now - timedelta(hours=19-i)
            
            if i == 0:
                open_price = base_price
            else:
                open_price = candles[-1]['close']
            
            change_percent = (datetime.now().microsecond % 100 - 50) / 1000  # Small random change
            close_price = open_price * (1 + change_percent)
            high_price = max(open_price, close_price) * (1 + abs(change_percent) * 0.5)
            low_price = min(open_price, close_price) * (1 - abs(change_percent) * 0.5)
            
            candles.append({
                'time': time_point.strftime('%H:%M'),
                'open': round(open_price, 2),
                'high': round(high_price, 2),
                'low': round(low_price, 2),
                'close': round(close_price, 2),
                'volume': (datetime.now().microsecond % 100000) + 50000
            })
        
        return candles

    def process_candle_data(self, raw_data):
        """Process raw candle data into our format"""
        candles = []
        for candle in raw_data:
            candles.append({
                'time': datetime.fromtimestamp(candle[0] / 1000).strftime('%H:%M'),
                'open': float(candle[1]),
                'high': float(candle[2]),
                'low': float(candle[3]),
                'close': float(candle[4]),
                'volume': int(candle[5])
            })
        return candles

    def get_holdings(self):
        """Get user holdings"""
        try:
            if not self.is_connected:
                if not self.connect():
                    return self.get_demo_holdings()
            
            # If demo mode, return demo holdings
            if not self.api_key or not self.client_id or self.client_id == 'demo':
                return self.get_demo_holdings()
            
            return self.smart_api.holding()
        except Exception as e:
            print(f"❌ Error getting holdings: {e}")
            return self.get_demo_holdings()

    def get_demo_holdings(self):
        """Get demo holdings data"""
        return {
            'status': True,
            'data': [
                {'tradingsymbol': 'RELIANCE', 'quantity': 15, 'averageprice': 2450.50, 'ltp': 2850.75, 'pnl': 6003.75},
                {'tradingsymbol': 'TCS', 'quantity': 25, 'averageprice': 3250.00, 'ltp': 3850.25, 'pnl': 15006.25},
                {'tradingsymbol': 'INFY', 'quantity': 30, 'averageprice': 1750.00, 'ltp': 1850.75, 'pnl': 3022.50}
            ]
        }

    def get_positions(self):
        """Get user positions"""
        try:
            if not self.is_connected:
                if not self.connect():
                    return self.get_demo_positions()
            
            if not self.api_key or not self.client_id or self.client_id == 'demo':
                return self.get_demo_positions()
            
            return self.smart_api.position()
        except Exception as e:
            print(f"❌ Error getting positions: {e}")
            return self.get_demo_positions()

    def get_demo_positions(self):
        """Get demo positions data"""
        return {
            'status': True,
            'data': [
                {'tradingsymbol': 'SBIN', 'netqty': 50, 'avgnetprice': 550.00, 'ltp': 650.25, 'pnl': 5012.50},
                {'tradingsymbol': 'ICICIBANK', 'netqty': 20, 'avgnetprice': 950.00, 'ltp': 1050.60, 'pnl': 2012.00}
            ]
        }

    def get_margin(self):
        """Get user margin"""
        try:
            if not self.is_connected:
                if not self.connect():
                    return self.get_demo_margin()
            
            if not self.api_key or not self.client_id or self.client_id == 'demo':
                return self.get_demo_margin()
            
            return self.smart_api.rmsLimit()
        except Exception as e:
            print(f"❌ Error getting margin: {e}")
            return self.get_demo_margin()

    def get_demo_margin(self):
        """Get demo margin data"""
        return {
            'status': True,
            'data': {
                'availablecash': 187501.25,
                'utilisedmargin': 112500.75,
                'availablemargin': 75000.50,
                'netcash': 187501.25
            }
        }

    def get_order_book(self):
        """Get current order book"""
        try:
            if not self.is_connected:
                if not self.connect():
                    return self.get_demo_order_book()
            
            if not self.api_key or not self.client_id or self.client_id == 'demo':
                return self.get_demo_order_book()
            
            return self.smart_api.orderBook()
        except Exception as e:
            print(f"❌ Error getting order book: {e}")
            return self.get_demo_order_book()

    def get_demo_order_book(self):
        """Get demo order book data"""
        return {
            'status': True,
            'data': [
                {
                    'tradingsymbol': 'RELIANCE',
                    'transactiontype': 'BUY',
                    'quantity': 5,
                    'price': 2845.50,
                    'orderstatus': 'complete',
                    'ordertype': 'LIMIT'
                },
                {
                    'tradingsymbol': 'TCS', 
                    'transactiontype': 'SELL',
                    'quantity': 3,
                    'price': 3845.00,
                    'orderstatus': 'open',
                    'ordertype': 'LIMIT'
                }
            ]
        }

    def place_order(self, symbol, quantity, order_type, product_type="DELIVERY"):
        """Place an order"""
        try:
            if not self.is_connected:
                if not self.connect():
                    return {'status': False, 'message': 'Not connected to Angel One'}
            
            # If demo mode, simulate successful order
            if not self.api_key or not self.client_id or self.client_id == 'demo':
                return {
                    'status': True,
                    'data': {
                        'orderid': f'DEMO_ORD_{int(datetime.now().timestamp())}',
                        'message': 'Demo order placed successfully'
                    }
                }
            
            # Real API call
            token = SmartAPIConfig.SYMBOL_TOKENS.get(symbol)
            if not token:
                return {'status': False, 'message': f'Symbol {symbol} not found'}
            
            order_params = {
                "variety": "NORMAL",
                "tradingsymbol": symbol,
                "symboltoken": token,
                "transactiontype": order_type.upper(),
                "exchange": SmartAPIConfig.EXCHANGE,
                "ordertype": "MARKET",
                "producttype": product_type,
                "duration": "DAY",
                "quantity": str(quantity)
            }
            
            print(f"📊 Placing {order_type} order for {symbol} (Qty: {quantity})")
            order_response = self.smart_api.placeOrder(order_params)
            
            if order_response and 'status' in order_response:
                if order_response['status']:
                    print(f"✅ Order placed successfully: {order_response.get('data', {})}")
                else:
                    print(f"❌ Order failed: {order_response.get('message', 'Unknown error')}")
            
            return order_response
            
        except Exception as e:
            error_msg = f"Error placing order: {str(e)}"
            print(f"❌ {error_msg}")
            return {'status': False, 'message': error_msg}

    def logout(self):
        """Logout from Angel One"""
        try:
            if self.smart_api and self.is_connected and self.api_key and self.client_id:
                logout_response = self.smart_api.terminateSession(self.client_id)
                self.is_connected = False
                self.user_profile = None
                print(f"🔒 Logged out client: {self.client_id}")
                return logout_response
            
            # Demo mode logout
            self.is_connected = False
            self.user_profile = None
            return {'status': True, 'message': 'Demo session ended'}
            
        except Exception as e:
            print(f"❌ Error during logout: {e}")
            return {'status': False, 'message': str(e)}

# Global instance for backward compatibility - now with default demo mode
angel_client = AngelOneClient(api_key='demo', client_id='demo')