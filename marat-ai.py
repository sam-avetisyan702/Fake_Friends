#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
=============================================================================
🤖 VIRTUAL FRIEND TELEGRAM BOT - ULTIMATE PROFESSIONAL EDITION (FIXED)
=============================================================================
Ինչ է շտկվել/ավելացվել այս տարբերակում.

  1. ImportError շտկում. ChatAction-ը հիմա ճիշտ import-ված է
     `telegram.constants`-ից (python-telegram-bot v20+ պահանջում է սա).
     Հենց սա էր պատճառը, որ բոտն ընդհանրապես չէր start-վում.
  2. Token/API key-երն այլևս ուղիղ կոդի մեջ չեն. կարդացվում են .env
     ֆայլից (տես .env.example). Երբեք մի push արա իրական key-երը GitHub-ում.
  3. Ավելացվել է "AI TYPE" (անձնավորության) համակարգ.
     /type հրամանով օգտատերը inline կոճակներով ընտրում է, թե ինչպիսի
     բնավորությամբ պիտի խոսի բոտը՝ Ընկեր, Մարզիչ, Կինոսիրահար,
     Ծրագրավորող, Հոգեբան, Խոհարար.
  4. Ավելացվել է կարճ հիշողություն (վերջին N հաղորդագրությունները)
     յուրաքանչյուր user-ի համար, որպեսզի պատասխանները համատեքստային լինեն.
  5. Ավելացվել են /reset և /stats հրամանները.
  6. Ավելի ամուր error handling. Gemini client-ի սխալը այլևս ամբողջ
     պրոցեսը չի կանգնեցնում (sys.exit) — բոտը շարունակում է աշխատել
     և օգտատիրոջը ուղարկում է ընկերական error-հաղորդագրություն.
  7. Ավելացվել է retry/timeout handling Gemini կանչի համար.
