import requests
import base64
from io import BytesIO
from PIL import Image
from datetime import datetime
import piexif
import os
import time


IP = 'localhost'  # IP OF FLASK SERVER
PORT = 5600  # PORT OF CAMERA
folder_name = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

os.makedirs(f"images/{folder_name}", exist_ok=True)


def make_folder():
    global folder_name
    folder_name = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    os.makedirs(f"images/{folder_name}", exist_ok=True)

def add_metadata(img: Image):
    exif_dict = {
        "0th": {},
        "Exif": {},
    }
    focal_length = (35, 10)  # 35/10
    exif_dict["Exif"][piexif.ExifIFD.FocalLength] = focal_length

    exif_dict["0th"][piexif.ImageIFD.Make] = "NUWAVE"
    exif_dict["0th"][piexif.ImageIFD.Model] = "NUWAVE"


    exif_bytes = piexif.dump(exif_dict)
    return exif_bytes
    
def save_image(img: Image, name: str):
    img.save(f"images/{folder_name}/{name}.jpg", exif=add_metadata(img))


if __name__ == "__main__":
    folder_name = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    os.makedirs(f"images/{folder_name}", exist_ok=True)
    counter = 0
    while True:
        input("Press enter to take a picture")
        start_time = time.time()
        save_image(get_image(PORT), f"images/{folder_name}/{counter}")
        print(f"Saved image {counter} in {time.time() - start_time} seconds")
        counter += 1