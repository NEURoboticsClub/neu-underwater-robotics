from PyQt5.QtWidgets import QApplication, QWidget, QGridLayout, QLabel, QVBoxLayout, QSlider, QHBoxLayout
from PyQt5.QtCore import Qt
from .video_player import VideoPlayerWidget

class SurfaceCentralWidget(QWidget):
    """The central widget for the surface window.
    """
    def __init__(self, tl_qurl, tr_qurl, bl_qurl, br_qurl):
        """Constructs this widget with the given camera QUrl.

        tl_qurl : QUrl -- For the top-left camera view.
        tr_qurl : QUrl -- For the top-right camera view.
        bl_qurl : QUrl -- For the bottom-left camera view.
        br_qurl : QUrl -- For tthe bottom-right camera view.
        """
        super().__init__()

        # Set up the grid layout
        grid = QGridLayout()

        # Create camera views and status labels
        self.tl_vp = VideoPlayerWidget(tl_qurl)
        self.bl_vp = VideoPlayerWidget(bl_qurl)
        self.tr_vp = VideoPlayerWidget(tr_qurl)
        self.br_vp = VideoPlayerWidget(br_qurl)
        self.telemetry = QLabel("Depth: 0\nVelocity: 10\nAcceleration: 5", self)
        self.photogrammetry = QLabel("Photogrammetry", self)

        self.status_view = self.telemetry

        # Set alignment and styles for demonstration
        for label in [self.telemetry, self.photogrammetry]:
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet("background-color: #2a6b7e; color: white; font-size: 36px;")

        # Place widgets in the grid layout
        grid.addWidget(self.tl_vp, 0, 0)
        grid.addWidget(self.tr_vp, 0, 1)
        grid.addWidget(self.telemetry, 0, 2)
        grid.addWidget(self.bl_vp, 1, 0)
        grid.addWidget(self.br_vp, 1, 1)
        grid.addWidget(self.photogrammetry, 1, 2)

        grid.setColumnStretch(0, 2)  # Wider columns on the left
        grid.setColumnStretch(1, 2)
        grid.setColumnStretch(2, 1)  # Narrow column on the right

        self.setLayout(grid)
