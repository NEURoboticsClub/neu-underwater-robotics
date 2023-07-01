import requests
import base64
from io import BytesIO
from PIL import Image
from datetime import datetime
import piexif
import os


IP = '192.168.0.150'  # IP OF FLASK SERVER
PORT = 5600  # PORT OF CAMERA

def get_image(port):
    url = f'http://{IP}:5000/raw_frame/{port}'
    r = requests.get(url)
    im = Image.open(BytesIO(base64.b64decode(r.text[34:-10])))
    return im

def add_metadata(img: Image):
    exif_dict = {
        "0th": {},
        "Exif": {},
    }
    focal_length = (35, 10)  # 35/10
    exif_dict["Exif"][piexif.ExifIFD.FocalLength] = focal_length

    width, height = img.size
    exif_dict["0th"][piexif.ImageIFD.Make] = "NUWAVE"
    exif_dict["0th"][piexif.ImageIFD.LocalizedCameraModel] = "NUWAVE"


    exif_bytes = piexif.dump(exif_dict)
    return exif_bytes
    
def save_image(img: Image, name: str):
    img.save(f"{name}.jpg", exif=add_metadata(img))

save_image(Image.open("images/MATE_5601_4.png"), "images/MATE_5601_4_edited")

# if __name__ == "__main__":
#     try:
#         os.makedirs(f"images/{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}")
#     except FileExistsError:
#         pass
#     counter = 0
#     while True:
#         save_image(get_image(PORT), f"images/{counter}")
#         counter += 1