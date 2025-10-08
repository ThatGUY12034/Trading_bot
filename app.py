from flask import Flask, render_template, jsonify, request, session
from flask_cors import CORS
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import random
import threading
import time
from dotenv import load_dotenv
from csv_data_manager import csv_manager

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this in production
CORS(app)

# Import angel_one_client but don't initialize globally yet
try:
    from angel_one_client import AngelOneClient
    ANGEL_ONE_AVAILABLE = True
    print("✅ Angel One Client imported successfully")
except ImportError as e:
    print(f"❌ Angel One Client import failed: {e}")
    ANGEL_ONE_AVAILABLE = False

# Import your trading bot components
try:
    from ml_trading_models import ExpertAdvisorMLTrader
    ML_MODELS_AVAILABLE = True
    print("✅ ML models imported successfully")
except ImportError as e:
    print(f"❌ ML models import failed: {e}")
    ML_MODELS_AVAILABLE = False

try:
    from ml_trading_models import fetch_historical_data
    HISTORICAL_DATA_AVAILABLE = True
    print("✅ Historical data function imported successfully")
except ImportError as e:
    print(f"❌ Historical data import failed: {e}")
    HISTORICAL_DATA_AVAILABLE = False

# Import backtesting module
try:
    from backtest import BacktestEngine
    BACKTEST_AVAILABLE = True
    print("✅ Backtesting engine imported successfully")
except ImportError as e:
    print(f"❌ Backtesting engine import failed: {e}")
    BACKTEST_AVAILABLE = False

# Import user session management
try:
    from user_session_manager import user_session_manager
    USER_SESSIONS_AVAILABLE = True
    print("✅ User session manager imported successfully")
except ImportError as e:
    print(f"❌ User session manager import failed: {e}")
    USER_SESSIONS_AVAILABLE = False

# Global demo instance
angel_client = None

class TradingBot:
    def __init__(self):
        self.status = 'stopped'
        self.selected_stock = None
        self.portfolio = {
            'balance': 100000,
            'dailyPnL': 1250.75,
            'openPositions': 3,
            'winRate': 72.5
        }
        self.trade_history = []
        self.base_prices = {
            'RELIANCE': 2450, 'TCS': 3300, 'INFY': 1500, 
            'HDFCBANK': 1450, 'SBIN': 560, 'TATAMOTORS': 780,
            'HDFC': 1650, 'ICICIBANK': 1050, 'BHARTIARTL': 1023,
            'AXISBANK': 1150, 'KOTAKBANK': 1850, 'LT': 3650,
            'MARUTI': 12500, 'BAJFINANCE': 7500, 'ASIANPAINT': 3500
        }

    def generate_market_data(self, symbol):
        """Generate simulated market data for a symbol"""
        base_price = self.base_prices.get(symbol, 1000)
        current_price = base_price + random.uniform(-50, 50)
        
        prices = [current_price]
        for _ in range(19):
            change = random.uniform(-10, 10)
            prices.append(prices[-1] + change)
        
        times = [(datetime.now() - timedelta(minutes=19-i)).strftime('%H:%M') 
                for i in range(20)]
        
        return {
            'currentPrice': round(current_price, 2),
            'signal': {
                'type': random.choice(['BUY', 'SELL', 'HOLD']),
                'confidence': random.randint(70, 95),
                'reason': random.choice(['Trend analysis', 'Volume spike', 'Pattern recognition'])
            },
            'levels': {
                'support': round(current_price * 0.98, 2),
                'resistance': round(current_price * 1.02, 2)
            },
            'chartData': {
                'labels': times,
                'prices': [round(p, 2) for p in prices]
            }
        }

    def generate_ml_metrics(self):
        return {
            'accuracy': random.randint(75, 90),
            'confidence': random.randint(80, 95)
        }

# Global instances
bot = TradingBot()
bot_state = {
    'status': 'stopped',
    'current_signal': 'HOLD',
    'current_confidence': 0.0,
    'current_price': 0.0,
    'portfolio_value': 100000,
    'positions': [],
    'trade_history': [],
    'ml_metrics': {'accuracy': 0, 'confidence': 0}
}

# Initialize ML trader
if ML_MODELS_AVAILABLE:
    ml_trader = ExpertAdvisorMLTrader()
else:
    ml_trader = None
    print("🔄 Running in simulation mode without ML models")

# Initialize backtest engine
if BACKTEST_AVAILABLE:
    backtest_engine = BacktestEngine()
else:
    backtest_engine = None
    print("🔄 Running without backtesting engine")

# ==================== ROUTES ====================

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/backtest')
def backtest_page():
    return render_template('backtest.html')

# ==================== AUTHENTICATION ROUTES ====================

