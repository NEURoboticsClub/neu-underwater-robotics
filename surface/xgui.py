"""Surface GUI App Launcher

Run this file as a module in command line, supplying the arguments as
specified in the README.md.

"""

import argparse
import importlib
import logging
import os
import sys
import threading
import asyncio
import json
from common import utils
import time
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtCore import QtMsgType, QUrl, qInstallMessageHandler
from surface.gui.widgets.surface_central import SurfaceCentralWidget
from surface.gui.surface_window import SurfaceWindow

HOST = "192.168.0.114"  # The server's hostname or IP address
PORT = 2049  # The port used by the server
READ_LOOP_FREQ = 5

logger = logging.getLogger(__name__)
logging.basicConfig(format='%(levelname)s:%(message)s')

RPATH_TO_SUPRESSED_MESSAGES_FILE = './supressed_qt_messages.txt'
PATH_TO_SUPRESSED_MESSAGES_FILE = os.path.join(os.path.dirname(__file__),
                                                RPATH_TO_SUPRESSED_MESSAGES_FILE)
MODULE_PATH_TO_SURFACE_CENTRAL_WIDGETS = '.gui.widgets.surface_central'

def get_cmdline_args():
    """Gets the values of the command line arguments.

    Returns: argparse's Namespace that holds the values of the command
    line arguments

    """
    parser = argparse.ArgumentParser(
        prog='launch',
        description=('Reads the video and non-video data from the given '
                     'ports, and renders them with PyQt5.'))

    parser.add_argument('-p', '--lowest-port-num', type=int, required=True)
    parser.add_argument('-n', '--num-cameras', type=int, required=True)
    parser.add_argument('-w', '--widget', default=None)
    parser.add_argument('-s', '--show-supressed', action='store_true')

    return parser.parse_args()

def get_port_nums_or_exit(lowest_port_num, num_cameras):
    """Gets the port number list if the port numbers are legal;
    else exits with error code 1.

    The length of the output list equals the given number of
    cameras, and each port number is equal to the given
    lowest_port_num plus its index.

    lowest_port_num : nat
    num_cameras : nat

    Returns: List[int]

    """
    highest_port_num = lowest_port_num + num_cameras - 1

    if _check_valid_port_num(lowest_port_num) and _check_valid_port_num(highest_port_num):
        return range(lowest_port_num, highest_port_num + 1)
    else:
        logger.error(('Invalid port number. A port number must be between 1 and 65536. '
                      'The given port numbers are in range [%s,%s]. Shutting down...'), 
                     lowest_port_num, highest_port_num)
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

    Returns: ISurfaceCentralWidget?
    """
    if maybe_widget_name:
        widget_name = maybe_widget_name
        maybe_cls = class_for_name(MODULE_PATH_TO_SURFACE_CENTRAL_WIDGETS, widget_name)

        if maybe_cls:
            if isinstance(maybe_cls, QWidget):
                return maybe_cls
            else:
                logging.error(('The class, %s, is not a widget. The name provided must '
                               'be a widget. Shutting down...'),
                              maybe_widget_name)
                return False
        else:
            logging.error(('The given widget name, %s, does not exist in '
                           'gui/widgets/surface_central.py. Shutting down..'),
                          widget_name)
            return False
    else:
        return SurfaceCentralWidget

# TODO(allocation): Probably should move this into a utils folder.
# From https://stackoverflow.com/a/13808375
def class_for_name(module_name, class_name):
    """Gets the class associated with the given class name in the given
    module name from the enclosing of this module.

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

def get_supressed_message_handler(msgs_to_supress):
    """Gets the custom message handler that supresses the given messages.

    If no messages to supress, then the check is skipped completely.

    messages_to_supress : List[str]

    Returns: [QtMsgType, QMessageLogContext, str] -> None

    """
    def custom_message_handler_checked(msg_type, msg_log_context, msg):
        if msg in msgs_to_supress:
            return
        custom_message_handler(msg_type, msg_log_context, msg)

    def custom_message_handler(msg_type, msg_log_context, msg):
        # msg_log_context is pretty useless. It is all zero'ed out.
        logger_func = get_logger_func(msg_type)
        logger_func(msg)

    def get_logger_func(msg_type):
        """Maps the given Qt message type to a logging function with an appropriate level.

        msg_type : QtMsgType

        Returns: [str *args **kwargs -> None]
        """
        # Pylint complains Class 'QtMsgType' has no X member. Pylint is wrong.
        match msg_type:
            case QtMsgType.QtCriticalMsg:
                return logging.critical
            case QtMsgType.QtDebugMsg:
                return logging.debug
            case QtMsgType.QtFatalMsg:
                return logging.critical
            case QtMsgType.QtInfoMsg:
                return logging.info
            case QtMsgType.QtSystemMsg:
                return logging.info
            case QtMsgType.QtWarningMsg:
                return logging.warning

    return custom_message_handler_checked if msgs_to_supress else custom_message_handler

