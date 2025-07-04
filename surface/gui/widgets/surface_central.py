from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QGridLayout
from PyQt5.QtCore import Qt, QTime, QTimer, QElapsedTimer
from .grid_video_players import GridVideoPlayersWidget
from common import utils

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
        self.grid_player = GridVideoPlayersWidget(video_player_qurls, self)
        layout.addWidget(self.grid_player, 0, 0)

        # telemetry attributes
        self.telemetry_depth = 0
        self.telemetry_velocity = utils.make_xyz_dict(0,0,0)
        self.telemetry_acceleration = utils.make_xyz_dict(0,0,0)
        self.elapsed_timer = QElapsedTimer()
        self.elapsed_timer.start()

        # telemetry box
        self.telemetry = QLabel(self._format_telemetry_text(), self)
        self.telemetry.setFixedSize(280, 75)
        layout.addWidget(self.telemetry, 0, 0, Qt.AlignTop | Qt.AlignRight)

        # status flags
        self.agnes_mode_flag = False
        self.agnes_mode_multiplier = 0.3
        self.auto_depth_flag = False

        # status flags box
        self.status_flags = QLabel(self._format_status_flags_text(), self)
        self.status_flags.setFixedSize(150, 50)
        layout.addWidget(self.status_flags, 0, 0, Qt.AlignBottom | Qt.AlignLeft)

        self.telemetry.setStyleSheet("""
            background-color: rgb(42, 107, 126);  /* Semi-transparent teal background */
            color: white;
            font-size: 16px;
            padding: 5px;
        """)

        self.status_flags.setStyleSheet("""
            background-color: rgb(42, 107, 126);  /* Semi-transparent teal background */
            color: white;
            font-size: 16px;
            padding: 5px;
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

        return f"Depth: {self.telemetry_depth:.2f}\nAcceleration(x, y, z): {self.telemetry_acceleration['x']:.2f}, {self.telemetry_acceleration['y']:.2f}, {self.telemetry_acceleration['z']:.2f}\nTimer: {min:02}:{sec:02}:{ms2:02}"
    
    def _format_status_flags_text(self):
        """Helper method to format the status flags text."""
        return f"Agnes Mode {'ON' if self.agnes_mode_flag else 'OFF'}\nMultiplier: {self.agnes_mode_multiplier:.2f}"

    def update_depth(self, depth):
        """Sets depth on the GUI and updates label"""
        self.telemetry_depth = depth
        self.telemetry.setText(self._format_telemetry_text())

    def update_imu(self, imu_data):
        """Sets depth on the GUI and updates label"""
        self.telemetry_velocity = imu_data["velocity"]
        self.telemetry_acceleration = imu_data["acceleration"]
        self.telemetry.setText(self._format_telemetry_text())
        game_quaternion = imu_data["game_quaternion"]
        roll, pitch, yaw = utils.euler_from_quaternion(game_quaternion["i"], game_quaternion["j"], game_quaternion["k"], game_quaternion["real"])
        self.grid_player.attitude_indicator.setRollPitch(roll, pitch)
    
    def update_status_flags(self, status_flags):
        self.agnes_mode_flag = status_flags["agnes_mode"]
        self.agnes_mode_multiplier = status_flags["agnes_factor"]
        self.auto_depth_flag = status_flags["auto_depth"]

    # mock incrementing 
    def _increment_telemetry(self):
        self.telemetry_depth += 0.1
        self.telemetry_velocity = 2.0
        self.telemetry.setText(self._format_telemetry_text())
