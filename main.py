import os
from decouple import config
from pyrogram import Client, errors
import asyncio
import pyrogram.utils as utils
from plugins.database import users_db
from plugins.utils.commandslist import set_bot_commands
from plugins.generator import background_key_generator, initialize_proxy_rotator, load_keys_from_file, load_user_key_limits

BOT_TOKEN = config('BOT_TOKEN')
API_ID = config('API_ID', cast=int)
API_HASH = config('API_HASH')

load_keys_from_file()
load_user_key_limits()

def create_bot():
    return Client(
        f"session_files/Bot_{BOT_TOKEN.split(':')[0]}",
        bot_token=BOT_TOKEN,
        api_id=API_ID,
        api_hash=API_HASH,
        plugins=dict(root="plugins"),
    )

def get_peer_type(peer_id: int) -> str:
    print('get_peer_type call')
    peer_id_str = str(peer_id)
    if not peer_id_str.startswith("-"):
        return "user"
    elif peer_id_str.startswith("-100"):
        return "channel"
    else:
        return "chat"

utils.get_peer_type = get_peer_type


async def run_bot(bot):
    await bot.start()
    await initialize_proxy_rotator()
    await asyncio.create_task(background_key_generator(bot))

    try:
        await set_bot_commands(bot)
        # Save PID
        with open(f"pids/{bot.me.id}.pid", "w") as f:
            f.write(str(os.getpid()))
        # Keep the bot running
        await asyncio.Event().wait()
    except errors.FloodWait as e:
        print(f"Flood wait error for {bot.me.username}: Waiting for {e.value} seconds.")
        await asyncio.sleep(e.value)
    except ConnectionError as e:
        print(f"Connection error for {bot.me.username}: {e}")
    except asyncio.CancelledError:
        print(f"Shutting down {bot.me.username}...")
    finally:
        await bot.stop()

async def initialize_database(bot):
    try:
        await bot.start()  # Start the bot to get its information
    except errors.UserDeactivated:
        print(f"Bot {bot.bot_token.split(':')[0]} has been deactivated. Removing from database.")
    except Exception as e:
        print(f"Error initializing database for bot {bot.bot_token.split(':')[0]}: {e}")
    finally:
        try:
            if bot.is_initialized:
                await bot.stop()  # Stop the bot after initialization only if it's initialized
        except Exception as e:
            print(f"Error stopping bot {bot.bot_token.split(':')[0]}: {e}")

async def main():

    print("Bot is starting...")
    await users_db.initialize()
    
    # Create main bot
    main_bot = create_bot()
    
    
    # Run bot
    await run_bot(main_bot)
    print("Bot started!")


async def shutdown_signal_handler(loop, shutdown_event):
    try:
        await shutdown_event.wait()
    finally:
        tasks = [task for task in asyncio.all_tasks(loop) if task is not asyncio.current_task()]
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
        loop.stop()
        
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    shutdown_event = asyncio.Event()

    # Create a background task to handle shutdown signals
    shutdown_task = loop.create_task(shutdown_signal_handler(loop, shutdown_event))

    try:
        loop.run_until_complete(main())
    except (KeyboardInterrupt, SystemExit):
        print("Trying to shutdown...")
        shutdown_event.set()
    finally:
        try:
            # Cancel the shutdown_signal_handler task
            shutdown_task.cancel()
            # Wait for the task to be cancelled
            loop.run_until_complete(shutdown_task)
            # Shutdown asyncgens
            loop.run_until_complete(loop.shutdown_asyncgens())
        except asyncio.CancelledError:
            pass
        finally:
            print("Bot stopped!")
            loop.close()