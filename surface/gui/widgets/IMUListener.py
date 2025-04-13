import socket
import json
from PyQt5.QtCore import QThread, pyqtSignal

class IMUListener(QThread):
    """component of Attitude Indicator that listens to IMU data"""
    
    imu_data_received = pyqtSignal(dict)  # Signal to send IMU data to the main thread

    def __init__(self, host, port, parent=None):
        super(IMUListener, self).__init__(parent)
        self.host = host
        self.port = port
        self.running = True

    def run(self):
        """Connect to the IMU server and listen for data."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            print(f"Connecting to {self.host}:{self.port}")
            try:
                s.connect((self.host, self.port))  # Connect to the mock IMU server
                print("Connected to IMU server")
                while self.running:
                    data = s.recv(1024)  # Receive up to 1024 bytes
                    if not data:
                        break
                    imu_data = json.loads(data.decode('utf-8'))  # Decode JSON data
                    self.imu_data_received.emit(imu_data)  # Emit signal with data
            except Exception as e:
                print(f"Error: {e}")

    def stop(self):
        """Stop the thread."""
        self.running = False
