# -*- coding: utf-8 -*-
import asyncio
import logging
import time
import random
import json
import os
import sys
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, CallbackQueryHandler
from telethon import TelegramClient, events, errors
from telethon.tl.functions.account import ReportPeerRequest
from telethon.tl.types import InputReportReasonSpam, InputReportReasonOther
import aiohttp
from PIL import Image, ImageDraw, ImageFont

# ==================== ԿՈՆՖԻԳ ====================
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"  # Փոխարինել քո բոտի token-ով
API_ID = 12345  # Փոխարինել քո API ID-ով
API_HASH = "your_api_hash_here"  # Փոխարինել քո API HASH-ով
REPORT_COOLDOWN = 5  # վայրկյան սպասել յուրաքանչյուր ժալոբայից հետո
MAX_REPORTS_PER_ACCOUNT = 999999  # անվերջ
TARGET_FILE = "targets.txt"
LOG_FILE = "report_log.txt"
LOGO_PATH = "logo.png"

# ==================== ԼՈԳԱՎՈՐՈՒՄ ====================
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ==================== ԴԻԶԱՅՆ ԳՈՒՆՆԵՐ ====================
COLORS = {
    "red": "\033[91m",
    "green": "\033[92m",
    "yellow": "\033[93m",
    "blue": "\033[94m",
    "purple": "\033[95m",
    "cyan": "\033[96m",
    "white": "\033[97m",
    "reset": "\033[0m",
    "bold": "\033[1m"
}

BANNER = f"""
{COLORS['cyan']}{COLORS['bold']}
╔═══════════════════════════════════════════════════╗
║     SWILL REPORT BOT v3.0 - TOTAL ANNIHILATION   ║
║          Telegram Account Reporting System        ║
╚═══════════════════════════════════════════════════╝
{COLORS['reset']}
"""

# ==================== ՖՈՒՆԿՑԻԱՆԵՐ ՖԱՅԼԻ ՀԱՄԱՐ ====================
def load_targets():
    if not os.path.exists(TARGET_FILE):
        return []
    with open(TARGET_FILE, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip()]

def save_target(username):
    targets = load_targets()
    if username not in targets:
        with open(TARGET_FILE, 'a', encoding='utf-8') as f:
            f.write(username + "\n")
        return True
    return False

def remove_target(username):
    targets = load_targets()
    if username in targets:
        targets.remove(username)
        with open(TARGET_FILE, 'w', encoding='utf-8') as f:
            for t in targets:
                f.write(t + "\n")
        return True
    return False

def log_report(username, success, msg=""):
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(f"{datetime.now()} | {username} | {'SUCCESS' if success else 'FAIL'} | {msg}\n")

# ==================== ԴԻԶԱՅՆԻ ԳԵՆԵՐԱՏՈՐ ====================
def generate_progress_bar(current, total, length=30):
    filled = int(round(length * current / float(total)))
    bar = '█' * filled + '░' * (length - filled)
    return f"{COLORS['green']}{bar}{COLORS['reset']}"

def generate_status_ui(username, reports_done, is_blocked=False):
    status = f"{COLORS['red']}🔴 BLOCKED{COLORS['reset']}" if is_blocked else f"{COLORS['green']}🟢 ACTIVE{COLORS['reset']}"
    bar = generate_progress_bar(min(reports_done, 500), 500)
    ui = f"""
{COLORS['cyan']}═══════════════════════════════════════{COLORS['reset']}
{COLORS['yellow']}👤 TARGET:{COLORS['reset']} {COLORS['bold']}{username}{COLORS['reset']}
{COLORS['yellow']}📊 REPORTS:{COLORS['reset']} {reports_done}
{COLORS['yellow']}📈 PROGRESS:{COLORS['reset']} {bar}
{COLORS['yellow']}🚦 STATUS:{COLORS['reset']} {status}
{COLORS['cyan']}═══════════════════════════════════════{COLORS['reset']}
"""
    return ui

