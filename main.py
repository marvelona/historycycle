import logging
import asyncio
from telegram.ext import ApplicationBuilder, ContextTypes
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta

# Load environment variables
load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')
TARGET_USER_ID = os.getenv('TARGET_USER_ID', '5359112184')

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
    logger.info("Executing send_history_message job...")
    now = datetime.now()
    start_date = datetime(2025, 3, 22)  # Starting date
    days_since_start = (now - start_date).days
    historical_index = context.job.data["historical_count"] % len(HISTORICAL_PROMPTS)
    musician_index = context.job.data["musician_count"] % len(MUSICIAN_PROMPTS)
    context.job.data["historical_count"] += 1
    context.job.data["musician_count"] += 1

    # Update date in prompts
    current_date = start_date + timedelta(days=days_since_start)
    date_str = current_date.strftime("%B %d")  # e.g., "April 11"

    historical_prompt = HISTORICAL_PROMPTS[historical_index].replace("December 17", date_str)
    musician_prompt = MUSICIAN_PROMPTS[musician_index].replace("December 17", date_str)

    try:
        target_id = int(TARGET_USER_ID)
        # Send historical prompt
        await context.bot.send_message(
            chat_id=target_id,
            text=historical_prompt
        )
        logger.info(f"Sent historical prompt {historical_index + 1}/{len(HISTORICAL_PROMPTS)} to user {target_id}")

        # Wait 5 seconds
        await asyncio.sleep(5)

        # Send musician prompt
        await context.bot.send_message(
            chat_id=target_id,
            text=musician_prompt
        )
        logger.info(f"Sent musician prompt {musician_index + 1}/{len(MUSICIAN_PROMPTS)} to user {target_id}")
    except Exception as e:
        logger.error(f"Failed to send message to {TARGET_USER_ID}: {str(e)}")

def main():
    try:
        if not BOT_TOKEN:
            logger.error("BOT_TOKEN is not set in environment variables")
            return

        application = ApplicationBuilder().token(BOT_TOKEN).build()
        if application.job_queue is None:
            logger.error("JobQueue not initialized. Install with: pip install python-telegram-bot[job-queue]")
            return

        logger.info("Scheduling automated messaging...")
        application.job_queue.run_repeating(
            send_history_message,
            interval=60,  # 1 minute for testing
            first=0,  # Start immediately
            data={"historical_count": 0, "musician_count": 0}
        )

        logger.info("Starting bot polling...")
        application.run_polling()
    except Exception as e:
        logger.error(f"Bot failed to start: {str(e)}", exc_info=True)

if __name__ == "__main__":
    main()
