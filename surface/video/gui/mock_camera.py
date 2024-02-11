from PIL import Image
from io import BytesIO


class Camera:
    def __init__(self, port):
        
        self.whichFrame = True

        img1 = Image.open('./nuwave.jpg')
        file_object1 = BytesIO()
        img1 = img1.convert('RGB')
        img1.save(file_object1, 'JPEG')
        file_object1.seek(0)
        self.frame1 = file_object1.read()

        img2 = Image.open('./jonahJ.jpg')
        file_object2 = BytesIO()
        img2 = img2.convert('RGB')
        img2.save(file_object2, 'JPEG')
        file_object2.seek(0)
        self.frame2 = file_object2.read()
        
    def get_frame(self) -> bytes:

         if self.whichFrame :
             self.whichFrame = not self.whichFrame
             return self.frame1
         else :
             self.whichFrame = not self.whichFrame
             return self.frame2
