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

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s - %(pathname)s:%(lineno)d',
    level=logging.INFO,
    handlers=[logging.StreamHandler(), logging.FileHandler('historycycle.log')]
)
logger = logging.getLogger(__name__)

# Group chat IDs for each identifier
GROUP_IDS = {
    "/chat": [
        "2389474950", "2466861703", "2491432519",
        "2329211369", "2284070859", "2184790995"
    ],
    "/grok": ["2343706272"],
    "/R1": ["2432319988"],
    "/perplexity": ["2432319988"],
    "/deepseek": ["2428801617"],
    "/claude": ["2414168078"],
    "/ask": ["2451627445"]
}

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
    date_str = current_date.strftime("%B %d")  # e.g., "April 10"

    historical_prompt = HISTORICAL_PROMPTS[historical_index].replace("December 17", date_str)
    musician_prompt = MUSICIAN_PROMPTS[musician_index].replace("December 17", date_str)

    message = (
        f"📜 <b>History Prompt</b> 📜\n"
        f"{historical_prompt}\n"
        f"🎶 <b>Music Prompt</b> 🎶\n"
        f"{musician_prompt}\n"
        f"Enjoy exploring the past! 🌟"
    )

    # Send to groups based on identifiers
    historical_id = historical_prompt.split()[0]  # e.g., "/chat"
    musician_id = musician_prompt.split()[0]
    historical_groups = GROUP_IDS.get(historical_id, [])
    musician_groups = GROUP_IDS.get(musician_id, [])

    all_groups = list(set(historical_groups + musician_groups))  # Combine unique group IDs
    for group_id in all_groups:
        try:
            await context.bot.send_message(
                chat_id=int(group_id),
                text=message,
                parse_mode="HTML"
            )
            logger.info(f"Sent prompts {historical_index + 1}/{len(HISTORICAL_PROMPTS)} (history) and {musician_index + 1}/{len(MUSICIAN_PROMPTS)} (music) to group {group_id}")
        except Exception as e:
            logger.error(f"Failed to send message to group {group_id}: {str(e)}")

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    # Allow /start from any user to trigger prompts, but send to groups
    logger.info(f"Received /start from user {user_id}")
    await update.message.reply_text(
        "✨ <b>HistoryCycle Bot Started!</b> ✨\n"
        "I’ll send historical and musician prompts to the designated groups every minute for testing.\n"
        "First prompt coming up now!",
        parse_mode="HTML"
    )
    # Trigger an immediate prompt
    await send_history_message(context)

async def send_initial_message(application):
    message = (
        f"📜 <b>Bot Online!</b> 📜\n"
        f"I’m live and will send history and musician prompts to groups every minute for testing! 🌟"
    )
    for identifier, groups in GROUP_IDS.items():
        for group_id in groups:
            try:
                await application.bot.send_message(
                    chat_id=int(group_id),
                    text=message,
                    parse_mode="HTML"
                )
                logger.info(f"Sent initial message to group {group_id}")
            except Exception as e:
                logger.error(f"Failed to send initial message to group {group_id}: {str(e)}")

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
        asyncio.get_event_loop().run_until_complete(send_initial_message(application))

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
