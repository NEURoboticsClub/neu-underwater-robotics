import asyncio
import json
import os
import time

import pyfirmata
from pyfirmata import Pin

from common import utils

from .hardware import Servo, Thruster, LinActuator
from .rov_state import ROVState

SERVER_IP = "192.168.0.102"  # raspberry pi ip
PORT = 2049
ARDUINO_PORT = "/dev/ttyACM0"
RESPONSE_LOOP_FREQ = 10 # Hz

if os.environ.get("SIM"):
    from .sim_hardware import SimThruster

    SERVER_IP = "127.0.0.1"


class Server:
    """Server class."""

    def __init__(self):
        self.loop = asyncio.get_event_loop()
        self.lock = asyncio.Lock()
        self.tasks = []
        self.incoming = []
        self.last_update = utils.time_ms()
        if not os.environ.get("SIM"):
            self._init_firmata()
            self.rov_state = ROVState(
                actuators={
                    "rotate": Servo(self._get_pin(10, "s")),
                    "close_main": Servo(self._get_pin(2, "s")),
                    "close_side": Servo(self._get_pin(12, "s")),
                    "camera": Servo(self._get_pin(13, "s")),
                    "extend": LinActuator(self._get_pin(14, "o"), self._get_pin(15, "o")),
                    "sample": LinActuator(self._get_pin(18, "o"), self._get_pin(19, "o")),
                },
                thrusters={
                    #remove to isolate claw
                    "front_left_horizontal": Thruster(self._get_pin(2, "s")),
                    "front_right_horizontal": Thruster(self._get_pin(4, "s")),
                    "back_left_horizontal": Thruster(self._get_pin(6, "s")), 
                    "back_right_horizontal": Thruster(self._get_pin(8, "s")),
                    "front_left_vertical": Thruster(self._get_pin(3, "s")),
                    "front_right_vertical": Thruster(self._get_pin(5, "s"), reverse=True), 
                    "back_left_vertical": Thruster(self._get_pin(7, "s"), reverse=True),
                    "back_right_vertical": Thruster(self._get_pin(9, "s")),
                    
                },
                sensors={

                },
            )
            self.board.servo_config(3, 1100, 1900, 1500)
            self.board.servo_config(5, 1100, 1900, 1500)
            self.board.servo_config(7, 1100, 1900, 1500)
            self.board.servo_config(9, 1100, 1900, 1500)
            # TOASK: can we remove
            time.sleep(10)
        else:
            print(f"{'='*10} SIMULATION MODE. Type YES to continue {'='*10}")
            if input() != "YES":
                raise RuntimeError("Simulation mode not confirmed")
            self.rov_state = ROVState(
                actuators={},
                thrusters={
                    "front_left_horizontal": SimThruster(4),
                    "front_right_horizontal": SimThruster(5),
                    "back_left_horizontal": SimThruster(6),
                    "back_right_horizontal": SimThruster(7),
                    "front_left_vertical": SimThruster(8),
                    "front_right_vertical": SimThruster(9),
                    "back_left_vertical": SimThruster(10),
                    "back_right_vertical": SimThruster(11),
                },
                sensors={},
            )
        self.tasks.append(self.rov_state.control_loop())
        self.tasks.extend(self.rov_state.get_tasks())

    def __del__(self):
        try:
            for task in self.tasks:
                task.cancel()
        except:  # pylint: disable=bare-except
            pass
        self.loop.close()

    def _init_firmata(self):
        self.board = pyfirmata.ArduinoMega(ARDUINO_PORT)
        print("Successfully connected to Arduino")
        it = pyfirmata.util.Iterator(self.board)
        it.start()

    def _get_pin(self, pin: int, mode: str = "o") -> Pin:
        """get a pin from the board. mode can be 'i', 'o', or 's' for servo"""
        assert self.board is not None
        return self.board.get_pin(f"d:{pin}:{mode}")
    
    async def run(self):
        """run the server"""
        _server = await asyncio.start_server(self._handle_client, SERVER_IP, PORT)
        print(f"{len(self.tasks)}")
        for task in self.tasks:
            print("ensuring future")
            asyncio.create_task(task)
        async with _server:
            print(f"Ready to accept connection. Please start client.py {SERVER_IP=} {PORT=}")
            await _server.serve_forever()

    async def _handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        """called when a client connects to the server"""
        print("client connected:")
        asyncio.create_task(self._parse())
        print("started parser")
        
        async def read_messages():
            """reads incoming messages"""
            msg = (await reader.read(1024)).decode("utf-8")
            print(f"received first message: {msg}")
            while msg:
                async with self.lock:
                    self.incoming.append(msg)
                    self.last_update = utils.time_ms()
                msg = (await reader.read(1024)).decode("utf-8")
            print("client disconnected, closing parser")
        
        async def send_responses():
            """sends responses to clients"""
            last_response_time = time.time()
            while True:
                response = {
                    "imu_data": json.dumps(self.rov_state._current_imu_data),
                    "depth": json.dumps(self.rov_state._current_depth),
                }
                await self._send_response(writer, response)
                if time.time() - last_response_time < 1 / RESPONSE_LOOP_FREQ:
                    await asyncio.sleep(1 / RESPONSE_LOOP_FREQ - (time.time() - last_response_time))
                else:
                    print("Warning: write loop took too long")
                last_response_time = time.time()

        asyncio.create_task(read_messages())
        asyncio.create_task(send_responses())
        
        print("started reader and writer")

    async def _send_response(self, writer: asyncio.StreamWriter, response: dict):
        """send a response back to the client"""
        try:
            msg = json.dumps(response)
            writer.write(str.encode(msg))
            await writer.drain()
            print(f"Sent response: {msg}")
        except Exception as e:
            print(f"Error sending response: {e}")

    async def _parse(self):
        """parses incoming messages"""
        while True:
            await asyncio.sleep(0.01)
            async with self.lock:
                if len(self.incoming) > 0:
                    msg = self.incoming.pop()
                    if len(self.incoming) > 5:
                        self.incoming = []
                else:
                    msg = None
            
            if msg is None:
                await asyncio.sleep(0.01)
                continue

            try:
                json_msg = json.loads(msg)
            except json.JSONDecodeError as e:
                print(f"error decoding json: {e} | received: {msg}")
                await asyncio.sleep(0.01)
                continue

            if "target_velocity" in json_msg:
                self.rov_state.set_target_velocity(
                    utils.VelocityVector(json.loads(json_msg["target_velocity"]))
                )

            if "imu_data" in json_msg:
                self.rov_state.set_current_imu_data(
                    dict(json.loads(json_msg["imu_data"]))
                )

            if "claw_movement" in json_msg:
                self.rov_state.set_claw_movement(
                    dict(json.loads(json_msg["claw_movement"]))
                )
            
            if "depth" in json_msg:
                self.rov_state.set_current_depth(
                    list(json.loads(json_msg["depth"]))
                )


if __name__ == "__main__":
    server = Server()
    asyncio.run(server.run())
