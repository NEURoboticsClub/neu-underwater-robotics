#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#     ||          ____  _ __
#  +------+      / __ )(_) /_______________ _____  ___
#  | 0xBC |     / __  / / __/ ___/ ___/ __ `/_  / / _ \
#  +------+    / /_/ / / /_/ /__/ /  / /_/ / / /_/  __/
#   ||  ||    /_____/_/\__/\___/_/   \__,_/ /___/\___/
#
#  Copyright (C) 2011-2013 Bitcraze AB
#
#  Crazyflie Nano Quadcopter Client
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.

#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

"""
(Off the shelf) Attitude indicator widget.
"""

__author__ = 'Bitcraze AB'
__all__ = ['AttitudeIndicator']

import sys
from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtCore import pyqtSlot, pyqtSignal, Qt

class AttitudeIndicator(QtWidgets.QWidget):
    """Widget for showing attitude"""

    sigMakeSpace = pyqtSignal()


    def __init__(self, hz=30):
        super(AttitudeIndicator, self).__init__()


        self.roll = 0
        self.pitch = 0
        self.hover = False
        self.hoverASL = 0.0
        self.hoverTargetASL = 0.0
        self.pixmap = None # Background camera image
        self.needUpdate = True
        self.killswitch = False # killswitch active
        self.recovery = False # recovery mode active

        self.msg = ""
        self.hz = hz

        self.freefall = 0
        self.crashed  = 0
        self.ff_acc   = 0
        self.ff_m     = 0
        self.ff_v     = 0

        self.setMinimumSize(30, 30)
        # self.setMaximumSize(240,240)

        # Update self at 30hz
        self.updateTimer = QtCore.QTimer(self)
        self.updateTimer.timeout.connect(self.updateAI)
        self.updateTimer.start(round(1000/self.hz))

        self.msgRemove = 0


    def mouseDoubleClickEvent (self, e):
        self.sigMakeSpace.emit()


    def updateAI(self):
        if self.msgRemove>0:
            self.msgRemove -= 1
            if self.msgRemove <= 0:
                self.msg = ""
                self.needUpdate = True


        if self.freefall>0:
            self.freefall = self.freefall*5/6 -1
            self.needUpdate = True

        if self.crashed>0:
            self.crashed = self.crashed*5/6 -1
            self.needUpdate = True

        if self.isVisible() and self.needUpdate:
            self.needUpdate = False
            self.repaint()

    def setRoll(self, roll):
        self.roll = roll
        self.needUpdate = True

    def setPitch(self, pitch):
        self.pitch = pitch
        self.needUpdate = True
        
    def setHover(self, target):        
        self.hoverTargetASL = target
        self.hover = target>0
        self.needUpdate = True
        
    def setBaro(self, asl):
        self.hoverASL = asl;
        self.needUpdate = True

    def setRollPitch(self, roll, pitch):
        self.roll = roll
        self.pitch = pitch
        self.needUpdate = True

    def paintEvent(self, e):
        qp = QtGui.QPainter()
        qp.begin(self)
        self.drawWidget(qp)
        qp.end()

    @pyqtSlot(QtGui.QPixmap)
    def setPixmap(self, pm):
        self.pixmap = pm
        self.needUpdate = True

    @pyqtSlot(bool)
    def setVideo(self, on):
        if not on:
            self.pixmap = None
            self.needUpdate = True

    @pyqtSlot(bool)
    def setKillSwitch(self, on):
        self.killswitch = on
        self.needUpdate = True

    @pyqtSlot()
    def setFreefall(self):
        self.setMsg("Free fall detected!")
        self.freefall = 250
        self.needUpdate = True

    @pyqtSlot(float)
    def setCrash(self, badness=1.):
        """ a bad crash has badnees = 1, severe = badness = 2, and everything between landing softly and a crash between 0 and 1"""
        self.crashed = 128+badness*128
        self.needUpdate = True

    @pyqtSlot(float, float, float)
    def setFFAccMeanVar(self, a, m ,v):
        self.ff_acc = a
        self.ff_m = m
        self.ff_v = v
        self.needUpdate = True

    def setRecovery(self, on, msg=""):
        """ Set the AUTO caption """
        self.recovery = on
        self.needUpdate = True
        self.setMsg(msg)

    @pyqtSlot(str)
    def setMsg(self, msg, duration=2):
        """ Set a message to display at the bottom of the AI for duration seconds """
        self.msg = msg
        self.msgRemove = duration * self.hz




    def drawWidget(self, qp):
        size = self.size()
        w = size.width()
        h = size.height()

        blue = QtGui.QColor(min(255,0+self.crashed), min(255,61+self.freefall),144, 255 if self.pixmap is None else 64)
        maroon = QtGui.QColor(min(255,59+self.crashed), min(255,41+self.freefall), 39, 255 if self.pixmap is None else 64)


        # Draw background image (camera)
        if self.pixmap is not None:
            qp.drawPixmap(0, 0, w, h, self.pixmap)

        qp.translate(w / 2, h / 2)
        qp.rotate(self.roll)
        qp.translate(0, (self.pitch * h) / 50)
        qp.translate(-w / 2, -h / 2)
        qp.setRenderHint(qp.Antialiasing)



        font = QtGui.QFont('Serif', 7, QtGui.QFont.Light)
        qp.setFont(font)

        #Draw the blue
        qp.setPen(blue)
        qp.setBrush(blue)
        qp.drawRect(-w, round(h/2), 3*w, -3*h)

        #Draw the maroon
        qp.setPen(maroon)
        qp.setBrush(maroon)
        qp.drawRect(-w, round(h/2), 3*w, 3*h)

        pen = QtGui.QPen(QtGui.QColor(255, 255, 255), 1.5,
            QtCore.Qt.SolidLine)
        qp.setPen(pen)
        qp.drawLine(-w, round(h / 2), 3 * w, round(h / 2))

        # Drawing pitch lines
        for ofset in [-180, 0, 180]:
            for i in range(-900, 900, 25):
                pos = (((i / 10.0) + 25 + ofset) * h / 50.0)
                if i % 100 == 0:
                    length = 0.35 * w
                    if i != 0:
                        if ofset == 0:
                            qp.drawText(round((w / 2) + (length / 2) + (w * 0.06)),
                                        round(pos), "{}".format(-i / 10))
                            qp.drawText(round((w / 2) - (length / 2) - (w * 0.08)),
                                        round(pos), "{}".format(-i / 10))
                        else:
                            qp.drawText(round((w / 2) + (length / 2) + (w * 0.06)),
                                        round(pos), "{}".format(i / 10))
                            qp.drawText(round((w / 2) - (length / 2) - (w * 0.08)),
                                        round(pos), "{}".format(i / 10))
                elif i % 50 == 0:
                    length = 0.2 * w
                else:
                    length = 0.1 * w

                qp.drawLine(round((w / 2) - (length / 2)), round(pos),
                            round((w / 2) + (length / 2)), round(pos))

        qp.setWorldMatrixEnabled(False)

        pen = QtGui.QPen(QtGui.QColor(0, 0, 0), 2,
            QtCore.Qt.SolidLine)
        qp.setBrush(QtGui.QColor(0, 0, 0))
        qp.setPen(pen)
        qp.drawLine(0, round(h / 2), w, round(h / 2))
        
        
        
        # Draw Hover vs Target
        
        qp.setWorldMatrixEnabled(False)
        
        pen = QtGui.QPen(QtGui.QColor(255, 255, 255), 2,
                         QtCore.Qt.SolidLine)
        qp.setBrush(QtGui.QColor(255, 255, 255))
        qp.setPen(pen)
        fh = max(7,round(h/50))
        font = QtGui.QFont('Sans', fh, QtGui.QFont.Light)
        qp.setFont(font)
        qp.resetTransform()


        qp.translate(0,h/2)      
        if not self.hover:  
            #qp.drawText(w-fh*10, round(fh/2), str(round(self.hoverASL,2)))  # asl
            pass
               
        
        if self.hover:
            #qp.drawText(w-fh*10, round(fh/2), str(round(self.hoverTargetASL,2)))  # target asl (center)    
            diff = round(self.hoverASL-self.hoverTargetASL,2)
            pos_y = -h/6*diff
            
            # cap to +- 2.8m
            if diff<-2.8:
                pos_y = -h/6*-2.8
            elif diff>2.8:
                pos_y= -h/6*2.8
            else:
                pos_y = -h/6*diff
            #qp.drawText(round(w-fh*3.8),round(pos_y+fh/2), str(diff)) # difference from target (moves up and down +- 2.8m)        
            qp.drawLine(round(w-fh*4.5),round(    0),round(w-fh*4.5),round(pos_y)) # vertical line     
            qp.drawLine(round(w-fh*4.7),round(    0),round(w-fh*4.5),round(0) )    #left horizontal line
            qp.drawLine(round(w-fh*4.2),round(pos_y),round(w-fh*4.5),round(pos_y)) #right horizontal line




         # FreeFall Detection
        qp.resetTransform()
        qp.translate(0,h/2)
        #qp.drawText(fh*6, round(fh/2), str(round(self.ff_acc+1,2))+'G')  # acc

        pos_y = h/6*self.ff_acc

        # cap to +- 2.8m
        if self.ff_acc<-2.8:
            pos_y = -h/6*-2.8
        elif self.ff_acc>2.8:
            pos_y= -h/6*2.8
        else:
            pos_y = -h/6*self.ff_acc
        qp.drawLine(round(fh*4.5),round(    0),round(fh*4.5),round(pos_y)) # vertical line
        qp.drawLine(round(fh*4.7),round(    0),round(fh*4.5),round(    0)) # left horizontal line
        qp.drawLine(round(fh*4.2),round(pos_y),round(fh*4.5),round(pos_y)) #right horizontal line


        # Draw killswitch

        qp.resetTransform()
        if self.killswitch:
            pen = QtGui.QPen(QtGui.QColor(255, 0, 0, 200), 8, QtCore.Qt.SolidLine)
            qp.setBrush(QtGui.QColor(255, 0, 0,200))
            qp.setPen(pen)
            qp.drawLine(round(w/8.), round(   h/8.), round(w/8.*7.), round(h/8.*7.)) # vertical line
            qp.drawLine(round(w/8.), round(h/8.*7.), round(w/8.*7.), round(   h/8.)) # vertical line


        if self.msg != "":
            qp.drawText(0,0,w,h, QtCore.Qt.AlignBottom | QtCore.Qt.AlignHCenter, self.msg)

        if self.recovery:
            pen = QtGui.QPen(QtGui.QColor(255, 255, 0, 170), 8, QtCore.Qt.SolidLine)
            qp.setBrush(QtGui.QColor(255, 255, 0, 170))
            qp.setPen(pen)
            qp.setFont(QtGui.QFont('Sans', max(7,h/11), QtGui.QFont.DemiBold))
            qp.drawText(0,0,w,h, QtCore.Qt.AlignCenter, 'AUTO')
            
        r = min(w,h)
        center = QtCore.QPoint(round(w/2), round(h/2))
        qp.setBrush(QtGui.QColor(0, 0, 0, 0))
        pen = QtGui.QPen(self.palette().brush(QtGui.QPalette.Window), 2, QtCore.Qt.SolidLine)
        qp.setPen(pen)
        qp.drawEllipse(center, round(r/2), round(r/2))
        pen = QtGui.QPen(QtGui.QColor(217, 217, 217), 2, QtCore.Qt.SolidLine)
        qp.setPen(pen)
        for i in range(1, round(max(w,h)-round(r/2))):
            qp.drawEllipse(center, round(r/2+i), round(r/2+i))


if __name__ == "__main__":
    class Example(QtWidgets.QWidget):

        def __init__(self):
            super(Example, self).__init__()

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
            self.setWindowTitle('Attitude Indicator')
            self.show()

        def changeValue(self, value):

            self.c.updateBW.emit(value)
            self.wid.repaint()

    def main():

        app = QtWidgets.QApplication(sys.argv)
        ex = Example()
        sys.exit(app.exec_())


    if __name__ == '__main__':
        main()
