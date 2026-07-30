#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, CommandHandler, filters
from google import genai

# Սահմանում ենք լոգավորման (logging) մանրամասն կարգավորումներ, որ տեսնենք ամեն ինչ սերվերում
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Վերցնում ենք բանալիները Environment Variables-ից
TELEGRAM_TOKEN = os.environ.get("8766725521:AAE2fEB8-2nu05ON026ILLV3-avcEp1q2fc")
GEMINI_KEY = os.environ.get("AQ.Ab8RN6JyJ534KX4FUxkhvWsSkS_r6SE3UAMZJ5tC9JBNJSYuAw")

# Ստուգում ենք բանալիների առկայությունը
if not TELEGRAM_TOKEN:
    logger.error("❌ Սխալ: TELEGRAM_BOT_TOKEN-ը գտնված չէ Environment Variables-ում!")
    sys.exit(1)

if not GEMINI_KEY:
    logger.error("❌ Սխալ: GEMINI_API_KEY-ը գտնված չէ Environment Variables-ում!")
    sys.exit(1)

# Ինիցիալիզացնում ենք Gemini AI հաճախորդը նոր google-genai գրադարանով
try:
    ai_client = genai.Client(api_key=GEMINI_KEY)
    logger.info("✅ Gemini AI հաճախորդը հաջողությամբ ստեղծվեց։")
except Exception as e:
    logger.error(f"❌ Չհաջողվեց միանալ Gemini AI-ին: {e}")
    sys.exit(1)

# Բոտի անձնական նկարագրությունը (System Prompt)
SYSTEM_PROMPT = (
    "Դու օգտատիրոջ լավագույն վիրտուալ ընկերն ես։ "
    "Շփվիր ջերմ, անմիջական, ընկերական ոճով, հասկացիր նրա սովորություններն ու հետաքրքրությունները։ "
    "Պատասխանիր հայերեն, եղիր հետաքրքրասեր, աջակցող և դրական։"
)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Մշակում է /start հրամանը"""
    user_name = update.effective_user.first_name or "Ընկեր"
    logger.info(f"👤 /start հրամանը ստացվեց {user_name}-ից")
    welcome_text = f"Բարև, {user_name}! Ես քո վիրտուալ ընկերն եմ։ Պատրաստ եմ շփվելու և զրուցելու քեզ հետ։ Գրիր ինձ ինչ-որ բան։"
    await update.message.reply_text(welcome_text)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Մշակում է օգտատիրոջ ուղարկած բոլոր տեքստային հաղորդագրությունները"""
    if not update.message or not update.message.text:
        return

    user_text = update.message.text
    user_name = update.effective_user.first_name or "Ընկեր"
    chat_id = update.effective_chat.id
    
    logger.info(f"📩 Հաղորդագրություն ստացվեց ({user_name}-ից): {user_text}")

    # Ուղարկում ենք գրելու կարգավիճակ (typing status), որ բոտը կենդանի երևա
    try:
        await context.bot.send_chat_action(chat_id=chat_id, action="typing")
    except Exception as e:
        logger.warning(f"⚠️ Չհաջողվեց ուղարկել chat action: {e}")

    try:
        # Կանչում ենք Gemini AI մոդելը (gemini-2.5-flash)
        response = ai_client.models.generate_content(
            model='gemini-2.5-flash',
            contents=f"{SYSTEM_PROMPT}\n\nՕգտատեր {user_name}-ն ասում է՝ {user_text}"
        )
        
        reply_text = response.text if response and response.text else "Hmm, ինչ-որ բան այն չէ, չկարողացա պատասխանել։"
        
        logger.info(f"🤖 AI-ի պատասխանը ({user_name}-ին): {reply_text[:50]}...")
        await update.message.reply_text(reply_text)

    except Exception as e:
        logger.error(f"❌ AI գեներացման սխալ: {e}")
        await update.message.reply_text("Ցավոք, այս պահին տեխնիկական փոքրիկ խնդիր առաջացավ AI-ի հետ կապված։ Փորձիր մի փոքր ուշ։")

def main():
    """Հիմնական ֆունկցիա, որը գործարկում է բոտը"""
    logger.info("🚀 Բոտի սկզբնավորում...")
    
    try:
        # Ստեղծում ենք Telegram Application-ը
        application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

        # Ավելացնում ենք հրամանների և հաղորդագրությունների լսիչները
        application.add_handler(CommandHandler("start", start_command))
        application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

        logger.info("🤖 Virtual Friend բոտը հաջողությամբ միացավ և սկսեց լսել հաղորդագրությունները...")
        
        # Գործարկում ենք պոլինգը
        application.run_polling(allowed_updates=Update.ALL_TYPES)

    except Exception as e:
        logger.error(f5"❌ Կրիտիկական սխալ բոտի աշխատանքի ժամանակ: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
