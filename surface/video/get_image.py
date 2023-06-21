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

img_count = 0   
def on_press(key):
    global img_count                                                                               
    if(key == Key.space):
        print('capturing images')
        img = get_image(5600)
        add_metadata(img)
        img_str = '/surface/video/output/img'+str(img_count)+'.png'
        save_image(img,img_str)
        #img = img.save(img_str)
        img_count +=1
    if key == Key.esc:
        return False
        
def on_release(key):
    print('stopping image capture')


#save_image(Image.open("images/MATE_5601_4.png"), "images/MATE_5601_4_edited")

with Listener(
        on_press=on_press,
        on_release=on_release) as listener:
    listener.join()
