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

        # telemetry attributes
        self.telemetry_depth = 0
        self.telemetry_velocity = 10
        self.elapsed_timer = QElapsedTimer()
        self.elapsed_timer.start()

        # telemetry box
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
        # 1. HAVE ATTITUDE CONTROL THRU SENSOR
        # 2. WIDGETIZE THE TELEMETRY BOX
        # 3. ADD TIMER WITH START/STOP BUTTONS
        # 4. SHOW AUTONOMY STATUS(ES)

        self.setLayout(layout)

        self.update_timer = QTimer(self)
        #self.update_timer.timeout.connect(self._increment_telemetry) # mock incrementing
        self.update_timer.start(50)

    def _format_telemetry_text(self):
        """Helper method to format the telemetry text."""
        elapsed_ms = self.elapsed_timer.elapsed()
        min = (elapsed_ms // 60000) % 60
        sec = (elapsed_ms // 1000)  % 60
        ms2 = (elapsed_ms  % 1000) // 10

        return f"Depth: {self.telemetry_depth:.2f}\nVelocity: {self.telemetry_velocity:.2f}\nTimer: {min:02}:{sec:02}:{ms2:02}"
    
    def update_depth(self, depth):
        """Sets depth on the GUI and updates label"""
        self.telemetry_depth = depth
        self.telemetry.setText(self._format_telemetry_text())

    # mock incrementing 
    def _increment_telemetry(self):
        self.telemetry_depth += 0.1
        self.telemetry_velocity = 2.0
        self.telemetry.setText(self._format_telemetry_text())
