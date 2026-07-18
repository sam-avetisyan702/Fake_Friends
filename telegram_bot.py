from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

BOT_TOKEN = "8766725521:AAE2fEB8-2nu05ON026ILLV3-avcEp1q2fc"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "✅ **SAMFRIENDS_BOT** աշխատում է!\n\n"
        "📌 **Հրամաններ**\n"
        "/broadcast [տեքստ] - Զանգվածային ուղարկում\n"
        "/status - Վիճակագրություն"
    )

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❗ /broadcast [տեքստ]")
        return
    text = ' '.join(context.args)
    await update.message.reply_text(f"✅ Ուղարկված է: {text}")

app = Application.builder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("broadcast", broadcast))

print("🚀 Բոտը գործարկվում է...")
app.run_polling()

# Ավելացնել /status
elif text == "/status":
    send_message(chat_id, "📊 **ՎԻՃԱԿԱԳՐՈՒԹՅՈՒՆ**\n👥 Օգտատերեր՝ 5000\n✅ Կարգավիճակ՝ ԱՆԽՈՑԵԼԻ")

# Ավելացնել /join
elif text.startswith("/join"):
    parts = text.split(" ", 1)
    if len(parts) >= 2:
        send_message(chat_id, f"🔗 Միանում եմ {parts[1]}...")

# Ավելացնել /follow
elif text.startswith("/follow"):
    parts = text.split(" ", 1)
    if len(parts) >= 2:
        send_message(chat_id, f"👤 Ֆոլով եմ անում {parts[1]}...")