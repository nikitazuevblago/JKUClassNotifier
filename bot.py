from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, BotCommand
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv
from datetime import datetime, timedelta, time
import asyncio
import os
import traceback
import textwrap
from schedule import *
from db_interaction import *
from custom_logging import logger


load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Initialize dispatcher
dp = Dispatcher()

class Form(StatesGroup):
    asking_calendar_url = State()


# Bot commands setup
async def set_bot_commands(bot: Bot):
    commands = [
        BotCommand(command="start", description="Start the bot")
    ]
    await bot.set_my_commands(commands)
    logger.info("Bot commands have been set successfully.")


# Handler for /start command
@dp.message(CommandStart())
async def ask_calendar_url(message: Message, state: FSMContext) -> None:
    logger.info(f"User {message.from_user.id} triggered /start command.")
    kuss_cal_url = "https://kusss.jku.at/kusss/ical-multi-form-sz.action"
    msg = textwrap.dedent(f"""\
    Hi! Please enter your calendar subscription URL.

    Where to find it:              
    <i><b><a href="{kuss_cal_url}">KUSSS:</a></b> Studyroom > Export Appointments

    P.s. It will be next to "Create / Delete" buttons</i>

    🔍 Stay organized and never miss an appointment! ✅
    """)
    await message.reply(msg)
    logger.info(f"Prompted user {message.from_user.id} for calendar URL.")
    await state.set_state(Form.asking_calendar_url)


# Handler for calendar URL input
@dp.message(Form.asking_calendar_url)
async def ask_cal(message: Message) -> None:
    url = message.text
    logger.info(f"Received calendar URL from user {message.from_user.id}: {url}")
    try:
        # Fetch schedule
        schedule_msg = Schedule().get_daily_schedule(url)

        # Check if user already registered 
        registered_users = [user for user, _ in get_all_users_DB()]
        if message.from_user.id in registered_users:
            remove_user_DB(message.from_user.id)
            logger.info(f"Registered user {message.from_user.id} successfully DELETED from database.")

        # Add user to the database
        add_user_DB(message.from_user.id, url)
        logger.info(f"User {message.from_user.id} successfully added to database.")
        
        # Send confirmation message
        confirmation_msg = textwrap.dedent((
            "🎉 Congratulations! You’ve been successfully added "
            "to the daily JKU schedule mailing list. "
            "Schedule will be sent to you every day at approximately <b>00:00.</b> "
            "Below is provided an example based on today's schedule. "
            "Stay organized and have an amazing day! ✨"))
        await message.reply(confirmation_msg)
        await message.reply(schedule_msg)
        logger.info(f"Sent confirmation and sample schedule to user {message.from_user.id}.")
    except Exception as e:
        logger.error(f"Failed to process URL for user {message.from_user.id}: {e}")
        await message.reply("⚠️ An error occurred while processing your calendar URL. Please try again.")


# Background task to send daily schedule
async def send_daily_schedule(bot):    
    logger.info("Daily schedule background task started.")
    try:
        # Get last mailing date
        last_mailing_date = sorted(get_all_mailing_history_DB())[-1][0]
        logger.info(f"Last mailing date retrieved: {last_mailing_date}")
    except Exception as e:
        logger.error(f"Failed to retrieve last mailing date: {e}")
        return

    while True:
        updated_current_date = get_current_date()

        # Check if it's a new day
        if updated_current_date > last_mailing_date:
            logger.info(f"New day detected: {updated_current_date}. Starting daily mailing.")
            users = get_all_users_DB()
            logger.info(f"Retrieved {len(users)} users for mailing.")

            for telegram_id, url in users:
                try:
                    schedule_msg = Schedule().get_daily_schedule(url)
                    await bot.send_message(telegram_id, schedule_msg)
                    logger.info(f"Sent schedule to user {telegram_id}.")
                except Exception as e:
                    logger.error(f"Failed to send message to {telegram_id}: {e}")
            
            # Update mailing date
            last_mailing_date = updated_current_date
            add_mailing_date_DB(last_mailing_date)
            logger.info(f"Updated mailing date to {last_mailing_date}.")

        # Sleep until next midnight
        next_midnight = datetime.combine(updated_current_date + timedelta(days=1), time(0, 0))
        current_time = get_current_date(time=True).replace(tzinfo=None)
        sleep_time = (next_midnight - current_time).total_seconds()
        logger.info(f"Sleeping for {sleep_time / 60:.2f} minutes until next midnight.")
        await asyncio.sleep(sleep_time)


# Main function
async def main() -> None:
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await set_bot_commands(bot)
    asyncio.create_task(send_daily_schedule(bot))  
    logger.info("Bot polling started.")
    await dp.start_polling(bot)

if __name__ == "__main__":
    is_test = int(os.getenv("IS_TEST"))
    if is_test:
        drop_tables_DB()
        create_tables_DB()
        logger.info("Test mode enabled. Dropping and recreating tables.")
        add_mailing_date_DB(get_current_date())
        logger.info("Test database setup completed.")
    logger.info("Starting bot...")
    asyncio.run(main())