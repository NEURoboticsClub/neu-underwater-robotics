#!/usr/bin/env python3

"""Surface App Launcher

Usage:
python video --lowest-port-num <VIDEO PORT NUMBER>
             --num-cameras <NUMBER OF CAMERAS>
             --widget <NAME OF SURFACE CENTRAL WIDGET IN `widgets/surface_central` FOLDER>

OR

python video -p <VIDEO PORT NUMBER>
             -n <NUMBER OF CAMERAS>
             -w <NAME OF SURFACE CENTRAL WIDGET IN `widgets/surface_central` FOLDER>

NOTE: You may have to use python3 instead of python depending on your
environment variables.

Provide first port number, number of cameras in cmdline, and surface window to launch.
The port numbers used will be n, n+1, ..., n+k-1, where k is the number of cameras and n is the first port number.

"""

import argparse
import logging
import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QUrl
from .gui.widgets.surface_central import SurfaceCentralWidget
from .gui.surface_window import SurfaceWindow

logger = logging.getLogger(__name__)

MODULE_PATH_TO_SURFACE_CENTRAL_WIDGETS = '.gui.widgets.surface_central'

# TODO(config): Users ought to be able to specify this without prying
# into the code.
PORT_NUM_TO_GST_PIPELINE_COMMAND = lambda port_num : f"gst-pipeline: udpsrc port={port_num} ! application/x-rtp ! rtpjitterbuffer ! rtph264depay ! avdec_h264 ! videoconvert ! xvimagesink name=\"qtvideosink\""

def get_cmdline_args():
    parser = argparse.ArgumentParser(
        prog='launch',
        description=('Reads the video and non-video data from the given '
                     'ports, and renders them with PyQt5.'))

    parser.add_argument('-p', '--lowest-port-num', type=int, required=True)
    parser.add_argument('-n', '--num-cameras', type=int, required=True)
    parser.add_argument('-w', '--widget', default=None)

    return parser.parse_args()

def get_qurls_or_exit(lowest_port_num, num_cameras):
    """Gets the QUrls list if the port numbers are legal, exits
    with error code 1 otherwise.

    The length of the output list equals to the given number of
    cameras, and each QUrl has the port number equal to the given
    lowest_port_num plus its index.

    lowest_port_num : natural
    num_cameras : natural

    """
    highest_port_num = lowest_port_num + num_cameras - 1

    if _check_valid_port_num(lowest_port_num) and _check_valid_port_num(highest_port_num):
        return [QUrl(PORT_NUM_TO_GST_PIPELINE_COMMAND(port_num))
                for port_num in range(lowest_port_num, highest_port_num + 1)]
    else:
        logger.error('Invalid port number. A port number must be between 1 and 65536. The given port numbers are in range [%s,%s]. Shutting down...', lowest_port_num, highest_port_num)
        sys.exit(1)

def _check_valid_port_num(port_num):
    """Verifies that the given port number is within 1 and 65535.

    port_num : int

    Returns: bool
    """
    return 1 <= port_num <= 65535

def get_surface_central_if_can(maybe_widget_name):
    """Gets the surface central widget associated with the given name
    if it is not None.

    Defaults to SurfaceCentralWidget if it is None.

    If the given widget name does not actually exist as a class,
    returns False.

    maybe_widget_name : str?

    Returns: ISurfaceCentral?
    """
    if maybe_widget_name:
        widget_name = maybe_widget_name
        maybe_cls = class_for_name(MODULE_PATH_TO_SURFACE_CENTRAL_WIDGETS, widget_name)

        if maybe_cls:
            return maybe_cls
        else:
            return False
    else:
        return SurfaceCentralWidget

# TODO(allocation): Probably should move this into a utils folder.
# From https://stackoverflow.com/a/13808375
import importlib
def class_for_name(module_name, class_name):
    """Gets the class associated with the given class name in the given module name from the enclosing of this module.

    If such a class name cannot be found, produce False.

    module_name : str
    class_name : str

    Returns: False or Class as first class value

    """
    # load the module, will raise ImportError if module cannot be loaded
    m = importlib.import_module(module_name, package=__package__)
    # get the class, will raise AttributeError if class cannot be found
    try:
        return getattr(m, class_name)
    except AttributeError:
        # Thrown when class_name not found in m
        return False

def main():
    args = get_cmdline_args()

    qurls = get_qurls_or_exit(args.lowest_port_num, args.num_cameras)
    sc_widget_cls = get_surface_central_if_can(args.widget)

    if not sc_widget_cls:
        logging.error('The given widget name, %s, does not exist in gui/widgets/surface_central.py. Shutting down..',
                      widget_name)
        sys.exit(1)

    app = QApplication(sys.argv)
    try:
        scw = sc_widget_cls(qurls)
    except TypeError as e:
        logger.error('There is a TypeError with the instantiation of the widget class. Make sure that the __init__ of the widget class takes in the expected arguments. As for what the expected arguments are, refer to the README.md of the surface module.')
        logger.error(e)
        logger.error('Shutting down...')
        sys.exit(1)

    main_window = SurfaceWindow(scw)
    main_window.show()
    app.exec_()

if __name__ == '__main__':
    main()
