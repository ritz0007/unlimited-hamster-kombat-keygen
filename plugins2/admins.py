import os
import time
import string
import random
import traceback
import asyncio
import psutil
import datetime
import aiofiles
from tqdm import tqdm
from .database import users_db2 as users_db
from pyrogram import Client, filters
from pyrogram.errors import FloodWait, InputUserDeactivated, UserIsBlocked, PeerIdInvalid, UserIsBot
from pyrogram.errors.exceptions.bad_request_400 import PeerIdInvalid
from .config import is_user_admin, cb_status
from .utils.buttons import NAVIGATION_BUTTONS
from decouple import config

PRO_ADMIN = config("PRO_ADMIN")


async def send_msg(user_id, message):
    try:
        await message.copy(chat_id=user_id)
        return 200, None
    except FloodWait as e:
        await asyncio.sleep(e.x)
        return send_msg(user_id, message)
    except InputUserDeactivated:
        return 400, f"{user_id} : deactivated\n"
    except UserIsBlocked:
        return 400, f"{user_id} : blocked the bot\n"
    except PeerIdInvalid:
        return 400, f"{user_id} : user id invalid\n"
    except UserIsBot:
        return 400, f"{user_id} : user is a bot\n"
    except Exception as e:
        return 500, f"{user_id} : {traceback.format_exc()}\n"

@Client.on_message(filters.private & filters.command("broadcast"))
async def broadcast(bot, message):
    is_admin = await is_user_admin(message.from_user.id)
    if not is_admin:
        await cb_status(message, "You do not have permission to use this command.")
        return

    if not message.reply_to_message:
        await message.reply_text("Please reply to a message to broadcast.")
        return

    broadcast_ids = {}
    all_users = await users_db.get_all_users()
    broadcast_msg = message.reply_to_message

    while True:
        broadcast_id = ''.join([random.choice(string.ascii_letters) for i in range(3)])
        if not broadcast_ids.get(broadcast_id):
            break

    out = await message.reply_text(
        text=f"Broadcast Started! You will be notified with log file when all the users are notified."
    )

    start_time = time.time()
    total_users = await users_db.total_users_count()
    done = 0
    failed = 0
    success = 0
    broadcast_ids[broadcast_id] = dict(total=total_users, current=done, failed=failed, success=success)


    async with aiofiles.open('broadcast.txt', 'w') as broadcast_log_file:
        for user in all_users:
            sts, msg = await send_msg(user_id=int(user[0]), message=broadcast_msg)
            if msg is not None:
                await broadcast_log_file.write(msg)
            if sts == 200:
                success += 1
            else:
                failed += 1
            if sts == 400:
                await users_db.delete_user(user[0])
            done += 1
            if broadcast_ids.get(broadcast_id) is None:
                break
            else:
                broadcast_ids[broadcast_id].update(dict(current=done, failed=failed, success=success))

    if broadcast_ids.get(broadcast_id):
        broadcast_ids.pop(broadcast_id)

    completed_in = datetime.timedelta(seconds=int(time.time() - start_time))
    await asyncio.sleep(3)
    await out.delete()

    broadcast_text = f"Broadcast completed in `{completed_in}`\n" \
                     f"\n<u>Total users:<u/> {total_users}\n--------\n**Processed:** `{done}`" \
                     f"\n**Sucess:** `{success}`\n**Failed:**`{failed}`"
    if failed == 0:
        await message.reply_text(text=broadcast_text, quote=True)
    else:
        await message.reply_document(document='broadcast.txt', caption=broadcast_text)
    os.remove('broadcast.txt')

