import json
import os
import time
import asyncio
from common import utils

from joystick import XBoxDriveController

HOST = "192.168.0.102"  # The server's hostname or IP address
PORT = 2049  # The port used by the server
WRITE_LOOP_FREQ = 100  # Hz
READ_LOOP_FREQ = 5

drive_controller = XBoxDriveController(joy_id=0)
claw_controller = XBoxDriveController(joy_id=1)

class SurfaceClient:
    """Surface client class."""

    def __init__(self):
        self.loop = asyncio.get_event_loop()
        self.lock = asyncio.Lock()
        self.last_msg = ""
        self.last_update = utils.time_ms()
        if not os.environ.get("SIM"):
            self._init_firmata()
        else:
            print(f"{'='*10} SIMULATION MODE. Type YES to continue {'='*10}")
            if input() != "YES":
                raise RuntimeError("Simulation mode not confirmed")
            HOST = "127.0.0.1"

    def __del__(self):
        self.loop.close()

    async def run(self):
        reader, writer = await asyncio.open_connection(HOST, PORT)

        send_task = asyncio.create_task(self.send_messages(writer))
        receive_task = asyncio.create_task(self.receive_messages(reader))

        await asyncio.gather(send_task, receive_task)

    async def send_messages(self, writer):
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

    async def receive_messages(self, reader):
        print("client connected:")
        asyncio.create_task(self._parse())
        print("started parser")
        msg = (await reader.read(1024)).decode("utf-8")
        print(f"received first message: {msg}")
        while msg:
            async with self.lock:
                self.last_msg = msg
                self.last_update = utils.time_ms()
            msg = (await reader.read(1024)).decode("utf-8")
        print("client disconnected, closing parser")

    async def _parse(self):
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
                print(dict(json.loads(json_msg["imu_data"])))
            
            if "depth" in json_msg:
                print(dict(json.loads(json_msg["depth"])))
            
            if time.time() - last_parse_time < 1 / READ_LOOP_FREQ:
                await asyncio.sleep(1 / READ_LOOP_FREQ - (time.time() - last_parse_time))
            else:
                print("Warning: write loop took too long")
            last_parse_time = time.time()

if __name__ == "__main__":
    surface_client = SurfaceClient()
    asyncio.run(surface_client.run())