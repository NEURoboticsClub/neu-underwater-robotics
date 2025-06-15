from PyQt5.QtWidgets import QWidget, QVBoxLayout
from .camera_feed import CameraFeed
from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtCore import QUrl
import time

PORT_NUM_TO_VIDEO_PATH = lambda port_no : f"/dev/video{port_no}"

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
    def __init__(self, port_no : int, camera_no : int, parent=None, on_media_status_changed=None, on_error=None):
        """Constructs this widget, and set this media player to play
        state.

        port_no : int -- port number of the camera

        """
        super(VideoPlayerWidget, self).__init__()

        print("Initializing video player on port " + str(port_no))

        self.media_player = QMediaPlayer(self, QMediaPlayer.VideoSurface)
        if on_media_status_changed:
            self.media_player.mediaStatusChanged.connect(on_media_status_changed)
        if on_error:
            self.media_player.error.connect(on_error)
        self.media_player.error.connect(self.on_error)

        video_widget = QVideoWidget(self)
        self._set_layout_to_given(video_widget)

        self.media_player.setVideoOutput(video_widget)
        self.media_player.setMedia(QMediaContent(QUrl.fromLocalFile(PORT_NUM_TO_VIDEO_PATH(camera_no))))
        self.media_player.play()
        self.camera_feed = CameraFeed(port_no, camera_no)
        self.open_camera()
    
    def open_camera(self):        
        self.camera_feed.start()
        print("Camera feed running? " + str(self.camera_feed.isRunning()))

    def _set_layout_to_given(self, w):
        """Sets the layout of this widget to the given widget.

        w : QWidget
        """
        layout = QVBoxLayout()
        layout.addWidget(w)
        layout.setContentsMargins(0, 0, 0, 0) 
        self.setLayout(layout)

    def on_error(self, new_error):
        """Watches for changes to the error state, and raises an
        exception if there is one.

        new_error : QMediaPlayer.Error
        """
        # TODO(error): Ought to make a custom exception, Exception is
        # too generic.
        if new_error != 0:
            raise Exception(f"Media player error state: {new_error}")

    def save_image(self):
        print("saving image (video_player)")
        self.camera_feed.save_image()
