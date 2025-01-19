import sys
import pytest
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer, QUrl
from PyQt5.QtMultimedia import QMediaPlayer
from ..video_player import VideoPlayerWidget

WAIT_TIME = 500  # In miliseconds

VIDEOTESTSRC_QURL_STR = "gst-pipeline: videotestsrc ! xvimagesink name=\"qtvideosink\""
BAD_QURL_STR = "gs-pipeline: videotestsrc ! xvimagesink name=\"qtvideosink\""


def test_media_player_ok():
    """Verifies that when QUrl is legal, media player behaves as
    expected.

    """
    recorded_media_list = []  # [Listof MediaStatus]
    expected_media_list = [2, 6]  # [Listof MediaStatus]
    recorded_error_names_list = [] # [Listof QMediaPlayer.Error]
    
    def on_media_status_changed(new_media_status):
        recorded_media_list.append(new_media_status)

    def on_error(new_error):
        recorded_error_names_list.append(new_error)
        
    app = QApplication(sys.argv)
    videotestsrc_qurl = QUrl(VIDEOTESTSRC_QURL_STR)
    player = VideoPlayerWidget(videotestsrc_qurl,
                               on_media_status_changed=on_media_status_changed,
                               on_error=on_error)
    QTimer.singleShot(WAIT_TIME, lambda: app.exit())
    app.exec_()
    assert recorded_media_list == expected_media_list
    assert recorded_error_names_list == []

def test_error_raised_when_illegal():
    """
    Verifies that illegal input leads to an exception raised.
    """
    error_found = False
    
    def excepthook(exc_type, exc_value, exc_tb):
        nonlocal error_found
        error_found = True
        QApplication.quit()
    
    sys.excepthook = excepthook
    app = QApplication(sys.argv)
    bad_qurl = QUrl(BAD_QURL_STR)
    player = VideoPlayerWidget(bad_qurl)
    QTimer.singleShot(WAIT_TIME, lambda: app.exit())
    app.exec_()

    if not error_found:
        pytest.fail("Should have raised an exception but didn't.")

