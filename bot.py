from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, BotCommand
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv
import asyncio
import os
import traceback
import textwrap
from schedule import Schedule
from db_interaction import *


load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
# Configure logging
#logging.basicConfig(level=logging.INFO)
# Initialize dispatcher
dp = Dispatcher()

class Form(StatesGroup):
    asking_calendar_url = State()


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
    schedule_msg = Schedule(url).message
    add_user_DB(message.from_user.id, url)
    confirmation_msg = textwrap.dedent((
    "🎉 Congratulations! You’ve been successfully added "
    "to the daily JKU schedule mailing list. "
    "Schedule will be sent to you every day at <b>00:10.</b> "
    "Below provided example based on today's schedule. "
    "Stay organized and have an amazing day! ✨"))
    await message.reply(confirmation_msg)
    await message.reply(schedule_msg)


async def main() -> None:
    # Initialize Bot instance with default bot properties which will be passed to all API calls
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    # And the run events dispatching
    await dp.start_polling(bot)


if __name__ == "__main__":
    #logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    is_test = int(os.getenv("IS_TEST"))
    if is_test:
        drop_tables_DB()
        create_tables_DB()
    asyncio.run(main())