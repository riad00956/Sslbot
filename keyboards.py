from typing import List, Dict, Any
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from config import Config

class KeyboardGenerator:
    @staticmethod
    def get_main_keyboard() -> ReplyKeyboardMarkup:
        """মূল মেনু কিবোর্ড"""
        keyboard = [
            [KeyboardButton("🛒 Order Services"), KeyboardButton("💰 My Wallet")],
            [KeyboardButton("📊 My Orders"), KeyboardButton("👥 Referral")],
            [KeyboardButton("📞 Support"), KeyboardButton("⚙️ Settings")]
        ]
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)
    
    @staticmethod
    def get_admin_keyboard() -> ReplyKeyboardMarkup:
        """এডমিন কিবোর্ড"""
        keyboard = [
            [KeyboardButton("📈 Dashboard"), KeyboardButton("👥 Users")],
            [KeyboardButton("📊 Orders"), KeyboardButton("💰 Payments")],
            [KeyboardButton("⚙️ Services"), KeyboardButton("📢 Broadcast")],
            [KeyboardButton("🔙 Back to User")]
        ]
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)
    
    @staticmethod
    def get_service_categories() -> InlineKeyboardMarkup:
        """সার্ভিস ক্যাটেগরি ইনলাইন কিবোর্ড"""
        keyboard = [
            [
                InlineKeyboardButton("📷 Instagram", callback_data="category_instagram"),
                InlineKeyboardButton("👤 Facebook", callback_data="category_facebook")
            ],
            [
                InlineKeyboardButton("🎬 YouTube", callback_data="category_youtube"),
                InlineKeyboardButton("🎵 TikTok", callback_data="category_tiktok")
            ],
            [
                InlineKeyboardButton("🐦 Twitter", callback_data="category_twitter"),
                InlineKeyboardButton("💼 LinkedIn", callback_data="category_linkedin")
            ],
            [InlineKeyboardButton("🔙 Back", callback_data="back_main")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_instagram_services() -> InlineKeyboardMarkup:
        """ইনস্টাগ্রাম সার্ভিসেস"""
        keyboard = [
            [
                InlineKeyboardButton("👥 Followers", callback_data="service_instagram_followers"),
                InlineKeyboardButton("❤️ Likes", callback_data="service_instagram_likes")
            ],
            [
                InlineKeyboardButton("👀 Views", callback_data="service_instagram_views"),
                InlineKeyboardButton("💬 Comments", callback_data="service_instagram_comments")
            ],
            [InlineKeyboardButton("🔙 Back to Categories", callback_data="back_categories")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_payment_methods() -> InlineKeyboardMarkup:
        """পেমেন্ট মেথডস"""
        keyboard = [
            [
                InlineKeyboardButton("💰 bKash", callback_data="payment_bkash"),
                InlineKeyboardButton("💎 Nagad", callback_data="payment_nagad")
            ],
            [
                InlineKeyboardButton("🚀 Rocket", callback_data="payment_rocket"),
                InlineKeyboardButton("📱 Upay", callback_data="payment_upay")
            ],
            [InlineKeyboardButton("❌ Cancel", callback_data="cancel_payment")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_wallet_keyboard() -> InlineKeyboardMarkup:
        """ওয়ালেট মেনু"""
        keyboard = [
            [
                InlineKeyboardButton("💳 Add Balance", callback_data="add_balance"),
                InlineKeyboardButton("📊 Transaction History", callback_data="transactions")
            ],
            [InlineKeyboardButton("🎁 Redeem Code", callback_data="redeem_code")],
            [InlineKeyboardButton("🔙 Back", callback_data="back_main")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_order_confirmation(order_details: Dict) -> InlineKeyboardMarkup:
        """অর্ডার কনফার্মেশন"""
        keyboard = [
            [
                InlineKeyboardButton("✅ Confirm Order", callback_data=f"confirm_order_{order_details['service']}"),
                InlineKeyboardButton("❌ Cancel", callback_data="cancel_order")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_admin_order_actions(order_id: int) -> InlineKeyboardMarkup:
        """এডমিন অর্ডার একশনস"""
        keyboard = [
            [
                InlineKeyboardButton("✅ Approve", callback_data=f"admin_approve_{order_id}"),
                InlineKeyboardButton("❌ Reject", callback_data=f"admin_reject_{order_id}")
            ],
            [
                InlineKeyboardButton("🔄 Processing", callback_data=f"admin_processing_{order_id}"),
                InlineKeyboardButton("✅ Complete", callback_data=f"admin_complete_{order_id}")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_admin_payment_actions(payment_id: int) -> InlineKeyboardMarkup:
        """এডমিন পেমেন্ট একশনস"""
        keyboard = [
            [
                InlineKeyboardButton("✅ Approve Payment", callback_data=f"approve_payment_{payment_id}"),
                InlineKeyboardButton("❌ Reject Payment", callback_data=f"reject_payment_{payment_id}")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_quantity_keyboard(base: int = 100) -> InlineKeyboardMarkup:
        """কোয়ান্টিটি সিলেকশন"""
        keyboard = [
            [
                InlineKeyboardButton(f"{base}", callback_data=f"qty_{base}"),
                InlineKeyboardButton(f"{base*2}", callback_data=f"qty_{base*2}"),
                InlineKeyboardButton(f"{base*5}", callback_data=f"qty_{base*5}")
            ],
            [
                InlineKeyboardButton(f"{base*10}", callback_data=f"qty_{base*10}"),
                InlineKeyboardButton(f"{base*50}", callback_data=f"qty_{base*50}"),
                InlineKeyboardButton(f"{base*100}", callback_data=f"qty_{base*100}")
            ],
            [InlineKeyboardButton("✏️ Custom", callback_data="qty_custom")],
            [InlineKeyboardButton("🔙 Back", callback_data="back_service")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_back_button() -> InlineKeyboardMarkup:
        """সিঙ্গেল ব্যাক বাটন"""
        keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="back_main")]]
        return InlineKeyboardMarkup(keyboard)
