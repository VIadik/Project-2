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

@router.message(StateFilter(FSMFillForm.phone))
async def qr_code_from_phone(message: Message, state: FSMContext):
    await state.update_data(phone=message.text)
    users_db[message.from_user.id] = await state.get_data()
    if "mecard" in users_db[message.from_user.id]:
        await message.answer("Теперь отправьте email.")
        await state.set_state(FSMFillForm.email)
    else:
        await send_qr_code(message)
        await state.clear()


@router.message(StateFilter(FSMFillForm.email))
async def qr_code_from_email(message: Message, state: FSMContext):
    email = message.text
    is_correct = validators.email(email)
    if is_correct:
        await state.update_data(email=message.text)
        users_db[message.from_user.id] = await state.get_data()
        if "mecard" in users_db[message.from_user.id]:
            await message.answer("Теперь отправьте url.")
            await state.set_state(FSMFillForm.link)
        else:
            await send_qr_code(message)
            await state.clear()
    else:
        await message.answer("Адрес электронной почты некорректен. Попробуйте отправть другой.")


@router.message(StateFilter(FSMFillForm.link))
async def qr_code_from_link(message: Message, state: FSMContext):
    link = message.text
    is_correct = validators.url(link)
    if is_correct:
        await state.update_data(url=message.text)
        users_db[message.from_user.id] = await state.get_data()
        if "mecard" in users_db[message.from_user.id]:
            qrcode = helpers.make_mecard(name=users_db[message.from_user.id]["name"],
                                         phone=users_db[message.from_user.id]["phone"],
                                         email=users_db[message.from_user.id]["email"],
                                         url=users_db[message.from_user.id]["url"])
            qrcode.save('data/qr_code.png')
            file = FSInputFile("../data/qr_code.png", filename="qr_code.png")
            await bot.send_document(message.from_user.id, file)
        else:
            await send_qr_code(message)
        await state.clear()
    else:
        await message.answer("Ссылка на ресурс некорректна. Отправьте другую.")


@router.message(StateFilter(FSMFillForm.text))
async def qr_code_from_text(message: Message, state: FSMContext):
    await send_qr_code(message)
    await state.clear()



@router.message(StateFilter(FSMFillForm.name))
async def get_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    users_db[message.from_user.id] = await state.get_data()
    if users_db[message.from_user.id]["mecard"]:
        await message.answer("Теперь отправьте телефон.")
        await state.set_state(FSMFillForm.phone)
    else:
        await state.clear()


@router.message(StateFilter(FSMFillForm.latitude))
async def get_latitude(message: Message, state: FSMContext):
    latitude = message.text
    try:
        is_correct = abs(float(latitude)) <= 90.0
    except:
        is_correct = False
    if is_correct:
        await state.update_data(latitude=float(message.text))
        await message.answer("Отправьте долготу")
        await state.set_state(FSMFillForm.longitude)
    else:
        await message.answer("Введенная широта некорректна. -90.0 <= φ <= 90.0")


@router.message(StateFilter(FSMFillForm.longitude))
async def get_longitude(message: Message, state: FSMContext):
    longitude = message.text
    try:
        is_correct = abs(float(longitude)) <= 180.0
    except:
        is_correct = False
    if is_correct:
        await state.update_data(longitude=float(message.text))
        users_db[message.from_user.id] = await state.get_data()
        latitude = users_db[message.from_user.id]["latitude"]
        longitude = users_db[message.from_user.id]["longitude"]
        qrcode = helpers.make_geo(latitude, longitude)
        qrcode.save('data/qr_code.png')
        file = FSInputFile("../data/qr_code.png", filename="qr_code.png")
        await bot.send_document(message.from_user.id, file)
        await state.clear()
    else:
        await message.answer("Введенная долгота некорректна. -180.0 <= λ <= 180.0")

