import os
import subprocess
from copy import deepcopy
import segno
import validators
from aiogram import F, Bot

from aiogram import Router, types
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, FSInputFile

import services.zip
import services.unzip
import services.pdf
from keyboards.wifi_ikb import ikb_wifi
from segno import helpers

import FSM.FSMFillForm
from keyboards.qr_ikb import qr_ikb
from database.database import user_dict_template, users_db
from lexicon.lexicon_ru import LEXICON
from config_data.config import Config, load_config

router: Router = Router()

from FSM.FSMFillForm import *

config: Config = load_config()


@router.message(Command(commands='help'))
async def process_help_command(message: Message):
    await message.answer(LEXICON['/help'])


@router.message(Command(commands='start'))
async def process_help_command(message: Message):
    await message.answer(LEXICON['/start'])
    if message.from_user.id not in users_db:
        users_db[message.from_user.id] = deepcopy(user_dict_template)


@router.message(Command(commands='cancel'))
async def process_cancel_command_state(message: Message, state):
    await message.answer(LEXICON["/cancel"])
    await state.clear()


@router.message(Command("qr"))
async def generate_qr(message: types.Message, state: FSMContext):
    await message.answer(LEXICON['/qr'], reply_markup=qr_ikb)
    await state.set_state(FSMFillForm.make_qr)


