from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import pyqtSlot as Slot, Qt
from .camera_feed import CameraFeed

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
        scaled_pixmap = QPixmap.fromImage(img).scaled(self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.label.setPixmap(scaled_pixmap)
    
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
