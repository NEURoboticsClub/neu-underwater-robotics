import asyncio

from common import utils

from .hardware import Servo


class SimThruster(Servo):
    """Simulator Thruster. Prints out values."""

    active_range: tuple

    def __init__(
        self, pin_number: int, active_range: tuple = (30, 150)
    ):  # pylint: disable=super-init-not-called
        self.pin_number = pin_number
        self.active_range = active_range
        self.lock = asyncio.Lock()
        self.angle = 90

    def linear_map(self, x: float):
        """map value to thruster value"""
        return int(utils.linear_map(x, -1, 1, self.active_range[0], self.active_range[1]))

    async def set_val(self, val: int):
        """set angle of servo motor in degrees"""
        val = self.linear_map(val)
        if val < 0 or val > 180:
            raise ValueError("Angle must be between 0 and 180")
        async with self.lock:
            self.angle = val

    async def run(self):
        """continuously print val of thruster"""
        while True:
            # async with self.lock:
                # print(f"Thruster {self.pin_number}: {self.angle}")
            await asyncio.sleep(0.1)
