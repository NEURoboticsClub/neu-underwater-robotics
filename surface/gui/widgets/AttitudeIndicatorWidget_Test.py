from PyQt5 import QtWidgets, QtCore
from .ai import AttitudeIndicator

class AttitudeIndicatorWidget_Test(QtWidgets.QWidget):
    """Test class for ai with sliders"""

    def __init__(self):
        super(AttitudeIndicatorWidget_Test, self).__init__()

        self.initUI()

    def updatePitch(self, pitch):
        self.wid.setPitch(pitch - 90)

    def updateRoll(self, roll):
        self.wid.setRoll((roll / 10.0) - 180.0)
    
    def updateTarget(self, target):
        self.wid.setHover(500+target/10.)
    def updateBaro(self, asl):
        self.wid.setBaro(500+asl/10.)           
    
    
    def initUI(self):

        vbox = QtWidgets.QVBoxLayout()

        sld = QtWidgets.QSlider(QtCore.Qt.Horizontal, self)
        sld.setFocusPolicy(QtCore.Qt.NoFocus)
        sld.setRange(0, 3600)
        sld.setValue(1800)
        vbox.addWidget(sld)
        
        
        self.wid = AttitudeIndicator()

        sld.valueChanged[int].connect(self.updateRoll)
        vbox.addWidget(self.wid)

        hbox = QtWidgets.QHBoxLayout()
        hbox.addLayout(vbox)

        sldPitch = QtWidgets.QSlider(QtCore.Qt.Vertical, self)
        sldPitch.setFocusPolicy(QtCore.Qt.NoFocus)
        sldPitch.setRange(0, 180)
        sldPitch.setValue(90)
        sldPitch.valueChanged[int].connect(self.updatePitch)
        hbox.addWidget(sldPitch)
                    

        self.setLayout(hbox)
        scale = 0.5

        self.setGeometry(round(50*scale), round(50*scale), round(510*scale), round(510*scale))


    def changeValue(self, value):

        self.c.updateBW.emit(value)
        self.wid.repaint()
        