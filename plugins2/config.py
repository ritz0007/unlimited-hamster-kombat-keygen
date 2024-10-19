from decouple import config

async def is_user_admin(user_id):
    pro_admin = config("PRO_ADMIN")
    if pro_admin is None:
        return False
    if str(user_id) not in pro_admin.split(","):
        return False
    return True

async def cb_status(message, text, reply_markup=None, disable_web_page_preview=True, quote=True):
    if hasattr(message, 'message'):
        await message.message.edit_text(
            text=text,
            reply_markup=reply_markup,
            disable_web_page_preview=disable_web_page_preview,
        )
    else:
        await message.reply_text(
            text=text,
            reply_markup=reply_markup,
            disable_web_page_preview=disable_web_page_preview,
            quote=quote,
        )