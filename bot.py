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


load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
# Configure logging
#logging.basicConfig(level=logging.INFO)
# Initialize dispatcher
dp = Dispatcher()

class Form(StatesGroup):
    asking_calendar_url = State()


async def set_bot_commands(bot: Bot):
    commands = [
        BotCommand(command="start", description="Start the bot")
    ]
    await bot.set_my_commands(commands)


@dp.message(CommandStart())
async def ask_calendar_url(message: Message, state: FSMContext) -> None:
    kuss_cal_url = "https://kusss.jku.at/kusss/ical-multi-form-sz.action"
    msg = textwrap.dedent(f"""\
    Hi! Please enter your calendar subscription URL.

    Where to find it:              
    <i><b><a href="{kuss_cal_url}">KUSSS:</a></b> Studyroom > Export Appointments

    P.s. It will be next to "Create / Delete" buttons</i>

    🔍 Stay organized and never miss an appointment! ✅
    """)
    await message.reply(msg)
    await state.set_state(Form.asking_calendar_url)


@dp.message(Form.asking_calendar_url)
async def ask_cal(message: Message) -> None:
    url = message.text
    schedule_msg = Schedule().get_daily_schedule(url)
    add_user_DB(message.from_user.id, url)
    confirmation_msg = textwrap.dedent((
    "🎉 Congratulations! You’ve been successfully added "
    "to the daily JKU schedule mailing list. "
    "Schedule will be sent to you every day at approximately <b>00:00.</b> "
    "Below is provided an example based on today's schedule. "
    "Stay organized and have an amazing day! ✨"))
    await message.reply(confirmation_msg)
    await message.reply(schedule_msg)


# Background task to send daily schedule
async def send_daily_schedule(bot):    
    # Get last mailing date
    last_mailing_date = sorted(get_all_mailing_history_DB())[-1][0]
    
    while True:
        updated_current_date = get_current_date()
        
        # Check if we have reached a new day
        if updated_current_date > last_mailing_date:
            users = get_all_users_DB()
            for telegram_id, url in users:
                try:
                    schedule_msg = Schedule().get_daily_schedule(url)
                    await bot.send_message(telegram_id, schedule_msg)
                except Exception as e:
                    print(f"Failed to send message to {telegram_id}: {e}")
            
            # Update last_mailing_date
            last_mailing_date = updated_current_date
            add_mailing_date_DB(last_mailing_date)
        
        # Calculate sleep time until next midnight
        next_midnight = datetime.combine(updated_current_date + timedelta(days=1), time(0, 0))
        current_time = get_current_date(time=True).replace(tzinfo=None)
        sleep_time = (next_midnight - current_time).total_seconds()
        await asyncio.sleep(sleep_time)


async def main() -> None:
    # Initialize Bot instance with default bot properties which will be passed to all API calls
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    # Set the bot commands
    await set_bot_commands(bot)
    # Start the background task
    asyncio.create_task(send_daily_schedule(bot))  
    # And the run events dispatching
    await dp.start_polling(bot)


if __name__ == "__main__":
    #logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    is_test = int(os.getenv("IS_TEST"))
    if is_test:
        drop_tables_DB()
        create_tables_DB()
        add_mailing_date_DB(get_current_date())
    asyncio.run(main())