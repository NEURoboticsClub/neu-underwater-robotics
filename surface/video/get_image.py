import requests
import base64
from io import BytesIO
from PIL import Image


IP = 'localhost'  # IP OF FLASK SERVER

def get_image(port):
    url = f'http://{IP}:5000/raw_frame/{port}'
    r = requests.get(url)
    im = Image.open(BytesIO(base64.b64decode(r.text[34:-10])))
    return im

print(get_image(5600))