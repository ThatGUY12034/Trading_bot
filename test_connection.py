# test_connection.py
from SmartApi import SmartConnect
import pyotp
from config import SmartAPIConfig

def test_smartapi_connection():
    print("🧪 Testing SmartAPI Connection...")
    
    try:
        # Initialize SmartAPI
        api = SmartConnect(api_key=SmartAPIConfig.API_KEY)
        print(f"🔑 API Key: {SmartAPIConfig.API_KEY[:10]}...")
        
        # Generate TOTP
        totp = pyotp.TOTP(SmartAPIConfig.TOTP).now()
        print(f"🔑 Generated TOTP: {totp}")
        print(f"👤 Client ID: {SmartAPIConfig.CLIENT_ID}")
        
        # Login
        print("🔄 Attempting login...")
        login_data = api.generateSession(
            SmartAPIConfig.CLIENT_ID, 
            SmartAPIConfig.PIN, 
            totp
        )
        
        if login_data['status']:
            print("✅ LOGIN SUCCESSFUL!")
            print(f"📊 Token: {login_data['data']['jwtToken'][:50]}...")
            print(f"👤 Client ID: {login_data['data']['clientID']}")
            
            # Test profile data
            profile = api.getProfile()
            print(f"👤 Profile Name: {profile['data']['name']}")
            
            # Test market data - SBIN
            print("📈 Testing market data...")
            quote = api.ltpData(
                exchange="NSE", 
                tradingymbol="SBIN-EQ", 
                symboltoken="3045"
            )
            print(f"💰 SBIN Current Price: ₹{quote['data']['ltp']}")
            
            return True
        else:
            print(f"❌ LOGIN FAILED: {login_data['message']}")
            return False
            
    except Exception as e:
        print(f"💥 CONNECTION ERROR: {e}")
        return False

if __name__ == "__main__":
    success = test_smartapi_connection()
    if success:
        print("\n🎉 CONNECTION TEST PASSED! Your bot is ready.")
    else:
        print("\n❌ CONNECTION TEST FAILED! Check your credentials.")