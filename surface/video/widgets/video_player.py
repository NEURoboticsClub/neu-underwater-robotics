from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtCore import QUrl

class VideoPlayerWidget(QWidget):
    """A PyQt5 Widget that plays a video with the given URL.

    This is best understood as a convenience class for combining
    QVideoWidget with QMediaPlayer.  While there are no methods, the
    class needs to inherit from QWidget.

    For documentation on the interactions between GST, the video
    widget and the media player, see
    https://doc.qt.io/qt-5/qmediaplayer.html#setMedia

    By accepting a QUrl, this widget expects that its clients assemble
    the QUrl. In the future, we may find that we prefer to have the
    parsing done within this widget.

    """
    def __init__(self, qurl, parent=None):
        """Constructs a new video player widget.
        
        qurl : QUrl -- To be passed into a QMediaContent, and is set
        to the internal media player.
        
        parent : QWidget?

        """
        super(VideoPlayerWidget, self).__init__(parent)

        media_player = QMediaPlayer(self, QMediaPlayer.VideoSurface)
        media_player.mediaStatusChanged.connect(self.on_media_changed)
        media_player.error.connect(self.on_state_changed)
        video_widget = QVideoWidget(self)
        self._set_layout_to_given(video_widget)
        media_player.setVideoOutput(video_widget)
        media_content = QMediaContent(qurl)
        media_player.setMedia(media_content)
        media_player.play()

    def _set_layout_to_given(self, w):
        """Sets the layout of this widget to the given widget.

        w : QWidget
        """
        layout = QVBoxLayout()
        layout.addWidget(w)
        self.setLayout(layout)

    def on_media_changed(self, new_media):
        print(f"Media changed to: {new_media}")

    def on_state_changed(self, new_state):
        print(f"State changed to: {new_state}")

if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    qurl = QUrl("gst-pipeline: udpsrc port=5000 ! application/x-rtp ! rtpjitterbuffer ! rtph264depay ! avdec_h264 ! videoconvert ! xvimagesink name=\"qtvideosink\"")
    player = VideoPlayerWidget(qurl)
    player.show()
    sys.exit(app.exec_())
