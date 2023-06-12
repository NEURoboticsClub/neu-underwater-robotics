import os 
import sys
import exiftool

EXIF_PATH = sys.argv[0]
FOCAL_LENGTH = sys.argv[1]

files = os.listdir('/surface/video/output/')
with exiftool.ExifTool(EXIF_PATH) as et:
    metadata = et.get_metadata(files)
    for file in files:
        et.execute("-FocalLength=f{FOCAL_LENGTH}", file)
   
 