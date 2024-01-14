from PIL import Image
from io import BytesIO


class Camera: # use for testing, displays mate logo
    def __init__(self, port):
        img = Image.open('nuwave.jpg')
        file_object = BytesIO()
        img.save(file_object, 'JPEG')
        file_object.seek(0)
        self.frame = file_object.read()
        
    def get_frame(self) -> bytes:
        return self.frame
