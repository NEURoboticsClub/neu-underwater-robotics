from PIL import Image
from io import BytesIO


class Camera:
    def __init__(self, port):
        img = Image.open('./nuwave.jpg')
        file_object = BytesIO()
        img = img.convert('RGB')
        img.save(file_object, 'JPEG')
        file_object.seek(0)
        self.frame = file_object.read()
        
    def get_frame(self) -> bytes:
        return self.frame
