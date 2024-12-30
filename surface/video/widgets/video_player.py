from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtCore import QUrl

class VideoPlayerWidget(QWidget):
    """
    A PyQt5 Widget that plays a video with the given URL.

    This is best understood as a convenience class for combining
    QVideoWidget with QMediaPlayer.  While there are no methods, the
    class needs to inherit from QWidget.

    """
    def __init__(self, qurl, video_widget, parent=None):
        super(VideoPlayerWidget, self).__init__(parent)

        self.media_player = QMediaPlayer(self, QMediaPlayer.VideoSurface)
        self.video_widget = video_widget
        #self._set_layout_to_given(self.video_widget)
        self.media_player.setVideoOutput(self.video_widget)
        self.media_player.setMedia(QMediaContent(qurl))
        self.video_widget.show()
        self.media_player.play()

    def _set_layout_to_given(self, w):
        """Sets the layout of this widget to the given widget.

        w : QWidget
        """
        layout = QVBoxLayout()
        layout.addWidget(w)
        self.setLayout(layout)

from PyQt5 import QtWidgets

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        qurl = QUrl("gst-pipeline: udpsrc port=5000 ! application/x-rtp ! rtpjitterbuffer ! rtph264depay ! avdec_h264 ! videoconvert ! xvimagesink name=\"qtvideosink\"")
        video_widget = QVideoWidget(self)
        player = VideoPlayerWidget(qurl, video_widget, parent=self)
        self.setCentralWidget(video_widget)
        
        
if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    sys.exit(app.exec_())
