import sys
import zipfile
import os
import config

# https://realpython.com/python-zipfile/

token = sys.argv[1]

files = sorted(os.listdir(f"telegram-bot-api/bin/{token}/documents/"), key=lambda x: int(x[5:-4]))

with zipfile.ZipFile("archive.zip", mode="w") as archive:
    archive.write(f"telegram-bot-api/bin/{token}/documents/{files[-1]}", compresslevel=9)

old_file = 'archive.zip'
destination_file = 'data/archive.zip'

os.rename(old_file, destination_file)
