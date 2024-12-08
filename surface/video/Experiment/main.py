import sys
from PyQt5.QtWidgets import QApplication
from views import MainWindow
from controller import Controller

def main():
    app = QApplication(sys.argv)

    # Initialize the main window (view) and controller
    main_window = MainWindow()
    controller = Controller(main_window)

    # Show the main window
    main_window.show()
    #main_window.showFullScreen()  # Set to fullscreen mod

    # Start the application loop
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()