from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QGridLayout, QGraphicsOpacityEffect
from PyQt5.QtCore import Qt, QTime, QTimer, QElapsedTimer
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

        layout = QGridLayout()
        layout.setContentsMargins(0, 0, 0, 0)  #
        layout.addWidget(GridVideoPlayersWidget(video_player_qurls, self), 0, 0)

        self.telemetry_depth = 0
        self.telemetry_velocity = 10
        self.elapsed_timer = QElapsedTimer()
        self.elapsed_timer.start()

        #self.telemetry = QLabel("Depth: 0\nVelocity: 10\nTimer: 00:00:00", self)
        #self.telemetry.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        #self.telemetry.setAttribute(Qt.WA_TranslucentBackground, True)
        self.telemetry = QLabel(self._format_telemetry_text(), self)
        layout.addWidget(self.telemetry, 0, 0, Qt.AlignTop | Qt.AlignRight)
        opacity_effect = QGraphicsOpacityEffect(self.telemetry)
        opacity_effect.setOpacity(0.8)  # Set the opacity (0.8 = 80% visible)
        self.telemetry.setGraphicsEffect(opacity_effect)
        
        self.telemetry.setStyleSheet("""
            background-color: rgb(42, 107, 126);  /* Semi-transparent teal background */
            color: white;
            font-size: 32px;
            padding: 10px;
        """)

        #TODO:
        # 1. RUN TO SEE IT WORKING DONE
        # 2. UPDATE NUMBERS (FROM URAQT) DONE
        # 3. HAVE ATTITUDE CONTROL THRU SENSOR
        # 4. WIDGETIZE IT
        # 5. ADD TIMER, 

        #inner_vlayout = QVBoxLayout()
        #layout.addLayout(inner_vlayout)

        #self.telemetry = QLabel("Depth: 0\nVelocity: 10\nAcceleration: 5", self)
        #self.photogrammetry = QLabel("Photogrammetry", self)
        #self.status_view = self.telemetry

        # Set alignment and styles for demonstration
        # for label in [self.telemetry, self.photogrammetry]:
        #     label.setAlignment(Qt.AlignRight | Qt.AlignTop)
        #     label.setStyleSheet("background-color: #2a6b7e; color: white; font-size: 36px;")

        #layout.addWidget(self.photogrammetry)

        # # Place widgets in the vlayout
        # inner_vlayout.addWidget(self.telemetry)
        # inner_vlayout.addWidget(self.photogrammetry)

        self.setLayout(layout)

        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self._increment_telemetry)
        self.update_timer.start(50)

    def _format_telemetry_text(self):
        """Helper method to format the telemetry text."""
        elapsed_ms = self.elapsed_timer.elapsed()
        min = (elapsed_ms // 60000) % 60
        sec = (elapsed_ms // 1000)  % 60
        ms2 = (elapsed_ms  % 1000) // 10

        return f"Depth: {self.telemetry_depth:.2f}\nVelocity: {self.telemetry_velocity:.2f}\nTimer: {min:02}:{sec:02}:{ms2:02}"

    def _increment_telemetry(self):
        self.telemetry_depth += 0.1
        self.telemetry_velocity = 2.0
        self.telemetry.setText(self._format_telemetry_text())

    # def update_telemetry(self, depth=None, velocity=None, timer_value=None):
    #     """Update telemetry values on the UI."""
    #     if depth is not None:
    #         self.depth = depth
    #     if velocity is not None:
    #         self.velocity = velocity
    #     if timer_value is not None:
    #         self.timer_value = timer_value

    #     self.telemetry.setText(self._format_telemetry_text())
