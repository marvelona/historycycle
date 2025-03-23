import logging
import asyncio
from telegram.ext import ApplicationBuilder, ContextTypes
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta

# Load environment variables
load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')
TARGET_USER_ID = int(os.getenv('TARGET_USER_ID', '5313257171'))  # Replace with your Telegram ID

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s - %(pathname)s:%(lineno)d',
    level=logging.INFO,
    handlers=[logging.StreamHandler(), logging.FileHandler('historycycle.log')]
)
logger = logging.getLogger(__name__)

# List of historical event prompts with /chat prefix
PROMPTS = [
    "/chat Describe in detail, What important historical events took place in Australia or New Zealand on December 17?",
    "/chat Could you describe in detail the major historical events that happened in Canada on December 17?",
    "/chat Give a thorough account and details of key events that influenced the United States on December 17?",
    "/chat List the major historical events and describe them in detail that occurred in the United Kingdom (including England, Scotland, Wales, Ireland, and London) on December 17?",
    "/chat Identify the significant historical events and describe them in detail that took place in Europe on December 17?",
    "/chat Provide a detailed description of important historical events in Russian history on December 17?"
]

async def send_history_message(context: ContextTypes.DEFAULT_TYPE):
    logger.info("Executing send_history_message job...")
    now = datetime.now()
    start_date = datetime(2025, 3, 22)  # Starting date: March 22, 2025
    days_since_start = (now - start_date).days
    prompt_index = (context.job.data["count"] % len(PROMPTS))
    context.job.data["count"] += 1

    current_date = start_date + timedelta(days=days_since_start)
    date_str = current_date.strftime("%B %d")  # e.g., "March 23"
    
    prompt = PROMPTS[prompt_index].replace("December 17", date_str)

    # Simplified message starting with the prompt
    message = f"{prompt}\nEnjoy exploring the past! 🌟"

    try:
        await context.bot.send_message(
            chat_id=TARGET_USER_ID,
            text=message,
            parse_mode="HTML"
        )
        logger.info(f"Sent prompt {prompt_index + 1}/{len(PROMPTS)} to user {TARGET_USER_ID}")
    except Exception as e:
        logger.error(f"Failed to send message to {TARGET_USER_ID}: {str(e)}")

async def send_initial_message(application):
    message = (
        f"📜 <b>Bot Online!</b> 📜\n"
        f"I’m live and will send your history prompts every 6 hours! 🌟"
    )
    try:
        await application.bot.send_message(
            chat_id=TARGET_USER_ID,
            text=message,
            parse_mode="HTML"
        )
        logger.info(f"Sent initial message to user {TARGET_USER_ID}")
    except Exception as e:
        logger.error(f"Failed to send initial message to {TARGET_USER_ID}: {str(e)}")

def main():
    try:
        application = ApplicationBuilder().token(BOT_TOKEN).build()
        if application.job_queue is None:
            logger.error("JobQueue not initialized. Install with: pip install python-telegram-bot[job-queue]")
            return
        
        # Send an initial message to confirm bot is live
        asyncio.get_event_loop().run_until_complete(send_initial_message(application))

        # Start the automated messaging
        logger.info("Scheduling automated messaging...")
        application.job_queue.run_repeating(
            send_history_message,
            interval=21600,  # 6 hours
            first=0,  # Start immediately
            data={"count": 0}  # Initial counter
        )

        logger.info("Starting bot polling...")
        application.run_polling()
    except Exception as e:
        logger.error(f"Bot failed to start: {str(e)}", exc_info=True)

if __name__ == "__main__":
    main()