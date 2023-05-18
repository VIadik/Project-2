from aiogram import Router, types
from aiogram.dispatcher import router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from FSM.FSMFillForm import *

router: Router = Router()


@router.callback_query(StateFilter(FSMFillForm.wifi_security))
async def get_callback(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(wifi_security=callback.data)
    users_db[callback.from_user.id] = await state.get_data()
    qrcode = helpers.make_wifi(ssid=users_db[callback.from_user.id]["wifi_ssid"],
                               password=users_db[callback.from_user.id]["wifi_password"],
                               security=users_db[callback.from_user.id]["wifi_security"])
    qrcode.save('data/qr_code.png')
    file = FSInputFile("../data/qr_code.png", filename="qr_code.png")
    await bot.send_document(callback.from_user.id, file)
    await state.clear()


@router.message(StateFilter(FSMFillForm.wifi_ssid))
async def get_name(message: Message, state: FSMContext):
    await state.update_data(wifi_ssid=message.text)
    await message.answer("Отправьте пароль от wi-fi сети.")
    await state.set_state(FSMFillForm.wifi_password)


@router.message(StateFilter(FSMFillForm.wifi_password))
async def get_name(message: Message, state: FSMContext):
    await state.update_data(wifi_password=message.text)
    await message.answer("Выберете стандарт безопасности", reply_markup=ikb_wifi)
    await state.set_state(FSMFillForm.wifi_security)
