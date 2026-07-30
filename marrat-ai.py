#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import asyncio
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from google import genai

# Կարգավորում ենք լոգավորումը (Logging)
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Քո տրամադրած բանալիները
TELEGRAM_TOKEN = "8766725521:AAE2fEB8-2nu05ON026ILLV3-avcEp1q2fc"
GEMINI_KEY = "AQ.Ab8RN6JyJ534KX4FUxkhvWsSkS_r6SE3UAMZJ5tC9JBNJSYuAw"

# Ստեղծում ենք Gemini AI հաճախորդը
ai_client = genai.Client(api_key=GEMINI_KEY)

# Բոտի անձնական նկարագրությունը / System Prompt-ը (Virtual Friend)
SYSTEM_PROMPT = (
    "Դու օգտատիրոջ լավագույն վիրտուալ ընկերն ես։ "
    "Շփվիր ջերմ, անմիջական, ընկերական ոճով, հասկացիր նրա սովորություններն ու հետաքրքրությունները։ "
    "Պատասխանիր հայերեն, եղիր հետաքրքրասեր, աջակցող և դրական։"
)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ֆունկցիա, որը լսում է հաղորդագրությունները և պատասխանում AI-ի միջոցով"""
    user_text = update.message.text
    user_name = update.effective_user.first_name or "Ընկեր"
    
    logger.info(f"Ստացված հաղորդագրություն {user_name}-ից: {user_text}")

    # Ցույց տանք, որ բոտը գրում է (typing status)
    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id, action="typing"
    )

    try:
        # Ուղարկում ենք տեքստը Gemini-ին (օգտագործելով gemini-2.5-flash կամ gemini-1.5-flash)
        response = ai_client.models.generate_content(
            model='gemini-2.5-flash',
            contents=f"{SYSTEM_PROMPT}\n\nՕգտատեր {user_name}-ն ասում է՝ {user_text}"
        )
        
        reply_text = response.text if response.text else "Hmm, ինչ-որ բան այն չէ, չկարողացա պատասխանել։"
        
        await update.message.reply_text(reply_text)

    except Exception as e:
        logger.error(f"AI Error-ի սխալ: {e}")
        await update.message.reply_text("Ցավոք, այս պահին կապի փոքրիկ խնդիր առաջացավ AI-ի հետ։")

def main():
    """Բոտի գործարկման հիմնական ֆունկցիան"""
    # Ստեղծում ենք Telegram Application-ը
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    # Ավելացնում ենք հաղորդագրությունների լսիչ (բացառելով բոտերի հրամանները եթե պետք է)
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

    logger.info("Virtual Friend բոտը սկսեց աշխատել...")
    
    # Գործարկում ենք պոլինգը (polling)
    application.run_polling()

if __name__ == "__main__":
    main()
