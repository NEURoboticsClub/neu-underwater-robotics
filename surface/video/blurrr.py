import cv2
import numpy as np
import os
import piexif

def make_metadata(img):
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


PATH = os.path.join(os.getcwd(),"images")

for img_name in os.listdir(os.path.join(PATH,"2023-06-21_21-11-50")):
    print(img_name)
    img = cv2.imread(PATH+'/2023-06-21_21-11-50/'+img_name)
    blurred_img = cv2.GaussianBlur(img, (21, 21), 0)

#mask = np.zeros((720, 1280, 3), dtype=np.uint8)

#mask = cv2.circle(mask, (258, 258), 100, (255, 255, 255), -1)
#out = np.where(mask==(255, 255, 255), img, blurred_img)
    cv2.imwrite("images/out/"+img_name, blurred_img,exif=make_metadata(img))
