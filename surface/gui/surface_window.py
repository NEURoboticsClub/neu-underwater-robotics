from PyQt5.QtWidgets import QMainWindow
from .widgets.surface_central import SurfaceCentralWidget

SURFACE_WINDOW_TITLE = "NURobotics Surface Window"

class SurfaceWindow(QMainWindow):
    """The PyQt5 main window which we will see on the surface machine.
    """
    def __init__(self, tl_qurl, tr_qurl, bl_qurl, br_qurl):
        """Constructs the surface window.

        tl_qurl : QUrl -- For the top-left camera view.
        tr_qurl : QUrl -- For the top-right camera view.
        bl_qurl : QUrl -- For the bottom-left camera view.
        br_qurl : QUrl -- For tthe bottom-right camera view.
        """
        super().__init__()
        self.setWindowTitle(SURFACE_WINDOW_TITLE)
        central_widget = SurfaceCentralWidget(tl_qurl, tr_qurl, bl_qurl, br_qurl)
        self.setCentralWidget(central_widget)


# TODO(temp): Leaving this here for testing purposes. Remove once we
# can launch the app normally.
if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication
    from PyQt5.QtCore import QUrl
    app = QApplication(sys.argv)
    QURL_STR = "gst-pipeline: videotestsrc ! xvimagesink name=\"qtvideosink\""
    a = QUrl(QURL_STR)
    b = QUrl(QURL_STR)
    c = QUrl(QURL_STR)
    d = QUrl(QURL_STR)
    sw = SurfaceWindow(a, b, c, d)
    sw.show()
    app.exec_()
        

