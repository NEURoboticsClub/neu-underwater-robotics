from PyQt5.QtWidgets import QGridLayout, QWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeyEvent
from .video_player import VideoPlayerWidget
from .AttitudeIndicatorWidget_Test import AttitudeIndicatorWidget_Test
from .AttitudeIndicatorWidget import AttitudeIndicatorWidget
from .ai import AttitudeIndicator

class GridVideoPlayersWidget(QWidget):
    """A grid of [1,4] video player widgets.

    The number of cells adapts to the number of given video player
    qurls.

    """
    def __init__(self, video_player_qurls, parent=None):
        """Constructs this widget with the given QUrls.

        Errors if the number of QUrls are not within the range [1,4]

        video_player_qurls : List[QUrl]

        """
        self.num_saved_images = 0
        num_cells = len(video_player_qurls)

        if num_cells == 0 or num_cells > 4:
            raise ValueError(("GridVideoPlayersWidget needs to be given [1,4] QUrls, "
                              f"but given {num_cells}."))

        super(GridVideoPlayersWidget, self).__init__(parent)

        # Set up the grid layout
        grid = QGridLayout()
        grid.setSpacing(0)
        grid.setContentsMargins(0, 0, 0, 0)

        self._video_players = [VideoPlayerWidget(qurl) for qurl in video_player_qurls]

        for i, video_player in enumerate(self._video_players):
            grid.addWidget(video_player, i // 2, i % 2)

        # Equally-sized cells
        grid.setColumnStretch(0, 1)
        grid.setRowStretch(0, 1)

        # Attitude indicator
        HOST = "127.0.0.1"  # Use localhost for testing
        PORT = 2049  # Same port as the GUI listener
        self.attitude_indicator = AttitudeIndicator()
        self.attitude_indicator.setFixedSize(200, 200)
        grid.addWidget(self.attitude_indicator, 0, 0, 2, 2, alignment=Qt.AlignCenter)



        if num_cells >= 2:
            grid.setColumnStretch(1, 1)

        if num_cells >= 3:
            grid.setRowStretch(1, 1)

        self.setLayout(grid)

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key_1:
            for i, video_player in enumerate(self._video_players):
                if i == 0:
                    video_player.show()
                else:
                    video_player.hide()
        elif event.key() == Qt.Key_2:
            for i, video_player in enumerate(self._video_players):
                if i == 1:
                    video_player.show()
                else:
                    video_player.hide()
        elif event.key() == Qt.Key_3:
            for i, video_player in enumerate(self._video_players):
                if i == 2:
                    video_player.show()
                else:
                    video_player.hide()
        elif event.key() == Qt.Key_4:
            for i, video_player in enumerate(self._video_players):
                if i == 3:
                    video_player.show()
                else:
                    video_player.hide()
        elif event.key() == Qt.Key_Escape:
            for i, video_player in enumerate(self._video_players):
                video_player.show()
        elif event.key() == Qt.Key_S:
            for i, video_player in enumerate(self._video_players):
                video_player.save_image(i, self.num_saved_images)
            self.num_saved_images += 1
