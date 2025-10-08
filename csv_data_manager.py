# csv_data_manager.py
import pandas as pd
import os
import csv
from datetime import datetime
import json

class CSVDataManager:
    def __init__(self, data_folder="trading_data"):
        self.data_folder = data_folder
        self.data_dir = data_folder  # Add this for backtest compatibility
        self.setup_data_folder()
    
    def setup_data_folder(self):
        """Create data folder if it doesn't exist"""
        if not os.path.exists(self.data_folder):
            os.makedirs(self.data_folder)
            print(f"✅ Created data folder: {self.data_folder}")
    
    def save_trade(self, trade_data):
        """Save trade to CSV"""
        csv_file = f"{self.data_folder}/trades.csv"
        
        # Add timestamp if not present
        if 'timestamp' not in trade_data:
            trade_data['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Create DataFrame with the trade data
        df_new = pd.DataFrame([trade_data])
        
        # Append to existing CSV or create new
        if os.path.exists(csv_file):
            df_existing = pd.read_csv(csv_file)
            df_combined = pd.concat([df_existing, df_new], ignore_index=True)
        else:
            df_combined = df_new
        
        df_combined.to_csv(csv_file, index=False)
        print(f"💾 Trade saved to CSV: {trade_data['direction']} {trade_data.get('symbol', 'SBIN')}")
    
    def save_signal(self, signal_data):
        """Save signal to CSV"""
        csv_file = f"{self.data_folder}/signals.csv"
        
        # Add timestamp if not present
        if 'timestamp' not in signal_data:
            signal_data['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Create DataFrame with the signal data
        df_new = pd.DataFrame([signal_data])
        
        # Append to existing CSV or create new
        if os.path.exists(csv_file):
            df_existing = pd.read_csv(csv_file)
            df_combined = pd.concat([df_existing, df_new], ignore_index=True)
        else:
            df_combined = df_new
        
        df_combined.to_csv(csv_file, index=False)
        print(f"📊 Signal saved to CSV: {signal_data['signal_type']}")
    
    def get_trade_history(self, limit=10):
        """Get recent trade history from CSV"""
        csv_file = f"{self.data_folder}/trades.csv"
        
        if not os.path.exists(csv_file):
            return []
        
        df = pd.read_csv(csv_file)
        # Sort by timestamp and get latest
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df.sort_values('timestamp', ascending=False)
        
        return df.head(limit).to_dict('records')
    
    def get_signals_history(self, limit=10):
        """Get recent signals history from CSV"""
        csv_file = f"{self.data_folder}/signals.csv"
        
        if not os.path.exists(csv_file):
            return []
        
        df = pd.read_csv(csv_file)
        # Sort by timestamp and get latest
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df.sort_values('timestamp', ascending=False)
        
        return df.head(limit).to_dict('records')
    
    def get_portfolio_stats(self):
        """Get portfolio statistics from CSV"""
        trades_file = f"{self.data_folder}/trades.csv"
        
        if not os.path.exists(trades_file):
            return {
                'open_positions': 0,
                'total_pnl': 0,
                'win_rate': 0,
                'total_trades': 0
            }
        
        df = pd.read_csv(trades_file)
        
        # Calculate stats
        open_positions = len(df[df['status'] == 'open']) if 'status' in df.columns else 0
        
        if 'pnl' in df.columns:
            total_pnl = df['pnl'].sum()
            winning_trades = len(df[df['pnl'] > 0])
        else:
            total_pnl = 0
            winning_trades = 0
        
        total_trades = len(df)
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        
        return {
            'open_positions': int(open_positions),
            'total_pnl': float(total_pnl),
            'win_rate': round(win_rate, 2),
            'total_trades': int(total_trades)
        }

    def save_backtest_results(self, backtest_data):
        """Save backtest results to CSV"""
        try:
            filename = 'backtest_results.csv'
            filepath = os.path.join(self.data_folder, filename)
            
            # Prepare data for CSV
            data_to_save = {
                'timestamp': backtest_data.get('timestamp', datetime.now().isoformat()),
                'symbol': backtest_data.get('symbol', 'UNKNOWN'),
                'strategy': backtest_data.get('strategy', 'unknown'),
                'start_date': backtest_data.get('start_date', ''),
                'end_date': backtest_data.get('end_date', ''),
                'total_return': backtest_data.get('results', {}).get('total_return', 0),
                'sharpe_ratio': backtest_data.get('results', {}).get('sharpe_ratio', 0),
                'win_rate': backtest_data.get('results', {}).get('win_rate', 0),
                'max_drawdown': backtest_data.get('results', {}).get('max_drawdown', 0),
                'total_trades': backtest_data.get('results', {}).get('total_trades', 0)
            }
            
            # Check if file exists to write header
            file_exists = os.path.isfile(filepath)
            
            with open(filepath, 'a', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=data_to_save.keys())
                if not file_exists:
                    writer.writeheader()
                writer.writerow(data_to_save)
                
            print(f"✅ Backtest results saved for {backtest_data.get('symbol', 'UNKNOWN')}")
            
        except Exception as e:
            print(f"❌ Error saving backtest results: {e}")
    
    def update_trade_pnl(self, trade_id, pnl, exit_price=None, status='closed'):
        """Update trade PNL in CSV"""
        csv_file = f"{self.data_folder}/trades.csv"
        
        if not os.path.exists(csv_file):
            print("❌ No trades CSV file found")
            return
        
        df = pd.read_csv(csv_file)
        
        # Update the specific trade
        if 'id' in df.columns and trade_id in df['id'].values:
            df.loc[df['id'] == trade_id, 'pnl'] = pnl
            df.loc[df['id'] == trade_id, 'status'] = status
            if exit_price:
                df.loc[df['id'] == trade_id, 'exit_price'] = exit_price
            
            df.to_csv(csv_file, index=False)
            print(f"📊 Trade {trade_id} updated in CSV: PNL = {pnl}")
        else:
            print(f"❌ Trade ID {trade_id} not found in CSV")
    
    def save_market_data(self, market_data):
        """Save market data snapshot to CSV"""
        csv_file = f"{self.data_folder}/market_data.csv"
        
        # Add timestamp
        market_data['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        df_new = pd.DataFrame([market_data])
        
        if os.path.exists(csv_file):
            df_existing = pd.read_csv(csv_file)
            df_combined = pd.concat([df_existing, df_new], ignore_index=True)
        else:
            df_combined = df_new
        
        df_combined.to_csv(csv_file, index=False)

    def get_backtest_history(self, limit=10):
        """Get recent backtest results"""
        csv_file = f"{self.data_folder}/backtest_results.csv"
        
        if not os.path.exists(csv_file):
            return []
        
        df = pd.read_csv(csv_file)
        # Sort by timestamp and get latest
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df.sort_values('timestamp', ascending=False)
        
        return df.head(limit).to_dict('records')

# Global CSV data manager instance
csv_manager = CSVDataManager()