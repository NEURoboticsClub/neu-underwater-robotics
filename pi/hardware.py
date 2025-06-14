import asyncio
from abc import ABC, abstractmethod

from pyfirmata import Pin

from common import utils

linear_map = utils.linear_map

class Sensor(ABC):
    """Abstract sensor class."""

    # TODO: temporary, fill out

    @abstractmethod
    async def get_val(self):
        """get value of sensor"""


class Actuator(ABC):
    """Abstract actuator class."""

    def linear_map(self, _: float):
        """map value to actuator value"""

    @abstractmethod
    async def set_val(self, val: float):
        """set value of actuator"""

    @abstractmethod
    async def run(self):
        """run actuator"""


class Stepper(Actuator):
    """Stepper motor class."""

    def __init__(self, pin: Pin, direction_pin: Pin, direction: bool = True):
        self.pin = pin
        self.direction_pin = direction_pin
        self.direction = direction
        self.speed = 0  # rev / s
        self.lock = asyncio.Lock()

    def linear_map(self, x: float):
        return int(linear_map(x, -50, 50, -5, 5))

    async def set_val(self, val: int):
        """set speed of stepper motor in rev / s
        Args:
            speed (float): speed in rev / s
        """
        async with self.lock:
            self.speed = val

    async def reverse(self):
        """reverse direction of stepper motor"""
        async with self.lock:
            self.direction_pin.write(self.direction_pin)
            self.direction = not self.direction

    async def run(self):
        while True:
            async with self.lock:
                speed = self.speed
            if speed == 0:
                await asyncio.sleep(0.1)
                continue
            delay = (1 / 200) * (1 / speed)
            asyncio.ensure_future(self.reverse())
            self.pin.write(1)
            await asyncio.sleep(delay)
            self.pin.write(0)
            await asyncio.sleep(delay)


class Servo(Actuator):
    """Servo motor class."""

    def __init__(self, pin: Pin):
        self.pin = pin
        self.angle = 90
        self.lock = asyncio.Lock()

    def linear_map(self, x: float):
        """no mapping needed"""
        return int(x)

    async def set_val(self, val: int):
        """set angle of servo motor in degrees"""
        val = self.linear_map(val)
        if val < 0 or val > 1800:
            raise ValueError("Angle must be between 0 and 180")
        async with self.lock:
            self.angle = val

    async def run(self):
        """continuously set angle of servo motor"""
        while True:
            async with self.lock:
                #print(f"{self.pin}: writing {self.angle}") # Debugging line
                self.pin.write(self.angle)
            await asyncio.sleep(0.7)


class Thruster(Servo):
    """Thruster class."""

    active_range: tuple

    # TOASK: are we limiting our range here for all thrusters
    def __init__(self, pin: Pin, active_range: tuple = (1200, 1800), reverse=False):
        super().__init__(pin)
        self.angle = 1500
        self.active_range = active_range
        self.reverse = reverse

    def linear_map(self, x: float):
        """map value to thruster value"""
        if not self.reverse:
            return int(linear_map(x, -1, 1, self.active_range[0], self.active_range[1]))
        return int(linear_map(x, -1, 1, self.active_range[1], self.active_range[0]))


class LinActuator(Actuator):
    """Linear actuator class."""

    def __init__(self, pin: Pin, pin2: Pin, deadzone: int = 0.1):
        self.pin = pin
        self.pin2 = pin2
        self.pos = 0
        self.deadzone = deadzone
        self.lock = asyncio.Lock()

    def linear_map(self, x: float):
        """no mapping needed"""
        return int(x)

    async def set_val(self, val: int):
        """set extension rate of linear actuator motor in degrees"""
        if val < -1 or val > 1:
            raise ValueError("Angle must be between -1 and 1")
        async with self.lock:
            self.pos = val

    async def run(self):
        """continuously set extension rate of linear actuator"""
        while True:
            async with self.lock:
                if self.pos < 0 - self.deadzone:
                    self.pin.write(1)
                    self.pin2.write(0)
                elif self.pos > 0 + self.deadzone:
                    self.pin.write(0)
                    self.pin2.write(1)
                else:
                    self.pin.write(0)
                    self.pin2.write(0)
            await asyncio.sleep(0.1)
