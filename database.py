import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from config import Config

class Database:
    def __init__(self):
        self.conn = sqlite3.connect(Config.DB_PATH, check_same_thread=False)
        self.create_tables()
    
    def create_tables(self):
        cursor = self.conn.cursor()
        
        # Users টেবিল
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                balance REAL DEFAULT 0,
                total_orders INTEGER DEFAULT 0,
                total_spent REAL DEFAULT 0,
                join_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                referral_code TEXT UNIQUE,
                referred_by INTEGER,
                is_banned INTEGER DEFAULT 0
            )
        ''')
        
        # Orders টেবিল
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                order_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                service_type TEXT,
                service_name TEXT,
                link TEXT,
                quantity INTEGER,
                price REAL,
                status TEXT DEFAULT 'pending',
                admin_approved INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        # Payments টেবিল
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS payments (
                payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                amount REAL,
                method TEXT,
                transaction_id TEXT,
                screenshot TEXT,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                approved_at TIMESTAMP,
                approved_by INTEGER,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        # Services টেবিল
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS services (
                service_id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT,
                name TEXT,
                description TEXT,
                price_per_1000 REAL,
                min_quantity INTEGER,
                max_quantity INTEGER,
                is_active INTEGER DEFAULT 1
            )
        ''')
        
        # Referrals টেবিল
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS referrals (
                referral_id INTEGER PRIMARY KEY AUTOINCREMENT,
                referrer_id INTEGER,
                referred_id INTEGER,
                bonus_given INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (referrer_id) REFERENCES users (user_id),
                FOREIGN KEY (referred_id) REFERENCES users (user_id)
            )
        ''')
        
        self.conn.commit()
    
    # User CRUD অপারেশন
    def get_user(self, user_id: int) -> Optional[Dict]:
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        row = cursor.fetchone()
        if row:
            columns = [description[0] for description in cursor.description]
            return dict(zip(columns, row))
        return None
    
    def create_user(self, user_id: int, username: str, first_name: str):
        referral_code = f"REF{user_id}{datetime.now().strftime('%H%M%S')}"
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT OR IGNORE INTO users (user_id, username, first_name, referral_code)
            VALUES (?, ?, ?, ?)
        ''', (user_id, username, first_name, referral_code))
        self.conn.commit()
    
    def update_balance(self, user_id: int, amount: float):
        cursor = self.conn.cursor()
        cursor.execute('UPDATE users SET balance = balance + ? WHERE user_id = ?', (amount, user_id))
        self.conn.commit()
    
    # Order মেথডস
    def create_order(self, user_id: int, service_type: str, service_name: str, 
                    link: str, quantity: int, price: float) -> int:
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO orders (user_id, service_type, service_name, link, quantity, price)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, service_type, service_name, link, quantity, price))
        order_id = cursor.lastrowid
        
        # Update user stats
        cursor.execute('''
            UPDATE users 
            SET total_orders = total_orders + 1, 
                total_spent = total_spent + ?
            WHERE user_id = ?
        ''', (price, user_id))
        
        self.conn.commit()
        return order_id
    
    def get_user_orders(self, user_id: int, limit: int = 10) -> List[Dict]:
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM orders 
            WHERE user_id = ? 
            ORDER BY created_at DESC 
            LIMIT ?
        ''', (user_id, limit))
        rows = cursor.fetchall()
        columns = [description[0] for description in cursor.description]
        return [dict(zip(columns, row)) for row in rows]
    
    # Payment মেথডস
    def create_payment(self, user_id: int, amount: float, method: str, 
                      transaction_id: str, screenshot: str = None) -> int:
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO payments (user_id, amount, method, transaction_id, screenshot)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, amount, method, transaction_id, screenshot))
        payment_id = cursor.lastrowid
        self.conn.commit()
        return payment_id
    
    def get_pending_payments(self) -> List[Dict]:
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM payments WHERE status = "pending"')
        rows = cursor.fetchall()
        columns = [description[0] for description in cursor.description]
        return [dict(zip(columns, row)) for row in rows]
    
    # Admin মেথডস
    def get_all_users(self) -> List[Dict]:
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM users ORDER BY join_date DESC')
        rows = cursor.fetchall()
        columns = [description[0] for description in cursor.description]
        return [dict(zip(columns, row)) for row in rows]
    
    def get_all_orders(self, status: str = None) -> List[Dict]:
        cursor = self.conn.cursor()
        if status:
            cursor.execute('SELECT * FROM orders WHERE status = ? ORDER BY created_at DESC', (status,))
        else:
            cursor.execute('SELECT * FROM orders ORDER BY created_at DESC')
        rows = cursor.fetchall()
        columns = [description[0] for description in cursor.description]
        return [dict(zip(columns, row)) for row in rows]
    
    def get_stats(self) -> Dict:
        cursor = self.conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM users')
        total_users = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM orders')
        total_orders = cursor.fetchone()[0]
        
        cursor.execute('SELECT SUM(price) FROM orders WHERE status = "completed"')
        total_revenue = cursor.fetchone()[0] or 0
        
        cursor.execute('SELECT SUM(balance) FROM users')
        total_balance = cursor.fetchone()[0] or 0
        
        return {
            "total_users": total_users,
            "total_orders": total_orders,
            "total_revenue": total_revenue,
            "total_balance": total_balance
  }
