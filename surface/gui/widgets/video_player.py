from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent, QVideoProbe, QVideoFrame
from PyQt5.QtGui import QImage
from PyQt5.QtMultimediaWidgets import QVideoWidget

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
    def __init__(self, qurl, parent=None, on_media_status_changed=None, on_error=None):
        """Constructs this widget, and set this media player to play
        state.

        qurl : QUrl -- To be passed into a QMediaContent, and is set
        to the internal media player.

        parent : Optional[QWidget]

        on_media_status_changed : Optional[[MediaStatus -> Void]]

        on_error : Optional[[QMediaPlayer.Error -> Void]]

        """
        super(VideoPlayerWidget, self).__init__(parent)

        # Create media player, and attach listeners
        self.media_player = QMediaPlayer(self, QMediaPlayer.VideoSurface)
        if on_media_status_changed:
            self.media_player.mediaStatusChanged.connect(on_media_status_changed)
        if on_error:
            self.media_player.error.connect(on_error)
        self.media_player.error.connect(self.on_error)

        # Video widget
        video_widget = QVideoWidget(self)
        self._set_layout_to_given(video_widget)

        # Finish setting up media player
        self.media_player.setVideoOutput(video_widget)

        self.do_save_image = False
        self.img_save_path = "capture_path_error.jpg"
        self.probe = QVideoProbe()
        self.probe.setSource(self.media_player)
        self.probe.videoFrameProbed.connect(self.process_frame)

        self.media_player.setMedia(QMediaContent(qurl))
        self.media_player.play()

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
    
    def save_image(self, camera_no, num_saved_images):
        self.do_save_image = True
        self.img_save_path = "camera_" + camera_no + "_capture_" + num_saved_images + ".jpg"

    def process_frame(self, frame: QVideoFrame):
        if frame.isValid() and self.do_save_image:
            self.do_save_image = False

            frame.map(QVideoFrame.ReadOnly)

            image = QImage(
                frame.bits(),
                frame.width(),
                frame.height(),
                frame.bytesPerLine(),
                QVideoFrame.imageFormatFromPixelFormat(frame.pixelFormat())
            )

            frame.unmap()

            image.save(self.img_save_path)
            print("Image saved to " + self.img_save_path)

