#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
=============================================================================
🤖 VIRTUAL FRIEND TELEGRAM BOT - ULTIMATE PROFESSIONAL EDITION
=============================================================================
* Features: Gemini 2.5/1.5 Flash Integration, Advanced Logging, 
  Error Handling, Friendly Persona, and Direct Key Embedding.
* Created for: Virtual Friend project on Railway / Local.
=============================================================================
"""

import os
import sys
import logging
import asyncio
from datetime import datetime
from typing import Dict, Any

# Telegram Bot Library
from telegram import Update, ChatAction
from telegram.ext import (
    ApplicationBuilder, 
    ContextTypes, 
    MessageHandler, 
    CommandHandler, 
    filters
)

# Google GenAI Library
from google import genai

# =============================================================================
# 1. LOGGING CONFIGURATION (Detailed Server Logs)
# =============================================================================
logging.basicConfig(
    format="%(asctime)s [%(levelname)s] [%(filename)s:%(lineno)d] - %(message)s",
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("VirtualFriendBot")

# =============================================================================
# 2. CREDENTIALS & API KEYS (Directly embedded as requested)
# =============================================================================
TELEGRAM_BOT_TOKEN = "8766725521:AAE2fEB8-2nu05ON026ILLV3-avcEp1q2fc"
GEMINI_API_KEY = "AQ.Ab8RN6JyJ534KX4FUxkhvWsSkS_r6SE3UAMZJ5tC9JBNJSYuAw"

# =============================================================================
# 3. INITIALIZING GOOGLE GEMINI CLIENT
# =============================================================================
logger.info("Initializing Google GenAI client...")
try:
    ai_client = genai.Client(api_key=GEMINI_API_KEY)
    logger.info("Successfully connected to Gemini API.")
except Exception as e:
    logger.critical(f"FATAL: Failed to initialize Gemini Client: {e}")
    sys.exit(1)

# =============================================================================
# 4. SYSTEM PROMPT & PERSONA CONFIGURATION
# =============================================================================
SYSTEM_PROMPT = (
    "Դու օգտատիրոջ լավագույն վիրտուալ ընկերն ես։ "
    "Շփվիր ջերմ, անմիջական, ընկերական և աջակցող ոճով։ "
    "Հասկացիր նրա սովորությունները, հետաքրքրություններն ու տրամադրությունը։ "
    "Միշտ պատասխանիր հայերեն լեզվով, եղիր հետաքրքրասեր, մի փոքր հումորով և շատ բնական։ "
    "Մի եղիր չափազանց պաշտոնական, խոսիր այնպես, ինչպես իսկական մտերիմ ընկերը։"
)

# Simple memory structure to track user interactions or statistics if needed
user_session_stats: Dict[int, Dict[str, Any]] = {}

# =============================================================================
# 5. HANDLER FUNCTIONS
# =============================================================================

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handles the /start command sent by the user.
    Welcomes the user and initializes their virtual friendship session.
    """
    if not update.effective_user or not update.message:
        return

    user = update.effective_user
    user_id = user.id
    user_name = user.first_name or "Ընկեր"
    
    logger.info(f"Received /start command from user: {user_name} (ID: {user_id})")
    
    # Track user session
    user_session_stats[user_id] = {
        "start_time": datetime.now(),
        "messages_count": 0
    }

    welcome_text = (
        f"Բարև, {user_name}! 👋 Ես քո վիրտուալ ընկերն եմ։\n\n"
        f"Այստեղ եմ, որ զրուցեմ քեզ հետ, լսեմ քո օրվա մասին, օգնեմ մտքերովդ կամ պարզապես միասին անցկացնենք ժամանակը։ "
        f"Ի՞նչ կա նոր, կամ ինչի՞ մասին կուզես խոսենք հիմա։"
    )

    try:
        await update.message.reply_text(welcome_text)
        logger.info(f"Successfully sent welcome message to {user_name}")
    except Exception as e:
        logger.error(f"Failed to send welcome message: {e}")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handles the /help command to give information about the bot.
    """
    if not update.message:
        return
        
    help_text = (
        "🤖 **Virtual Friend Bot - Օգնություն**\n\n"
        "Ես քո անձնական AI ընկերն եմ։ Ինձ կարողես գրել ցանկացած թեմայով՝\n"
        "• Զրուցել առօրյայիցդ ու նպատակներիցդ\n"
        "• Հարցեր տալ կամ խորհուրդ հարցնել\n"
        "• Կամ պարզապես կիսվել տրամադրությամբդ\n\n"
        "Պարզապես գրիր ինձ ինչ-որ բան, և սկսենք զրույցը։"
    )
    await update.message.reply_text(help_text, parse_mode="Markdown")


async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Core function that listens to all incoming text messages,
    sends 'typing' action, queries Gemini AI, and replies to the user.
    """
    if not update.message or not update.message.text or not update.effective_user:
        return

    user_text = update.message.text
    user = update.effective_user
    user_id = user.id
    user_name = user.first_name or "Ընկեր"
    chat_id = update.effective_chat.id

    logger.info(f"Message from [{user_name} ({user_id})]: {user_text}")

    # Update stats
    if user_id in user_session_stats:
        user_session_stats[user_id]["messages_count"] += 1
    else:
        user_session_stats[user_id] = {"start_time": datetime.now(), "messages_count": 1}

    # Show typing action so user knows the bot is processing
    try:
        await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
    except Exception as act_err:
        logger.warning(f"Could not send typing action: {act_err}")

    # Construct prompt for AI
    full_prompt = (
        f"{SYSTEM_PROMPT}\n\n"
        f"Տեղեկություն զրուցակցի մասին՝ Անունը՝ {user_name}.\n"
        f"Օգտատիրոջ հաղորդագրությունը՝ \"{user_text}\"\n\n"
        f"Պատասխանիր նրան որպես լավագույն ընկեր:"
    )

    try:
        # Call Google Gemini API (gemini-2.5-flash model)
        response = ai_client.models.generate_content(
            model='gemini-2.5-flash',
            contents=full_prompt
        )

        if response and response.text:
            reply_text = response.text.strip()
        else:
            reply_text = "Hmm, մի պահ մտքերս շփոթվեցին, կարո՞ղ ես նորից կրկնել, ընկերս։"

        logger.info(f"AI Response to [{user_name}]: {reply_text[:60]}...")
        await update.message.reply_text(reply_text)

    except Exception as e:
        logger.error(f"Error generating AI content for user {user_name}: {e}")
        error_reply = (
            "Ընկերս, փոքրիկ տեխնիկական խնդիր առաջացավ իմ կողմից, "
            "բայց շուտով ամեն ինչ կկարգավորվի։ Փորձիր մի փոքր ուշ գրել։"
        )
        await update.message.reply_text(error_reply)


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Global error handler for unexpected Telegram bot exceptions.
    """
    logger.error(f"Exception while handling an update: {context.error}")


# =============================================================================
# 6. MAIN EXECUTION FUNCTION
# =============================================================================
def main() -> None:
    """
    Starts the bot application, registers handlers, and begins polling.
    """
    logger.info("Starting Virtual Friend Telegram Bot application...")

    if not TELEGRAM_BOT_TOKEN or not GEMINI_API_KEY:
        logger.critical("CRITICAL: Tokens are missing inside the script!")
        sys.exit(1)

    try:
        # Build application
        application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

        # Register Command Handlers
        application.add_handler(CommandHandler("start", start_command))
        application.add_handler(CommandHandler("help", help_command))

        # Register Message Handler (listens to all standard text messages except commands)
        application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_text_message))

        # Register Error Handler
        application.add_error_handler(error_handler)

        logger.info("Bot is fully configured and starting polling loop...")
        
        # Start polling (runs continuously)
        application.run_polling(allowed_updates=Update.ALL_TYPES)

    except Exception as e:
        logger.critical(f"Critical error during bot execution: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