# ==================== ՀԻՄՆԱԿԱՆ ԲՈՏԻ ԴԱՍ ====================
class ReportBot:
    def __init__(self):
        self.reporting = False
        self.targets = load_targets()
        self.blocked_targets = {}
        self.report_counts = {}
        self.loop = asyncio.get_event_loop()
        
    async def report_account(self, client, username):
        """Մեկ ժալոբա գցել տվյալ username-ին"""
        try:
            entity = await client.get_entity(username)
            result = await client(ReportPeerRequest(
                peer=entity,
                reason=InputReportReasonSpam(),
                message="This account is spamming and violating Telegram terms. Constant unsolicited messages and scam activity."
            ))
            return True, "Report sent"
        except errors.FloodWaitError as e:
            wait = e.seconds
            logger.warning(f"Flood wait {wait}s")
            await asyncio.sleep(wait)
            return False, f"Flood wait {wait}s"
        except Exception as e:
            logger.error(f"Report error: {e}")
            return False, str(e)
    
    async def check_blocked(self, client, username):
        """Ստուգել՝ արդյոք ակաունտը բլոկ է"""
        try:
            entity = await client.get_entity(username)
            # Եթե կարողանում ենք ստանալ, ուրեմն բլոկ չէ
            return False
        except errors.UserDeactivatedError:
            return True
        except errors.UserInvalidError:
            return True
        except Exception:
            return False
    
    async def report_loop(self, username):
        """Անվերջ ցիկլ ժալոբաների համար մինչև բլոկ"""
        async with TelegramClient(f'session_{username.replace("@","")}', API_ID, API_HASH) as client:
            await client.start()
            self.report_counts[username] = 0
            logger.info(f"Started reporting on {username}")
            
            while self.reporting:
                # Ստուգել բլոկ
                if await self.check_blocked(client, username):
                    self.blocked_targets[username] = True
                    logger.info(f"✅ {username} is BLOCKED! Stopping.")
                    break
                
                # Ուղարկել ժալոբա
                success, msg = await self.report_account(client, username)
                if success:
                    self.report_counts[username] = self.report_counts.get(username, 0) + 1
                    log_report(username, True, msg)
                    logger.info(f"✅ Report #{self.report_counts[username]} sent to {username}")
                else:
                    log_report(username, False, msg)
                    logger.warning(f"❌ Failed report to {username}: {msg}")
                
                # Թարմացնել UI
                print(f"\r{generate_status_ui(username, self.report_counts.get(username,0), self.blocked_targets.get(username,False))}", end="")
                
                # Սպասել
                await asyncio.sleep(REPORT_COOLDOWN)
    
    async def start_reporting(self, username):
        """Սկսել ռեպորտինգ մեկ username-ի համար"""
        if username in self.targets:
            return False, "Already in targets"
        
        save_target(username)
        self.targets.append(username)
        self.blocked_targets[username] = False
        self.report_counts[username] = 0
        
        # Սկսել ասինխրոն աշխատանք
        asyncio.create_task(self.report_loop(username))
        return True, "Started reporting"
    
    async def stop_reporting(self, username):
        """Դադարեցնել ռեպորտինգը"""
        if username in self.targets:
            remove_target(username)
            self.targets.remove(username)
            self.blocked_targets[username] = False
            return True
        return False
    
    def get_stats(self):
        total = len(self.targets)
        blocked = sum(1 for u in self.targets if self.blocked_targets.get(u, False))
        active = total - blocked
        reports = sum(self.report_counts.values())
        return total, active, blocked, reports

