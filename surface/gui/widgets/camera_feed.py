from PyQt5.QtGui import QImage
from PyQt5.QtCore import QThread, pyqtSignal as Signal
import cv2, imutils
from os.path import expanduser

# TODO(config): Users ought to be able to specify this without prying
# into the code.
PORT_NO_TO_CV2_GST_PIPELINE_COMMAND = lambda port_no : f"udpsrc port={port_no} ! application/x-rtp ! rtpjitterbuffer ! rtph264depay ! avdec_h264 ! videoconvert ! appsink"

class CameraFeed(QThread):
    def __init__(self, port_no : int):
        self.frame_signal = Signal(QImage)
        self.video_capture_pipeline = PORT_NO_TO_CV2_GST_PIPELINE_COMMAND(port_no)

    def run(self):
        self.capture = cv2.VideoCapture(self.video_capture_pipeline, cv2.CAP_GSTREAMER)
        if not self.capture.isOpened():
            print("Error: Failed to start video capture")
        while self.capture.isOpened():
            capture_read_successful, frame = self.capture.read()
            if not capture_read_successful:
                print("Error: Failed to capture frame from video feed")
            else:
                img = self.cvimage_to_label(frame)
                self.frame_signal.emit(img)
    
    def cvimage_to_label(self, img):
        img = imutils.resize(img, width = 640)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = QImage(img,
                     img.shape[1],
                     img.shape[0],
                     QImage.Format_RGB888)
        return img
    
    def save_image(self, camera_no, num_saved_images):
        img_save_path = expanduser("~/neu-underwater-robotics/surface/camera_"
                                   + str(camera_no)
                                   + "_capture_"
                                   + str(num_saved_images) + ".jpg")

        capture_read_successful, frame = self.capture.read()
        if not capture_read_successful:
            print("Error: Failed to capture frame from video feed")

        img_save_successful = cv2.imwrite(img_save_path, frame)
        if img_save_successful:
            print("Image saved to " + img_save_path)
        else:
            print("Error: Image failed to save")