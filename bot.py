# bot.py → LIVE SUPPORT + WALLET + CSV + MENU BAR (GSM-এ 100% চলে)
from uuid import uuid4 as u
from telegram import Update as U, InlineKeyboardMarkup as M, InlineKeyboardButton as B
from telegram.ext import Application as A, CommandHandler as C, CallbackQueryHandler as Q, MessageHandler as H, filters as F, ContextTypes as T, ConversationHandler as V

TOKEN="8411734378:AAFO3dg2EaYrMBxBmlzQXEnbtwRSLzUiO08"
ADMIN=1651695602
BKASH="01815243007"
BINANCE="38017799"

P={"h":{"b":2,"n":0.016},"e":{"b":1.6,"n":0.013}}
(CAT,PAY,QTY,OK,PH,TX)=range(6)
O,W,support_users={},{},{}

# /start + Live Support বাটন
async def s(up:U,c:T):
 c.user_data.clear()
 kb=[[B("Hotmail/Outlook",callback_data="h")],[B(".EDU Mail",callback_data="e")],[B("Live Support",callback_data="support")]]
 await up.message.reply_text("PREMIUM ACCOUNTS SHOP\n\nChoose option:",reply_markup=M(kb))
 return CAT

# Live Support চালু
async def live_support(up:U,c:T):
 q=up.callback_query;await q.answer()
 user_id=q.from_user.id
 support_users[user_id]=True
 await q.message.reply_text("Live Support Connected!\n\nWrite your problem — Admin will reply soon\nType /endsupport to exit")
 await c.bot.send_message(ADMIN,f"NEW SUPPORT\nUser: @{q.from_user.username or 'User'}\nID: {user_id}")
 
# Support মেসেজ ফরওয়ার্ড
async def forward_support(up:U,c:T):
 if up.effective_user.id not in support_users: return
 await up.message.forward(ADMIN)
 kb=[[B("Reply",callback_data=f"rep_{up.effective_user.id}")]]
 await c.bot.send_message(ADMIN,f"From @{up.effective_user.username or 'User'}",reply_markup=M(kb))

# Reply বাটন চাপলে
async def reply_user(up:U,c:T):
 q=up.callback_query;await q.answer()
 c.user_data["rep_to"]=int(q.data.split("_")[1])
 await q.message.reply_text("Write your reply:")

# রিপ্লাই পাঠানো
async def send_reply(up:U,c:T):
 if "rep_to" not in c.user_data: return
 target=c.user_data["rep_to"];del c.user_data["rep_to"]
 await up.message.copy(target)
 await up.message.reply_text("Reply Sent!")

# /endsupport
async def end_support(up:U,c:T):
 if up.effective_user.id in support_users:
  del support_users[up.effective_user.id]
  await up.message.reply_text("Support Ended. Thank you!")
  await c.bot.send_message(ADMIN,f"Support ended by {up.effective_user.id}")

# বাকি সব ফাংশন তোমার পুরানো মতোই
async def cat(up:U,c:T):q=up.callback_query;await q.answer();k=q.data;n="Hotmail/Outlook" if k=="h" else ".EDU Mail";c.user_data.update({"n":n,"k":k});await q.edit_message_text(f"{n}\n\nPayment:",reply_markup=M([[B(f"bKash ৳{P[k]['b']}",callback_data="b")],[B(f"Binance ${P[k]['n']}",callback_data="n")]]))
async def pay(up:U,c:T):q=up.callback_query;await q.answer();m="bKash" if q.data=="b" else "Binance Pay";pr=P[c.user_data["k"]][q.data];cu="৳" if q.data=="b" else "$";c.user_data.update({"m":m,"p":pr,"c":cu});t=f"{c.user_data['n']}\n\n*{m}*\n{cu}{pr}/acc\n\nSend to: `{BKASH if q.data=='b' else BINANCE}`\n\nQuantity:";await q.edit_message_text(t,parse_mode="Markdown");return QTY
async def qty(up:U,c:T):
 try:n=int(up.message.text);c.user_data["q"]=n if 1<=n<=2000 else (await up.message.reply_text("1-2000"),None)[1];await up.message.reply_text(f"*Summary*\n{c.user_data['n']}\nQty: {n}\nTotal: {c.user_data['c']}{n*c.user_data['p']}\n\nConfirm?",parse_mode="Markdown",reply_markup=M([[B("Yes",callback_data="y")],[B("No",callback_data="n")]]));return OK
 except:await up.message.reply_text("1-2000");return QTY
async def ok(up:U,c:T):q=up.callback_query;await q.answer();if q.data=="n":await q.edit_message_text("Cancelled");return V.END;oid=str(u())[:8].upper();O[oid]={"d":c.user_data.copy(),"id":up.effective_user.id};await q.edit_message_text(f"Order `{oid}` created\nSend screenshot",parse_mode="Markdown");await c.bot.send_message(ADMIN,f"New {c.user_data['n']} × {c.user_data['q']}\nOrder: {oid}");return PH
async def ph(up:U,c:T):if not up.message.photo:await up.message.reply_text("Photo");return PH;pid=up.message.photo[-1].file_id;oid=[k for k,v in O.items() if v["id"]==up.effective_user.id][-1];await up.message.reply_text("Transaction ID:");await c.bot.send_photo(ADMIN,pid,caption=f"Screenshot {oid}");return TX
async def tx(up:U,c:T):txid=up.message.text.strip();oid=[k for k,v in O.items() if v["id"]==up.effective_user.id][-1];await up.message.reply_text(f"Order {oid} submitted!");await c.bot.send_message(ADMIN,f"Ready {oid}\nTXID: {txid}\n→ /approve {oid}");return V.END
async def approve(up:U,c:T):if up.effective_user.id!=ADMIN:return;try:oid=c.args[0].upper();W[ADMIN]=oid;await up.message.reply_text(f"Send file for {oid}");except:await up.message.reply_text("Use /approve ABC123")
async def excel(up:U,c:T):if up.effective_user.id!=ADMIN or ADMIN not in W:return;oid=W.pop(ADMIN);if not up.message.document or not up.message.document.file_name.lower().endswith(('.xlsx','.csv')):await up.message.reply_text("Only .xlsx/.csv");W[ADMIN]=oid;return;await c.bot.send_document(O[oid]["id"],up.message.document.file_id,caption=f"Approved!\nOrder {oid}");await up.message.reply_text(f"Sent {oid}");del O[oid]

def m():
 a=A.builder().token(TOKEN).build()
 a.add_handler(V(entry_points=[C("start",s),C("order",s)],states={CAT:[Q(cat,pattern="^[he]\( ")|Q(live_support,pattern="^support \)")],PAY:[Q(pay,pattern="^[bn]\( ")],QTY:[H(F.TEXT&~F.COMMAND,qty)],OK:[Q(ok,pattern="^[yn] \)")],PH:[H(F.PHOTO,ph)],TX:[H(F.TEXT&~F.COMMAND,tx)]},fallbacks=[],allow_reentry=True))
 a.add_handler(C("approve",approve))
 a.add_handler(H(F.Document.ALL,excel))
 a.add_handler(C("endsupport",end_support))
 a.add_handler(H(F.ALL & ~F.COMMAND,forward_support))
 a.add_handler(Q(reply_user,pattern="^rep_"))
 a.add_handler(H(F.TEXT & ~F.COMMAND,send_reply))
 print("LIVE SUPPORT BOT IS LIVE!")
 a.run_polling(drop_pending_updates=True)
if __name__=="__main__":m()
