import logging
from datetime import datetime
from typing import Dict, Any
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, 
    CallbackQueryHandler, ContextTypes, 
    ConversationHandler, filters
)
from telegram.constants import ParseMode

from config import Config
from database import Database
from keyboards import KeyboardGenerator
from messages import MessageFormatter

# লগিং সেটআপ
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# কনভারসেশন স্টেটস
CATEGORY, SERVICE, LINK, QUANTITY, CONFIRM = range(5)
PAYMENT_METHOD, PAYMENT_SCREENSHOT, PAYMENT_TRX_ID = range(5, 8)
ADMIN_ACTION = 8

# গ্লোবাল ইনস্ট্যান্স
db = Database()
keyboards = KeyboardGenerator()
formatter = MessageFormatter()

# Helper Functions
def is_admin(user_id: int) -> bool:
    return user_id in Config.ADMIN_IDS

async def edit_or_reply(update: Update, text: str, keyboard=None, parse_mode=ParseMode.MARKDOWN):
    """মেসেজ এডিট অথবা রিপ্লাই"""
    try:
        if update.callback_query:
            await update.callback_query.edit_message_text(
                text=text,
                reply_markup=keyboard,
                parse_mode=parse_mode,
                disable_web_page_preview=True
            )
        else:
            await update.message.reply_text(
                text=text,
                reply_markup=keyboard,
                parse_mode=parse_mode,
                disable_web_page_preview=True
            )
    except Exception as e:
        logger.error(f"Error editing message: {e}")
        await update.message.reply_text(
            text=text,
            reply_markup=keyboard,
            parse_mode=parse_mode,
            disable_web_page_preview=True
        )

# Command Handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    
    # ইউজার ক্রিয়েট/ফেচ
    user_data = db.get_user(user_id)
    if not user_data:
        db.create_user(user_id, user.username, user.first_name)
        user_data = db.get_user(user_id)
    
    # ওয়েলকাম মেসেজ
    welcome_text = formatter.welcome_message(user_data)
    
    # এডমিন চেক
    if is_admin(user_id):
        await edit_or_reply(update, welcome_text, keyboards.get_admin_keyboard())
    else:
        await edit_or_reply(update, welcome_text, keyboards.get_main_keyboard())

async def wallet_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_data = db.get_user(user_id)
    
    wallet_text = formatter.wallet_message(user_data)
    await edit_or_reply(update, wallet_text, keyboards.get_wallet_keyboard())

async def orders_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    orders = db.get_user_orders(user_id)
    
    if not orders:
        await edit_or_reply(update, "📭 You have no orders yet!", keyboards.get_back_button())
        return
    
    text = "📊 **Your Recent Orders**\n\n"
    for order in orders[:10]:
        status_icon = {
            "pending": "⏳",
            "processing": "🔄",
            "completed": "✅",
            "cancelled": "❌"
        }.get(order['status'], "📊")
        
        text += f"{status_icon} **#{order['order_id']}** - {order['service_name']}\n"
        text += f"   Quantity: {order['quantity']} | Amount: ₹{order['price']:.2f}\n"
        text += f"   Status: {order['status'].title()} | Date: {order['created_at'][:10]}\n\n"
    
    text += "\n👇 **Use buttons to navigate**"
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔄 Refresh", callback_data="refresh_orders")],
        [InlineKeyboardButton("🔙 Back", callback_data="back_main")]
    ])
    
    await edit_or_reply(update, text, keyboard)

# Order Flow Handlers
async def start_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await edit_or_reply(
        update, 
        "📦 **Select a Category**\n\nChoose the platform you want to order from:",
        keyboards.get_service_categories()
    )
    return CATEGORY

async def category_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data
    if data == "category_instagram":
        context.user_data['service_type'] = 'instagram'
        await edit_or_reply(
            update,
            "📷 **Instagram Services**\n\nSelect the service you want:",
            keyboards.get_instagram_services()
        )
        return SERVICE
    elif data == "back_main":
        await start(update, context)
        return ConversationHandler.END

async def service_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data
    if data.startswith("service_"):
        _, platform, service = data.split("_")
        context.user_data['service_name'] = service
        context.user_data['service_type'] = platform
        
        # প্রাইস ফেচ করুন (এখানে কনফিগ থেকে)
        service_info = Config.SERVICES.get(platform, {}).get(service, {})
        
        service_text = formatter.service_details(
            platform, service,
            service_info.get('price', 100),
            service_info.get('min', 100),
            service_info.get('max', 10000)
        )
        
        await edit_or_reply(update, service_text, keyboards.get_quantity_keyboard())
        return LINK
    elif data == "back_categories":
        await start_order(update, context)
        return CATEGORY