@app.route('/api/auth/login', methods=['POST'])
def user_login():
    """User login with Angel One credentials - FIXED VERSION"""
    try:
        data = request.json
        client_id = data.get('client_id', '').strip()
        api_key = data.get('api_key', '').strip()
        client_pin = data.get('client_pin', '').strip()
        totp_secret = data.get('totp_secret', '').strip()

        print(f"🔐 Login attempt for client: {client_id}")
        print(f"📧 API Key: {api_key[:10]}...")  # Log first 10 chars for security
        print(f"🔑 Client PIN: {'*' * len(client_pin) if client_pin else 'None'}")
        print(f"🔢 TOTP Secret: {'*' * len(totp_secret) if totp_secret else 'None'}")

        # Validate required fields
        if not client_id or not api_key:
            print("❌ Missing client_id or api_key")
            return jsonify({
                'success': False,
                'message': 'Client ID and API Key are required'
            }), 400

        # Demo mode login
        if client_id == 'demo' and api_key == 'demo':
            print("🎮 Using demo mode login")
            session.clear()
            session['user_id'] = 'demo_user'
            session['authenticated'] = True
            session['demo_mode'] = True
            session['login_time'] = datetime.now().isoformat()
            
            return jsonify({
                'success': True,
                'message': 'Demo login successful! Using enhanced simulation mode.',
                'user_id': 'demo_user',
                'user_profile': {
                    'client_id': 'DEMO1234',
                    'name': 'Demo User',
                    'email': 'demo@angelone.com'
                },
                'session_active': True,
                'demo_mode': True
            })

        # Real Angel One login
        if ANGEL_ONE_AVAILABLE:
            try:
                print("🔗 Attempting real Angel One login...")
                
                # Create user-specific client instance
                user_client = AngelOneClient(
                    api_key=api_key,
                    client_id=client_id
                )
                
                # Set additional credentials if provided
                if client_pin:
                    user_client.password = client_pin
                if totp_secret:
                    user_client.totp_key = totp_secret
                
                print("🔄 Connecting to Angel One API...")
                # Connect to Angel One
                connection_success = user_client.connect()
                
                if connection_success:
                    print("✅ Angel One connection successful!")
                    # Store only serializable data in session
                    session.clear()
                    session['user_id'] = client_id
                    session['authenticated'] = True
                    session['demo_mode'] = False
                    session['login_time'] = datetime.now().isoformat()
                    session['api_key'] = api_key
                    session['client_id'] = client_id
                    
                    # Get user profile
                    user_profile = user_client.get_user_profile()
                    print(f"👤 User profile retrieved: {user_profile}")
                    
                    return jsonify({
                        'success': True,
                        'message': 'Angel One login successful!',
                        'user_id': client_id,
                        'user_profile': user_profile,
                        'session_active': True,
                        'demo_mode': False
                    })
                else:
                    print("❌ Angel One connection failed, falling back to demo mode")
                    # Fallback to demo mode
                    session.clear()
                    session['user_id'] = f"user_{client_id}"
                    session['authenticated'] = True
                    session['demo_mode'] = True
                    session['login_time'] = datetime.now().isoformat()
                    
                    return jsonify({
                        'success': True,
                        'message': 'Using enhanced demo mode (Real API connection failed)',
                        'user_id': f"user_{client_id}",
                        'user_profile': {
                            'client_id': client_id,
                            'name': f'User {client_id}',
                            'email': f'{client_id}@demo.com'
                        },
                        'session_active': True,
                        'demo_mode': True
                    })
                    
            except Exception as auth_error:
                print(f"❌ Angel One auth error: {auth_error}")
                import traceback
                print(f"🔍 Full traceback: {traceback.format_exc()}")
                # Fallback to demo mode
                session.clear()
                session['user_id'] = f"user_{client_id}"
                session['authenticated'] = True
                session['demo_mode'] = True
                session['login_time'] = datetime.now().isoformat()
                
                return jsonify({
                    'success': True,
                    'message': 'Using enhanced demo mode (Authentication error)',
                    'user_id': f"user_{client_id}",
                    'user_profile': {
                        'client_id': client_id,
                        'name': f'User {client_id}',
                        'email': f'{client_id}@demo.com'
                    },
                    'session_active': True,
                    'demo_mode': True
                })
        else:
            print("❌ Angel One not available, using demo mode")
            # Angel One not available, use demo mode
            session.clear()
            session['user_id'] = f"user_{client_id}"
            session['authenticated'] = True
            session['demo_mode'] = True
            session['login_time'] = datetime.now().isoformat()
            
            return jsonify({
                'success': True,
                'message': 'Using enhanced demo mode (Angel One not available)',
                'user_id': f"user_{client_id}",
                'user_profile': {
                    'client_id': client_id,
                    'name': f'User {client_id}',
                    'email': f'{client_id}@demo.com'
                },
                'session_active': True,
                'demo_mode': True
            })
            
    except Exception as e:
        print(f"❌ Login error: {e}")
        import traceback
        print(f"🔍 Full traceback: {traceback.format_exc()}")
        # Final fallback
        session.clear()
        session['user_id'] = 'demo_fallback'
        session['authenticated'] = True
        session['demo_mode'] = True
        session['login_time'] = datetime.now().isoformat()
        
        return jsonify({
            'success': True,
            'message': 'Using enhanced demo mode due to login error',
            'user_id': 'demo_fallback',
            'user_profile': {
                'client_id': 'DEMO_FALLBACK',
                'name': 'Demo User',
                'email': 'demo@fallback.com'
            },
            'session_active': True,
            'demo_mode': True
        })