@Client.on_message(filters.private & filters.command("speed_broadcast"))
async def speed_broadcast(bot, message):
    is_admin = await is_user_admin(message.from_user.id)
    if not is_admin:
        await cb_status(message, "You do not have permission to use this command.")
        return

    if not message.reply_to_message:
        await message.reply_text("Please reply to a message to broadcast.")
        return

    all_users = await users_db.get_all_users()
    broadcast_msg = message.reply_to_message
    
    out = await message.reply_text("Broadcast Started!")
    start_time = time.time()
    total_users = await users_db.total_users_count()
    done = 0
    failed = 0
    success = 0

    async with aiofiles.open('broadcast.txt', 'w') as broadcast_log_file:
        progress_bar = tqdm(total=total_users, desc="Broadcasting", ncols=70)
        last_update_time = time.time()
        
        for user in all_users:
            sts, msg = await send_msg(user_id=int(user[0]), message=broadcast_msg)
            if msg is not None:
                await broadcast_log_file.write(msg)
            if sts == 200:
                success += 1
            else:
                failed += 1
            if sts == 400:
                await users_db.delete_user(user[0])
            done += 1
            progress_bar.update(1)
            
            current_time = time.time()
            if current_time - last_update_time >= 4:
                await out.edit_text(f"Broadcast in progress...\n\nTotal: {total_users}\nDone: {done}\nSuccess: {success}\nFailed: {failed}")
                last_update_time = current_time
            
            # Limit to 10 items per second
            if done % 10 == 0:
                await asyncio.sleep(0.2)

    progress_bar.close()
    completed_in = datetime.timedelta(seconds=int(time.time() - start_time))
    await out.delete()

    broadcast_text = f"Broadcast completed in `{completed_in}`\n" \
                     f"\n<u>Total users:</u> {total_users}\n\n**Processed:** `{done}`" \
                     f"\n**Success:** `{success}`\n**Failed:** `{failed}`"
    if failed == 0:
        await message.reply_text(text=broadcast_text, quote=True)
    else:
        await message.reply_document(document='broadcast.txt', caption=broadcast_text)
    os.remove('broadcast.txt')

@Client.on_message(filters.private & filters.command(["status", "bot_status"]))
async def status(bot, message, cb=False):
    is_admin = await is_user_admin(message.from_user.id)
    if not is_admin:
        await cb_status(message, "You do not have permission to use this command.")
        return
    
    total_users = await users_db.total_users_count()
    cpu_usage = psutil.cpu_percent()
    ram_usage = psutil.virtual_memory().percent
    text = "🤖 Bot Status\n"
    text += f"\nTotal Users: {total_users}"
    text += f"\nCPU Usage: {cpu_usage}%"
    text += f"\nRAM Usage: {ram_usage}%"
    await cb_status(message, text, NAVIGATION_BUTTONS)


@Client.on_message(filters.private & filters.command(["get_users_db"]))
async def get_users_db(bot, message):
    if str(message.from_user.id) != PRO_ADMIN:
        await cb_status(message, "You do not have permission to use this command.")
        return

    all_users = await users_db.get_all_users()
    users_data = "ID\n" + "\n".join([str(user[0]) for user in all_users])

    with open("database/users_db.txt", "w", encoding="utf-8") as file:
        file.write(users_data)

    await bot.send_document(message.chat.id, "database/users_db.txt")


@Client.on_message(filters.private & filters.command(["get_bot_info_db"]))
async def get_bot_info_db(bot, message):
    if str(message.from_user.id) != PRO_ADMIN:
        await cb_status(message, "You do not have permission to use this command.")
        return

    bot_info = await users_db._fetchall("SELECT * FROM bot_info")
    bot_info_data = ""
    for info in bot_info:
        bot_info_data += f"Log Channel ID: {info[0]}\n"
        bot_info_data += f"Shortlink: {info[1]}\n"
        bot_info_data += f"Shortlink Domain: {info[2]}\n"
        bot_info_data += f"Get Shortlink: {info[3]}\n"
        bot_info_data += f"Start Message: {info[4]}\n"
        bot_info_data += f"Store Message: {info[5]}\n"
        bot_info_data += f"Start Button Names: {info[6]}\n"
        bot_info_data += f"Start Button Links: {info[7]}\n"
        bot_info_data += f"Store Button Names: {info[8]}\n"
        bot_info_data += f"Store Button Links: {info[9]}\n"
        bot_info_data += f"Autodel: {info[10]}\n"
        bot_info_data += f"Get Autodel: {info[11]}\n"
        bot_info_data += f"Bot Admins: {info[12]}\n"
        bot_info_data += f"Database Channel ID: {info[13]}\n\n"

    with open("database/bot_info_db.txt", "w", encoding="utf-8") as file:
        file.write(bot_info_data)

    await bot.send_document(message.chat.id, "database/bot_info_db.txt")

