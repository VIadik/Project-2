import sys
import zipfile
import os


# https://realpython.com/python-zipfile/

def main(user_id: int):
    files = os.listdir(f"users_files/{user_id}/documents")

    with zipfile.ZipFile(f"{user_id}archive.zip", mode="w") as archive:
        for file in files:
            archive.write(f"users_files/{user_id}/documents/{file}")

    old_file = f"{user_id}archive.zip"
    destination_file = f'users_files/{user_id}/archive.zip'

    print(os.listdir(f"users_files/{user_id}"))

    os.rename(old_file, destination_file)