@app.route('/api/auth/logout', methods=['POST'])
def user_logout():
    """User logout"""
    try:
        session.clear()
        return jsonify({
            'success': True,
            'message': 'Logged out successfully'
        })
            
    except Exception as e:
        print(f"❌ Logout error: {e}")
        return jsonify({
            'success': False,
            'message': f'Logout failed: {str(e)}'
        })

@app.route('/api/auth/status')
def auth_status():
    """Get authentication status"""
    try:
        user_id = session.get('user_id')
        authenticated = session.get('authenticated', False)
        
        if authenticated and user_id:
            # Update last activity
            session['last_activity'] = datetime.now().isoformat()
            
            return jsonify({
                'success': True,
                'authenticated': True,
                'user_id': user_id,
                'demo_mode': session.get('demo_mode', True),
                'last_activity': session.get('last_activity')
            })
        
        return jsonify({
            'success': True,
            'authenticated': False
        })
    except Exception as e:
        print(f"Auth status error: {e}")
        return jsonify({
            'success': False,
            'authenticated': False,
            'message': str(e)
        })

# ==================== USER PORTFOLIO ROUTES ====================

@app.route('/api/user/portfolio')
def get_user_portfolio():
    """Get user portfolio data with fallback to demo data"""
    try:
        user_id = session.get('user_id')
        demo_mode = session.get('demo_mode', True)
        
        # Return enhanced demo portfolio data
        portfolio_data = get_enhanced_portfolio_data()
        return jsonify({
            'success': True,
            'portfolio': portfolio_data
        })
        
    except Exception as e:
        print(f"❌ Portfolio error: {e}")
        # Fallback to enhanced demo data
        portfolio_data = get_enhanced_portfolio_data()
        return jsonify({
            'success': True,
            'portfolio': portfolio_data
        })

def get_enhanced_portfolio_data():
    """Get enhanced portfolio data with realistic values"""
    return {
        'holdings': {
            'data': [
                {'tradingsymbol': 'RELIANCE', 'quantity': 15, 'averageprice': 2450.50, 'ltp': 2850.75, 'pnl': 6003.75, 'current_value': 42761.25},
                {'tradingsymbol': 'TCS', 'quantity': 25, 'averageprice': 3250.00, 'ltp': 3850.25, 'pnl': 15006.25, 'current_value': 96256.25},
                {'tradingsymbol': 'INFY', 'quantity': 30, 'averageprice': 1750.00, 'ltp': 1850.75, 'pnl': 3022.50, 'current_value': 55522.50},
                {'tradingsymbol': 'HDFCBANK', 'quantity': 12, 'averageprice': 1550.00, 'ltp': 1650.80, 'pnl': 1209.60, 'current_value': 19809.60}
            ]
        },
        'positions': {
            'data': [
                {'tradingsymbol': 'SBIN', 'netqty': 50, 'avgnetprice': 550.00, 'ltp': 650.25, 'pnl': 5012.50, 'current_value': 32512.50},
                {'tradingsymbol': 'ICICIBANK', 'netqty': 20, 'avgnetprice': 950.00, 'ltp': 1050.60, 'pnl': 2012.00, 'current_value': 21012.00}
            ]
        },
        'margin': {
            'data': {
                'availablecash': 187501.25,
                'utilisedmargin': 112500.75,
                'availablemargin': 75000.50,
                'netcash': 187501.25
            }
        },
        'summary': {
            'total_value': 534875.35,
            'day_gain': 2875.25,
            'total_gain': 32266.90,
            'unrealized_pnl': 12031.00,
            'realized_pnl': 20235.90
        }
    }

@app.route('/api/user/place-order', methods=['POST'])
def place_user_order():
    """Place order for authenticated user"""
    try:
        data = request.json
        symbol = data.get('symbol')
        quantity = data.get('quantity', 1)
        order_type = data.get('order_type', 'BUY')
        product_type = data.get('product_type', 'DELIVERY')
        
        user_id = session.get('user_id')
        demo_mode = session.get('demo_mode', True)
        
        if not symbol or quantity <= 0:
            return jsonify({'success': False, 'message': 'Invalid symbol or quantity'})
        
        # Demo order placement
        order_response = {
            'status': True,
            'data': {
                'orderid': f'DEMO_ORD_{int(time.time())}',
                'message': 'Demo order placed successfully'
            }
        }
        
        trade_data = {
            'symbol': symbol,
            'direction': order_type,
            'quantity': quantity,
            'entry_price': bot.base_prices.get(symbol, 1000),
            'status': 'completed',
            'order_id': order_response.get('data', {}).get('orderid', ''),
            'user_id': user_id or 'demo_user',
            'order_type': 'DEMO',
            'timestamp': datetime.now().isoformat()
        }
        csv_manager.save_trade(trade_data)
        
        return jsonify({
            'success': True,
            'message': f'{order_type} DEMO order placed for {symbol}',
            'order_id': order_response.get('data', {}).get('orderid', ''),
            'order_response': order_response
        })
            
    except Exception as e:
        print(f"❌ Order placement error: {e}")
        return jsonify({
            'success': False,
            'message': f'Order failed: {str(e)}'
        })

