from PyQt5.QtWidgets import QMainWindow

SURFACE_WINDOW_TITLE = "NURobotics Surface Window"
WINDOW_POSX = 100
WINDOW_POSY = 100
WINDOW_W = 800
WINDOW_H = 600

class SurfaceWindow(QMainWindow):
    """The PyQt5 main window which we will see on the surface machine.
    """
    def __init__(self, surface_central):
        """Constructs this window with the given surface central
        widget.

        Our architecture of the window relies on the fact that the
        layout is determined by the central widget, and this
        constructor requires the user to supply said widget.

        surface_central : ISurfaceCentralWidget

        """
        super().__init__()
        self.setWindowTitle(SURFACE_WINDOW_TITLE)
        self.setGeometry(WINDOW_POSX, WINDOW_POSY, WINDOW_W, WINDOW_H)
        self.setCentralWidget(surface_central)
