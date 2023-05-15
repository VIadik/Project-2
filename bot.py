from __future__ import annotations

import asyncio
import subprocess
import segno
from segno import helpers
import validators
import logging

from keyboards.wifi_ikb import ikb_wifi
from keyboards.qr_ikb import qr_ikb

from aiogram import Bot, Dispatcher, F
from aiogram import types
from aiogram.types import FSInputFile
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.filters.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (CallbackQuery, InlineKeyboardButton,
                           InlineKeyboardMarkup, Message, PhotoSize)
from aiogram.client.telegram import TelegramAPIServer

dp = Dispatcher()
config: Config
bot: Bot

from config import Config, load_config

user_dict: dict[int, dict[str, str | int | bool | float]] = {}

HELP_COMMAND = """
start - начало работы
help - список команд
zip - сжать файл/файлы в один архив
unzip - разархивировать zip архив
pdf - конвертировать файл/файлы в один pdf файл
qr - создать qr-code
"""

storage: MemoryStorage = MemoryStorage()


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


@dp.message(Command(commands='cancel'))
async def process_cancel_command_state(message: Message, state):
    await message.answer("Вы вышли в главное меню.")
    await message.answer("Отправь команду /help, чтобы узнать что умеет этот бот.")
    await state.clear()


@dp.message(Command("qr"))
async def generate_qr(message: types.Message, state: FSMContext):
    await message.answer("Выберейте тип данных, который Вы хотите закодировать.", reply_markup=ikb_wifi)
    await state.set_state(FSMFillForm.make_qr)


