from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout
from PyQt5.QtCore import Qt
from .grid_video_players import GridVideoPlayersWidget

# An ISurfaceCentralWidget is a QWidget that takes in a list of QUrls
# in its __init__.

class SurfaceCentralWidget(QWidget):
    """The central widget for the surface window.
    """
    def __init__(self, video_player_qurls):
        """Constructs this widget with the given QUrls.

        video_player_qurls : List[QUrl]

        """
        super().__init__()

        layout = QHBoxLayout()
        layout.addWidget(GridVideoPlayersWidget(video_player_qurls, self))
        inner_vlayout = QVBoxLayout()
        layout.addLayout(inner_vlayout)

        self.telemetry = QLabel("Depth: 0\nVelocity: 10\nAcceleration: 5", self)
        self.photogrammetry = QLabel("Photogrammetry", self)
        self.status_view = self.telemetry

        # Set alignment and styles for demonstration
        for label in [self.telemetry, self.photogrammetry]:
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet("background-color: #2a6b7e; color: white; font-size: 36px;")

        # Place widgets in the vlayout
        inner_vlayout.addWidget(self.telemetry)
        inner_vlayout.addWidget(self.photogrammetry)

        self.setLayout(layout)
