import argparse
import json
import os
import time
import asyncio
from common import utils
import surface.xgui as xgui
from surface.joystick import XBoxDriveController

HOST = "192.168.0.102"  # The server's hostname or IP address
PORT = 2049  # The port used by the server
WRITE_LOOP_FREQ = 100  # Hz

drive_controller = XBoxDriveController(joy_id=0)
claw_controller = XBoxDriveController(joy_id=1)

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
    parser.add_argument('-s', '--show-surpressed', action='store_true')

    return parser.parse_args()

class SurfaceClient:
    """Surface client class."""

    def __init__(self):
        self.loop = asyncio.get_event_loop()
        self.lock = asyncio.Lock()
        self.last_msg = ""
        self.last_update = utils.time_ms()
        if os.environ.get("SIM"):
            print(f"{'='*10} SIMULATION MODE. Type YES to continue {'='*10}")
            if input() != "YES":
                raise RuntimeError("Simulation mode not confirmed")
            HOST = "127.0.0.1"
        
        args = get_cmdline_args()
        self.gui = xgui.XguiApplication(args.lowest_port_num, args.num_cameras, args.widget, args.show_surpressed)

        self.depth = 0
        self.imu_data = ""


        # Ensure GUI is initialized before connecting update function
        # if hasattr(self.gui, 'scw') and hasattr(self.gui.scw, 'update_timer'):
        #     self.gui.scw.update_timer.timeout.connect(self._update_sensor_data)
        # else:
        #     print("Warning: SurfaceCentralWidget or update_timer not initialized yet!")
        

    def __del__(self):
        self.loop.close()

    async def run(self):
        """start reader, writer, and parser"""
        reader, writer = await asyncio.open_connection(HOST, PORT)

        send_task = asyncio.create_task(self.send_messages(writer))

        await asyncio.gather(send_task)

    async def send_messages(self, writer):
        """sends controller inputs to bottomside."""
        last_send_time = time.time()
        while True:
            vec = drive_controller.get_velocity_vector()
            claw_vec = claw_controller.get_claw_vector()
            msg = {
                "target_velocity": json.dumps(vec.to_dict()),
                "claw_movement": json.dumps(claw_vec),
            }
            writer.write(str.encode(json.dumps(msg)))
            await writer.drain()
            print(f"sent: {msg}")

            if time.time() - last_send_time < 1 / WRITE_LOOP_FREQ:
                await asyncio.sleep(1 / WRITE_LOOP_FREQ - (time.time() - last_send_time))
            else:
                print("Warning: write loop took too long")
            last_send_time = time.time()

if __name__ == "__main__":
    surface_client = SurfaceClient()
    asyncio.run(surface_client.run())

