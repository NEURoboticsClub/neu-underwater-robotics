from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QGridLayout, QGraphicsOpacityEffect
from PyQt5.QtCore import Qt, QTime, QTimer, QElapsedTimer
from .grid_video_players import GridVideoPlayersWidget
import math

# An ISurfaceCentralWidget is a QWidget that takes in a list of QUrls
# in its __init__.

def euler_from_quaternion(x, y, z, w):
        """
        Convert a quaternion into euler angles (roll, pitch, yaw)
        roll is rotation around x in radians (counterclockwise)
        pitch is rotation around y in radians (counterclockwise)
        yaw is rotation around z in radians (counterclockwise)
        """
        t0 = +2.0 * (w * x + y * z)
        t1 = +1.0 - 2.0 * (x * x + y * y)
        roll_x = math.atan2(t0, t1)
     
        t2 = +2.0 * (w * y - z * x)
        t2 = +1.0 if t2 > +1.0 else t2
        t2 = -1.0 if t2 < -1.0 else t2
        pitch_y = math.asin(t2)
     
        t3 = +2.0 * (w * z + x * y)
        t4 = +1.0 - 2.0 * (y * y + z * z)
        yaw_z = math.atan2(t3, t4)
     
        return roll_x, pitch_y, yaw_z # in radians

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
        self.telemetry_velocity = {}
        self.telemetry_velocity["x"] = 0
        self.telemetry_velocity["y"] = 0
        self.telemetry_velocity["z"] = 0
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

        return f"Depth: {self.telemetry_depth:.2f}\nVelocity(x, y, z): {self.telemetry_velocity['x']:.2f}, {self.telemetry_velocity['y']:.2f}, {self.telemetry_velocity['z']:.2f}\nTimer: {min:02}:{sec:02}:{ms2:02}"
    
    def update_depth(self, depth):
        """Sets depth on the GUI and updates label"""
        self.telemetry_depth = depth
        self.telemetry.setText(self._format_telemetry_text())

    def update_imu(self, imu_data):
        """Sets depth on the GUI and updates label"""
        self.telemetry_velocity = imu_data["acceleration"]
        self.telemetry.setText(self._format_telemetry_text())
        game_quaternion = imu_data["game quaternion"]
        roll, pitch, yaw = euler_from_quaternion(game_quaternion["i"], game_quaternion["j"], game_quaternion["k"], game_quaternion["real"])
        self.grid_player.attitude_indicator.setRollPitch(roll, pitch)

    # mock incrementing 
    def _increment_telemetry(self):
        self.telemetry_depth += 0.1
        self.telemetry_velocity = 2.0
        self.telemetry.setText(self._format_telemetry_text())
