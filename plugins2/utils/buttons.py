from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

help_button = InlineKeyboardButton('🆘 Help', callback_data='help')
about_button = InlineKeyboardButton('🔰 About', callback_data='about')
close_button = InlineKeyboardButton('🔒 Close', callback_data='close')
home_button = InlineKeyboardButton('🏡 Home', callback_data='start')
botstatus_button = InlineKeyboardButton('✅ Bot Status', callback_data='botstatus')
updates_channel_button = InlineKeyboardButton('🆎 Updates Channel', url='https://t.me/xibots_india')


START_BUTTONS = InlineKeyboardMarkup(
    [
        [updates_channel_button],
        [help_button, about_button],
        [botstatus_button , close_button],
    ]
)

HELP_BUTTONS = InlineKeyboardMarkup(
    [
        [home_button, close_button]
    ]
)

ABOUT_BUTTONS = InlineKeyboardMarkup(
    [
        [home_button, close_button]
    ]
)

CLOSE_BUTTON = InlineKeyboardMarkup(
    [
        [close_button]
    ]
)

NAVIGATION_BUTTONS = InlineKeyboardMarkup(
    [
        [home_button, close_button]
    ]
)