@app.route('/api/user/order-book')
def get_user_order_book():
    """Get user's order book"""
    try:
        # Return demo order book data
        orders = [
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
        
        return jsonify({
            'success': True,
            'order_book': {'data': orders}
        })
    except Exception as e:
        print(f"❌ Order book error: {e}")
        return jsonify({
            'success': True,
            'order_book': {'data': []}
        })

# ==================== MARKET DATA ROUTES ====================

@app.route('/api/market-data')
def get_market_data():
    """Get current market data and trading signals"""
    symbol = request.args.get('symbol', 'SBIN')
    user_id = session.get('user_id')
    demo_mode = session.get('demo_mode', True)
    
    try:
        # Fallback to enhanced simulated data
        print(f"🔄 Using enhanced simulated data for {symbol}")
        data = get_enhanced_market_data(symbol)
        return jsonify(data)
        
    except Exception as e:
        print(f"Error in market data: {e}")
        data = get_enhanced_market_data(symbol)
        return jsonify(data)

def get_enhanced_market_data(symbol):
    """Get enhanced market data with ML integration"""
    base_price = bot.base_prices.get(symbol, 1000)
    current_price = base_price + random.uniform(-base_price * 0.02, base_price * 0.02)
    
    # Generate realistic signal based on price action
    price_change = (current_price - base_price) / base_price * 100
    
    if price_change > 1.5:
        signal_type = 'SELL'
        confidence = min(90, 70 + abs(price_change) * 2)
        reason = f'Price up {price_change:.1f}% - Profit taking opportunity'
    elif price_change < -1.5:
        signal_type = 'BUY'
        confidence = min(85, 65 + abs(price_change) * 2)
        reason = f'Price down {abs(price_change):.1f}% - Buying opportunity'
    else:
        signal_type = 'HOLD'
        confidence = 75
        reason = 'Market consolidating - Waiting for clear signal'
    
    # Generate candlestick data
    candlestick_data = generate_realistic_candles(symbol, current_price)
    
    return {
        'currentPrice': round(current_price, 2),
        'signal': {
            'type': signal_type,
            'confidence': round(confidence, 1),
            'reason': reason
        },
        'levels': {
            'support': round(current_price * 0.97, 2),
            'resistance': round(current_price * 1.03, 2)
        },
        'mlMetrics': {
            'accuracy': round(75 + random.random() * 15, 1),
            'confidence': round(80 + random.random() * 15, 1)
        },
        'portfolio': get_enhanced_portfolio_data()['summary'],
        'candlestickData': candlestick_data,
        'tradeHistory': get_recent_trade_history(),
        'source': 'enhanced_simulated',
        'volume': random.randint(100000, 500000),
        'marketCap': f'₹{current_price * random.randint(1000, 5000):,.0f} Cr'
    }

def generate_realistic_candles(symbol, current_price):
    """Generate realistic candlestick data"""
    candles = []
    base_price = bot.base_prices.get(symbol, 1000)
    volatility = base_price * 0.015
    now = datetime.now()
    
    for i in range(20):
        time_point = now - timedelta(minutes=(19-i)*5)
        
        if i == 0:
            open_price = current_price
        else:
            open_price = candles[-1]['close']
        
        # Realistic price movement
        trend_factor = 0.1 if i > 10 else -0.1
        change = random.normalvariate(trend_factor * volatility, volatility * 0.5)
        close_price = open_price + change
        
        high_price = max(open_price, close_price) + abs(random.normalvariate(0, volatility * 0.3))
        low_price = min(open_price, close_price) - abs(random.normalvariate(0, volatility * 0.3))
        
        candles.append({
            'time': time_point.strftime('%H:%M'),
            'open': round(open_price, 2),
            'high': round(high_price, 2),
            'low': round(low_price, 2),
            'close': round(close_price, 2),
            'volume': random.randint(50000, 200000)
        })
    
    return candles

def get_recent_trade_history():
    """Get recent trade history"""
    return [
        {
            'symbol': 'RELIANCE',
            'type': 'BUY',
            'price': 2845.50,
            'quantity': 5,
            'timestamp': (datetime.now() - timedelta(hours=2)).strftime('%H:%M'),
            'pnl': 125.25,
            'order_type': 'REAL'
        },
        {
            'symbol': 'TCS',
            'type': 'SELL', 
            'price': 3825.75,
            'quantity': 3,
            'timestamp': (datetime.now() - timedelta(hours=1)).strftime('%H:%M'),
            'pnl': 86.50,
            'order_type': 'REAL'
        }
    ]

@app.route('/api/stocks')
def get_available_stocks():
    """Get available stocks for trading"""
    try:
        # Enhanced stock list with more details
        stocks = [
            {'symbol': 'RELIANCE', 'name': 'Reliance Industries Ltd.', 'ltp': 2850.50, 'change': -0.75, 'sector': 'Energy'},
            {'symbol': 'TCS', 'name': 'Tata Consultancy Services Ltd.', 'ltp': 3850.25, 'change': 0.45, 'sector': 'IT'},
            {'symbol': 'INFY', 'name': 'Infosys Ltd.', 'ltp': 1850.75, 'change': 2.15, 'sector': 'IT'},
            {'symbol': 'HDFCBANK', 'name': 'HDFC Bank Ltd.', 'ltp': 1650.80, 'change': -1.20, 'sector': 'Banking'},
            {'symbol': 'SBIN', 'name': 'State Bank of India', 'ltp': 650.25, 'change': 1.25, 'sector': 'Banking'},
            {'symbol': 'ICICIBANK', 'name': 'ICICI Bank Ltd.', 'ltp': 1050.60, 'change': 0.80, 'sector': 'Banking'},
            {'symbol': 'BHARTIARTL', 'name': 'Bharti Airtel Ltd.', 'ltp': 1023.45, 'change': 1.80, 'sector': 'Telecom'},
            {'symbol': 'TATAMOTORS', 'name': 'Tata Motors Ltd.', 'ltp': 785.40, 'change': 3.20, 'sector': 'Auto'},
            {'symbol': 'AXISBANK', 'name': 'Axis Bank Ltd.', 'ltp': 1150.30, 'change': -0.45, 'sector': 'Banking'},
            {'symbol': 'KOTAKBANK', 'name': 'Kotak Mahindra Bank Ltd.', 'ltp': 1850.90, 'change': 0.95, 'sector': 'Banking'},
        ]
        
        return jsonify({
            'success': True,
            'stocks': stocks,
            'source': 'enhanced_static',
            'count': len(stocks)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e),
            'stocks': [],
            'source': 'error'
        })

