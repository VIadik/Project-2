from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

ib_url = InlineKeyboardButton(text="Ссылка", callback_data="url")
ib_text = InlineKeyboardButton(text="Текст", callback_data="text")
ib_email = InlineKeyboardButton(text="Электронная почта", callback_data="email")
ib_phone = InlineKeyboardButton(text="Номер телефона", callback_data="phone")
ib_geo = InlineKeyboardButton(text="Геопозиция", callback_data="geo")
ib_wifi = InlineKeyboardButton(text="wifi", callback_data="wifi")
ib_mecard = InlineKeyboardButton(text="mecard", callback_data="mecard")

qr_ikb: InlineKeyboardMarkup = InlineKeyboardMarkup(
    inline_keyboard=[[ib_url],
                     [ib_text],
                     [ib_email],
                     [ib_phone],
                     [ib_geo],
                     [ib_wifi],
                     [ib_mecard]])
