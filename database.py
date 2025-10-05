import sqlite3
import os
from datetime import datetime
from typing import Dict, List, Optional
import threading

class DatabaseManager:
    def __init__(self, db_path: str = "wallet.db"):
        self.db_path = db_path
        self.lock = threading.Lock()
        self.init_database()
    
    def init_database(self):
        """Initialize database tables"""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Wallets table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS wallets (
                    address TEXT PRIMARY KEY,
                    balance REAL NOT NULL,
                    created_at TEXT NOT NULL
                )
            ''')
            
            # Transactions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    from_address TEXT NOT NULL,
                    to_address TEXT NOT NULL,
                    amount REAL NOT NULL,
                    usd_amount REAL,
                    timestamp TEXT NOT NULL,
                    FOREIGN KEY (from_address) REFERENCES wallets (address),
                    FOREIGN KEY (to_address) REFERENCES wallets (address)
                )
            ''')
            
            conn.commit()
            conn.close()
    
    def create_wallet(self, address: str, initial_balance: float):
        """Create a new wallet"""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            timestamp = datetime.now().isoformat()
            cursor.execute('''
                INSERT OR REPLACE INTO wallets (address, balance, created_at)
                VALUES (?, ?, ?)
            ''', (address, initial_balance, timestamp))
            
            conn.commit()
            conn.close()
    
    def get_wallet(self, address: str) -> Optional[Dict]:
        """Get wallet by address"""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT address, balance, created_at FROM wallets WHERE address = ?
            ''', (address,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return {
                    'address': row[0],
                    'balance': row[1],
                    'created_at': row[2]
                }
            return None
    
    def update_balance(self, address: str, new_balance: float):
        """Update wallet balance"""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE wallets SET balance = ? WHERE address = ?
            ''', (new_balance, address))
            
            conn.commit()
            conn.close()
    
    def transfer_balance(self, from_address: str, to_address: str, amount: float):
        """Transfer balance between wallets"""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            try:
                # Start transaction
                cursor.execute('BEGIN TRANSACTION')
                
                # Get sender balance
                cursor.execute('SELECT balance FROM wallets WHERE address = ?', (from_address,))
                sender_row = cursor.fetchone()
                if not sender_row:
                    raise ValueError("Sender wallet not found")
                
                sender_balance = sender_row[0]
                if sender_balance < amount:
                    raise ValueError("Insufficient balance")
                
                # Get or create recipient wallet
                cursor.execute('SELECT balance FROM wallets WHERE address = ?', (to_address,))
                recipient_row = cursor.fetchone()
                
                if recipient_row:
                    recipient_balance = recipient_row[0]
                else:
                    # Create recipient wallet with 0 balance
                    timestamp = datetime.now().isoformat()
                    cursor.execute('''
                        INSERT INTO wallets (address, balance, created_at)
                        VALUES (?, ?, ?)
                    ''', (to_address, 0.0, timestamp))
                    recipient_balance = 0.0
                
                # Update balances
                new_sender_balance = sender_balance - amount
                new_recipient_balance = recipient_balance + amount
                
                cursor.execute('UPDATE wallets SET balance = ? WHERE address = ?', 
                             (new_sender_balance, from_address))
                cursor.execute('UPDATE wallets SET balance = ? WHERE address = ?', 
                             (new_recipient_balance, to_address))
                
                # Commit transaction
                cursor.execute('COMMIT')
                
            except Exception as e:
                cursor.execute('ROLLBACK')
                raise e
            finally:
                conn.close()
    
    def add_transaction(self, from_address: str, to_address: str, 
                       amount: float, usd_amount: Optional[float] = None):
        """Add transaction record"""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            timestamp = datetime.now().isoformat()
            cursor.execute('''
                INSERT INTO transactions (from_address, to_address, amount, usd_amount, timestamp)
                VALUES (?, ?, ?, ?, ?)
            ''', (from_address, to_address, amount, usd_amount, timestamp))
            
            conn.commit()
            conn.close()
    
    def get_transactions(self, address: str) -> List[Dict]:
        """Get transaction history for an address"""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT from_address, to_address, amount, usd_amount, timestamp
                FROM transactions
                WHERE from_address = ? OR to_address = ?
                ORDER BY timestamp DESC
                LIMIT 50
            ''', (address, address))
            
            rows = cursor.fetchall()
            conn.close()
            
            transactions = []
            for row in rows:
                transactions.append({
                    'from_address': row[0],
                    'to_address': row[1],
                    'amount': row[2],
                    'usd_amount': row[3],
                    'timestamp': row[4]
                })
            
            return transactions