@dp.callback_query(StateFilter(FSMFillForm.wifi_security))
async def get_callback(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(wifi_security=callback.data)
    user_dict[callback.from_user.id] = await state.get_data()
    qrcode = helpers.make_wifi(ssid=user_dict[callback.from_user.id]["wifi_ssid"],
                               password=user_dict[callback.from_user.id]["wifi_password"],
                               security=user_dict[callback.from_user.id]["wifi_security"])
    qrcode.save('data/qr_code.png')
    file = FSInputFile("data/qr_code.png", filename="qr_code.png")
    await bot.send_document(callback.from_user.id, file)
    await state.clear()


@dp.callback_query()
async def get_callback(callback: types.CallbackQuery, state: FSMContext):
    if callback.data == "url":
        await callback.message.answer("Отправьте ссылку на ресурс.")
        await state.set_state(FSMFillForm.link)
    if callback.data == "text":
        await callback.message.answer("Отправьте текстовое сообщение.")
        await state.set_state(FSMFillForm.text)
    if callback.data == "email":
        await callback.message.answer("Отправьте электронный адрес.")
        await state.set_state(FSMFillForm.email)
    if callback.data == "phone":
        await callback.message.answer("Отправьте номер телефона.")
        await state.set_state(FSMFillForm.phone)
    if callback.data == "geo":
        await callback.message.answer("Отправьте широту")
        await state.set_state(FSMFillForm.latitude)
    if callback.data == "wifi":
        await callback.message.answer("Отправьте ssid")
        await state.set_state(FSMFillForm.wifi_ssid)
    if callback.data == "mecard":
        await callback.message.answer("Ответьте на несколько вопросов про себя. Отправьте имя и фамилию.")
        await state.set_state(FSMFillForm.name)
        await state.update_data(mecard=True)


async def send_qr_code(message: Message, mode=None):
    qrcode = segno.make(message.text, micro=False, mode=mode)
    qrcode.save('data/qr_code.png')
    file = FSInputFile("data/qr_code.png", filename="qr_code.png")
    await bot.send_document(message.from_user.id, file)


@dp.message(StateFilter(FSMFillForm.name))
async def get_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    user_dict[message.from_user.id] = await state.get_data()
    if user_dict[message.from_user.id]["mecard"]:
        await message.answer("Теперь отправьте телефон.")
        await state.set_state(FSMFillForm.phone)
    else:
        await state.clear()


@dp.message(StateFilter(FSMFillForm.latitude))
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


@dp.message(StateFilter(FSMFillForm.longitude))
async def get_longitude(message: Message, state: FSMContext):
    longitude = message.text
    try:
        is_correct = abs(float(longitude)) <= 180.0
    except:
        is_correct = False
    if is_correct:
        await state.update_data(longitude=float(message.text))
        user_dict[message.from_user.id] = await state.get_data()
        latitude = user_dict[message.from_user.id]["latitude"]
        longitude = user_dict[message.from_user.id]["longitude"]
        qrcode = helpers.make_geo(latitude, longitude)
        qrcode.save('data/qr_code.png')
        file = FSInputFile("data/qr_code.png", filename="qr_code.png")
        await bot.send_document(message.from_user.id, file)
        await state.clear()
    else:
        await message.answer("Введенная долгота некорректна. -180.0 <= λ <= 180.0")


@dp.message(StateFilter(FSMFillForm.wifi_ssid))
async def get_name(message: Message, state: FSMContext):
    await state.update_data(wifi_ssid=message.text)
    await message.answer("Отправьте пароль от wi-fi сети.")
    await state.set_state(FSMFillForm.wifi_password)


@dp.message(StateFilter(FSMFillForm.wifi_password))
async def get_name(message: Message, state: FSMContext):
    await state.update_data(wifi_password=message.text)
    await message.answer("Выберете стандарт безопасности", reply_markup=ikb_wifi)
    await state.set_state(FSMFillForm.wifi_security)


@dp.message(StateFilter(FSMFillForm.phone))
async def qr_code_from_phone(message: Message, state: FSMContext):
    await state.update_data(phone=message.text)
    user_dict[message.from_user.id] = await state.get_data()
    if "mecard" in user_dict[message.from_user.id]:
        await message.answer("Теперь отправьте email.")
        await state.set_state(FSMFillForm.email)
    else:
        await send_qr_code(message)
        await state.clear()

    # if state.get_data()
    #     await state.clear()
    # import re
    #
    # validate_phone_number_pattern = "^\\+?\\d{1,4}?[-.\\s]?\\(?\\d{1,3}?\\)?[-.\\s]?\\d{1,4}[-.\\s]?\\d{1,4}[-.\\s]?\\d{1,9}$"
    # is_correct = re.match(validate_phone_number_pattern, message.text)
    # if is_correct:
    #     await send_qr_code(message)
    #     await state.clear()
    # else:
    #     await message.answer("heello")
    #     await message.answer("heello2")


@dp.message(StateFilter(FSMFillForm.email))
async def qr_code_from_email(message: Message, state: FSMContext):
    email = message.text
    is_correct = validators.email(email)
    if is_correct:
        await state.update_data(email=message.text)
        user_dict[message.from_user.id] = await state.get_data()
        if "mecard" in user_dict[message.from_user.id]:
            await message.answer("Теперь отправьте url.")
            await state.set_state(FSMFillForm.link)
        else:
            await send_qr_code(message)
            await state.clear()
    else:
        await message.answer("Адрес электронной почты некорректен. Попробуйте отправть другой.")


@dp.message(StateFilter(FSMFillForm.link))
async def qr_code_from_link(message: Message, state: FSMContext):
    link = message.text
    is_correct = validators.url(link)
    if is_correct:
        await state.update_data(url=message.text)
        user_dict[message.from_user.id] = await state.get_data()
        if "mecard" in user_dict[message.from_user.id]:
            qrcode = helpers.make_mecard(name=user_dict[message.from_user.id]["name"],
                                         phone=user_dict[message.from_user.id]["phone"],
                                         email=user_dict[message.from_user.id]["email"],
                                         url=user_dict[message.from_user.id]["url"])
            qrcode.save('data/qr_code.png')
            file = FSInputFile("data/qr_code.png", filename="qr_code.png")
            await bot.send_document(message.from_user.id, file)
        else:
            await send_qr_code(message)
        await state.clear()
    else:
        await message.answer("Ссылка на ресурс некорректна. Отправьте другую.")


@dp.message(StateFilter(FSMFillForm.text))
async def qr_code_from_text(message: Message, state: FSMContext):
    await send_qr_code(message)
    await state.clear()


@dp.message(Command("zip"))
@dp.message(lambda message: message.text == 'Сжать файл')
async def doc_info(message: types.Message):
    await message.answer("Отправьте файл/файлы одним сообщением")


@dp.message(Command("pdf"))
@dp.message(lambda message: message.text == "Собрать фотографии в pdf")
async def photo_info(message: types.Message):
    await message.answer("Отправьте фото/фотографии одним сообщением")


class FSMF_unzip(StatesGroup):
    get_zip_file = State


@dp.message(Command("unzip"))
@dp.message(lambda message: message.text == 'Разархивировать файл')
async def doc_info(message: types.Message):
    await message.answer("Отправьте zip архив")


# #-------------------------------------------------------------
#
# class Form(StatesGroup):
#     next_photo = State()
#     photo_0 = State()
#     photo_couter = State()
#
# @dp.message(lambda message: message.content_type == 'photo')
# async def photo_handler(message: types.Message, state: FSMContext):
#     # we are here if the first message.content_type == 'photo'
#
#     # save the largest photo (message.photo[-1]) in FSM, and start photo_counter
#     await state.update_data(photo_0=message.photo[-1], photo_counter=0)
#
#     await state.set_state('next_photo')
#
#
# @dp.message(lambda message: message.content_type == 'photo', state="next_photo")
# async def next_photo_handler(message: types.Message, state: FSMContext):
#     # we are here if the second and next messages are photos
#
#     async with state.get_data() as data:
#         data['photo_counter'] += 1
#         photo_counter = data['photo_counter']
#         data[f'photo_{photo_counter}'] = message.photo[-1]
#     await state.set_state('next_photo')
#
#
# @dp.message(state='next_photo')
# async def not_foto_handler(message: types.Message, state: FSMContext):
#     # we are here if the second and next messages are not photos
#
#     async with state.get_data() as data:
#         # here you can do something with data dictionary with all photos
#         print(data)
#
#     await state.finish()
# -------------------------------------------------------------


used = set()


@dp.message(lambda message: message.content_type == 'photo')
async def photo_handler(message: types.Message):
    if message.media_group_id not in used:
        print(message.photo)
        file_ids = [file.file_id for file in message.photo]
        print(file_ids)
        ss = set(file_ids)
        print(ss)
        file_ids = list(set(file_ids))
        print(file_ids)
        files = [await bot.get_file(id) for id in file_ids]
        print(file_ids)
        subprocess.run("python3 pdf.py", shell=True)
        file = FSInputFile("data/doc.pdf", filename="result.pdf")
        await bot.send_document(message.from_user.id, file)
        subprocess.run(f"python3 clear_directory.py telegram-bot-api/bin/{config.tg_bot.token}/photos", shell=True)
        used.add(message.media_group_id)
        print(message.media_group_id)


@dp.message(lambda message: message.content_type == 'document')
async def document_hander(message: types.Message):
    file_id = message.document.file_id
    file = await bot.get_file(file_id)
    subprocess.run("python3 zip.py", shell=True)
    file = FSInputFile("data/archive.zip", filename="result.zip")
    await bot.send_document(message.from_user.id, file)


@dp.message(Command("help"))
async def help_command(message: types.Message):
    await message.answer(HELP_COMMAND)


@dp.message(Command("start"))
async def process_start_command(message: types.Message):
    await message.answer("Привет! Отправь команду /help, чтобы узнать что умеет этот бот")


@dp.message()
async def echo_message(msg: types.Message):
    await bot.send_message(msg.from_user.id, msg.text)


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(filename)s:%(lineno)d #%(levelname)-8s '
               '[%(asctime)s] - %(name)s - %(message)s')
    config = load_config()
    session = AiohttpSession(api=TelegramAPIServer.from_base('http://127.0.0.1:8081/'))
    bot = Bot(token=config.tg_bot.token, session=session)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
