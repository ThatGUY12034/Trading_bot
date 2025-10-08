import requests
import json
import websocket
import threading
import time
from datetime import datetime
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class MarketFeedsAPI:
    def __init__(self, api_key: str, base_url: str):
        self.api_key = api_key
        self.base_url = base_url
        self.ws_url = "wss://your-market-feeds-websocket-url"  # Replace with your WebSocket URL
        self.ws_connection = None
        self.is_connected = False
        self.subscribed_symbols = set()
        self.price_callbacks = []
        
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
    
    def connect_websocket(self):
        """Connect to WebSocket for real-time data"""
        try:
            self.ws_connection = websocket.WebSocketApp(
                self.ws_url,
                on_open=self._on_websocket_open,
                on_message=self._on_websocket_message,
                on_error=self._on_websocket_error,
                on_close=self._on_websocket_close
            )
            
            # Start WebSocket in a separate thread
            ws_thread = threading.Thread(target=self.ws_connection.run_forever)
            ws_thread.daemon = True
            ws_thread.start()
            
            logger.info("WebSocket connection started")
            
        except Exception as e:
            logger.error(f"Failed to start WebSocket: {e}")
    
    def _on_websocket_open(self, ws):
        """Handle WebSocket connection open"""
        self.is_connected = True
        logger.info("✅ WebSocket connected to market feeds")
        
        # Resubscribe to previously subscribed symbols
        for symbol in self.subscribed_symbols:
            self.subscribe_realtime(symbol)
    
    def _on_websocket_message(self, ws, message):
        """Handle incoming WebSocket messages"""
        try:
            data = json.loads(message)
            
            # Process different message types based on your API structure
            if data.get('type') == 'price_update':
                symbol = data.get('symbol')
                price_data = {
                    'symbol': symbol,
                    'price': data.get('price'),
                    'change': data.get('change'),
                    'change_percent': data.get('change_percent'),
                    'volume': data.get('volume'),
                    'timestamp': datetime.now().isoformat(),
                    'source': 'market_feeds_websocket'
                }
                
                # Notify all callbacks
                self.notify_price_update(symbol, price_data)
                
        except Exception as e:
            logger.error(f"Error processing WebSocket message: {e}")
    
    def _on_websocket_error(self, ws, error):
        """Handle WebSocket errors"""
        logger.error(f"WebSocket error: {error}")
        self.is_connected = False
    
    def _on_websocket_close(self, ws, close_status_code, close_msg):
        """Handle WebSocket connection close"""
        logger.info("WebSocket connection closed")
        self.is_connected = False
    
    def subscribe_realtime(self, symbol: str):
        """Subscribe to real-time updates for a symbol"""
        try:
            if self.is_connected and self.ws_connection:
                subscribe_message = {
                    'action': 'subscribe',
                    'symbol': symbol,
                    'api_key': self.api_key
                }
                self.ws_connection.send(json.dumps(subscribe_message))
                self.subscribed_symbols.add(symbol)
                logger.info(f"Subscribed to real-time data for {symbol}")
            else:
                logger.warning("WebSocket not connected, cannot subscribe")
        except Exception as e:
            logger.error(f"Error subscribing to {symbol}: {e}")
    
    def unsubscribe_realtime(self, symbol: str):
        """Unsubscribe from real-time updates for a symbol"""
        try:
            if self.is_connected and self.ws_connection:
                unsubscribe_message = {
                    'action': 'unsubscribe',
                    'symbol': symbol,
                    'api_key': self.api_key
                }
                self.ws_connection.send(json.dumps(unsubscribe_message))
                self.subscribed_symbols.discard(symbol)
                logger.info(f"Unsubscribed from real-time data for {symbol}")
        except Exception as e:
            logger.error(f"Error unsubscribing from {symbol}: {e}")
    
    def get_live_quote(self, symbol: str) -> Optional[Dict]:
        """Get live quote via REST API"""
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            # Adjust endpoint based on your API
            endpoint = f"{self.base_url}/quotes/{symbol}"
            response = requests.get(endpoint, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Map response to standardized format
                return {
                    'symbol': symbol,
                    'price': data.get('last_price'),
                    'change': data.get('change'),
                    'change_percent': data.get('change_percent'),
                    'volume': data.get('volume'),
                    'day_high': data.get('high_price'),
                    'day_low': data.get('low_price'),
                    'prev_close': data.get('previous_close'),
                    'timestamp': datetime.now().isoformat(),
                    'source': 'market_feeds_rest'
                }
            else:
                logger.error(f"API error: {response.status_code} - {response.text}")
                
        except Exception as e:
            logger.error(f"Error fetching live quote for {symbol}: {e}")
        
        return None
    
    def get_historical_data(self, symbol: str, interval: str = '1h', days: int = 30) -> Optional[Dict]:
        """Get historical data via REST API"""
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            # Adjust endpoint and parameters based on your API
            endpoint = f"{self.base_url}/historical/{symbol}"
            params = {
                'interval': interval,
                'days': days
            }
            
            response = requests.get(endpoint, headers=headers, params=params, timeout=15)
            
            if response.status_code == 200:
                return response.json()  # Return raw data for processing
            else:
                logger.error(f"Historical data API error: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Error fetching historical data for {symbol}: {e}")
        
        return None