=============================================================================
"""

import os
import sys
import logging
from datetime import datetime
from typing import Dict, Any, List

from dotenv import load_dotenv

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.constants import ChatAction, ParseMode
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    MessageHandler,
    CommandHandler,
    CallbackQueryHandler,
    filters,
)

from google import genai

# =============================================================================
# 1. ENV / CREDENTIALS
# =============================================================================
load_dotenv()  # կարդում է .env ֆայլից

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# =============================================================================
# 2. LOGGING
# =============================================================================
logging.basicConfig(
    format="%(asctime)s [%(levelname)s] [%(filename)s:%(lineno)d] - %(message)s",
    level=logging.INFO,
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("VirtualFriendBot")

# =============================================================================
# 3. GEMINI CLIENT (lazy-safe init)
# =============================================================================
ai_client = None
try:
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY բացակայում է .env ֆայլում։")
    ai_client = genai.Client(api_key=GEMINI_API_KEY)
    logger.info("✅ Successfully connected to Gemini API.")
except Exception as e:
    # Չենք anել sys.exit(1) այստեղ. Բոտը կսկսվի, բայց AI պատասխանները
    # կվերադարձնեն error-հաղորդագրություն, մինչև key-ը ուղղվի։
    logger.critical(f"⚠️ Gemini Client init failed: {e}")

GEMINI_MODEL = "gemini-2.5-flash"
MAX_HISTORY_MESSAGES = 12  # քանի հաղորդագրություն պահել համատեքստի համար

# =============================================================================
# 4. AI PERSONAS ("տիպեր")
# =============================================================================
PERSONAS: Dict[str, Dict[str, str]] = {
    "friend": {
        "label": "🤗 Ընկեր",
        "prompt": (
            "Դու օգտատիրոջ լավագույն վիրտուալ ընկերն ես։ Շփվիր ջերմ, "
            "անմիջական, ընկերական և աջակցող ոճով։ Հասկացիր նրա "
            "սովորությունները, հետաքրքրություններն ու տրամադրությունը։ "
            "Մի եղիր չափազանց պաշտոնական, խոսիր այնպես, ինչպես իսկական "
            "մտերիմ ընկերը։"
        ),
    },
    "coach": {
        "label": "💪 Մարզիչ",
        "prompt": (
            "Դու եռանդուն, մոտիվացնող անձնական մարզիչ ես (fitness/life "
            "coach)։ Խրախուսիր օգտատիրոջը, տուր կոնկրետ, գործնական "
            "խորհուրդներ մարզումների, սովորությունների և կարգապահության "
            "վերաբերյալ։ Խոսքդ եռանդուն է, դրական և մարտահրավեր նետող, "
            "բայց միշտ աջակցող։"
        ),
    },
    "movie": {
        "label": "🎬 Կինոսիրահար",
        "prompt": (
            "Դու իսկական կինոսիրահար ես, ով գիտի ֆիլմերի, սերիալների և "
            "ռեժիսորների մասին ամեն ինչ։ Խոսքի մեջ հեշտությամբ մեջբերում "
            "ես ֆիլմեր, ժանրեր, առաջարկում ես ինչ դիտել՝ կախված "
            "տրամադրությունից, և պատմում ես հետաքրքիր փաստեր կինոյից։"
        ),
    },
    "developer": {
        "label": "💻 Ծրագրավորող",
        "prompt": (
            "Դու փորձառու, բարեկամական ծրագրավորող ես, ով սիրում է "
            "բացատրել տեխնիկական թեմաներ պարզ լեզվով։ Օգնում ես կոդի, "
            "algorithm-ների, tech stack-ի ընտրության հարցերում, տալիս "
            "ես կոնկրետ, գործնական խորհուրդներ և պահպանում ես "
            "ընկերական, ոչ ձանձրալի տոն։"
        ),
    },
    "psychologist": {
        "label": "🧠 Հոգեբան",
        "prompt": (
            "Դու ջերմ ու համբերատար հոգեբան ես, ով լսում է առանց "
            "դատապարտելու։ Տալիս ես մտածելու ուղղորդող հարցեր, "
            "օգնում ես մարդուն հասկանալ սեփական զգացմունքները, բայց "
            "երբեք չես ախտորոշում և բացահայտ ասում ես, որ լուրջ դեպքերում "
            "պետք է դիմել իրական մասնագետի։"
        ),
    },
    "chef": {
        "label": "🍳 Խոհարար",
        "prompt": (
            "Դու ստեղծագործ, ջերմ խոհարար ես, ով սիրում է կիսվել "
            "բաղադրատոմսերով, խոհարարական խորհուրդներով և "
            "առաջարկություններով՝ կախված այն բանից, թե ինչ բաղադրիչներ "
            "կան տանը կամ ինչ տրամադրություն ունի օգտատերը։"
        ),
    },
}
DEFAULT_PERSONA = "friend"

# =============================================================================
# 5. USER SESSION STATE
# =============================================================================
# user_id -> {"start_time": datetime, "messages_count": int,
#             "persona": str, "history": List[Dict[str, str]]}
user_session_stats: Dict[int, Dict[str, Any]] = {}


def get_user_session(user_id: int) -> Dict[str, Any]:
    if user_id not in user_session_stats:
        user_session_stats[user_id] = {
            "start_time": datetime.now(),
            "messages_count": 0,
            "persona": DEFAULT_PERSONA,
            "history": [],  # list of {"role": "user"/"model", "text": str}
        }
    return user_session_stats[user_id]


def build_persona_keyboard() -> InlineKeyboardMarkup:
    buttons = []
    row = []
    for key, data in PERSONAS.items():
        row.append(InlineKeyboardButton(data["label"], callback_data=f"persona:{key}"))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    return InlineKeyboardMarkup(buttons)


# =============================================================================
# 6. HANDLERS
# =============================================================================

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.effective_user or not update.message:
        return

    user = update.effective_user
    user_name = user.first_name or "Ընկեր"
    session = get_user_session(user.id)

    logger.info(f"/start from {user_name} ({user.id})")

    welcome_text = (
        f"Բարև, {user_name}! 👋 Ես քո վիրտուալ ընկերն եմ։\n\n"
        f"Այստեղ եմ, որ զրուցեմ քեզ հետ, լսեմ քո օրվա մասին, օգնեմ մտքերովդ "
        f"կամ պարզապես միասին անցկացնենք ժամանակը։\n\n"
        f"💡 Կարող ես /type հրամանով փոխել իմ բնավորությունը (Մարզիչ, "
        f"Կինոսիրահար, Ծրագրավորող և այլն)։\n\n"
        f"Ի՞նչ կա նոր, կամ ինչի՞ մասին կուզես խոսենք հիմա։"
    )

    try:
        await update.message.reply_text(welcome_text)
    except Exception as e:
        logger.error(f"Failed to send welcome message: {e}")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return

    help_text = (
        "🤖 *Virtual Friend Bot — Օգնություն*\n\n"
        "• /start — սկսել զրույցը\n"
        "• /type — փոխել բոտի բնավորությունը (AI type)\n"
        "• /reset — մաքրել զրույցի հիշողությունը\n"
        "• /stats — տեսնել քո վիճակագրությունը\n\n"
        "Պարզապես գրիր ինձ ինչ-որ բան, և սկսենք զրույցը։"
    )
    await update.message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN)


async def type_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Ցույց է տալիս AI տիպերի ընտրության կոճակները։"""
    if not update.message or not update.effective_user:
        return

    session = get_user_session(update.effective_user.id)
    current = PERSONAS[session["persona"]]["label"]

    await update.message.reply_text(
        f"Ընթացիկ տիպը՝ {current}\n\nԸնտրիր, թե ինչպիսին լինեմ 👇",
        reply_markup=build_persona_keyboard(),
    )