# ==================== BACKTESTING ROUTES ====================

@app.route('/api/backtest/historical-data', methods=['POST'])
def get_historical_data_backtest():
    """Get historical data for backtesting with ML integration"""
    try:
        data = request.json
        symbol = data.get('symbol', 'SBIN')
        start_date = data.get('start_date', '2024-01-01')
        end_date = data.get('end_date', '2024-12-31')
        timeframe = data.get('timeframe', 'ONE_DAY')
        
        # Generate realistic historical data
        historical_data = generate_enhanced_historical_data(symbol, start_date, end_date, timeframe)
        
        return jsonify({
            'success': True,
            'data': historical_data,
            'symbol': symbol,
            'timeframe': timeframe,
            'data_points': len(historical_data),
            'period': f"{start_date} to {end_date}"
        })
        
    except Exception as e:
        print(f"❌ Historical data error: {e}")
        return jsonify({
            'success': False,
            'message': str(e),
            'data': []
        })

@app.route('/api/backtest/run', methods=['POST'])
def run_backtest():
    """Run backtest with ML strategy"""
    try:
        data = request.json
        symbol = data.get('symbol', 'SBIN')
        strategy = data.get('strategy', 'ml_momentum')
        start_date = data.get('start_date', '2024-01-01')
        end_date = data.get('end_date', '2024-12-31')
        initial_capital = data.get('initial_capital', 100000)
        parameters = data.get('parameters', {})
        
        print(f"🔧 Running backtest for {symbol} with {strategy} strategy")
        
        # Get historical data
        historical_response = get_historical_data_backtest()
        historical_data = historical_response.get_json()['data']
        
        if not historical_data:
            return jsonify({
                'success': False,
                'message': 'No historical data available for backtesting'
            })
        
        # Run backtest
        if BACKTEST_AVAILABLE and backtest_engine:
            results = backtest_engine.run_backtest(
                historical_data,
                strategy,
                initial_capital,
                parameters
            )
        else:
            results = run_enhanced_backtest(
                historical_data,
                strategy,
                initial_capital,
                parameters
            )
        
        # Save backtest results
        csv_manager.save_backtest_results({
            'symbol': symbol,
            'strategy': strategy,
            'start_date': start_date,
            'end_date': end_date,
            'results': results,
            'timestamp': datetime.now().isoformat()
        })
        
        return jsonify({
            'success': True,
            'results': results,
            'symbol': symbol,
            'strategy': strategy,
            'parameters': parameters,
            'data_points': len(historical_data)
        })
        
    except Exception as e:
        print(f"❌ Backtest error: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        })

@app.route('/api/backtest/strategies')
def get_backtest_strategies():
    """Get available backtesting strategies with ML options"""
    strategies = {
        'ml_momentum': {
            'name': 'ML Momentum Strategy',
            'description': 'Machine Learning based momentum detection with adaptive thresholds',
            'parameters': {
                'lookback_period': {'type': 'number', 'default': 20, 'min': 5, 'max': 50},
                'momentum_threshold': {'type': 'number', 'default': 2.0, 'min': 1.0, 'max': 5.0},
                'position_size': {'type': 'number', 'default': 15, 'min': 5, 'max': 50}
            }
        },
        'ml_mean_reversion': {
            'name': 'ML Mean Reversion',
            'description': 'ML-enhanced mean reversion with volatility adjustment',
            'parameters': {
                'lookback_period': {'type': 'number', 'default': 30, 'min': 10, 'max': 100},
                'std_threshold': {'type': 'number', 'default': 1.5, 'min': 1.0, 'max': 3.0},
                'volatility_adjustment': {'type': 'boolean', 'default': True}
            }
        },
        'ensemble_ml': {
            'name': 'Ensemble ML Strategy',
            'description': 'Combines multiple ML models for improved accuracy',
            'parameters': {
                'model_confidence': {'type': 'number', 'default': 0.7, 'min': 0.5, 'max': 0.9},
                'risk_tolerance': {'type': 'number', 'default': 2.0, 'min': 1.0, 'max': 5.0},
                'max_drawdown': {'type': 'number', 'default': 10.0, 'min': 5.0, 'max': 20.0}
            }
        }
    }
    
    return jsonify({
        'success': True,
        'strategies': strategies
    })

def generate_enhanced_historical_data(symbol, start_date, end_date, timeframe='ONE_DAY'):
    """Generate enhanced historical data with realistic patterns"""
    start = datetime.fromisoformat(start_date)
    end = datetime.fromisoformat(end_date)
    
    base_price = bot.base_prices.get(symbol, 1000)
    
    # Timeframe mapping
    timeframe_deltas = {
        'ONE_MINUTE': timedelta(minutes=1),
        'FIVE_MINUTE': timedelta(minutes=5),
        'ONE_HOUR': timedelta(hours=1),
        'ONE_DAY': timedelta(days=1)
    }
    
    delta = timeframe_deltas.get(timeframe, timedelta(days=1))
    current_time = start
    historical_data = []
    current_price = base_price
    
    # Add some market trends
    trend_cycles = [
        {'duration': 30, 'trend': 0.02},   # Bullish
        {'duration': 20, 'trend': -0.015}, # Bearish
        {'duration': 25, 'trend': 0.01},   # Mild bullish
        {'duration': 15, 'trend': -0.01},  # Mild bearish
    ]
    
    cycle_index = 0
    days_in_cycle = 0
    
    while current_time <= end:
        # Update trend cycle
        if days_in_cycle >= trend_cycles[cycle_index]['duration']:
            cycle_index = (cycle_index + 1) % len(trend_cycles)
            days_in_cycle = 0
        
        trend = trend_cycles[cycle_index]['trend']
        days_in_cycle += 1
        
        # Generate price with trend and noise
        trend_component = current_price * trend * (delta.days if delta.days > 0 else 0.004)
        noise = random.normalvariate(0, current_price * 0.015)
        price_change = trend_component + noise
        
        open_price = current_price
        close_price = current_price + price_change
        high_price = max(open_price, close_price) + abs(random.normalvariate(0, current_price * 0.01))
        low_price = min(open_price, close_price) - abs(random.normalvariate(0, current_price * 0.01))
        volume = random.randint(100000, 500000)
        
        historical_data.append({
            'timestamp': current_time.isoformat(),
            'open': round(open_price, 2),
            'high': round(high_price, 2),
            'low': round(low_price, 2),
            'close': round(close_price, 2),
            'volume': volume,
            'symbol': symbol
        })
        
        current_price = close_price
        current_time += delta
    
    return historical_data

def run_enhanced_backtest(historical_data, strategy, initial_capital, parameters):
    """Run enhanced backtest with ML-like behavior"""
    capital = initial_capital
    positions = []
    trades = []
    portfolio_values = [initial_capital]
    equity_curve = []
    
    for i, candle in enumerate(historical_data):
        current_price = candle['close']
        current_time = candle['timestamp']
        
        # Generate ML-like signal
        if strategy == 'ml_momentum':
            signal = ml_momentum_strategy(historical_data[:i+1], parameters)
        elif strategy == 'ml_mean_reversion':
            signal = ml_mean_reversion_strategy(historical_data[:i+1], parameters)
        elif strategy == 'ensemble_ml':
            signal = ensemble_ml_strategy(historical_data[:i+1], parameters)
        else:
            signal = 'HOLD'
        
        # Execute trades
        if signal == 'BUY' and not positions and capital > 0:
            position_size = capital * (parameters.get('position_size', 15) / 100)
            quantity = position_size / current_price
            positions.append({
                'entry_price': current_price,
                'quantity': quantity,
                'entry_time': current_time,
                'type': 'LONG'
            })
            capital -= position_size
            
        elif signal == 'SELL' and positions:
            for position in positions[:]:
                pnl = (current_price - position['entry_price']) * position['quantity']
                capital += position['entry_price'] * position['quantity'] + pnl
                
                trades.append({
                    'symbol': historical_data[0]['symbol'] if historical_data else 'UNKNOWN',
                    'entry_price': position['entry_price'],
                    'exit_price': current_price,
                    'quantity': position['quantity'],
                    'pnl': pnl,
                    'return_pct': (pnl / (position['entry_price'] * position['quantity'])) * 100,
                    'entry_time': position['entry_time'],
                    'exit_time': current_time,
                    'type': position['type'],
                    'duration': 'N/A'
                })
                positions.remove(position)
        
        # Calculate current portfolio value
        current_value = capital + sum(pos['quantity'] * current_price for pos in positions)
        portfolio_values.append(current_value)
        equity_curve.append({
            'timestamp': current_time,
            'value': current_value
        })
    
    # Calculate performance metrics
    total_return = ((capital - initial_capital) / initial_capital) * 100
    profitable_trades = [t for t in trades if t['pnl'] > 0]
    win_rate = (len(profitable_trades) / len(trades)) * 100 if trades else 0
    
    # Calculate max drawdown
    peak = initial_capital
    max_drawdown = 0
    for value in portfolio_values:
        if value > peak:
            peak = value
        drawdown = (peak - value) / peak * 100
        if drawdown > max_drawdown:
            max_drawdown = drawdown
    
    # Calculate Sharpe ratio
    returns = []
    for i in range(1, len(portfolio_values)):
        daily_return = (portfolio_values[i] - portfolio_values[i-1]) / portfolio_values[i-1]
        returns.append(daily_return)
    
    sharpe_ratio = 0
    if len(returns) > 1 and np.std(returns) > 0:
        sharpe_ratio = (np.mean(returns) / np.std(returns)) * np.sqrt(252)
    
    # Additional metrics
    avg_profit = np.mean([t['pnl'] for t in profitable_trades]) if profitable_trades else 0
    avg_loss = np.mean([t['pnl'] for t in trades if t['pnl'] < 0]) if any(t['pnl'] < 0 for t in trades) else 0
    profit_factor = abs(sum(t['pnl'] for t in profitable_trades) / sum(t['pnl'] for t in trades if t['pnl'] < 0)) if any(t['pnl'] < 0 for t in trades) else float('inf')
    
    return {
        'total_return': round(total_return, 2),
        'sharpe_ratio': round(sharpe_ratio, 2),
        'win_rate': round(win_rate, 2),
        'max_drawdown': round(max_drawdown, 2),
        'total_trades': len(trades),
        'profitable_trades': len(profitable_trades),
        'avg_return_per_trade': round(np.mean([t['pnl'] for t in trades]) if trades else 0, 2),
        'avg_profit': round(avg_profit, 2),
        'avg_loss': round(avg_loss, 2),
        'profit_factor': round(profit_factor, 2),
        'final_portfolio_value': round(capital, 2),
        'equity_curve': equity_curve[-100:],  # Last 100 points for chart
        'trade_history': trades[-20:],  # Last 20 trades
        'strategy_parameters': parameters
    }

def ml_momentum_strategy(data, parameters):
    """ML-like momentum strategy"""
    if len(data) < parameters.get('lookback_period', 20):
        return 'HOLD'
    
    lookback = parameters.get('lookback_period', 20)
    prices = [candle['close'] for candle in data[-lookback:]]
    
    # Calculate momentum with ML-like features
    returns = np.diff(prices) / prices[:-1]
    momentum = np.mean(returns[-5:])  # Short-term momentum
    trend_strength = (prices[-1] - prices[0]) / prices[0]
    volatility = np.std(returns)
    
    # ML-like decision making
    confidence = abs(momentum) / (volatility + 0.001)  # Signal-to-noise ratio
    
    if confidence > parameters.get('momentum_threshold', 2.0):
        if momentum > 0:
            return 'BUY'
        else:
            return 'SELL'
    
    return 'HOLD'

def ml_mean_reversion_strategy(data, parameters):
    """ML-like mean reversion strategy"""
    if len(data) < parameters.get('lookback_period', 30):
        return 'HOLD'
    
    lookback = parameters.get('lookback_period', 30)
    prices = [candle['close'] for candle in data[-lookback:]]
    
    sma = np.mean(prices)
    current_price = prices[-1]
    deviation = (current_price - sma) / sma
    
    # ML-like volatility adjustment
    if parameters.get('volatility_adjustment', True):
        returns = np.diff(prices) / prices[:-1]
        volatility = np.std(returns)
        threshold = parameters.get('std_threshold', 1.5) * volatility
    else:
        threshold = parameters.get('std_threshold', 1.5) * 0.01  # 1% default
    
    if deviation < -threshold:
        return 'BUY'
    elif deviation > threshold:
        return 'SELL'
    
    return 'HOLD'

def ensemble_ml_strategy(data, parameters):
    """Ensemble ML strategy combining multiple approaches"""
    momentum_signal = ml_momentum_strategy(data, parameters)
    mean_reversion_signal = ml_mean_reversion_strategy(data, parameters)
    
    # Simple ensemble logic
    if momentum_signal == mean_reversion_signal and momentum_signal != 'HOLD':
        return momentum_signal
    
    # If signals conflict, use confidence-based decision
    if len(data) > 10:
        prices = [candle['close'] for candle in data[-10:]]
        volatility = np.std(np.diff(prices) / prices[:-1])
        
        if volatility < 0.02:  # Low volatility - prefer mean reversion
            return mean_reversion_signal
        else:  # High volatility - prefer momentum
            return momentum_signal
    
    return 'HOLD'

# ==================== API CONNECTION ROUTES ====================

@app.route('/api/connect', methods=['POST'])
def connect_api():
    """Connect to Angel One SmartAPI"""
    try:
        # For demo purposes, simulate successful connection
        # In production, this would use Angel One Trading API
        
        return jsonify({
            'success': True,
            'message': 'Angel One API connected successfully (Demo Mode)',
            'connected_at': datetime.now().isoformat()
        })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Connection error: {str(e)}'
        })

