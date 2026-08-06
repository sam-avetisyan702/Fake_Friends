from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram import Update

# Step 1: Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! I'm a bot!")

# Step 2: Echo message
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message.text
    await update.message.reply_text(f"You said: {message}")

# Step 3: Bot setup
TOKEN = "YOUR_TOKEN_HERE"  # @BotFather–ից ստացված

app = Application.builder().token(TOKEN).build()

# Step 4: Handlers
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

# Step 5: Run
app.run_polling()
