from PyQt5.QtWidgets import QApplication, QWidget, QGridLayout, QLabel, QVBoxLayout, QSlider, QHBoxLayout
from PyQt5.QtCore import Qt
from .video_player import VideoPlayerWidget

# An ISurfaceCentralWidget is a QWidget that takes in a list of QUrls
# in its __init__.

class SurfaceCentralWidget(QWidget):
    """The central widget for the surface window.
    """
    def __init__(self, video_player_qurls):
        """Constructs this widget with the given camera QUrl.

        video_player_qurls : [Listof QUrl]
        """
        super().__init__()

        # Set up the grid layout
        grid = QGridLayout()
        grid.setSpacing(0)
        grid.setContentsMargins(0, 0, 0, 0) 

        # Create camera views and status labels
        self.tl_vp = VideoPlayerWidget(video_player_qurls[0], self)
        self.bl_vp = VideoPlayerWidget(video_player_qurls[1], self)
        self.tr_vp = VideoPlayerWidget(video_player_qurls[2], self)
        self.br_vp = VideoPlayerWidget(video_player_qurls[3], self)
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

        # Top and bottom rows must have same height
        grid.setRowStretch(0, 1)
        grid.setRowStretch(1, 1)

        self.setLayout(grid)
