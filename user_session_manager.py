# user_session_manager.py
import threading
import time
from datetime import datetime, timedelta
from angel_one_client import AngelOneClient

class UserSessionManager:
    def __init__(self):
        self.active_sessions = {}
        self.session_lock = threading.Lock()
        
    def create_user_session(self, user_id, client_id, api_key, client_pin, totp_secret):
        """Create a new user session with Angel One connection"""
        try:
            # Create Angel One client for this user
            user_client = AngelOneClient()
            
            # Set user credentials
            user_client.set_credentials(client_id, api_key, client_pin, totp_secret)
            
            # Connect to Angel One
            connection_success = user_client.connect()
            
            if connection_success:
                session_data = {
                    'user_id': user_id,
                    'client_id': client_id,
                    'angel_client': user_client,
                    'created_at': datetime.now(),
                    'last_activity': datetime.now(),
                    'is_active': True,
                    'portfolio_value': 0,
                    'open_positions': []
                }
                
                with self.session_lock:
                    self.active_sessions[user_id] = session_data
                
                print(f"✅ User session created for {user_id}")
                return True, "Login successful", user_client
            else:
                return False, "Angel One connection failed", None
                
        except Exception as e:
            print(f"❌ Session creation error: {e}")
            return False, f"Login failed: {str(e)}", None
    
    def get_user_session(self, user_id):
        """Get user session data"""
        with self.session_lock:
            session = self.active_sessions.get(user_id)
            if session and session['is_active']:
                # Update last activity
                session['last_activity'] = datetime.now()
                return session
            return None
    
    def update_user_portfolio(self, user_id, portfolio_data):
        """Update user portfolio information"""
        with self.session_lock:
            if user_id in self.active_sessions:
                self.active_sessions[user_id]['portfolio_value'] = portfolio_data.get('total_value', 0)
                self.active_sessions[user_id]['open_positions'] = portfolio_data.get('positions', [])
    
    def logout_user(self, user_id):
        """Logout user and cleanup"""
        with self.session_lock:
            if user_id in self.active_sessions:
                try:
                    # Logout from Angel One
                    self.active_sessions[user_id]['angel_client'].logout()
                    self.active_sessions[user_id]['is_active'] = False
                    del self.active_sessions[user_id]
                    print(f"✅ User {user_id} logged out")
                except Exception as e:
                    print(f"❌ Logout error: {e}")
                return True
        return False
    
    def cleanup_expired_sessions(self):
        """Clean up expired sessions"""
        current_time = datetime.now()
        expired_users = []
        
        with self.session_lock:
            for user_id, session in self.active_sessions.items():
                if (current_time - session['last_activity']).total_seconds() > 3600:  # 1 hour
                    expired_users.append(user_id)
            
            for user_id in expired_users:
                self.logout_user(user_id)
        
        if expired_users:
            print(f"🧹 Cleaned up {len(expired_users)} expired sessions")
    
    def get_active_users_count(self):
        """Get count of active users"""
        with self.session_lock:
            return len([s for s in self.active_sessions.values() if s['is_active']])

# Global session manager
user_session_manager = UserSessionManager()