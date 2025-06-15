import logging
import asyncio
from telethon import TelegramClient
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta

# Load environment variables
load_dotenv()
API_ID = os.getenv('API_ID')
API_HASH = os.getenv('API_HASH')  # Must provide a valid api_hash
TARGET_GROUP_IDS = os.getenv('TARGET_GROUP_IDS', '2389474950,2466861703,2491432519,2329211369,2284070859,2184790995').split(',')

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

# Create the client
client = TelegramClient('historycycle_session', API_ID, API_HASH)

async def send_history_message(historical_count, musician_count):
    logger.info("Executing send_history_message job...")
    now = datetime.now()
    start_date = datetime(2025, 3, 22)  # Starting date
    days_since_start = (now - start_date).days
    historical_index = historical_count % len(HISTORICAL_PROMPTS)
    musician_index = musician_count % len(MUSICIAN_PROMPTS)

    # Update date in prompts
    current_date = start_date + timedelta(days=days_since_start)
    date_str = current_date.strftime("%B %d")  # e.g., "June 15"

    historical_prompt = HISTORICAL_PROMPTS[historical_index].replace("December 17", date_str)
    musician_prompt = MUSICIAN_PROMPTS[musician_index].replace("December 17", date_str)

    for group_id in TARGET_GROUP_IDS:
        try:
            target_id = int(group_id.strip())
            # Send historical prompt
            await client.send_message(
                entity=target_id,
                message=historical_prompt
            )
            logger.info(f"Sent historical prompt {historical_index + 1}/{len(HISTORICAL_PROMPTS)} to group {target_id}")

            # Wait 5 seconds
            await asyncio.sleep(5)

            # Send musician prompt
            await client.send_message(
                entity=target_id,
                message=musician_prompt
            )
            logger.info(f"Sent musician prompt {musician_index + 1}/{len(MUSICIAN_PROMPTS)} to group {target_id}")
        except Exception as e:
            logger.error(f"Failed to send message to {group_id}: {str(e)}")

    return historical_count + 1, musician_count + 1

async def main():
    await client.start()
    logger.info("Userbot is running. It will send historical and musician prompts to the target groups every 6 hours from your account.")
    
    historical_count = 0
    musician_count = 0
    
    while True:
        historical_count, musician_count = await send_history_message(historical_count, musician_count)
        await asyncio.sleep(21600)  # 6 hours

# Run the bot
with client:
    client.loop.run_until_complete(main())
