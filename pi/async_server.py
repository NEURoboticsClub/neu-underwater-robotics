import asyncio
import socket
from time import time_ns
import pyfirmata

SERVER_IP = "192.168.0.103"  # raspberry pi ip
PORT = 2049
ARDUINO_PORT = "/dev/ttyACM0"
STEPS_PER_REV = 200

# region: utils


def time_ms():
    """Returns the current time in milliseconds."""
    return int(time_ns() / 1000000)  # time in ms


def linear_map(
    x: float, in_min: float = -1, in_max: float = 1, out_min: float = -5, out_max: float = 5
):
    """Linear map function.

    Args:
        x (float): value to map
        in_min (float): minimum input value
        in_max (float): maximum input value
        out_min (float): minimum output value
        out_max (float): maximum output value

    Returns:
        float: mapped value
    """
    return min(max(((x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min), -5), 5)


# endregion: utils

# region: hardware


class Stepper:
    def __init__(self, pin: pyfirmata.Pin, direction_pin: pyfirmata.Pin, direction: bool = True):
        self.pin = pin
        self.direction_pin = direction_pin
        self.direction = direction
        self.speed = 0  # rev / s
        self.lock = asyncio.Lock()

    @classmethod
    def linear_map(cls, x: float):
        return int(linear_map(x, -50, 50, -5, 5))

    async def set_val(self, speed: int):
        """set speed of stepper motor in rev / s

        Args:
            speed (float): speed in rev / s
        """
        async with self.lock:
            self.speed = speed

    async def reverse(self):
        async with self.lock:
            self.direction_pin.write(self.direction_pin)
            self.direction = not self.direction
        # self.direction_pin.write(1)
        # await asyncio.sleep(0.01)
        # self.direction_pin.write(0)

    async def run(self):
        while True:
            async with self.lock:
                speed = self.speed
            # print(f"speed: {speed}")
            if speed == 0:
                await asyncio.sleep(0.1)
                continue
            delay = (1 / 200) * (1 / speed)
            # if speed < 0 and self.direction or speed > 0 and not self.direction:
            #     asyncio.ensure_future(self.reverse())
            asyncio.ensure_future(self.reverse())
            self.pin.write(1)
            await asyncio.sleep(delay)
            self.pin.write(0)
            await asyncio.sleep(delay)


class Servo:
    def __init__(self, pin: pyfirmata.Pin):
        self.pin = pin
        self.angle = 90
        self.lock = asyncio.Lock()

    @classmethod
    def linear_map(cls, x: float):
        # return int(linear_map(x, 0, 180, 0, 180))
        return int(x)

    async def set_val(self, angle: int):
        if angle < 0 or angle > 180:
            raise ValueError("Angle must be between 0 and 180")
        async with self.lock:
            self.angle = angle

    async def run(self):
        while True:
            async with self.lock:
                self.pin.write(self.angle)
            await asyncio.sleep(0.1)


# endregion: hardware


class Server:
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
        except:
            pass
        self.loop.close()

    def _init_firmata(self):
        self.board = pyfirmata.ArduinoMega(ARDUINO_PORT)
        print("Successfully connected to Arduino")
        it = pyfirmata.util.Iterator(self.board)
        it.start()
        self.pins = {
            0: None,
            1: None,
        }
        tasks = [None for i in range(40)]
        # for i in range(2, 6, 2):
        #     self.pins[i] = Stepper(
        #         self.board.get_pin(f"d:{i}:o"),
        #         self.board.get_pin(f"d:{i + 1}:o"),
        #     )
        #     tasks.append(self.pins[i].run())
        for i in range(4, 14):
            self.pins[i] = Servo(self.board.get_pin(f"d:{i}:s"))
            tasks.append(self.pins[i].run())

        # steppers = [Stepper(26, 28) 36 34]
        steppers = [Stepper(self.board.get_pin("d:26:o"), self.board.get_pin(
            "d:28:o")), Stepper(self.board.get_pin("d:36:o"), self.board.get_pin("d:34:o"))]
        self.pins[26] = steppers[0]
        tasks.append(self.pins[26].run())
        self.pins[36] = steppers[1]
        tasks.append(self.pins[36].run())

        for task in tasks:
            if task:
                print(f"adding task")
                self.tasks.append(task)
        
        # self.loop.run_forever()
        
    # def _init_server(self):
    #     self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #     self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    #     self.socket.bind((SERVER_IP, PORT))
    #     print(
    #         f"Ready to accept connection. Please start client.py {SERVER_IP=} {PORT=}")
    #     self.socket.listen(5)
    #     self.conn, addr = self.socket.accept()
    #     print(f"Connected by {addr}")

    async def run(self):
        self.server = await asyncio.start_server(self._handle_client, SERVER_IP, PORT)
        print(f"{len(self.tasks)}")
        for task in self.tasks:
            print(f"ensuring future")
            asyncio.create_task(task)
        async with self.server:
            print(
                f"Ready to accept connection. Please start client.py {SERVER_IP=} {PORT=}")
            await self.server.serve_forever()

    async def _handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        """called when a client connects to the server"""
        print(f"client connected:")
        asyncio.create_task(self._parse())
        print(f"started parser")
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

                if isinstance(self.pins[pin], Stepper) or isinstance(self.pins[pin], Servo):
                    await self.pins[pin].set_val(self.pins[pin].linear_map(value))
                else:
                    print(f"Invalid pin type: {type(self.pins[pin])}")


if __name__ == "__main__":
    server = Server()
    asyncio.run(server.run())