@router.callback_query(StateFilter(FSMFillForm.wifi_security))
async def get_callback(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(wifi_security=callback.data)
    users_db[callback.from_user.id] = await state.get_data()
    qrcode = helpers.make_wifi(ssid=users_db[callback.from_user.id]["wifi_ssid"],
                               password=users_db[callback.from_user.id]["wifi_password"],
                               security=users_db[callback.from_user.id]["wifi_security"])
    qrcode.save(f'data/qr_code{callback.message.from_user.id}.png')
    file = FSInputFile(f"data/qr_code{callback.message.from_user.id}.png", filename="qr_code.png")
    await callback.message.answer_document(file)
    await state.clear()


@router.callback_query()
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
    qrcode.save(f'data/qr_code{message.from_user.id}.png')
    file = FSInputFile(f"data/qr_code{message.from_user.id}.png", filename="qr_code.png")
    await message.answer_document(file)


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
    print("latitude", latitude)
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
    print("longitude", longitude)
    try:
        is_correct = abs(float(longitude)) <= 180.0
    except:
        is_correct = False
    if is_correct:
        print("it is false")
        await state.update_data(longitude=float(message.text))
        users_db[message.from_user.id] = await state.get_data()
        latitude = users_db[message.from_user.id]["latitude"]
        longitude = users_db[message.from_user.id]["longitude"]
        qrcode = helpers.make_geo(latitude, longitude)
        qrcode.save(f'data/qr_code{message.from_user.id}.png')
        file = FSInputFile(f"data/qr_code{message.from_user.id}.png", filename="qr_code.png")
        await message.answer_document(file)
        await state.clear()
    else:
        print("am here")
        await message.answer("Введенная долгота некорректна. -180.0 <= λ <= 180.0")


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
        await message.answer(LEXICON['incorrect_email'])


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
            qrcode.save(f'data/qr_code{message.from_user.id}.png')
            file = FSInputFile(f"data/qr_code{message.from_user.id}.png", filename="qr_code.png")
            await message.answer_document(file)
        else:
            await send_qr_code(message)
        await state.clear()
    else:
        await message.answer(LEXICON['incorrect_link'])


@router.message(StateFilter(FSMFillForm.text))
async def qr_code_from_text(message: Message, state: FSMContext):
    await send_qr_code(message)
    await state.clear()


# -------------------------------------------------------------
# -------------------------------------------------------------
# -------------------------------------------------------------
# -------------------------------------------------------------


class Form(StatesGroup):
    get_files_for_zip = State()
    unzip = State()
    get_photo_for_pdf = State()


@router.message(Command("pdf"))
@router.message(lambda message: message.text == "Собрать фотографии в pdf")
async def photo_info(message: types.Message, state: FSMContext):
    await message.answer("Отправьте фото/фотографии одним сообщением. Чтобы закончить ввод файлов, введите /stop.")
    subprocess.run(f"mkdir users_files/{message.from_user.id}", shell=True)
    subprocess.run(f"mkdir users_files/{message.from_user.id}/photos", shell=True)
    await state.set_state(Form.get_photo_for_pdf)


@router.message(lambda message: message.content_type == 'photo', StateFilter(Form.get_photo_for_pdf))
async def photo_handler(message: types.Message, state: FSMContext, bot: Bot):
    file_id = message.photo[-1].file_id
    file = await bot.get_file(file_id)
    file_path = file.file_path
    old_file = f"{file_path}"
    destination_file = f'users_files/{message.from_user.id}/{file_path[119:]}'
    os.rename(old_file, destination_file)


@router.message(Command(commands='stop'), StateFilter(Form.get_photo_for_pdf))
async def not_photo_handler(message: types.Message, state: FSMContext):
    services.pdf.main(message.from_user.id)
    file = FSInputFile(f"users_files/{message.from_user.id}/result.pdf", filename="result.pdf")
    await message.answer_document(file)
    subprocess.run(f"python3 services/clear_directory.py users_files/{message.from_user.id}/photos", shell=True)
    await state.clear()


@router.message(StateFilter(Form.get_photo_for_pdf))
async def not_photo_handler(message: types.Message, state: FSMContext):
    await message.answer("Сообщение не является фотографией, пришлите новую, либо вызовете команду /stop")


# ----------- unzip

@router.message(Command("unzip"))
@router.message(lambda message: message.text == 'Разархивировать файл')
async def doc_info(message: types.Message, state: FSMContext):
    await message.answer(LEXICON['/unzip'])
    subprocess.run(f"mkdir users_files/{message.from_user.id}", shell=True)
    subprocess.run(f"mkdir users_files/{message.from_user.id}/documents", shell=True)
    subprocess.run(f"mkdir users_files/{message.from_user.id}/unzip_files", shell=True)
    await state.set_state(Form.unzip)


@router.message(StateFilter(Form.unzip), lambda message: message.content_type == 'document')
async def doc_info(message: types.Message, state: FSMContext, bot: Bot):
    file_id = message.document.file_id
    file = await bot.get_file(file_id)
    file_path = file.file_path
    old_file = f"{file_path}"
    destination_file = f'users_files/{message.from_user.id}/{file_path[119:]}'
    os.rename(old_file, destination_file)
    services.unzip.main(message.from_user.id)
    files = os.listdir(f"users_files/{message.from_user.id}/unzip_files")
    if 'Icon\r' in files:
        files.remove('Icon\r')
    print(files)
    for file in files:
        file = FSInputFile(
            f"users_files/{message.from_user.id}/unzip_files/{file}",
            filename=f"{file}")
        await message.answer_document(file)
    subprocess.run(f"python3 services/clear_directory.py users_files/{message.from_user.id}/documents", shell=True)
    subprocess.run(f"python3 services/clear_directory.py users_files/{message.from_user.id}/unzip_files", shell=True)
    await state.clear()


@router.message(StateFilter(Form.unzip))
async def doc_info(message: types.Message, state: FSMContext):
    await message.answer(LEXICON['incorrect_archive_file'])


# --------------zip-------

@router.message(Command("zip"))
@router.message(lambda message: message.text == 'Сжать файл')
async def photo_info(message: types.Message, state: FSMContext):
    await message.answer(LEXICON['/zip'])
    subprocess.run(f"mkdir users_files/{message.from_user.id}", shell=True)
    subprocess.run(f"mkdir users_files/{message.from_user.id}/documents", shell=True)
    await state.set_state(Form.get_files_for_zip)


@router.message(lambda message: message.content_type == 'document', StateFilter(Form.get_files_for_zip))
async def photo_handler(message: types.Message, state: FSMContext, bot: Bot):
    file_id = message.document.file_id
    file = await bot.get_file(file_id)
    file_path = file.file_path
    old_file = f"{file_path}"
    destination_file = f'users_files/{message.from_user.id}/{file_path[119:]}'
    os.rename(old_file, destination_file)


@router.message(Command(commands='stop'), StateFilter(Form.get_files_for_zip))
async def not_photo_handler(message: types.Message, state: FSMContext, bot: Bot):
    services.zip.main(message.from_user.id)
    file = FSInputFile(f"users_files/{message.from_user.id}/archive.zip", filename="archive.zip")
    await message.answer_document(file)
    subprocess.run(f"python3 services/clear_directory.py users_files/{message.from_user.id}/documents", shell=True)
    await state.clear()


@router.message(StateFilter(Form.get_files_for_zip))
async def not_photo_handler(message: types.Message, state: FSMContext):
    await message.answer("Сообщение не является файлом, пришлите новый, либо вызовете команду /stop")
