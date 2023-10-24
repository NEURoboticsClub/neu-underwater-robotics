import asyncio
from typing import Any, Dict

import pyfirmata
from hardware import Actuator, LinActuator, Servo, Stepper
from utils import time_ms

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
        # all tasks so they can be destroyed (idk if this is necessary)

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
        self.pins: Dict[int, None | Actuator] = {
            0: None,
            1: None,
        }
        tasks: Any = [None for _ in range(40)]
        for i in range(4, 12):
            self.pins[i] = Servo(self.board.get_pin(f"d:{i}:s"))
            tasks.append(self.pins[i].run())
        for i in [2, 3, 12, 13]:
            self.pins[i] = LinActuator(self.board.get_pin(f"d:{i}:o"))
            tasks.append(self.pins[i].run())

        # steppers = [Stepper(26, 28) 36 34]
        steppers = [
            Stepper(self.board.get_pin("d:26:o"), self.board.get_pin("d:28:o")),
            Stepper(self.board.get_pin("d:36:o"), self.board.get_pin("d:34:o")),
        ]
        self.pins[26] = steppers[0]
        tasks.append(self.pins[26].run())
        self.pins[36] = steppers[1]
        tasks.append(self.pins[36].run())

        for task in tasks:
            if task:
                print("adding task")
                self.tasks.append(task)

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

            # if msg:
            #     print(f"from parse: {msg=}")
            msg = msg.split("&")[0]
            for x in msg.split(";"):
                if not x:
                    continue
                try:
                    pin, value = x.split(":")
                    pin = int(pin)
                    value = int(value)
                except ValueError:
                    print(f"Invalid message: {x}")
                    continue

                if pin not in self.pins:
                    print(f"Invalid pin: {pin}")
                    continue

                if isinstance(self.pins[pin], Actuator):
                    try:
                        await self.pins[pin].set_val(self.pins[pin].linear_map(value))
                    except:  # pylint: disable=bare-except
                        print(f"Invalid something: {pin} {value}")
                else:
                    print(f"Invalid pin type: {type(self.pins[pin])}")


if __name__ == "__main__":
    server = Server()
    asyncio.run(server.run())