async def link_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    link = update.message.text
    context.user_data['link'] = link
    
    await update.message.reply_text(
        "🔗 **Link Saved!**\n\n"
        f"Your link: `{link}`\n\n"
        "👇 **Now select quantity:**",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=keyboards.get_quantity_keyboard()
    )
    return QUANTITY

async def quantity_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data
    if data.startswith("qty_"):
        if data == "qty_custom":
            await query.edit_message_text(
                "✏️ **Enter Custom Quantity:**\n\n"
                "Please enter the quantity (numbers only):"
            )
            return QUANTITY
        else:
            quantity = int(data.split("_")[1])
            context.user_data['quantity'] = quantity
            
            # প্রাইস ক্যালকুলেশন
            platform = context.user_data['service_type']
            service = context.user_data['service_name']
            service_info = Config.SERVICES.get(platform, {}).get(service, {})
            price_per_1000 = service_info.get('price', 100)
            
            total_price = (quantity * price_per_1000) / 1000
            
            order_details = {
                'service_name': service,
                'link': context.user_data['link'],
                'quantity': quantity,
                'price': price_per_1000,
                'total_price': total_price
            }
            
            order_text = formatter.order_summary(order_details)
            await edit_or_reply(update, order_text, keyboards.get_order_confirmation(order_details))
            return CONFIRM
    elif data == "back_service":
        await service_selected(update, context)
        return SERVICE

async def confirm_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data
    if data.startswith("confirm_order_"):
        user_id = update.effective_user.id
        
        # অর্ডার ক্রিয়েট
        order_id = db.create_order(
            user_id=user_id,
            service_type=context.user_data['service_type'],
            service_name=context.user_data['service_name'],
            link=context.user_data['link'],
            quantity=context.user_data['quantity'],
            price=Config.SERVICES[context.user_data['service_type']][context.user_data['service_name']]['price']
        )
        
        # কনফার্মেশন মেসেজ
        order_details = {
            'service_name': context.user_data['service_name'],
            'quantity': context.user_data['quantity'],
            'price': Config.SERVICES[context.user_data['service_type']][context.user_data['service_name']]['price']
        }
        
        order_text = formatter.order_created(order_id, order_details)
        await edit_or_reply(update, order_text, keyboards.get_back_button())
        
        # এডমিনকে নোটিফাই করুন
        for admin_id in Config.ADMIN_IDS:
            try:
                admin_text = f"""
🚨 **New Order Alert**

📋 **Order ID:** #{order_id}
👤 **User:** {update.effective_user.first_name} (@{update.effective_user.username})
📦 **Service:** {context.user_data['service_name']}
🔗 **Link:** {context.user_data['link']}
🎯 **Quantity:** {context.user_data['quantity']}
💰 **Amount:** ₹{order_details['quantity'] * order_details['price'] / 1000:.2f}

👇 **Approve or reject:**
"""
                await context.bot.send_message(
                    chat_id=admin_id,
                    text=admin_text,
                    reply_markup=keyboards.get_admin_order_actions(order_id),
                    parse_mode=ParseMode.MARKDOWN
                )
            except Exception as e:
                logger.error(f"Error notifying admin: {e}")
        
        return ConversationHandler.END
    elif data == "cancel_order":
        await edit_or_reply(
            update,
            "❌ **Order Cancelled**\n\nYour order has been cancelled.",
            keyboards.get_main_keyboard()
        )
        return ConversationHandler.END

# Payment Handlers
async def add_balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    await edit_or_reply(
        update,
        "💰 **Add Balance**\n\nSelect payment method:",
        keyboards.get_payment_methods()
    )
    return PAYMENT_METHOD

async def payment_method_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data
    if data.startswith("payment_"):
        method = data.split("_")[1]
        context.user_data['payment_method'] = method
        
        await edit_or_reply(
            update,
            "💵 **Enter Amount**\n\nPlease enter the amount you want to add (minimum ₹50):"
        )
        return PAYMENT_TRX_ID
    elif data == "cancel_payment":
        await wallet_command(update, context)
        return ConversationHandler.END

async def payment_amount_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        amount = float(update.message.text)
        if amount < 50:
            await update.message.reply_text("❌ Minimum amount is ₹50. Please enter again:")
            return PAYMENT_TRX_ID
        
        context.user_data['payment_amount'] = amount
        
        # পেমেন্ট ইনস্ট্রাকশন
        details = {'amount': amount}
        instructions = formatter.payment_instructions(context.user_data['payment_method'], details)
        
        await update.message.reply_text(
            instructions,
            parse_mode=ParseMode.MARKDOWN
        )
        
        # স্ক্রিনশট আপলোড বাটন
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("📸 Send Screenshot", callback_data="upload_screenshot")],
            [InlineKeyboardButton("❌ Cancel", callback_data="cancel_payment")]
        ])
        
        await update.message.reply_text(
            "👇 **Click below to upload screenshot:**",
            reply_markup=keyboard
        )
        return PAYMENT_SCREENSHOT
        
    except ValueError:
        await update.message.reply_text("❌ Please enter a valid number:")
        return PAYMENT_TRX_ID

