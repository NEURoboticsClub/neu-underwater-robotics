from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import pyqtSlot as Slot, Qt
from .camera_feed import CameraFeed

# TODO(config): Users ought to be able to specify this without prying
# into the code.
PORT_NUM_TO_CV2_GST_PIPELINE_COMMAND = lambda qurl : str(qurl)[len("gst-pipeline: "):].replace('xvimagesink name=%22qtvideosink%22', 'appsink')

class VideoPlayerWidget(QWidget):
    """A PyQt5 Widget that plays a video with the given QUrl.

    If the media player is unable to play with the given QUrl, a
    generic exception is raised with the error state value.

    This is best understood as a convenience class for combining
    QVideoWidget with QMediaPlayer.

    For documentation on the interactions between GST, the video
    widget and the media player, see
    https://doc.qt.io/qt-5/qmediaplayer.html#setMedia

    """
    def __init__(self, port_no : int, camera_no : int):
        """Constructs this widget, and set this media player to play
        state.

        port_no : int -- port number of the camera

        """
        super(VideoPlayerWidget, self).__init__()

        print("Initializing video player on port " + str(port_no))

        self.camera_feed = CameraFeed(port_no, camera_no)
        self.label = QLabel()
        self.label.setAlignment(Qt.AlignCenter)
        self._set_layout_to_given(self.label)
        self.open_camera()
    
    def open_camera(self):        
        self.camera_feed.start()
        print("Camera feed running? " + str(self.camera_feed.isRunning()))
        self.camera_feed.frame_signal.connect(self._setImage)
        print("Camera feed signal connected to video player")

    @Slot(QImage)
    def _setImage(self, img : QImage):
        self.label.setPixmap(QPixmap.fromImage(img))

    def resizeEvent(self, event):
        if self.label.pixmap():
            scaled_pixmap = self.label.pixmap().scaled(self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.label.setPixmap(scaled_pixmap)
        super().resizeEvent(event)
    
    def _set_layout_to_given(self, w):
        """Sets the layout of this widget to the given widget.

        w : QWidget
        """
        layout = QVBoxLayout()
        layout.addWidget(w)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

    def save_image(self):
        self.camera_feed.save_image()
