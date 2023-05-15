from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

ib_WPA = InlineKeyboardButton(text="WPA", callback_data="WPA")
ib_WPA2 = InlineKeyboardButton(text="WPA2", callback_data="WPA2")
ib_WEP = InlineKeyboardButton(text="WEP", callback_data="WEP")

ikb_wifi: InlineKeyboardMarkup = InlineKeyboardMarkup(
    inline_keyboard=[[ib_WPA,
                      ib_WPA2,
                      ib_WEP]])
