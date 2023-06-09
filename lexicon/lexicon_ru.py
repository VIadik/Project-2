LEXICON: dict[str, str] = {
    '/start': """Привет! Отправь команду /help, чтобы узнать что умеет этот бот""",

    '/help': """
/start - начало работы
/help - список команд
/zip - сжать файл/файлы в один архив
/unzip - разархивировать zip архив
/pdf - конвертировать файл/файлы в один pdf файл
/qr - создать qr-code""",

    '/cancel': """
Вы вышли в главное меню.
Отправь команду /help, чтобы узнать что умеет этот бот.""",

    '/qr': "Выберейте тип данных, который Вы хотите закодировать.",
    '/zip': "Отправьте файлы боту. Чтобы закончить ввод файлов, введите /stop.",
    '/unzip': "Отправьте zip архив.",
    'incorrect_archive_file': "Файл не является архивом, пришлите другой файл, либо вызовете команду /cancel, чтобы выйти в главное меню.",
    'incorrect_link': "Ссылка на ресурс некорректна. Отправьте другую.",
    'incorrect_email': "Адрес электронной почты некорректен. Попробуйте отправть другой."
}