# ==================== TELEGRAM BOT HANDLERS ====================
bot = ReportBot()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📊 Status", callback_data="status")],
        [InlineKeyboardButton("➕ Add Target", callback_data="add")],
        [InlineKeyboardButton("❌ Remove Target", callback_data="remove")],
        [InlineKeyboardButton("⏹ Stop All", callback_data="stop_all")],
        [InlineKeyboardButton("📈 Full Stats", callback_data="stats")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Ուղարկել լոգո
    if os.path.exists(LOGO_PATH):
        with open(LOGO_PATH, 'rb') as f:
            await update.message.reply_photo(
                photo=f,
                caption=f"""
{COLORS['bold']}🔥 SWILL REPORT BOT ACTIVE 🔥{COLORS['reset']}

⚡ Powerful multi-account reporting system
🎯 Auto-detect block and stop
🔄 Infinite loop until target is banned
📊 Real-time progress and status

{COLORS['yellow']}⚠️  Use responsibly (or not){COLORS['reset']}
                """,
                reply_markup=reply_markup
            )
    else:
        await update.message.reply_text(
            f"{BANNER}\n\n"
            f"{COLORS['green']}Bot is ready. Use buttons below.{COLORS['reset']}",
            reply_markup=reply_markup
        )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    
    if data == "status":
        total, active, blocked, reports = bot.get_stats()
        text = f"""
{COLORS['cyan']}📊 SYSTEM STATUS{COLORS['reset']}
━━━━━━━━━━━━━━━━━━━━
{COLORS['yellow']}🎯 Total targets:{COLORS['reset']} {total}
{COLORS['green']}🟢 Active:{COLORS['reset']} {active}
{COLORS['red']}🔴 Blocked:{COLORS['reset']} {blocked}
{COLORS['purple']}📨 Total reports sent:{COLORS['reset']} {reports}
━━━━━━━━━━━━━━━━━━━━
        """
        await query.edit_message_caption(caption=text) if os.path.exists(LOGO_PATH) else await query.edit_message_text(text)
    
    elif data == "add":
        await query.edit_message_text(f"{COLORS['yellow']}Send me the username (e.g., @username or just username){COLORS['reset']}")
        context.user_data['awaiting'] = 'add_target'
    
    elif data == "remove":
        targets = bot.targets
        if not targets:
            await query.edit_message_text(f"{COLORS['red']}No targets in list.{COLORS['reset']}")
            return
        keyboard = [[InlineKeyboardButton(t, callback_data=f"rm_{t}")] for t in targets[:50]]
        keyboard.append([InlineKeyboardButton("🔙 Back", callback_data="back")])
        await query.edit_message_text(f"{COLORS['yellow']}Select target to remove:{COLORS['reset']}", reply_markup=InlineKeyboardMarkup(keyboard))
    
    elif data.startswith("rm_"):
        username = data[3:]
        success = await bot.stop_reporting(username)
        if success:
            await query.edit_message_text(f"{COLORS['green']}✅ Removed {username}{COLORS['reset']}")
        else:
            await query.edit_message_text(f"{COLORS['red']}❌ Failed to remove {username}{COLORS['reset']}")
    
    elif data == "stop_all":
        for u in bot.targets[:]:
            await bot.stop_reporting(u)
        await query.edit_message_text(f"{COLORS['red']}⏹ All reporting stopped.{COLORS['reset']}")
    
    elif data == "stats":
        total, active, blocked, reports = bot.get_stats()
        text = f"""
{COLORS['bold']}📈 DETAILED STATISTICS{COLORS['reset']}
━━━━━━━━━━━━━━━━━━━━━━━
{COLORS['yellow']}Total targets:{COLORS['reset']} {total}
{COLORS['green']}Active reports:{COLORS['reset']} {active}
{COLORS['red']}Blocked accounts:{COLORS['reset']} {blocked}
{COLORS['purple']}Total reports sent:{COLORS['reset']} {reports}
{COLORS['cyan']}Success rate:{COLORS['reset']} {round((reports/(reports+1))*100,2)}%
━━━━━━━━━━━━━━━━━━━━━━━
        """
        await query.edit_message_text(text)
    
    elif data == "back":
        await start(update, context)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get('awaiting') == 'add_target':
        username = update.message.text.strip()
        if username.startswith('@'):
            username = username[1:]
        
        success, msg = await bot.start_reporting(username)
        if success:
            await update.message.reply_text(f"{COLORS['green']}✅ {msg} for @{username}{COLORS['reset']}")
        else:
            await update.message.reply_text(f"{COLORS['red']}❌ {msg}{COLORS['reset']}")
        
        context.user_data['awaiting'] = None

# ==================== MAIN ====================
async def main():
    # Ստեղծել լոգո եթե չկա
    if not os.path.exists(LOGO_PATH):
        img = Image.new('RGB', (400, 200), color=(20, 20, 30))
        d = ImageDraw.Draw(img)
        try:
            font = ImageFont.truetype("arial.ttf", 36)
        except:
            font = ImageFont.load_default()
        d.text((50, 80), "SWILL REPORT", fill=(0, 255, 100), font=font)
        d.text((80, 120), "BOT v3.0", fill=(100, 200, 255), font=font)
        img.save(LOGO_PATH)
        logger.info(f"Generated logo at {LOGO_PATH}")
    
    app = Application.builder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("status", lambda u,c: button_callback(u,c) if u.callback_query else None))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    logger.info("🚀 Bot started! Press Ctrl+C to stop.")
    print(BANNER)
    print(f"{COLORS['green']}Bot is running...{COLORS['reset']}")
    
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    
    # Keep alive
    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{COLORS['red']}Bot stopped.{COLORS['reset']}")
