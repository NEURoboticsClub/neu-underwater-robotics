from PyQt5.QtWidgets import QApplication, QWidget, QGridLayout, QLabel, QVBoxLayout, QSlider, QHBoxLayout
from PyQt5.QtCore import Qt
from ai import AttitudeIndicator

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        

        # Set up the grid layout
        grid = QGridLayout()


        # Create camera views and status labels
        self.camera_view_1 = QLabel("Camera View 1", self)
        self.camera_view_2 = QLabel("Camera View 2", self)
        self.camera_view_3 = QLabel("Camera View 3", self)
        self.camera_view_4 = QLabel("Camera View 4", self)
        self.telemetry = QLabel("Depth: 0\nVelocity: 10\nAcceleration: 5", self)
        self.photogrammetry = QLabel("Photogrammetry", self)
        self.attitude_indicator = AttitudeIndicator()


        self.status_view = self.telemetry

        # Set alignment and styles for demonstration
        for label in [self.camera_view_1, self.camera_view_2, self.camera_view_3, self.camera_view_4, self.telemetry, self.photogrammetry]:
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet("background-color: #2a6b7e; color: white; font-size: 36px;")

        # Place widgets in the grid layout
        grid.addWidget(self.camera_view_1, 0, 0)
        grid.addWidget(self.camera_view_3, 0, 1)
        grid.addWidget(self.telemetry, 0, 2)
        grid.addWidget(self.camera_view_2, 1, 0)
        grid.addWidget(self.camera_view_4, 1, 1)
        grid.addWidget(self.photogrammetry, 1, 2)

        grid.setColumnStretch(0, 2)  # Wider columns on the left
        grid.setColumnStretch(1, 2)
        grid.setColumnStretch(2, 1)  # Narrow column on the right

        # Center circle (could be a separate widget or placeholder)
        # self.circle_placeholder = QLabel(self)
        # self.circle_placeholder.setFixedSize(100, 100)
        # self.circle_placeholder.setStyleSheet("background-color: #2a6b7e; border-radius: 50px;")


        grid.addWidget(self.attitude_indicator, 1, 1, 1, 2, alignment=Qt.AlignCenter)

        vbox = QVBoxLayout()
        sld = QSlider(Qt.Horizontal, self)
        sld.setFocusPolicy(Qt.NoFocus)
        sld.setRange(0, 3600)
        sld.setValue(1800)
        vbox.addWidget(sld)
        
        
        self.wid = AttitudeIndicator()

        sld.valueChanged[int].connect(self.updateRoll)
        vbox.addWidget(self.wid)

        hbox = QHBoxLayout()
        hbox.addLayout(vbox)

        sldPitch = QSlider(Qt.Vertical, self)
        sldPitch.setFocusPolicy(Qt.NoFocus)
        sldPitch.setRange(0, 180)
        sldPitch.setValue(90)
        sldPitch.valueChanged[int].connect(self.updatePitch)
        hbox.addWidget(sldPitch)

        # Set layout and window properties
        self.setLayout(grid)
        self.setWindowTitle("Camera View Layout")
        self.setGeometry(100, 100, 800, 600)
        
    def updatePitch(self, pitch):
        self.wid.setPitch(pitch - 90)

    def updateRoll(self, roll):
        self.wid.setRoll((roll / 10.0) - 180.0)
    
    def updateTarget(self, target):
        self.wid.setHover(500+target/10.)
    def updateBaro(self, asl):
        self.wid.setBaro(500+asl/10.)

    def changeValue(self, value):

        self.c.updateBW.emit(value)
        self.wid.repaint()