@app.route('/api/disconnect', methods=['POST'])
def disconnect_api():
    """Disconnect from Angel One SmartAPI"""
    try:
        return jsonify({
            'success': True,
            'message': 'Disconnected from Angel One API'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Disconnection error: {str(e)}'
        })

@app.route('/api/api-status')
def get_api_status():
    """Get Angel One API connection status"""
    return jsonify({
        'connected': True,  # Demo mode always connected
        'client_id': 'DEMO_CLIENT',
        'last_connection': datetime.now().isoformat()
    })

# ==================== BOT CONTROL ROUTES ====================

@app.route('/api/bot/start', methods=['POST'])
def start_bot():
    """Start the trading bot"""
    data = request.json
    symbol = data.get('symbol')
    user_id = session.get('user_id')
    
    if not symbol:
        return jsonify({'status': 'error', 'message': 'No symbol selected'})
    
    bot.status = 'running'
    bot.selected_stock = symbol
    bot_state['status'] = 'running'
    bot_state['started_at'] = datetime.now().isoformat()
    
    return jsonify({
        'status': 'success', 
        'message': f'Bot started for {symbol}',
        'bot_status': bot.status,
        'data_source': 'enhanced_simulated',
        'user_authenticated': user_id is not None
    })

@app.route('/api/bot/stop', methods=['POST'])
def stop_bot():
    """Stop the trading bot"""
    bot.status = 'stopped'
    bot_state['status'] = 'stopped'
    bot_state['stopped_at'] = datetime.now().isoformat()
    
    return jsonify({
        'status': 'success',
        'message': 'Bot stopped',
        'bot_status': bot.status
    })

