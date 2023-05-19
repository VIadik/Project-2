import os
import zipfile


def main(user_id: int):
    files = os.listdir(f"users_files/{user_id}/documents")
    if 'Icon\r' in files:
        files.remove('Icon\r')
    assert len(files) == 1
    file = files[0]
    with zipfile.ZipFile(f"users_files/{user_id}/documents/{file}", 'r') as zip_ref:
        zip_ref.extractall(f"users_files/{user_id}/unzip_files")
