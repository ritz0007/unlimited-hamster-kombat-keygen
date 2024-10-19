from pyrogram.types import BotCommand

async def set_bot_commands(bot):
    commands = [
        BotCommand("start", "Start the bot"),
        BotCommand("getkeys" "Get Hamster Game Keys"),
        BotCommand("about", "Get to know about the bot"),
        BotCommand("help", "Help menu"),
        BotCommand("broadcast", "Broadcast messages to users"),
        BotCommand("speed_broadcast", "Ultra speed method of broadcast"),
    ]
    
    await bot.set_bot_commands(commands)