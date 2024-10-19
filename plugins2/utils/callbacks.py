from plugins2.database import users_db2 as users_db
from pyrogram import Client
from plugins2.commands import start, help, about
from plugins2.admins import status


@Client.on_callback_query()
async def cb_data(_, callback_query):
    print(f"Callback data received: {callback_query.data}")
    await users_db.add_user(callback_query.from_user.id)
    if callback_query.data == "start":
        await start(_, callback_query)
    elif callback_query.data == "help":
        await help(_, callback_query)
    elif callback_query.data == "about":
        await about(_, callback_query)
    elif callback_query.data == "close":
        await callback_query.message.delete()
    elif callback_query.data == "botstatus":
        await status(_, callback_query)