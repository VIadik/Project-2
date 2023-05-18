from aiogram.fsm.state import StatesGroup, State


class FSMFillForm(StatesGroup):
    make_qr = State()
    link = State()
    text = State()
    phone = State()
    email = State()
    name = State()
    wifi_ssid = State()
    wifi_password = State()
    wifi_security = State()
    latitude = State()
    longitude = State()


