# config.py - Minimal version
import os
from dotenv import load_dotenv

load_dotenv()

class SmartAPIConfig:
    API_KEY = os.getenv('ANGEL_ONE_API_KEY', '')
    CLIENT_ID = os.getenv('ANGEL_ONE_CLIENT_ID', '')
    PASSWORD = os.getenv('ANGEL_ONE_PASSWORD', '')
    TOTP_KEY = os.getenv('ANGEL_ONE_TOTP_KEY', '')
    EXCHANGE = "NSE"
    
    SYMBOL_TOKENS = {
        'SBIN': '3045',
        'RELIANCE': '2885', 
        'INFY': '1594',
        'TCS': '2951',
        'HDFCBANK': '1330',
        'ICICIBANK': '4963',
        'TATAMOTORS': '3456',
        'BHARTIARTL': '10604'
    }

# Create the .env file if it doesn't exist
env_path = os.path.join(os.path.dirname(__file__), '.env')
if not os.path.exists(env_path):
    with open(env_path, 'w') as f:
        f.write("""# Angel One API Credentials
ANGEL_ONE_API_KEY=
ANGEL_ONE_CLIENT_ID=
ANGEL_ONE_PASSWORD=
ANGEL_ONE_TOTP_KEY=
""")
    print("📁 Created .env file. Please add your Angel One credentials.")