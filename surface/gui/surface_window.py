from PyQt5.QtWidgets import QMainWindow

SURFACE_WINDOW_TITLE = "NURobotics Surface Window"

class SurfaceWindow(QMainWindow):
    """The PyQt5 main window which we will see on the surface machine.
    """
    def __init__(self, surface_central):
        """Constructs the surface window with the given surface central widget.

        Our architecture of the window relies on the fact that the
        layout is provided by the central widget, and this constructor
        requires user to supply said widget.

        surface_central : ISurfaceCentralWidget

        """
        super().__init__()
        self.setWindowTitle(SURFACE_WINDOW_TITLE)
        self.setCentralWidget(surface_central)
