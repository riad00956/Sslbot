import os
from typing import Dict, List, Tuple

class Config:
    # Bot টোকেন
    BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
    
    # এডমিন আইডি (আপনার Telegram User ID)
    ADMIN_IDS = [123456789, 987654321]  # আপনার ID দিন
    
    # ডাটাবেস পাথ
    DB_PATH = "smm_panel.db"
    
    # পেমেন্ট সেটিংস
    PAYMENT_METHODS = {
        "bkash": "01xxxxxxxxx",
        "nagad": "01xxxxxxxxx",
        "rocket": "01xxxxxxxxx"
    }
    
    # সার্ভিস প্রাইস (পার 1000)
    SERVICES = {
        "instagram": {
            "followers": {"price": 100, "min": 100, "max": 10000},
            "likes": {"price": 50, "min": 50, "max": 5000},
            "views": {"price": 30, "min": 1000, "max": 100000}
        },
        "facebook": {
            "likes": {"price": 80, "min": 100, "max": 5000},
            "followers": {"price": 120, "min": 100, "max": 10000}
        },
        "youtube": {
            "views": {"price": 40, "min": 1000, "max": 50000},
            "subscribers": {"price": 200, "min": 100, "max": 5000}
        }
    }
    
    # বট সেটিংস
    WELCOME_MESSAGE = """
✨ **Welcome to Premium SMM Panel** ✨

📊 **Your Account Info:**
├─ Balance: ₹{balance}
├─ Total Orders: {orders}
└─ Member Since: {join_date}

💎 **Features:**
• Instant Services
• 24/7 Support
• Best Prices
• Refill Guarantee

👇 **Choose an option below:**
"""
    
    # কিবোর্ড লেআউট
    MAIN_KEYBOARD = [
        ["🛒 Order Services", "💰 My Wallet"],
        ["📊 My Orders", "👥 Referral"],
        ["📞 Support", "⚙️ Settings"]
    ]
    
    ADMIN_KEYBOARD = [
        ["📈 Dashboard", "👥 Users", "📊 Orders"],
        ["💰 Payments", "⚙️ Services", "📢 Broadcast"],
        ["📊 Stats", "🔙 Back to User"]
    ]
