from PIL import Image
import os


def main(user_id: int):
    files = os.listdir(f"users_files/{user_id}/photos")
    os.chdir(f"users_files/{user_id}/photos")
    if 'Icon\r' in files:
        files.remove('Icon\r')
    files.sort(key=os.path.getmtime)

    images = [Image.open(f"{file}") for file in files]
    pdf_path = f"../result.pdf"
    images[0].save(pdf_path, "PDF", resolution=100.0, save_all=True, append_images=images[1:])
    os.chdir("../../../")
