from PyQt5.QtCore import QThread
import cv2
from os.path import expanduser
from datetime import datetime

class CameraFeed(QThread):

    def __init__(self, port_no : int, camera_no : int):
        super(CameraFeed, self).__init__()

        print("Initializing camera feed on port " + str(port_no))

        self.camera_no = camera_no
        self._current_frame = None
        self._num_saved_images = 0
        self._do_save_img = False

        print("opening video capture")
        self.capture = cv2.VideoCapture(camera_no)
        print("opened video capture")
        if not self.capture.isOpened():
            print("Error: Failed to start video capture")
        else:
            print("Video capture started successfully on camera " + str(self.camera_no))

    def run(self):
        while self.capture.isOpened():
            print("running camera feed")
            capture_read_successful, self._current_frame = self.capture.read()
            if not capture_read_successful:
                print("Error: Failed to capture frame from video feed")
                if self._do_save_img:
                    print("Error: Failed to save image from video feed")
            else:
                if self._do_save_img:
                    self._save_image()
        print("Error: Camera closed. Exiting.")
    
    def save_image(self):
        print("saving image (camera_feed)")
        self._num_saved_images += 1
        self._do_save_img = True
    
    def _save_image(self):
        print("saving image (camera_feed private)")
        img_save_path = expanduser("~/neu-underwater-robotics/surface/camera_"
                                   + str(self.camera_no)
                                   + "_capture_"
                                   + str(self._num_saved_images)
                                   + datetime.now().strftime("%Y-%m-%d %H-%M-%S")
                                   + ".jpg")

        img_save_successful = cv2.imwrite(img_save_path, self._current_frame)
        if img_save_successful:
            print("Image saved to " + img_save_path)
            self._do_save_img = False
        else:
            print("Error: Image failed to save")