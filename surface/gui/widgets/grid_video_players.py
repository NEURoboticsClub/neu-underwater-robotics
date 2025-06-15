from PyQt5.QtWidgets import QGridLayout, QWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeyEvent
from .video_player import VideoPlayerWidget
from .ai import AttitudeIndicator
from typing import List
import os

PORT_NUM_TO_GST_PIPELINE_COMMAND = lambda port_no : f"gst-launch-1.0 udpsrc port={port_no} ! application/x-rtp ! rtpjitterbuffer ! rtph264depay ! avdec_h264 ! queue max-size-buffers=1 leaky=downstream ! videoconvert ! v4l2sink device=/dev/video{port_no} sync=false"

class GridVideoPlayersWidget(QWidget):
    """A grid of [1,4] video player widgets.

    The number of cells adapts to the number of given video player
    qurls.

    """
    def __init__(self, port_nums : List[int], parent=None):
        """Constructs this widget with the given QUrls.

        Errors if the number of QUrls are not within the range [1,4]

        video_player_qurls : List[QUrl]

        """
        self._current_fullscreen = -1
        num_cells = len(port_nums)

        if num_cells == 0 or num_cells > 4:
            raise ValueError(("GridVideoPlayersWidget needs to be given [1,4] QUrls, "
                              f"but given {num_cells}."))

        super(GridVideoPlayersWidget, self).__init__(parent)

        # Set up the grid layout
        self.grid = QGridLayout()
        self.grid.setSpacing(0)
        self.grid.setContentsMargins(0, 0, 0, 0)

        for i, _ in enumerate(port_nums):
            os.system(f"sudo modprobe v4l2loopback video_nr={i}")
            os.system(PORT_NUM_TO_GST_PIPELINE_COMMAND(i))
        
        self._video_players = [VideoPlayerWidget(port, i) for i, port in enumerate(port_nums)]

        for i, video_player in enumerate(self._video_players):
            self.grid.addWidget(video_player, i // 2, i % 2)

        # Equally-sized cells
        self.grid.setColumnStretch(0, 1)
        self.grid.setRowStretch(0, 1)

        # Attitude indicator
        self.attitude_indicator = AttitudeIndicator()
        self.attitude_indicator.setFixedSize(200, 200)
        self.grid.addWidget(self.attitude_indicator, 0, 0, 2, 2, alignment=Qt.AlignCenter)

        if num_cells >= 2:
            self.grid.setColumnStretch(1, 1)

        if num_cells >= 3:
            self.grid.setRowStretch(1, 1)

        self.setLayout(self.grid)

    def keyPressEvent(self, event: QKeyEvent):
        print("Key pressed")
        if event.key() == Qt.Key_1:
            print("Key 1 pressed")
            if self._current_fullscreen != -1:
                self.grid.addWidget(self._video_players[self._current_fullscreen],
                                        self._current_fullscreen // 2,
                                        self._current_fullscreen % 2)
                self._video_players[self._current_fullscreen].showNormal()
            self.grid.removeWidget(self._video_players[0])
            self._video_players[0].showFullScreen()
        elif event.key() == Qt.Key_2:
            print("Key 2 pressed")
            if self._current_fullscreen != -1:
                self.grid.addWidget(self._video_players[self._current_fullscreen],
                                        self._current_fullscreen // 2,
                                        self._current_fullscreen % 2)
                self._video_players[self._current_fullscreen].showNormal()
            self.grid.removeWidget(self._video_players[1])
            self._video_players[1].showFullScreen()
        elif event.key() == Qt.Key_3:
            print("Key 3 pressed")
            if self._current_fullscreen != -1:
                self.grid.addWidget(self._video_players[self._current_fullscreen],
                                        self._current_fullscreen // 2,
                                        self._current_fullscreen % 2)
                self._video_players[self._current_fullscreen].showNormal()
            self.grid.removeWidget(self._video_players[2])
            self._video_players[2].showFullScreen()
        elif event.key() == Qt.Key_4:
            print("Key 4 pressed")
            if self._current_fullscreen != -1:
                self.grid.addWidget(self._video_players[self._current_fullscreen],
                                        self._current_fullscreen // 2,
                                        self._current_fullscreen % 2)
                self._video_players[self._current_fullscreen].showNormal()
            self.grid.removeWidget(self._video_players[3])
            self._video_players[3].showFullScreen()
        elif event.key() == Qt.Key_Escape:
            print("Key esc pressed")
            if self._current_fullscreen != -1:
                self.grid.addWidget(self._video_players[self._current_fullscreen],
                                        self._current_fullscreen // 2,
                                        self._current_fullscreen % 2)
                self._video_players[self._current_fullscreen].showNormal()
        elif event.key() == Qt.Key_S:
            print("Key s pressed")
            for video_player in self._video_players:
                video_player.save_image()
        event.accept()
