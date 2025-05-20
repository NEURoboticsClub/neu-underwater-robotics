from .IMUListener import IMUListener
from PyQt5 import QtWidgets
from .ai import AttitudeIndicator

class AttitudeIndicatorWidget(QtWidgets.QWidget):
    """Wrapper for AttitudeIndicator with real-time IMU updates."""

    def __init__(self, host, port):
        super(AttitudeIndicatorWidget, self).__init__()
        self.initUI()

        # Start IMU listener thread
        self.imu_listener = IMUListener(host, port)
        self.imu_listener.imu_data_received.connect(self.handleIMUData)
        self.imu_listener.start()

    def handleIMUData(self, data):
        """Update the AttitudeIndicator based on received IMU data."""
        # Parse the rotation vector or any other data you need
        rotation_vector = data.get("rotation vector", "")
        if rotation_vector:

            components = rotation_vector.split()  # Example: "I: 0.123 J: 0.456 ..."
            print(components)
            i = float(components[1])  # Example: Parse 'I: 0.123' -> 0.123
            j = float(components[3])  # Example: Parse 'J: 0.456' -> 0.456
            r = float(components[7])  
            k = float(components[5])  
            roll, pitch, yaw = euler_from_quaternion(i,j,k,r)
            self.wid.setRoll(roll*180/math.pi)
            self.wid.setPitch(pitch*180/math.pi)

    def closeEvent(self, event):
        """Ensure the listener stops when the widget is closed."""
        self.imu_listener.stop()
        self.imu_listener.wait()
        super().closeEvent(event)

    def initUI(self):
        """Set up the AttitudeIndicator widget."""
        vbox = QtWidgets.QVBoxLayout()
        self.wid = AttitudeIndicator()
        vbox.addWidget(self.wid)
        self.setLayout(vbox)

import math
 
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
