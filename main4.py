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

# List of historical event prompts about Georgia, USA with new identifiers
HISTORICAL_PROMPTS = [
    "/text Describe in detail the founding of Georgia as a British colony by James Oglethorpe and its early development on December 17?",
    "/chat Provide a detailed account of the Native American tribes, such as the Cherokee and Creek, in Georgia and their interactions with settlers on December 17?",
    "/voice Give a thorough description of Georgia’s role in the American Revolution, including key events and figures, on December 17?",
    "/textplus List and describe in detail the major Civil War events in Georgia, such as Sherman’s March to the Sea, that occurred on December 17?",
    "/chatplus Provide a detailed description of Georgia’s contributions to the Civil Rights Movement, including events in Atlanta, on December 17?",
    "/voiceplus Describe significant modern historical events in Georgia, such as Atlanta’s growth as a major city, that took place on December 17?"
]

# List of musician prompts with new identifiers (unchanged)
MUSICIAN_PROMPTS = [
    "/text Which notable musicians passed away on December 17 in history?",
    "/chat Which notable musicians passed away on December 17 in history?",
    "/voice Which notable musicians passed away on December 17 in history?",
    "/textplus Which notable musicians passed away on December 17 in history?",
    "/chatplus Which notable musicians passed away on December 17 in history?",
    "/voiceplus Which notable musicians passed away on December 17 in history?",
    "/text Which notable musicians passed away on December 17 in history?"
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
    date_str = current_date.strftime("%B %d")  # e.g., "June 15"

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
            interval=21600,  # 6 hours
            first=0,  # Start immediately
            data={"historical_count": 0, "musician_count": 0}
        )

        logger.info("Starting bot polling...")
        application.run_polling()
    except Exception as e:
        logger.error(f"Bot failed to start: {str(e)}", exc_info=True)

if __name__ == "__main__":
    main()
