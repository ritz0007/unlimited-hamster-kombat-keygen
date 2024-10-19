from .database import users_db2 as users_db
from pyrogram import Client, filters
from .utils.buttons import HELP_BUTTONS, START_BUTTONS, ABOUT_BUTTONS
from .utils.constants import START_TEXT, HELP_TEXT, ABOUT_TEXT
from .config import cb_status


@Client.on_message(filters.private & filters.command(["start"]))
async def start(bot, message):
    await users_db.add_user(message.from_user.id)
    user_mention = message.from_user.mention
    start_text = START_TEXT.replace("{mention_user}", user_mention)
    await cb_status(message, start_text, START_BUTTONS)

@Client.on_message(filters.private & filters.command(["help"]))
async def help(bot, message):
    await users_db.add_user(message.from_user.id)
    await cb_status(message, HELP_TEXT, HELP_BUTTONS)

@Client.on_message(filters.private & filters.command(["about"]))
async def about(bot, message):
    await users_db.add_user(message.from_user.id)
    await cb_status(message, ABOUT_TEXT, ABOUT_BUTTONS)
