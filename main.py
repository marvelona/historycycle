import logging
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta

# Load environment variables
load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')
TARGET_USER_ID = os.getenv('TARGET_USER_ID', '5313257171')

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s - %(pathname)s:%(lineno)d',
    level=logging.INFO,
    handlers=[logging.StreamHandler(), logging.FileHandler('historycycle.log')]
)
logger = logging.getLogger(__name__)

# List of historical event prompts with identifiers
HISTORICAL_PROMPTS = [
    "/chat Describe in detail, What important historical events took place in Australia or New Zealand on December 17?",
    "/grok Could you describe in detail the major historical events that happened in Canada on December 17?",
    "/R1 Give a thorough account and details of key events that influenced the United States on December 17?",
    "/perplexity List the major historical events and describe them in detail that occurred in the United Kingdom (including England, Scotland, Wales, Ireland, and London) on December 17?",
    "/deepseek Identify the significant historical events and describe them in detail that took place in Europe on December 17?",
    "/claude Provide a detailed description of important historical events in Russian history on December 17?"
]

# List of musician prompts with identifiers
MUSICIAN_PROMPTS = [
    "/ask Which notable musicians passed away on December 17 in history?",
    "/chat Which notable musicians passed away on December 17 in history?",
    "/grok Which notable musicians passed away on December 17 in history?",
    "/R1 Which notable musicians passed away on December 17 in history?",
    "/perplexity Which notable musicians passed away on December 17 in history?",
    "/deepseek Which notable musicians passed away on December 17 in history?",
    "/claude Which notable musicians passed away on December 17 in history?"
]

async def send_history_message(context: ContextTypes.DEFAULT_TYPE):
    logger.info("Entering send_history_message function")
    now = datetime.now()
    start_date = datetime(2025, 3, 22)
    days_since_start = (now - start_date).days
    historical_index = context.job.data.get("historical_count", 0) % len(HISTORICAL_PROMPTS)
    musician_index = context.job.data.get("musician_count", 0) % len(MUSICIAN_PROMPTS)
    context.job.data["historical_count"] = historical_index + 1
    context.job.data["musician_count"] = musician_index + 1

    current_date = start_date + timedelta(days=days_since_start)
    date_str = current_date.strftime("%B %d")

    historical_prompt = HISTORICAL_PROMPTS[historical_index].replace("December 17", date_str)
    musician_prompt = MUSICIAN_PROMPTS[musician_index].replace("December 17", date_str)

    message = (
        f"📜 <b>History Prompt</b> 📜\n"
        f"{historical_prompt}\n"
        f"🎶 <b>Music Prompt</b> 🎶\n"
        f"{musician_prompt}\n"
        f"Enjoy exploring the past! 🌟"
    )

    try:
        target_id = int(TARGET_USER_ID)
        logger.info(f"Attempting to send message to {target_id}")
        await context.bot.send_message(
            chat_id=target_id,
            text=message,
            parse_mode="HTML"
        )
        logger.info(f"Sent prompts {historical_index + 1}/{len(HISTORICAL_PROMPTS)} (history) and {musician_index + 1}/{len(MUSICIAN_PROMPTS)} (music) to user {target_id}")
    except Exception as e:
        logger.error(f"Failed to send message to {TARGET_USER_ID}: {str(e)}")

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    if str(user_id) != TARGET_USER_ID:
        await update.message.reply_text("❌ This bot is configured for a specific user only.")
        return

    logger.info(f"Received /start from user {user_id}")
    await update.message.reply_text(
        "✨ <b>HistoryCycle Bot Started!</b> ✨\n"
        "I’ll send you historical and musician prompts every minute for testing.\n"
        "First prompt coming up now!",
        parse_mode="HTML"
    )

    # Trigger an immediate prompt and start the cycle
    context.job.data = {"historical_count": 0, "musician_count": 0}
    await send_history_message(context)
    if "history_job" not in context.bot_data:
        context.bot_data["history_job"] = context.job_queue.run_repeating(
            send_history_message, interval=60, first=60  # 1 minute for testing
        )
        logger.info("Started 1-minute prompt cycle for testing")

async def start(context: ContextTypes.DEFAULT_TYPE):
    logger.info("Bot started - Initializing job data")
    context.job.data = {"historical_count": 0, "musician_count": 0}
    await send_history_message(context)

def main():
    try:
        if not BOT_TOKEN:
            logger.error("BOT_TOKEN is not set in environment variables")
            return

        application = ApplicationBuilder().token(BOT_TOKEN).build()
        if application.job_queue is None:
            logger.error("JobQueue not initialized. Install with: pip install python-telegram-bot[job-queue]")
            return

        application.add_handler(CommandHandler("start", start_command))
        application.job_queue.run_once(start, 0)
        logger.info("Starting bot polling...")
        application.run_polling()
    except Exception as e:
        logger.error(f"Bot failed to start: {str(e)}", exc_info=True)

if __name__ == "__main__":
    main()