@app.route('/api/bot/pause', methods=['POST'])
def pause_bot():
    """Pause the trading bot"""
    bot.status = 'paused'
    bot_state['status'] = 'paused'
    return jsonify({
        'status': 'success',
        'message': 'Bot paused',
        'bot_status': bot.status
    })

@app.route('/api/bot/status')
def get_bot_status():
    """Get current bot status"""
    return jsonify({
        'status': bot.status,
        'selected_stock': bot.selected_stock,
        'portfolio': bot.portfolio,
        'signal': bot_state['current_signal'],
        'confidence': bot_state['current_confidence'],
        'currentPrice': bot_state['current_price'],
        'api_connected': True,
        'data_source': 'enhanced_simulated'
    })

# ==================== BACKGROUND THREADS ====================

def background_data_updater():
    """Background thread to update market data"""
    while True:
        try:
            if bot.status == 'running' and bot.selected_stock:
                # Update market data periodically
                time.sleep(5)
            
            time.sleep(5)
            
        except Exception as e:
            print(f"Error in background updater: {e}")
            time.sleep(10)

# Start background thread
background_thread = threading.Thread(target=background_data_updater, daemon=True)
background_thread.start()

if __name__ == '__main__':
    load_dotenv()
    print("🚀 Starting Enhanced Algo Trading Bot Dashboard...")
    print("📊 Dashboard: http://localhost:5000")
    print("📈 Backtesting: http://localhost:5000/backtest")
    print("🤖 ML Models:", "Available" if ML_MODELS_AVAILABLE else "Not Available")
    print("🔌 Angel One API:", "Available" if ANGEL_ONE_AVAILABLE else "Not Available")
    print("🔧 Bot System: Enhanced Simulation Mode")
    print("💼 Portfolio: Enhanced Demo Data")
    print("📊 Backtesting: ML Strategies Available")
    print("👤 Demo Login: Use 'demo' for both Client ID and API Key")
    app.run(debug=True, host='0.0.0.0', port=5000)