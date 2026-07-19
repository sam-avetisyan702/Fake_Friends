#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
===========================================================
   🌟  FRIENDS_BOT - PROFESSIONAL EDITION
   🔰  ULTIMATE UI + REAL USERS + 24/7
   📌  Version 5.0 (BLUE + PURPLE THEME)
===========================================================
"""

import sys
import asyncio
import os
import platform
import random
import time
import json
import hashlib
import sqlite3
from datetime import datetime, timedelta
from collections import defaultdict
from pyrogram import Client, filters, enums
from pyrogram.types import Message, Chat, User, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait, UserIsBlocked, PeerIdInvalid

# ================================================================
# 1. FIX FOR PYTHON 3.14+
# ================================================================
if sys.version_info >= (3, 14):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        asyncio.set_event_loop(asyncio.new_event_loop())

# ================================================================
# 2. PROFESSIONAL COLORS (BLUE + PURPLE)
# ================================================================
class Colors:
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

# ================================================================
# 3. CONFIG
# ================================================================
BOT_USERNAME = "samfriends_bot"
BOT_TOKEN = "8766725521:AAE2fEB8-2nu05ON026ILLV3-avcEp1q2fc"
API_ID = 36495047
API_HASH = "c194688a25fa2347687547320549b73b"
MAX_USERS = 1000
CACHE_FOLDER = "cache_files"

# Ստեղծել քեշի թղթապանակ
if not os.path.exists(CACHE_FOLDER):
    os.makedirs(CACHE_FOLDER)
os.chdir(CACHE_FOLDER)

# ================================================================
# 4. USER GENERATOR (REALISTIC)
# ================================================================
REAL_NAMES = [
    "Aram", "Armen", "Garik", "David", "Edgar", "Zaven", "Torgom",
    "Levon", "Khoren", "Hakob", "Mher", "Narek", "Samvel", "Vahe",
    "Ani", "Lusine", "Nina", "Mariam", "Anush", "Sona", "Lilit"
]

LAST_NAMES = [
    "Sargsyan", "Hovhannisyan", "Ghazaryan", "Khachatryan", "Mkrtchyan",
    "Harutyunyan", "Grigoryan", "Petrosyan", "Avetisyan", "Manukyan"
]

def generate_real_users(count=MAX_USERS):
    """Ստեղծում է իրական անուններով օգտատերեր"""
    users = set()
    while len(users) < count:
        first = random.choice(REAL_NAMES)
        last = random.choice(LAST_NAMES)
        year = random.randint(1980, 2005)
        users.add(f"{first}{last}{year}")
    return list(users)

def create_users():
    if not os.path.exists("users.txt"):
        print("👥 Ստեղծում եմ 1000 իրական օգտատեր...")
        users = generate_real_users(MAX_USERS)
        with open("users.txt", "w", encoding='utf-8') as f:
            for user in users:
                f.write(f"@{user}\n")
        print(f"✅ users.txt ստեղծված է ({MAX_USERS} օգտատեր)")
    else:
        print("✅ users.txt արդեն կա")

# ================================================================
# 5. PROFESSIONAL UI
# ================================================================
class UI:
    @staticmethod
    def banner():
        os.system('cls' if platform.system() == "Windows" else 'clear')
        print(f"""
{Colors.PURPLE}{Colors.BOLD}╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║   🌟  {Colors.BLUE}FRIENDS_BOT - PROFESSIONAL EDITION{Colors.PURPLE}                 ║
║   🔰  {Colors.CYAN}ULTIMATE UI + REAL USERS + 24/7{Colors.PURPLE}                  ║
║   📌  {Colors.BLUE}Version 5.0 (BLUE + PURPLE){Colors.PURPLE}                       ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝{Colors.END}
""")
    
    @staticmethod
    def menu():
        print(f"""
{Colors.BLUE}╔══════════════════════════════════════════════════════════════════╗
║ {Colors.BOLD}📌  ՀԻՄՆԱԿԱՆ ՄԵՆՈՒ{Colors.BLUE}                                         ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                  ║
║  {Colors.PURPLE}▶  {Colors.CYAN}1. ՍՏԵՂԾԵԼ ԿԵՂԾ ԱԿԿԱՈՒՆՏՆԵՐ{Colors.BLUE}                  ║
║  {Colors.PURPLE}▶  {Colors.CYAN}2. ԶԱՆԳՎԱԾԱՅԻՆ ՈՒՂԱՐԿՈՒՄ{Colors.BLUE}                  ║
║  {Colors.PURPLE}▶  {Colors.CYAN}3. ՀԱՐՑ ՈՒՂԱՐԿԵԼ 10 ՕԳՏԱՏԵՐԻ{Colors.BLUE}              ║
║  {Colors.PURPLE}▶  {Colors.CYAN}4. ՄԻԱՆԱԼ ԿԱՆԱԼԻՆ{Colors.BLUE}                        ║
║  {Colors.PURPLE}▶  {Colors.CYAN}5. ՖՈԼՈՎ ԱՆԵԼ{Colors.BLUE}                           ║
║  {Colors.PURPLE}▶  {Colors.CYAN}6. ՎԻՃԱԿԱԳՐՈՒԹՅՈՒՆ{Colors.BLUE}                       ║
║  {Colors.PURPLE}▶  {Colors.CYAN}7. ԴԱԴԱՐԵՑՆԵԼ ԱՄԵՆ ԻՆՉ{Colors.BLUE}                   ║
║  {Colors.PURPLE}▶  {Colors.CYAN}8. ԵԼՔ{Colors.BLUE}                                  ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝{Colors.END}
""")
    
    @staticmethod
    def status_panel(stats):
        print(f"""
{Colors.PURPLE}╔══════════════════════════════════════════════════════════════════╗
║ {Colors.BOLD}📊  ՎԻՃԱԿԱԳՐՈՒԹՅՈՒՆ{Colors.PURPLE}                                       ║
╠══════════════════════════════════════════════════════════════════╣
║  👤  {Colors.BLUE}Ակկաունտներ:{Colors.END} {stats.get('accounts', 0):<30}             ║
║  📨  {Colors.CYAN}Ուղարկված:{Colors.END} {stats.get('sent', 0):<30}                   ║
║  👥  {Colors.GREEN}Օգտատերեր:{Colors.END} {stats.get('users', 0):<30}                 ║
║  🛡️  {Colors.PURPLE}Կարգավիճակ:{Colors.END} {stats.get('status', 'ԱՆԽՈՑԵԼԻ'):<30}    ║
║  ⏱️  {Colors.YELLOW}Աշխատանքի ժամանակը:{Colors.END} {stats.get('uptime', '0:00:00'):<30} ║
╚══════════════════════════════════════════════════════════════════╝{Colors.END}
""")
    
    @staticmethod
    def log(message, level="INFO"):
        icons = {
            "INFO": f"{Colors.BLUE}ℹ️",
            "SUCCESS": f"{Colors.GREEN}✅",
            "WARNING": f"{Colors.YELLOW}⚠️",
            "ERROR": f"{Colors.RED}❌",
            "SEND": f"{Colors.CYAN}📤",
            "RECEIVE": f"{Colors.PURPLE}📥",
            "CREATE": f"{Colors.GREEN}🛡️",
            "STOP": f"{Colors.RED}⏹️",
        }
        icon = icons.get(level, "•")
        print(f"{icon} {message}{Colors.END}")

# ================================================================
# 6. HUMAN CLOCK & AUTO-ACTIONS (նույնն են, ինչ նախկինում)
# ================================================================
class HumanClock:
    @staticmethod
    def get_profile():
        profiles = [
            {"wake": 7, "sleep": 23, "peak": [10, 15, 20]},
            {"wake": 9, "sleep": 1, "peak": [12, 18, 22]},
            {"wake": 8, "sleep": 0, "peak": [11, 16, 21]},
        ]
        return random.choice(profiles)
    
    @staticmethod
    def is_active(profile):
        now = datetime.now()
        hour = now.hour
        if profile["sleep"] < profile["wake"]:
            if hour >= profile["sleep"] and hour < profile["wake"]:
                return False
        else:
            if hour < profile["wake"] or hour >= profile["sleep"]:
                return False
        if now.weekday() >= 5 and random.random() < 0.6:
            return False
        return True

class SmartDelay:
    @staticmethod
    def typing(text_length):
        base_speed = random.uniform(30, 80)
        minutes = text_length / base_speed
        noise = random.gauss(0, 0.2)
        return max(1, (minutes * 60) + noise * 10)
    
    @staticmethod
    def thinking(complexity=0):
        base = random.expovariate(1/5)
        return min(30, max(1, base + complexity * 2))
    
    @staticmethod
    def between_actions():
        return random.gauss(90, 30)

class DynamicContent:
    @staticmethod
    def generate(context=None):
        if context is None:
            context = {}
        templates = [
            "Բարև {name}! {greeting} {emoji}",
            "Սիրելի {name}, {question}? {emoji}",
            "{name}, {statement}! {emoji}",
            "Հարգելի {name}, {offer} {emoji}",
        ]
        greetings = ["ինչպես ես", "ինչ նորություն", "հետաքրքիր բան կա"]
        questions = ["կուզե՞ս փոխանակել", "ինչ ես կարծում", "կօգնե՞ս"]
        statements = ["նայիր սա", "ծիծաղելի է", "հավատում ես"]
        offers = ["միացիր", "փորձիր", "տես"]
        emojis = ["😊", "🔥", "💪", "🎯", "❤️", "🚀"]
        
        template = random.choice(templates)
        return template.format(
            name=context.get("name", "ընկեր"),
            greeting=random.choice(greetings),
            question=random.choice(questions),
            statement=random.choice(statements),
            offer=random.choice(offers),
            emoji=random.choice(emojis)
        )

class AutoActions:
    @staticmethod
    async def join_channel(client, channel_link):
        try:
            await client.join_chat(channel_link)
            return True
        except:
            return False
    
    @staticmethod
    async def follow_user(client, username):
        try:
            await client.follow_user(username)
            return True
        except:
            return False

# ================================================================
# 7. BAN-PROOF ACCOUNT
# ================================================================
class BanProofAccount:
    def __init__(self, phone, proxy=None):
        self.phone = phone
        self.proxy = proxy
        self.session_name = f"bp_{hashlib.md5(phone.encode()).hexdigest()[:10]}"
        self.client = None
        self.profile = HumanClock.get_profile()
        self.message_count = 0
        self.db = sqlite3.connect(f"{self.session_name}.db", check_same_thread=False)
        self._init_db()
        self.is_ready = False
        self.start_time = time.time()
        
    def _init_db(self):
        cursor = self.db.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id INTEGER,
                message TEXT,
                timestamp INTEGER,
                direction TEXT
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS contacts (
                chat_id INTEGER PRIMARY KEY,
                first_seen INTEGER,
                last_seen INTEGER,
                interaction_count INTEGER DEFAULT 0
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_type TEXT,
                target TEXT,
                status TEXT,
                timestamp INTEGER
            )
        ''')
        self.db.commit()
        
    async def start(self):
        client_params = {
            "api_id": API_ID,
            "api_hash": API_HASH,
            "phone_number": self.phone,
            "in_memory": False,
            "name": self.session_name
        }
        if self.proxy:
            client_params["proxy"] = self.proxy
            
        self.client = Client(**client_params)
        await self.client.start()
        await self._wake_up()
        asyncio.create_task(self._life_cycle())
        self.is_ready = True
        UI.log(f"[{self.session_name}] BAN-PROOF ակտիվացված", "CREATE")
        return self
        
    async def _wake_up(self):
        try:
            async for dialog in self.client.get_dialogs(limit=3):
                await self.client.read_chat_history(dialog.chat.id)
                await asyncio.sleep(random.uniform(2, 5))
        except:
            pass
        await self.client.set_status(status="online")
        if random.random() < 0.3:
            try:
                await self.client.set_profile(
                    bio=f"📱 {random.choice(['Կյանք','Կրիպտո','Գեյմինգ','Ճամփորդություն'])} | #{random.randint(100,999)}"
                )
            except:
                pass
        await asyncio.sleep(random.uniform(5, 15))
        
    async def _life_cycle(self):
        while True:
            if HumanClock.is_active(self.profile):
                actions = [
                    self._check_messages,
                    self._send_random_message,
                    self._browse_channels,
                    self._change_profile_gradually,
                    self._execute_pending_tasks,
                ]
                weights = [0.3, 0.2, 0.2, 0.1, 0.2]
                action = random.choices(actions, weights=weights)[0]
                try:
                    await action()
                except:
                    pass
                await asyncio.sleep(SmartDelay.between_actions())
            else:
                await asyncio.sleep(300)
                
    async def _execute_pending_tasks(self):
        cursor = self.db.cursor()
        cursor.execute(
            "SELECT id, task_type, target FROM tasks WHERE status='pending' LIMIT 5"
        )
        tasks = cursor.fetchall()
        
        for task_id, task_type, target in tasks:
            if task_type == "join":
                success = await AutoActions.join_channel(self.client, target)
                msg = f"Միացավ {target}" if success else f"Չհաջողվեց միանալ {target}"
                UI.log(msg, "SUCCESS" if success else "ERROR")
            elif task_type == "follow":
                success = await AutoActions.follow_user(self.client, target)
                msg = f"Ֆոլով արեց {target}" if success else f"Չհաջողվեց ֆոլով անել {target}"
                UI.log(msg, "SUCCESS" if success else "ERROR")
            else:
                success = False
                
            status = "done" if success else "failed"
            cursor.execute(
                "UPDATE tasks SET status=? WHERE id=?",
                (status, task_id)
            )
            self.db.commit()
            await asyncio.sleep(random.uniform(2, 5))
                
    async def _check_messages(self):
        try:
            async for dialog in self.client.get_dialogs(limit=5):
                try:
                    async for msg in self.client.get_chat_history(dialog.chat.id, limit=3):
                        if msg.from_user and msg.from_user.id != self.client.me.id:
                            if random.random() < 0.7:
                                await self.client.send_chat_action(dialog.chat.id, "typing")
                                thinking = SmartDelay.thinking(len(msg.text or ""))
                                await asyncio.sleep(thinking)
                                reply = DynamicContent.generate({
                                    "name": msg.from_user.first_name or "ընկեր"
                                })
                                await self.client.send_message(dialog.chat.id, reply)
                                self._log_interaction(dialog.chat.id, msg.text, reply)
                                break
                except:
                    continue
        except:
            pass
            
    async def _send_random_message(self):
        cursor = self.db.cursor()
        cursor.execute(
            "SELECT chat_id FROM contacts WHERE interaction_count > 2 ORDER BY RANDOM() LIMIT 1"
        )
        result = cursor.fetchone()
        if result:
            chat_id = result[0]
            cursor.execute(
                "SELECT timestamp FROM history WHERE chat_id=? ORDER BY timestamp DESC LIMIT 1",
                (chat_id,)
            )
            last = cursor.fetchone()
            if last and (time.time() - last[0]) > 86400 * 2:
                msg = DynamicContent.generate({"name": "ընկեր"})
                await self.client.send_message(chat_id, msg)
                self._log_interaction(chat_id, None, msg)
                
    async def _browse_channels(self):
        try:
            async for dialog in self.client.get_dialogs():
                if dialog.chat.type in [enums.ChatType.CHANNEL, enums.ChatType.GROUP]:
                    if random.random() < 0.2:
                        async for msg in self.client.get_chat_history(dialog.chat.id, limit=3):
                            await asyncio.sleep(random.uniform(1, 4))
                        break
        except:
            pass
            
    async def _change_profile_gradually(self):
        if random.random() < 0.05:
            first_names = ["Արամ","Արմեն","Գարիկ","Դավիթ","Էդգար","Զավեն"]
            last_names = ["Սարգսյան","Հովհաննիսյան","Ղազարյան","Խաչատրյան"]
            first = random.choice(first_names)
            last = random.choice(last_names)
            try:
                await self.client.set_profile(first_name=first, last_name=last)
                UI.log(f"[{self.session_name}] Փոխեց պրոֆիլը {first} {last}", "INFO")
            except:
                pass
                
    def _log_interaction(self, chat_id, received, sent):
        cursor = self.db.cursor()
        now = int(time.time())
        if received:
            cursor.execute(
                "INSERT INTO history (chat_id, message, timestamp, direction) VALUES (?, ?, ?, ?)",
                (chat_id, received, now, "in")
            )
        if sent:
            cursor.execute(
                "INSERT INTO history (chat_id, message, timestamp, direction) VALUES (?, ?, ?, ?)",
                (chat_id, sent, now, "out")
            )
        cursor.execute(
            "INSERT OR REPLACE INTO contacts (chat_id, first_seen, last_seen, interaction_count) "
            "VALUES (?, COALESCE((SELECT first_seen FROM contacts WHERE chat_id=?), ?), ?, "
            "COALESCE((SELECT interaction_count FROM contacts WHERE chat_id=?), 0) + 1)",
            (chat_id, chat_id, now, now, chat_id)
        )
        self.db.commit()
        
    async def send_to_target(self, target, text):
        cursor = self.db.cursor()
        cursor.execute("SELECT interaction_count FROM contacts WHERE chat_id=?", (target,))
        if cursor.fetchone():
            try:
                await self.client.send_chat_action(target, "typing")
                await asyncio.sleep(SmartDelay.thinking())
                await self.client.send_message(target, text)
                self._log_interaction(target, None, text)
                UI.log(f"Ուղարկեց {target}: {text[:30]}...", "SEND")
                return True
            except:
                return False
        else:
            if random.random() < 0.2:
                try:
                    await self.client.send_message(target, text)
                    self._log_interaction(target, None, text)
                    UI.log(f"Ուղարկեց նոր կոնտակտի {target}", "SEND")
                    return True
                except:
                    pass
            return False
    
    async def add_task(self, task_type, target):
        cursor = self.db.cursor()
        cursor.execute(
            "INSERT INTO tasks (task_type, target, status, timestamp) VALUES (?, ?, ?, ?)",
            (task_type, target, "pending", int(time.time()))
        )
        self.db.commit()
        UI.log(f"[{self.session_name}] Ավելացվեց առաջադրանք: {task_type} {target}", "INFO")
            
    async def stop(self):
        if self.client:
            await self.client.stop()
        self.db.close()

# ================================================================
# 8. SWARM
# ================================================================
class BanProofSwarm:
    def __init__(self):
        self.accounts = []
        self.stats = defaultdict(int)
        self.running = False
        self.start_time = time.time()
        
    async def create_accounts(self, count=5):
        UI.log(f"Ստեղծում եմ {count} կեղծ ակկաունտ...", "CREATE")
        phones = [f"+7999888{str(i).zfill(4)}" for i in range(count)]
        tasks = []
        for i, phone in enumerate(phones):
            account = BanProofAccount(phone)
            tasks.append(account.start())
        self.accounts = await asyncio.gather(*tasks)
        self.running = True
        self.stats["created"] = len(self.accounts)
        UI.log(f"✅ {len(self.accounts)} BAN-PROOF ակկաունտ ստեղծված", "SUCCESS")
        return self.accounts
        
    async def broadcast(self, text, max_per_account=10):
        if not self.accounts:
            return 0
        with open("users.txt", "r", encoding='utf-8') as f:
            targets = [line.strip() for line in f if line.strip()][:MAX_USERS]
        random.shuffle(targets)
        tasks = []
        for account in self.accounts:
            selected = random.sample(targets, min(max_per_account, len(targets)))
            for target in selected:
                tasks.append(account.send_to_target(target, text))
        results = await asyncio.gather(*tasks)
        sent = sum(1 for r in results if r)
        self.stats["sent"] += sent
        UI.log(f"📤 Ուղարկված է {sent} հաղորդագրություն", "SEND")
        return sent
    
    async def add_task_all(self, task_type, target):
        tasks = []
        for account in self.accounts:
            tasks.append(account.add_task(task_type, target))
        await asyncio.gather(*tasks)
        UI.log(f"📋 {task_type} {target} ավելացվեց բոլոր ակկաունտներին", "INFO")
        
    async def get_stats(self):
        active = len([a for a in self.accounts if a.is_ready])
        uptime = int(time.time() - self.start_time)
        hours = uptime // 3600
        minutes = (uptime % 3600) // 60
        seconds = uptime % 60
        return {
            "accounts": active,
            "sent": self.stats.get("sent", 0),
            "users": len(open("users.txt", "r", encoding='utf-8').readlines()),
            "status": "🟢 ԱՆԽՈՑԵԼԻ" if active > 0 else "🔴 ԱՆԳՈՐԾ",
            "uptime": f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        }
        
    async def stop_all(self):
        self.running = False
        tasks = [acc.stop() for acc in self.accounts]
        await asyncio.gather(*tasks)
        self.accounts.clear()
        UI.log("⏹️ Բոլոր ակկաունտները դադարեցված", "STOP")

# ================================================================
# 9. TELEGRAM BOT (PROFESSIONAL UI + MENU)
# ================================================================
class FriendsBot:
    def __init__(self, token):
        self.token = token
        self.bot = Client(
            "friends_bot",
            bot_token=token,
            api_id=API_ID,
            api_hash=API_HASH,
            in_memory=True
        )
        self.swarm = None
        self.user_data = {}
        create_users()
        
    def get_main_menu(self):
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("🛡️ Ստեղծել ակկաունտներ", callback_data="create")],
            [InlineKeyboardButton("📤 Զանգվածային ուղարկում", callback_data="broadcast")],
            [InlineKeyboardButton("❓ Հարց ուղարկել 10-ին", callback_data="ask")],
            [InlineKeyboardButton("🔗 Միանալ կանալին", callback_data="join")],
            [InlineKeyboardButton("👤 Ֆոլով անել", callback_data="follow")],
            [InlineKeyboardButton("📊 Վիճակագրություն", callback_data="status")],
            [InlineKeyboardButton("⏹️ Դադարեցնել", callback_data="stop")],
        ])
        
    async def start(self):
        @self.bot.on_message(filters.command("start"))
        async def start_cmd(client, message):
            await message.reply(
                f"{Colors.PURPLE}🌟 **FRIENDS_BOT - PROFESSIONAL EDITION**{Colors.END}\n\n"
                f"🔰 **BAN-PROOF** + **AUTO-JOIN** + **FOLLOW**\n"
                f"👥 **{MAX_USERS}** օգտատեր պատրաստ է\n"
                f"🛡️ 24/7 աշխատում է\n\n"
                f"📌 **ԸՆՏՐԵՔ ԳՈՐԾՈՂՈՒԹՅՈՒՆԸ** 👇",
                reply_markup=self.get_main_menu()
            )
            
        @self.bot.on_callback_query()
        async def handle_callback(client, callback_query):
            data = callback_query.data
            await callback_query.answer()
            
            if data == "create":
                if not self.swarm:
                    self.swarm = BanProofSwarm()
                await self.swarm.create_accounts(3)
                await callback_query.message.edit_text(
                    f"✅ **3 BAN-PROOF ակկաունտ ստեղծված!**\n\n"
                    f"🛡️ Կարող եք օգտագործել /broadcast, /join, /follow",
                    reply_markup=self.get_main_menu()
                )
                
            elif data == "broadcast":
                await callback_query.message.edit_text(
                    "📤 **Զանգվածային ուղարկում**\n\n"
                    "📌 Ուղարկեք հաղորդագրությունը՝ /broadcast [տեքստ]\n"
                    f"👥 {MAX_USERS} օգտատեր կստանան",
                    reply_markup=self.get_main_menu()
                )
                
            elif data == "ask":
                await callback_query.message.edit_text(
                    "❓ **Հարց ուղարկել 10 օգտատերերի**\n\n"
                    "📌 /ask [հարց]",
                    reply_markup=self.get_main_menu()
                )
                
            elif data == "join":
                await callback_query.message.edit_text(
                    "🔗 **Միանալ կանալին**\n\n"
                    "📌 /join [link]",
                    reply_markup=self.get_main_menu()
                )
                
            elif data == "follow":
                await callback_query.message.edit_text(
                    "👤 **Ֆոլով անել**\n\n"
                    "📌 /follow [username]",
                    reply_markup=self.get_main_menu()
                )
                
            elif data == "status":
                if self.swarm:
                    stats = await self.swarm.get_stats()
                    text = (
                        f"📊 **ՎԻՃԱԿԱԳՐՈՒԹՅՈՒՆ**\n\n"
                        f"👤 Ակկաունտներ՝ {stats['accounts']}\n"
                        f"📨 Ուղարկված՝ {stats['sent']}\n"
                        f"👥 Օգտատերեր՝ {stats['users']}\n"
                        f"🛡️ Կարգավիճակ՝ {stats['status']}\n"
                        f"⏱️ Աշխատանքի ժամանակը՝ {stats['uptime']}"
                    )
                else:
                    text = "❌ Չկան ակտիվ ակկաունտներ"
                await callback_query.message.edit_text(
                    text,
                    reply_markup=self.get_main_menu()
                )
                
            elif data == "stop":
                if self.swarm:
                    await self.swarm.stop_all()
                    await callback_query.message.edit_text(
                        "⏹️ **Բոլորը դադարեցված!**\n\n"
                        "✅ Ակկաունտներն անջատված են",
                        reply_markup=self.get_main_menu()
                    )
                else:
                    await callback_query.message.edit_text(
                        "❌ Չկան ակտիվ ակկաունտներ",
                        reply_markup=self.get_main_menu()
                    )
                    
        @self.bot.on_message(filters.command("broadcast"))
        async def broadcast_cmd(client, message):
            if not self.swarm or not self.swarm.accounts:
                await message.reply("❗ **Նախ /create** արեք", reply_markup=self.get_main_menu())
                return
            if len(message.command) < 2:
                await message.reply("❗ /broadcast [տեքստ]", reply_markup=self.get_main_menu())
                return
            text = ' '.join(message.command[1:])
            await message.reply(f"🚀 **Ուղարկում եմ {MAX_USERS} օգտատերերի...**")
            sent = await self.swarm.broadcast(text, max_per_account=10)
            await message.reply(f"✅ **{sent} հաղորդագրություն ուղարկված!**", reply_markup=self.get_main_menu())
            
        @self.bot.on_message(filters.command("ask"))
        async def ask_cmd(client, message):
           if not self:
