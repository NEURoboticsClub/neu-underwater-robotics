from dataclasses import dataclass, asdict
from time import time_ns


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


@dataclass
class VelocityVector:
    """Represents a velocity vector in 3D space."""

    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    yaw: float = 0.0
    pitch: float = 0.0
    roll: float = 0.0

    def __getitem__(self, key):
        return asdict(self)[key]

    def __setitem__(self, key, value):
        asdict(self)[key] = value

    @classmethod
    def keys(cls):
        return asdict(cls()).keys()


class PIDController:
    """Generic PID Controller"""

    def __init__(self, kp: float, ki: float, kd: float, max_output: float = 90, max_rate_of_change: float = 180):
        """
        Args:
            kp (float): proportional gain
            ki (float): integral gain
            kd (float): derivative gain
            max_output (float): maximum output (output is limited to [-max_output, max_output])
            max_rate_of_change (float): maximum rate of change of output (output/s)
        """
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.max_output = max_output
        self.max_rate_of_change = max_rate_of_change
        self.last_error = 0
        self.last_output = 0
        self.integral = 0

    def update(self, error: float, dt: float) -> float:
        """Update PID controller.
        Args:
            error (float): error
            dt (float): time since last update (seconds)
        Returns:
            float: output
        """
        self.integral += error * dt
        derivative = (error - self.last_error) / dt
        output = self.kp * error + self.ki * self.integral + self.kd * derivative

        # limit rate of change of output
        output = min(
            max(output, self.last_output - self.max_rate_of_change * dt),
            self.last_output + self.max_rate_of_change * dt,
        )

        # limit output to [-max_output, max_output]
        output = min(max(output, -self.max_output), self.max_output)

        self.last_error = error
        self.last_output = output
        return output