async def payment_screenshot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "upload_screenshot":
        await query.edit_message_text(
            "📸 **Upload Screenshot**\n\n"
            "Please send the payment screenshot as a photo:"
        )
        return PAYMENT_SCREENSHOT
    elif query.data == "cancel_payment":
        await wallet_command(update, context)
        return ConversationHandler.END

async def screenshot_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.photo:
        # সবচেয়ে বড় ফটো নিন
        photo = update.message.photo[-1]
        context.user_data['screenshot_id'] = photo.file_id
        
        await update.message.reply_text(
            "✅ **Screenshot Received!**\n\n"
            "📝 **Now enter Transaction ID:**\n"
            "(The ID you got after payment)"
        )
        return PAYMENT_TRX_ID
    else:
        await update.message.reply_text("❌ Please send a photo. Try again:")
        return PAYMENT_SCREENSHOT

async def trx_id_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    trx_id = update.message.text
    user_id = update.effective_user.id
    
    # পেমেন্ট রেকর্ড ক্রিয়েট
    payment_id = db.create_payment(
        user_id=user_id,
        amount=context.user_data['payment_amount'],
        method=context.user_data['payment_method'],
        transaction_id=trx_id,
        screenshot=context.user_data.get('screenshot_id')
    )
    
    # ইউজারকে কনফার্মেশন
    await update.message.reply_text(
        f"✅ **Payment Request Submitted!**\n\n"
        f"📋 **Payment ID:** `#{payment_id}`\n"
        f"💰 **Amount:** ₹{context.user_data['payment_amount']:.2f}\n"
        f"💳 **Method:** {context.user_data['payment_method'].upper()}\n"
        f"🎯 **Status:** ⏳ **Pending Approval**\n\n"
        f"⏱️ **Approval Time:** 1-10 minutes\n"
        f"🔔 You'll get notification when approved.",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=keyboards.get_main_keyboard()
    )
    
    # এডমিনকে নোটিফাই
    for admin_id in Config.ADMIN_IDS:
        try:
            admin_text = f"""
💳 **New Payment Request**

📋 **Payment ID:** #{payment_id}
👤 **User:** {update.effective_user.first_name}
💰 **Amount:** ₹{context.user_data['payment_amount']:.2f}
💎 **Method:** {context.user_data['payment_method'].upper()}
📝 **Trx ID:** {trx_id}

👇 **Approve or reject:**
"""
            await context.bot.send_message(
                chat_id=admin_id,
                text=admin_text,
                reply_markup=keyboards.get_admin_payment_actions(payment_id)
            )
            
            # স্ক্রিনশট ফরওয়ার্ড
            if 'screenshot_id' in context.user_data:
                await context.bot.send_photo(
                    chat_id=admin_id,
                    photo=context.user_data['screenshot_id'],
                    caption=f"Screenshot for Payment #{payment_id}"
                )
        except Exception as e:
            logger.error(f"Error notifying admin: {e}")
    
    return ConversationHandler.END

# Admin Handlers
async def admin_dashboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_admin(user_id):
        await update.message.reply_text("❌ Access denied!")
        return
    
    stats = db.get_stats()
    dashboard_text = formatter.admin_dashboard(stats)
    
    await edit_or_reply(update, dashboard_text, keyboards.get_admin_keyboard())

async def admin_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_admin(user_id):
        return
    
    users = db.get_all_users()
    
    text = "👥 **All Users**\n\n"
    for user in users[:20]:
        text += f"🆔 `{user['user_id']}` | 👤 {user['first_name']}\n"
        text += f"   💰 ₹{user['balance']:.2f} | 📦 {user['total_orders']} orders\n"
        text += f"   📅 {user['join_date'][:10]}\n\n"
    
    await edit_or_reply(update, text, keyboards.get_admin_keyboard())

