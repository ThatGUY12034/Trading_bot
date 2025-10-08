import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import yfinance as yf

def fetch_historical_data(symbol="99926009", exchange="NSE", interval="ONE_HOUR", periods=30):
    """
    Fetch historical market data for the ML model
    Replace this with your actual data source API
    """
    try:
        print(f"📈 Fetching historical data for {symbol}...")
        
        # Generate realistic simulated data that matches your ML model's expectations
        end_date = datetime.now()
        
        if interval == "ONE_HOUR":
            start_date = end_date - timedelta(days=periods)
            dates = pd.date_range(start=start_date, end=end_date, freq='1H')
        else:
            start_date = end_date - timedelta(days=periods)
            dates = pd.date_range(start=start_date, end=end_date, freq='1D')
        
        # Generate realistic price data with some trends
        np.random.seed(42)
        base_price = 50000
        
        # Create some market trends
        trend = np.cumsum(np.random.normal(0.0005, 0.01, len(dates)))  # Small upward bias
        noise = np.random.normal(0, 0.005, len(dates))
        
        prices = [base_price]
        for i in range(1, len(dates)):
            price_change = trend[i] + noise[i]
            new_price = prices[-1] * (1 + price_change)
            prices.append(new_price)
        
        # Create OHLC data with realistic relationships
        df = pd.DataFrame({
            'datetime': dates,
            'open': [price * (1 + np.random.normal(0, 0.002)) for price in prices],
            'high': [price * (1 + abs(np.random.normal(0.01, 0.005))) for price in prices],
            'low': [price * (1 - abs(np.random.normal(0.01, 0.005))) for price in prices],
            'close': prices,
            'volume': [abs(np.random.normal(1000, 300)) for _ in prices]
        })
        
        # Ensure high > low and high > open, close
        df['high'] = df[['high', 'open', 'close']].max(axis=1) * 1.001
        df['low'] = df[['low', 'open', 'close']].min(axis=1) * 0.999
        
        print(f"✅ Generated {len(df)} records of historical data")
        return df
        
    except Exception as e:
        print(f"❌ Error in fetch_historical_data: {e}")
        
        # Fallback: Try to get real data from yfinance
        try:
            print("🔄 Trying fallback data from yfinance...")
            # Use a popular symbol as fallback
            ticker = "AAPL"
            stock = yf.Ticker(ticker)
            
            if interval == "ONE_HOUR":
                hist = stock.history(period="1mo", interval="1h")
            else:
                hist = stock.history(period="3mo", interval="1d")
            
            if not hist.empty:
                hist = hist.reset_index()
                hist = hist.rename(columns={
                    'Date': 'datetime',
                    'Open': 'open', 
                    'High': 'high',
                    'Low': 'low',
                    'Close': 'close',
                    'Volume': 'volume'
                })
                print(f"✅ Fetched {len(hist)} records from yfinance fallback")
                return hist
        except Exception as yf_error:
            print(f"❌ Fallback data also failed: {yf_error}")
        
        return None

def calculate_technical_indicators(df):
    """
    Calculate additional technical indicators for the ML model
    """
    try:
        # Simple Moving Averages
        df['sma_20'] = df['close'].rolling(window=20).mean()
        df['sma_50'] = df['close'].rolling(window=50).mean()
        
        # RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        # MACD
        exp1 = df['close'].ewm(span=12).mean()
        exp2 = df['close'].ewm(span=26).mean()
        df['macd'] = exp1 - exp2
        df['macd_signal'] = df['macd'].ewm(span=9).mean()
        
        # Bollinger Bands
        df['bb_middle'] = df['close'].rolling(window=20).mean()
        bb_std = df['close'].rolling(window=20).std()
        df['bb_upper'] = df['bb_middle'] + (bb_std * 2)
        df['bb_lower'] = df['bb_middle'] - (bb_std * 2)
        
        # Volume indicators
        df['volume_sma'] = df['volume'].rolling(window=20).mean()
        df['volume_ratio'] = df['volume'] / df['volume_sma']
        
        return df
        
    except Exception as e:
        print(f"❌ Error calculating technical indicators: {e}")
        return df

# Test function
if __name__ == "__main__":
    test_data = fetch_historical_data()
    if test_data is not None:
        print(f"Data columns: {test_data.columns.tolist()}")
        print(f"Data shape: {test_data.shape}")
        print(f"Date range: {test_data['datetime'].min()} to {test_data['datetime'].max()}")
        print(f"Sample data:\n{test_data.head()}")