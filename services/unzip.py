import zipfile

with zipfile.ZipFile("data/archive.zip", 'r') as zip_ref:
    zip_ref.extractall("data/result")
