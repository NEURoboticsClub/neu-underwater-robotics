import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
import pyqt5_tools

def main():
    app = QApplication(sys.argv)
    window = QMainWindow()
    window.setGeometry(100, 100, 600, 400)  # x, y, width, height
    window.setWindowTitle("My First PyQt App")
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()