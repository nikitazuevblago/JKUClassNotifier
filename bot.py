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
    asking_display_time = State()

# Task management
global_task = None
task_lock = asyncio.Lock()

# Bot commands setup
async def set_bot_commands(bot: Bot):
    commands = [
        BotCommand(command="start", description="Start the bot"),
        BotCommand(command="help", description="Show help information"),
        BotCommand(command="update_time", description="Update message display time"),
    ]
    await bot.set_my_commands(commands)
    logger.info("Bot commands have been set successfully.")

# Restart the daily schedule task
async def restart_send_daily_schedule(bot):
    global global_task
    async with task_lock:
        if global_task and not global_task.done():
            logger.info("Cancelling existing send_daily_schedule task.")
            global_task.cancel()
            try:
                await global_task
            except asyncio.CancelledError:
                logger.info("Existing task cancelled successfully.")

        logger.info("Starting a new send_daily_schedule task.")
        global_task = asyncio.create_task(send_daily_schedule(bot))

# Handler for /start command
@dp.message(CommandStart())
async def ask_calendar_url(message: Message, state: FSMContext) -> None:
    logger.info(f"User {message.from_user.id} triggered /start command.")
    kuss_cal_url = "https://kusss.jku.at/kusss/ical-multi-form-sz.action"
    msg = textwrap.dedent(f"""
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
async def ask_cal(message: Message, state: FSMContext) -> None:
    url = message.text
    logger.info(f"Received calendar URL from user {message.from_user.id}: {url}")
    try:
        schedule_msg = Schedule().get_daily_schedule(url)
        registered_users = [user for user, _ in get_all_users_DB()]

        if message.from_user.id in registered_users:
            remove_user_DB(message.from_user.id)
            logger.info(f"Registered user {message.from_user.id} successfully DELETED from database.")

        add_user_DB(message.from_user.id, url)
        logger.info(f"User {message.from_user.id} successfully added to database.")

        confirmation_msg = textwrap.dedent((
            "🎉 Congratulations! You’ve been successfully added "
            "to the daily JKU schedule mailing list. "
            "Schedule will be sent to you every day at approximately <b>00:00.</b> "
            "Below is provided an example based on today's schedule. "
            "Stay organized and have an amazing day! ✨"))
        await message.reply(confirmation_msg)
        await message.reply(schedule_msg)
        await state.clear()
        logger.info(f"Sent confirmation and sample schedule to user {message.from_user.id}.")

    except Exception as e:
        logger.error(f"Failed to process URL for user {message.from_user.id}: {e}")
        await message.reply("⚠️ An error occurred while processing your calendar URL. Please try again.")

async def send_daily_schedule(bot):
    logger.info("Daily schedule background task started.")
    while True:
        users = get_all_users_DB()
        current_time = datetime.now()

        for telegram_id, url, display_hour, display_minutes in users:
            user_time = time(display_hour, display_minutes)
            next_user_time = datetime.combine(current_time.date(), user_time)

            # Send immediately if the updated time is close to now
            if current_time.time() < user_time <= (current_time + timedelta(minutes=1)).time():
                try:
                    schedule_msg = Schedule().get_daily_schedule(url)
                    await bot.send_message(telegram_id, schedule_msg)
                    logger.info(f"Sent schedule to user {telegram_id}.")
                except Exception as e:
                    logger.error(f"Failed to send message to {telegram_id}: {e}")

        # Sleep for a short duration (e.g., 30 seconds) before checking again
        await asyncio.sleep(30)



@dp.message(Command("update_time"))
async def ask_display_time(message: Message, state: FSMContext) -> None:
    logger.info(f"User {message.from_user.id} triggered /update_time command.")
    msg = textwrap.dedent("""
    Please enter the new display time in the format <b>HH:MM</b> (e.g., 08:30 for 8:30 AM):
    """)
    await message.reply(msg)
    await state.set_state(Form.asking_display_time)

@dp.message(Form.asking_display_time)
async def update_display_time_handler(message: Message, state: FSMContext) -> None:
    time_input = message.text.strip()
    try:
        display_time = datetime.strptime(time_input, "%H:%M").time()
        display_hour = display_time.hour
        display_minutes = display_time.minute

        update_display_time(message.from_user.id, display_hour, display_minutes)
        logger.info(f"Display time for user {message.from_user.id} updated to {display_hour:02d}:{display_minutes:02d}.")

        await message.reply(f"✅ Your message display time has been updated to <b>{display_hour:02d}:{display_minutes:02d}</b>.")
        await state.clear()

        # Restart the background task with updated schedules
        await restart_send_daily_schedule(message.bot)

    except ValueError:
        logger.warning(f"Invalid time format received from user {message.from_user.id}: {time_input}")
        await message.reply("⚠️ Invalid time format. Please enter the time in <b>HH:MM</b> format (e.g., 08:30).")


async def main() -> None:
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await set_bot_commands(bot)

    global global_task
    global_task = asyncio.create_task(send_daily_schedule(bot))

    logger.info("Bot polling started.")
    await dp.start_polling(bot)

@dp.message(Command("help"))
async def show_help(message: Message) -> None:
    logger.info(f"User {message.from_user.id} requested help.")
    help_text = textwrap.dedent(f"""
    🤖 <b>JKU Schedule Bot Help</b>

    Available commands:
    /start - Start the bot and set up your calendar
    /help - Show this help message
    /update_time - configure the time of notification

    📅 <b>How to use:</b>
    1. Get your calendar URL from KUSSS
    2. Send it to the bot
    3. Receive daily schedule updates at midnight

    🔗 <b>Getting your calendar URL:</b>
    1. Go to KUSSS
    2. Navigate to Studyroom > Export Appointments
    3. Copy the calendar subscription URL

    ⚠️ <b>Note:</b> If you need to update your calendar URL, just use /start again.

    Need more help? Contact @YourUsername
    """)
    await message.reply(help_text)
    logger.info(f"Sent help information to user {message.from_user.id}.")


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
