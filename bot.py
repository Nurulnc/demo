# bot.py → FULL WALLET + DEPOSIT APPROVAL SYSTEM ADDED (2025)
import logging, json, os
from uuid import uuid4
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ConversationHandler,
    filters,
    ContextTypes,
)

logging.basicConfig(level=logging.INFO)

TOKEN = "8411734378:AAFO3dg2EaYrMBxBmlzQXEnbtwRSLzUiO08"
ADMIN_ID = 1651695602

BKASH = "01815243007"
BINANCE = "38017799"

# তোমার প্রাইস
P = {
    "hotmail": {"bkash": 2, "binance": 0.016},
    "edu": {"bkash": 1.6, "binance": 0.013}
}

# ওয়ালেট ফাইল
WALLET_FILE = "wallet.json"
if os.path.exists(WALLET_FILE):
    with open(WALLET_FILE) as f:
        wallet = json.load(f)
else:
    wallet = {}

pending_deposits = {}
orders = {}
waiting = {}

CHOOSE_CAT, PAYMENT, QTY, CONFIRM, SCREENSHOT, TXID = range(6)

# /balance
async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    bal = wallet.get(user_id, 0)
    await update.message.reply_text(
        f"*Your Wallet*\n\n"
        f"Balance: ৳{bal}\n\n"
        f"Use /deposit to add money",
        parse_mode="Markdown"
    )

# /deposit
async def deposit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "*Add Money to Wallet*\n\n"
        f"bKash (Personal): `{BKASH}`\n"
        f"Binance Pay ID: `{BINANCE}`\n\n"
        f"Send payment & forward transaction message here\n"
        f"Admin will approve within 5 mins",
        parse_mode="Markdown"
    )

# বায়ার ট্রানজেকশন ফরওয়ার্ড করলে
async def receive_deposit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    username = update.effective_user.username or "User"
    text = update.message.text or update.message.caption or ""
    
    amount = None
    for word in text.split():
        if word.replace(".", "").isdigit():
            try:
                amount = int(float(word))
                if 50 <= amount <= 10000:
                    break
            except:
                pass
    
    if not amount:
        await update.message.reply_text("Amount not detected!\nForward full transaction message")
        return
    
    pending_deposits[user_id] = amount
    
    await update.message.reply_text(
        f"Deposit Request Sent!\n"
        f"Amount: ৳{amount}\n"
        f"Waiting for approval..."
    )
    
    kb = [
        [InlineKeyboardButton("Approve", callback_data=f"dep_approve_{user_id}_{amount}")],
        [InlineKeyboardButton("Reject", callback_data=f"dep_reject_{user_id}")]
    ]
    
    await context.bot.send_message(
        ADMIN_ID,
        f"DEPOSIT REQUEST\n\n"
        f"User: @{username}\n"
        f"ID: {user_id}\n"
        f"Amount: ৳{amount}",
        reply_markup=InlineKeyboardMarkup(kb)
    )

# Approve/Reject
async def deposit_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    data = q.data.split("_")
    
    user_id = data[2]
    if data[1] == "approve":
        amount = int(data[3])
        wallet[user_id] = wallet.get(user_id, 0) + amount
        with open(WALLET_FILE, "w") as f:
            json.dump(wallet, f, indent=2)
        await context.bot.send_message(user_id, f"DEPOSIT APPROVED!\n৳{amount} added\nNew Balance: ৳{wallet[user_id]}")
        await q.edit_message_text(f"Approved ৳{amount}")
    else:
        await context.bot.send_message(user_id, "Deposit Rejected")
        await q.edit_message_text("Rejected")

# বাকি সব ফাংশন তোমার পুরানো মতোই (start, cat, payment, qty, confirm, screenshot, txid, approve, excel)

# শুধু confirm ফাংশনটা এই নতুন ভার্সনে বদলে দাও (ব্যালেন্স চেক + কাটবে)
async def confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    
    if q.data == "no":
        await q.edit_message_text("Order Cancelled")
        return ConversationHandler.END

    user_id = str(update.effective_user.id)
    total = context.user_data["qty"] * context.user_data["price"]
    
    current_bal = wallet.get(user_id, 0)
    if current_bal < total:
        await q.edit_message_text(
            f"Insufficient Balance!\n"
            f"Required: ৳{total}\n"
            f"Available: ৳{current_bal}\n\n"
            f"Use /deposit to add money",
            parse_mode="Markdown"
        )
        return ConversationHandler.END
    
    # ব্যালেন্স কাটা
    wallet[user_id] = current_bal - total
    with open(WALLET_FILE, "w") as f:
        json.dump(wallet, f, indent=2)

    oid = str(uuid4())[:8].upper()
    orders[oid] = {**context.user_data, "uid": update.effective_user.id, "user": update.effective_user.username or "User"}
    
    await q.edit_message_text(
        f"*ORDER SUCCESSFUL!*\n\n"
        f"Order ID: `{oid}`\n"
        f"Deducted: ৳{total}\n"
        f"Remaining Balance: ৳{wallet[user_id]}\n\n"
        f"Accounts will be delivered soon",
        parse_mode="Markdown"
    )
    
    await context.bot.send_message(
        ADMIN_ID,
        f"AUTO ORDER (Wallet)\n"
        f"ID: `{oid}`\n"
        f"{context.user_data['cat']} × {context.user_data['qty']}\n"
        f"Paid: ৳{total}\n"
        f"User: @{orders[oid]['user']}"
    )
    return ConversationHandler.END

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start), CommandHandler("order", start)],
        states={
            CHOOSE_CAT: [CallbackQueryHandler(cat, pattern="^cat_")],
            PAYMENT:    [CallbackQueryHandler(payment, pattern="^pay_")],
            QTY:        [MessageHandler(filters.TEXT & ~filters.COMMAND, qty)],
            CONFIRM:    [CallbackQueryHandler(confirm, pattern="^(ok|no)$")],
            SCREENSHOT: [MessageHandler(filters.PHOTO, screenshot)],
            TXID:       [MessageHandler(filters.TEXT & ~filters.COMMAND, txid)],
        },
        fallbacks=[],
        allow_reentry=True
    )

    app.add_handler(conv)
    app.add_handler(CommandHandler("approve", approve))
    app.add_handler(MessageHandler(filters.Document.ALL, excel))
    
    # Wallet Commands
    app.add_handler(CommandHandler("balance", balance))
    app.add_handler(CommandHandler("deposit", deposit))
    app.add_handler(MessageHandler(filters.FORWARDED | filters.TEXT, receive_deposit))
    app.add_handler(CallbackQueryHandler(deposit_callback, pattern="^dep_"))

    print("BOT WITH FULL WALLET SYSTEM IS LIVE!")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
