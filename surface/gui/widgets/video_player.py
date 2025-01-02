from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtCore import QUrl

class VideoPlayerWidget(QWidget):
    """A PyQt5 Widget that plays a video with the given QUrl.

    If the media player is unable to play with the given QUrl, an
    generic exception is raised with the error state value.

    This is best understood as a convenience class for combining
    QVideoWidget with QMediaPlayer.  While there are no methods, the
    class needs to inherit from QWidget.

    For documentation on the interactions between GST, the video
    widget and the media player, see
    https://doc.qt.io/qt-5/qmediaplayer.html#setMedia

    By accepting a QUrl, this widget expects that its clients assemble
    the QUrl.  In the future, we may find that we prefer to have the
    parsing done within this widget.
    """
    def __init__(self, qurl, parent=None, on_media_status_changed=None, on_error=None):
        """Constructs a new video player widget.

        qurl : QUrl -- To be passed into a QMediaContent, and is set
        to the internal media player.

        parent : QWidget?

        on_media_status_changed : [MediaStatus -> Void]?

        on_error : [QMediaPlayer.Error -> Void]?
        """
        super(VideoPlayerWidget, self).__init__(parent)

        # Create media player, and attach listeners
        media_player = QMediaPlayer(self, QMediaPlayer.VideoSurface)
        if on_media_status_changed:
            media_player.mediaStatusChanged.connect(on_media_status_changed)
        if on_error:
            media_player.error.connect(on_error)
        media_player.error.connect(self.on_error)

        # Video widget
        video_widget = QVideoWidget(self)
        self._set_layout_to_given(video_widget)

        # Finish setting up media player
        media_player.setVideoOutput(video_widget)
        media_player.setMedia(QMediaContent(qurl))
        media_player.play()

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

