import asyncio
import json

import pyfirmata
from hardware import Actuator, LinActuator, Servo, Stepper, Thruster
from pyfirmata import Pin
from rov_state import ROVState
from utils import VelocityVector, time_ms

SERVER_IP = "192.168.0.102"  # raspberry pi ip
PORT = 2049
ARDUINO_PORT = "/dev/ttyACM0"
STEPS_PER_REV = 200


class Server:
    """Server class."""

    def __init__(self):
        self.loop = asyncio.get_event_loop()
        self.lock = asyncio.Lock()
        self.tasks = []
        self._init_firmata()
        self.last_msg = ""
        self.last_update = time_ms()
        self.rov_state = ROVState(
            actuators={
                "servo": Servo(self._get_pin(12, "s")),
            },
            thrusters={
                "front_left_horizontal": Thruster(self._get_pin(4, "s")),
                "front_right_horizontal": Thruster(self._get_pin(5, "s")),
                "back_left_horizontal": Thruster(self._get_pin(6, "s")),
                "back_right_horizontal": Thruster(self._get_pin(7, "s")),
                "left_vertical": Thruster(self._get_pin(8, "s")),
                "right_vertical": Thruster(self._get_pin(9, "s")),
            },
            sensors={},
        )

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

        # self.pins: Dict[int, None | Actuator] = {
        #     0: None,
        #     1: None,
        # }
        # tasks: Any = [None for _ in range(40)]
        # for i in range(4, 12):
        #     self.pins[i] = Servo(self.board.get_pin(f"d:{i}:s"))
        #     tasks.append(self.pins[i].run())
        # for i in [2, 3, 12, 13]:
        #     self.pins[i] = LinActuator(self.board.get_pin(f"d:{i}:o"))
        #     tasks.append(self.pins[i].run())
        #
        # # steppers = [Stepper(26, 28) 36 34]
        # steppers = [
        #     Stepper(self.board.get_pin("d:26:o"), self.board.get_pin("d:28:o")),
        #     Stepper(self.board.get_pin("d:36:o"), self.board.get_pin("d:34:o")),
        # ]
        # self.pins[26] = steppers[0]
        # tasks.append(self.pins[26].run())
        # self.pins[36] = steppers[1]
        # tasks.append(self.pins[36].run())
        #
        # for task in tasks:
        #     if task:
        #         print("adding task")
        #         self.tasks.append(task)

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

    async def _handle_client(self, reader: asyncio.StreamReader, _: asyncio.StreamWriter):
        """called when a client connects to the server"""
        print("client connected:")
        asyncio.create_task(self._parse())
        print("started parser")
        msg = (await reader.read(1024)).decode("utf-8")
        print(f"received first message: {msg}")
        while msg:
            print(f"from handle_client: {msg=}")
            async with self.lock:
                self.last_msg = msg
                self.last_update = time_ms()
            msg = (await reader.read(1024)).decode("utf-8")
        print("client disconnected, closing parser")

    async def _parse(self):
        while True:
            await asyncio.sleep(0.01)
            async with self.lock:
                msg = self.last_msg

            if msg is None:
                await asyncio.sleep(0.01)
                continue

            try:
                json_msg = json.loads(msg)
            except json.JSONDecodeError as e:
                print(f"error decoding json: {e} | rceived: {msg}")
                await asyncio.sleep(0.01)
                continue

            if "target_velocity" in json_msg:
                self.rov_state.set_target_velocity(VelocityVector(json_msg["target_velocity"]))


if __name__ == "__main__":
    server = Server()
    asyncio.run(server.run())
