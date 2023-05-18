import subprocess
from copy import deepcopy

from aiogram import Router, types
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery, Message, FSInputFile

import FSM.FSMFillForm
from keyboards.qr_ikb import qr_ikb
# from FSM import FSMFillForm
from database.database import user_dict_template, users_db
# from filters.filters import IsDelBookmarkCallbackData, IsDigitCallbackData
#
# from keyboards.bookmarks_kb import (create_bookmarks_keyboard,
#                                     create_edit_keyboard)
# from keyboards.pagination_kb import create_pagination_keyboard
from lexicon.lexicon_ru import LEXICON

router: Router = Router()

from FSM.FSMFillForm import *


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


@router.message(Command("zip"))
@router.message(lambda message: message.text == 'Сжать файл')
async def doc_info(message: types.Message):
    await message.answer("Отправьте файл/файлы одним сообщением")


@router.message(Command("pdf"))
@router.message(lambda message: message.text == "Собрать фотографии в pdf")
async def photo_info(message: types.Message):
    await message.answer("Отправьте фото/фотографии одним сообщением")


@router.message(Command("unzip"))
@router.message(lambda message: message.text == 'Разархивировать файл')
async def doc_info(message: types.Message):
    await message.answer("Отправьте zip архив")


@router.message(Command("qr"))
async def generate_qr(message: types.Message, state: FSMContext):
    await message.answer("Выберейте тип данных, который Вы хотите закодировать.", reply_markup=qr_ikb)
    await state.set_state(FSMFillForm.make_qr)


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

# async def send_qr_code(message: Message, mode=None):
#     qrcode = segno.make(message.text, micro=False, mode=mode)
#     qrcode.save('data/qr_code.png')
#     file = FSInputFile("../data/qr_code.png", filename="qr_code.png")
#     await bot.send_document(message.from_user.id, file)


# @router.message(lambda message: message.content_type == 'photo')
# async def photo_handler(message: types.Message):
#     file_ids = [file.file_id for file in message.photo]
#     files = [await bot.get_file(id) for id in file_ids]
#     print(file_ids)
#     subprocess.run(f"python3 sevices/pdf.py {config.tg_bot.token}", shell=True)
#     file = FSInputFile("data/doc.pdf", filename="result.pdf")
#     await bot.send_document(message.from_user.id, file)
#     subprocess.run(f"python3 clear_directory.py telegram-bot-api/bin/{config.tg_bot.token}/photos", shell=True)
#     used.add(message.media_group_id)
#     print(message.media_group_id)
#
#
# @router.message(lambda message: message.content_type == 'document')
# async def document_hander(message: types.Message):
#     file_id = message.document.file_id
#     file = await bot.get_file(file_id)
#     subprocess.run(f"python3 services/zip.py {config.tg_bot.token}", shell=True)
#     file = FSInputFile("../data/archive.zip", filename="result.zip")
#     await bot.send_document(message.from_user.id, file)