async def admin_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_admin(user_id):
        return
    
    orders = db.get_all_orders()
    
    text = "📊 **All Orders**\n\n"
    for order in orders[:15]:
        status_icon = {
            "pending": "⏳",
            "processing": "🔄",
            "completed": "✅",
            "cancelled": "❌"
        }.get(order['status'], "📊")
        
        text += f"{status_icon} **#{order['order_id']}** - {order['service_name']}\n"
        text += f"   👤 User: `{order['user_id']}` | 🔗 {order['link'][:30]}...\n"
        text += f"   📦 {order['quantity']} | 💰 ₹{order['price']:.2f}\n"
        text += f"   📊 {order['status']} | 📅 {order['created_at'][:10]}\n\n"
    
    await edit_or_reply(update, text, keyboards.get_admin_keyboard())

async def admin_payments(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_admin(user_id):
        return
    
    payments = db.get_pending_payments()
    
    if not payments:
        text = "✅ **No pending payments**"
    else:
        text = "💰 **Pending Payments**\n\n"
        for payment in payments[:10]:
            text += f"📋 **#{payment['payment_id']}**\n"
            text += f"   👤 User: `{payment['user_id']}`\n"
            text += f"   💰 Amount: ₹{payment['amount']:.2f}\n"
            text += f"   💎 Method: {payment['method']}\n"
            text += f"   📝 Trx ID: {payment['transaction_id']}\n"
            text += f"   📅 {payment['created_at'][:19]}\n\n"
    
    await edit_or_reply(update, text, keyboards.get_admin_keyboard())

# Callback Handlers
async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    # এডমিন অ্যাকশনস
    if data.startswith("admin_approve_"):
        order_id = int(data.split("_")[2])
        # অর্ডার আপডেট করুন
        # এখানে আপনার লজিক ইমপ্লিমেন্ট করুন
        await query.edit_message_text(
            f"✅ Order #{order_id} approved!",
            reply_markup=keyboards.get_back_button()
        )
    
    elif data.startswith("approve_payment_"):
        payment_id = int(data.split("_")[2])
        # পেমেন্ট আপডেট করুন
        await query.edit_message_text(
            f"✅ Payment #{payment_id} approved!",
            reply_markup=keyboards.get_back_button()
        )
    
    elif data == "back_main":
        await start(update, context)

# Main Function
def main():
    # বট অ্যাপ্লিকেশন ক্রিয়েট
    application = Application.builder().token(Config.BOT_TOKEN).build()
    
    # কমান্ড হ্যান্ডলারস
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("wallet", wallet_command))
    application.add_handler(CommandHandler("orders", orders_command))
    application.add_handler(CommandHandler("admin", admin_dashboard))
    
    # অর্ডার কনভারসেশন
    order_conv = ConversationHandler(
        entry_points=[
            MessageHandler(filters.Regex("🛒 Order Services"), start_order),
            CallbackQueryHandler(start_order, pattern="^start_order$")
        ],
        states={
            CATEGORY: [CallbackQueryHandler(category_selected, pattern="^category_|^back_")],
            SERVICE: [CallbackQueryHandler(service_selected, pattern="^service_|^back_")],
            LINK: [MessageHandler(filters.TEXT & ~filters.COMMAND, link_received)],
            QUANTITY: [
                CallbackQueryHandler(quantity_selected, pattern="^qty_|^back_"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, quantity_selected)
            ],
            CONFIRM: [CallbackQueryHandler(confirm_order, pattern="^confirm_order_|^cancel_order")]
        },
        fallbacks=[CommandHandler("cancel", start)]
    )
    application.add_handler(order_conv)
    
    # পেমেন্ট কনভারসেশন
    payment_conv = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(add_balance, pattern="^add_balance$")
        ],
        states={
            PAYMENT_METHOD: [CallbackQueryHandler(payment_method_selected, pattern="^payment_|^cancel_")],
            PAYMENT_TRX_ID: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, payment_amount_received)
            ],
            PAYMENT_SCREENSHOT: [
                CallbackQueryHandler(payment_screenshot, pattern="^upload_screenshot|^cancel_"),
                MessageHandler(filters.PHOTO, screenshot_received)
            ]
        },
        fallbacks=[CommandHandler("cancel", start)]
    )
    application.add_handler(payment_conv)
    
    # এডমিন হ্যান্ডলারস
    application.add_handler(MessageHandler(filters.Regex("📈 Dashboard"), admin_dashboard))
    application.add_handler(MessageHandler(filters.Regex("👥 Users"), admin_users))
    application.add_handler(MessageHandler(filters.Regex("📊 Orders"), admin_orders))
    application.add_handler(MessageHandler(filters.Regex("💰 Payments"), admin_payments))
    
    # ক্যালব্যাক হ্যান্ডলার
    application.add_handler(CallbackQueryHandler(callback_handler))
    
    # আনহ্যান্ডল্ড মেসেজ
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, start))
    
    # বট স্টার্ট
    print("🤖 Bot is running...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
