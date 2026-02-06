from datetime import datetime
from typing import Dict, Any, List
from config import Config

class MessageFormatter:
    @staticmethod
    def welcome_message(user_data: Dict) -> str:
        """ওয়েলকাম মেসেজ"""
        return f"""
✨ **Welcome to Premium SMM Panel Bot** ✨

👤 **Account Information:**
├─ ID: `{user_data['user_id']}`
├─ Name: {user_data['first_name']}
├─ Balance: **₹{user_data['balance']:.2f}**
├─ Total Orders: **{user_data['total_orders']}**
└─ Member Since: {user_data['join_date'][:10]}

💎 **Referral Code:** `{user_data['referral_code']}`
   Invite friends and earn **10%** commission!

👇 **Choose an option below to get started:**
"""
    
    @staticmethod
    def wallet_message(user_data: Dict) -> str:
        """ওয়ালেট মেসেজ"""
        transactions = user_data.get('recent_transactions', [])
        
        message = f"""
💰 **Your Wallet**

💵 **Balance:** **₹{user_data['balance']:.2f}**
📊 **Total Spent:** **₹{user_data['total_spent']:.2f}**
🎯 **Total Orders:** **{user_data['total_orders']}**

"""
        
        if transactions:
            message += "📜 **Recent Transactions:**\n"
            for i, trans in enumerate(transactions[:5], 1):
                status_icon = "✅" if trans['status'] == 'approved' else "⏳" if trans['status'] == 'pending' else "❌"
                message += f"{i}. {status_icon} ₹{trans['amount']:.2f} via {trans['method']} - {trans['status']}\n"
        
        message += "\n👇 **Choose an option:**"
        return message
    
    @staticmethod
    def service_details(service_type: str, service_name: str, price: float, 
                       min_qty: int, max_qty: int) -> str:
        """সার্ভিস ডিটেইলস"""
        return f"""
🛒 **Service Details**

📦 **Service:** {service_name}
📁 **Category:** {service_type.upper()}
💰 **Price:** **₹{price:.2f}** per 1000
🎯 **Min Order:** {min_qty}
🚀 **Max Order:** {max_qty}

⚡ **Delivery:** 5-30 minutes (usually)
🔄 **Refill:** 30 days guarantee
📞 **Support:** 24/7 available

👇 **Please enter quantity:**
"""
    
    @staticmethod
    def order_summary(order_details: Dict) -> str:
        """অর্ডার সামারি"""
        total_price = (order_details['quantity'] * order_details['price']) / 1000
        
        return f"""
📋 **Order Summary**

📦 **Service:** {order_details['service_name']}
🔗 **Link:** {order_details['link']}
🎯 **Quantity:** {order_details['quantity']}
💰 **Price per 1000:** ₹{order_details['price']:.2f}
💵 **Total Price:** **₹{total_price:.2f}**

⏱️ **Start Time:** Within 5 minutes
🔄 **Refill Policy:** 30 days
📞 **Support:** Contact @support_bot

👇 **Please confirm your order:**
"""
    
    @staticmethod
    def order_created(order_id: int, order_details: Dict) -> str:
        """অর্ডার ক্রিয়েটেড মেসেজ"""
        total_price = (order_details['quantity'] * order_details['price']) / 1000
        
        return f"""
✅ **Order Created Successfully!**

📋 **Order ID:** `#{order_id}`
📦 **Service:** {order_details['service_name']}
💰 **Amount:** **₹{total_price:.2f}**
📊 **Status:** ⏳ **Pending Approval**

📝 **Note:** 
• Your order is waiting for admin approval
• Approval usually takes 1-5 minutes
• You'll get notification when approved

🔍 **Track your order in "My Orders" section**
"""
    
    @staticmethod
    def admin_dashboard(stats: Dict) -> str:
        """এডমিন ড্যাশবোর্ড"""
        return f"""
👑 **Admin Dashboard**

📊 **Statistics:**
├─ 👥 Total Users: **{stats['total_users']}**
├─ 📦 Total Orders: **{stats['total_orders']}**
├─ 💰 Total Revenue: **₹{stats['total_revenue']:.2f}**
└─ 💵 Total Balance: **₹{stats['total_balance']:.2f}**

🚨 **Pending Actions:**
├─ ⏳ Pending Orders: {stats.get('pending_orders', 0)}
├─ 💳 Pending Payments: {stats.get('pending_payments', 0)}
└— ⚠️ Issues: {stats.get('issues', 0)}

👇 **Select an option to manage:**
"""
    
    @staticmethod
    def payment_instructions(method: str, details: Dict) -> str:
        """পেমেন্ট ইনস্ট্রাকশন"""
        method_info = {
            "bkash": {
                "name": "bKash",
                "number": Config.PAYMENT_METHODS.get("bkash", "01xxxxxxxxx"),
                "type": "Personal"
            },
            "nagad": {
                "name": "Nagad",
                "number": Config.PAYMENT_METHODS.get("nagad", "01xxxxxxxxx"),
                "type": "Personal"
            },
            "rocket": {
                "name": "Rocket",
                "number": Config.PAYMENT_METHODS.get("rocket", "01xxxxxxxxx"),
                "type": "Personal"
            }
        }
        
        info = method_info.get(method, method_info["bkash"])
        
        return f"""
💳 **Payment Instructions - {info['name']}**

📱 **Send money to:**
├─ Number: **{info['number']}**
├─ Type: **{info['type']} Account**
└─ Amount: **₹{details['amount']:.2f}**

📝 **Important Steps:**
1. Send exact amount: **₹{details['amount']:.2f}**
2. Save transaction ID
3. Take screenshot of payment
4. Send screenshot here

🎯 **After payment:**
1. Click "📸 Send Screenshot" button
2. Upload screenshot
3. Enter transaction ID

⏱️ **Approval Time:** 1-10 minutes
"""
    
    @staticmethod
    def order_status_update(order: Dict) -> str:
        """অর্ডার স্ট্যাটাস আপডেট"""
        status_icons = {
            "pending": "⏳",
            "processing": "🔄", 
            "completed": "✅",
            "cancelled": "❌"
        }
        
        icon = status_icons.get(order['status'], "📊")
        
        return f"""
{icon} **Order Update**

📋 **Order ID:** `#{order['order_id']}`
📦 **Service:** {order['service_name']}
🎯 **Quantity:** {order['quantity']}
💰 **Amount:** ₹{order['price']:.2f}
📊 **Status:** {icon} **{order['status'].upper()}**

⏰ **Ordered:** {order['created_at'][:19]}
{'✅ **Completed:** ' + order['completed_at'][:19] if order.get('completed_at') else ''}
"""
    
    @staticmethod
    def user_info_for_admin(user: Dict) -> str:
        """এডমিনের জন্য ইউজার ইনফো"""
        return f"""
👤 **User Information**

🆔 **ID:** `{user['user_id']}`
👤 **Name:** {user['first_name']}
📛 **Username:** @{user['username'] or 'N/A'}
💰 **Balance:** **₹{user['balance']:.2f}**
📦 **Total Orders:** {user['total_orders']}
💸 **Total Spent:** **₹{user['total_spent']:.2f}**
📅 **Join Date:** {user['join_date'][:10]}
🎯 **Referral Code:** `{user['referral_code']}`
{'🚫 **Status:** BANNED' if user['is_banned'] else '✅ **Status:** ACTIVE'}
"""
