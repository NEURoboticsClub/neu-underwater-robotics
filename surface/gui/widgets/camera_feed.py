from PyQt5.QtGui import QImage
from PyQt5.QtCore import QThread, pyqtSignal as Signal
import cv2
from os.path import expanduser
import time

# TODO(config): Users ought to be able to specify this without prying
# into the code.
PORT_NO_TO_CV2_GST_PIPELINE_COMMAND = lambda port_no : f"udpsrc port={port_no} ! application/x-rtp ! rtpjitterbuffer latency=0 ! rtph264depay ! avdec_h264 ! queue max-size-buffers=1 leaky=downstream ! videoconvert ! appsink max-buffers=1 sync=false drop=true"

class CameraFeed(QThread):

    frame_signal = Signal(QImage, float)

    def __init__(self, port_no : int, camera_no : int):
        super(CameraFeed, self).__init__()

        print("Initializing camera feed on port " + str(port_no))

        self.video_capture_pipeline = PORT_NO_TO_CV2_GST_PIPELINE_COMMAND(port_no)
        self.camera_no = camera_no
        self._current_frame = None
        self._num_saved_images = 0
        self._do_save_img = False

    def run(self):
        self.capture = cv2.VideoCapture(self.video_capture_pipeline, cv2.CAP_GSTREAMER)
        if not self.capture.isOpened():
            print("Error: Failed to start video capture")
        else:
            print("Video capture started successfully on camera " + str(self.camera_no))
        while self.capture.isOpened():
            capture_read_successful, self._current_frame = self.capture.read()
            if not capture_read_successful:
                print("Error: Failed to capture frame from video feed")
                if self._do_save_img:
                    print("Error: Failed to save image from video feed")
            else:
                img = self._cvimage_to_qimage(self._current_frame)
                self.frame_signal.emit(img, time.time())
                if self._do_save_img:
                    self._save_image()
        print("Error: Camera closed. Exiting.")
    
    def _cvimage_to_qimage(self, frame) -> QImage:
        height, width, _ = frame.shape
        bytes_per_line = 3 * width
        qimg = QImage(frame.data, width, height, bytes_per_line, QImage.Format_BGR888)
        return qimg
    
    def save_image(self):
        self._do_save_img = True
        self._num_saved_images += 1
    
    def _save_image(self):
        img_save_path = expanduser("~/neu-underwater-robotics/surface/camera_"
                                   + str(self.camera_no)
                                   + "_capture_"
                                   + str(self._num_saved_images) + ".jpg")

        img_save_successful = cv2.imwrite(img_save_path, self._current_frame)
        if img_save_successful:
            print("Image saved to " + img_save_path)
            self._do_save_img = False
        else:
            print("Error: Image failed to save")