def get_messages_to_supress(should_show_supressed):
    """Gets the list of messages to supress.

    should_show_supressed : bool

    Returns: List[String]
    """
    if should_show_supressed:
        return []
    else:
        with open(PATH_TO_SUPRESSED_MESSAGES_FILE, 'r', encoding='utf-8') as f:
            return [line for line in (x.strip() for x in f)]

class XguiApplication():
    """Xgui Application Class. 
    Intended for running Xgui as an attribute or an object from other entrypoints.    
    """
    def __init__(self, args):
        self.port_nums = get_port_nums_or_exit(args.lowest_port_num, args.num_cameras)
        self.sc_widget_cls = get_surface_central_if_can(args.widget)
        self.messages_to_supress = get_messages_to_supress(args.show_supressed)
        self.scw = None
        self.loop = asyncio.get_event_loop()
        self.lock = asyncio.Lock()
        self.last_msg = ""
        self.last_update = utils.time_ms()
        if os.environ.get("SIM"):
            print(f"{'='*10} SIMULATION MODE. Type YES to continue {'='*10}")
            if input() != "YES":
                raise RuntimeError("Simulation mode not confirmed")
            HOST = "127.0.0.1"

        self.depth = 0
        self.imu_data = ""
    
    def __del__(self):
        self.loop.close()

    async def receive_messages(self, reader):
        """receives sensor information from bottomside."""
        msg = (await reader.read(1024)).decode("utf-8")
        print(f"received first message: {msg}")
        while msg:
            async with self.lock:
                self.last_msg = msg
                self.last_update = utils.time_ms()
            msg = (await reader.read(1024)).decode("utf-8")
        print("client disconnected, closing parser")

    async def _parse(self):
        """parses received messages."""
        last_parse_time = time.time()
        while True:
            await asyncio.sleep(0.01)
            async with self.lock:
                msg = self.last_msg

            if msg is None:  # no message received yet
                await asyncio.sleep(0.01)
                continue

            try:
                json_msg = json.loads(msg)
            except json.JSONDecodeError as e:
                print(f"error decoding json: {e} | received: {msg}")
                await asyncio.sleep(0.01)
                continue

            if "imu_data" in json_msg:
                self.imu_data = json_msg["imu_data"]
                if self.scw != None:
                    if hasattr(self.scw, 'update_imu'):
                        self.scw.update_imu(dict(json.loads(json_msg["imu_data"])))
                        print(self.imu_data)
                    else:
                        print("Warning: GUI not fully initialized, skipping update.")
            
            if "depth" in json_msg:
                self.depth = float(json.loads(json_msg["depth"]))
                if self.scw != None:
                    if hasattr(self.scw, 'update_depth'):
                        self.scw.update_depth(self.depth)
                        print(self.depth)
                    else:
                        print("Warning: GUI not fully initialized, skipping update.")
            
            if time.time() - last_parse_time < 1 / READ_LOOP_FREQ:
                await asyncio.sleep(1 / READ_LOOP_FREQ - (time.time() - last_parse_time))
            else:
                print("Warning: read loop took too long")
            last_parse_time = time.time()
    
    async def run_asyncio(self):
        """start reader, writer, and parser"""
        reader, writer = await asyncio.open_connection(HOST, PORT)

        receive_task = asyncio.create_task(self.receive_messages(reader))
        parse_task = asyncio.create_task(self._parse())

        await asyncio.gather(receive_task, parse_task)

    def run(self):
        if not self.sc_widget_cls:
            sys.exit(1)
        
        self.app = QApplication(sys.argv)
        qInstallMessageHandler(get_supressed_message_handler(self.messages_to_supress))
        try:
            self.scw = self.sc_widget_cls(self.port_nums)
        except TypeError as e:
            logger.error(('There is a TypeError with the instantiation of the widget class. '
                        'Make sure that the __init__ of the widget class takes in the expected '
                        'arguments. As for what the expected arguments are, refer to the '
                        'README.md of the surface module.'))
            logger.error(e)
            logger.error('Shutting down...')
            sys.exit(1)

        main_window = SurfaceWindow(self.scw)
        main_window.show()
        self.scw.grid_player.setFocus()
        self.app.exec_()


if __name__ == '__main__':
    args = get_cmdline_args()
    gui = XguiApplication(args)
    asyncio_thread = threading.Thread(target=lambda: asyncio.run(gui.run_asyncio()))
    asyncio_thread.start()
    gui.run()