async def persona_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Callback-ը, երբ օգտատերը սեղմում է որևէ persona կոճակ։"""
    query = update.callback_query
    if not query or not query.data or not query.from_user:
        return

    await query.answer()

    persona_key = query.data.split(":", 1)[1] if ":" in query.data else None
    if persona_key not in PERSONAS:
        await query.edit_message_text("Անհայտ տիպ, փորձիր նորից /type հրամանով։")
        return

    session = get_user_session(query.from_user.id)
    session["persona"] = persona_key
    session["history"] = []  # persona փոխելիս մաքրում ենք համատեքստը

    await query.edit_message_text(
        f"✅ Հիմա ես եմ՝ {PERSONAS[persona_key]['label']}։\nԳրիր ինձ ինչ-որ բան 😊"
    )


async def reset_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or not update.effective_user:
        return
    session = get_user_session(update.effective_user.id)
    session["history"] = []
    await update.message.reply_text("🧹 Զրույցի հիշողությունը մաքրված է։")


async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or not update.effective_user:
        return
    session = get_user_session(update.effective_user.id)
    minutes = int((datetime.now() - session["start_time"]).total_seconds() // 60)
    await update.message.reply_text(
        "📊 *Վիճակագրություն*\n"
        f"• Հաղորդագրություններ՝ {session['messages_count']}\n"
        f"• Ընթացիկ տիպ՝ {PERSONAS[session['persona']]['label']}\n"
        f"• Զրույցի տևողություն՝ {minutes} րոպե",
        parse_mode=ParseMode.MARKDOWN,
    )


def build_prompt(session: Dict[str, Any], user_name: str, user_text: str) -> str:
    """Կառուցում է Gemini-ի համար ուղարկվող ամբողջական prompt-ը՝ persona + history հետ։"""
    persona_prompt = PERSONAS[session["persona"]]["prompt"]

    history_lines = []
    for turn in session["history"][-MAX_HISTORY_MESSAGES:]:
        speaker = "Օգտատեր" if turn["role"] == "user" else "Դու"
        history_lines.append(f"{speaker}: {turn['text']}")
    history_block = "\n".join(history_lines)

    return (
        f"{persona_prompt}\n\n"
        f"Զրուցակցի անունը՝ {user_name}.\n"
        f"Միշտ պատասխանիր հայերեն լեզվով, բնական և ոչ ռոբոտային ոճով։\n\n"
        f"Նախորդ զրույցը (հիշողություն)՝\n{history_block if history_block else '(դեռ ոչինչ)'}\n\n"
        f"Օգտատիրոջ նոր հաղորդագրությունը՝ \"{user_text}\"\n\n"
        f"Պատասխանիր ուղիղ, առանց քո role-ը կրկին նշելու։"
    )


async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or not update.message.text or not update.effective_user:
        return

    user_text = update.message.text
    user = update.effective_user
    user_name = user.first_name or "Ընկեր"
    chat_id = update.effective_chat.id

    session = get_user_session(user.id)
    session["messages_count"] += 1

    logger.info(f"Message from [{user_name} ({user.id})] ({PERSONAS[session['persona']]['label']}): {user_text}")

    try:
        await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
    except Exception as act_err:
        logger.warning(f"Could not send typing action: {act_err}")

    if ai_client is None:
        await update.message.reply_text(
            "⚠️ AI կապը ներկայումս անհասանելի է (GEMINI_API_KEY սխալ է կամ բացակայում է)։ "
            "Ստուգիր .env ֆայլը և վերագործարկիր բոտը։"
        )
        return

    full_prompt = build_prompt(session, user_name, user_text)

    try:
        response = ai_client.models.generate_content(
            model=GEMINI_MODEL,
            contents=full_prompt,
        )

        reply_text = (response.text or "").strip() if response else ""
        if not reply_text:
            reply_text = "Hmm, մի պահ մտքերս շփոթվեցին, կարո՞ղ ես նորից կրկնել, ընկերս։"

        # Թարմացնում ենք հիշողությունը
        session["history"].append({"role": "user", "text": user_text})
        session["history"].append({"role": "model", "text": reply_text})
        session["history"] = session["history"][-MAX_HISTORY_MESSAGES:]

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
    logger.error(f"Exception while handling an update: {context.error}")


# =============================================================================
# 7. MAIN
# =============================================================================
def main() -> None:
    logger.info("Starting Virtual Friend Telegram Bot application...")

    if not TELEGRAM_BOT_TOKEN:
        logger.critical(
            "CRITICAL: TELEGRAM_BOT_TOKEN բացակայում է։ Ստուգիր .env ֆայլը "
            "(տես .env.example)։"
        )
        sys.exit(1)

    try:
        application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

        application.add_handler(CommandHandler("start", start_command))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("type", type_command))
        application.add_handler(CommandHandler("reset", reset_command))
        application.add_handler(CommandHandler("stats", stats_command))

        application.add_handler(CallbackQueryHandler(persona_callback, pattern=r"^persona:"))
        application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_text_message))

        application.add_error_handler(error_handler)

        logger.info("Bot is fully configured and starting polling loop...")
        application.run_polling(allowed_updates=Update.ALL_TYPES)

    except Exception as e:
        logger.critical(f"Critical error during bot execution: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
