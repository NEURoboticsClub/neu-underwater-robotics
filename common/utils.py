from dataclasses import asdict, dataclass
from time import time_ns
import math

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
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

"""Creates a dictionary with the given x, y, and z arguments.

Args:
    x: the value to set dict["x"] to
    y: the value to set dict["y"] to
    z: the value to set dict["z"] to

Returns:
    dict: a dictionary with the given values as "x", "y", and "z"
"""
def make_xyz_dict(x, y, z) -> dict:
    xyz_dict = {}
    xyz_dict["x"] = x
    xyz_dict["y"] = y
    xyz_dict["z"] = z

    return xyz_dict

"""Returns a dictionary of the correct format for the IMU with zeroed data.

Returns:
    dict: a dictionary of dictionaries, each one containing a set of zeroed IMU data
        (accelerometer, gyroscope, magnetometer, or quaternion)
"""
def init_imu_data() -> dict:
    data = {}
    # acceleration
    data["acceleration"] = make_xyz_dict(0,0,0)

    # gyro
    data["gyroscope"] = make_xyz_dict(0,0,0)

    # magnetometer
    data["magnetometer"] = make_xyz_dict(0,0,0)

    # quaternion
    quaternion = {}
    quaternion["i"] = 0
    quaternion["j"] = 0
    quaternion["k"] = 0
    quaternion["real"] = 0
    data["game_quaternion"] = quaternion

    return data

def euler_from_quaternion(x, y, z, w):
        """
        Convert a quaternion into euler angles (roll, pitch, yaw)
        roll is rotation around x in degrees (counterclockwise)
        pitch is rotation around y in degrees (counterclockwise)
        yaw is rotation around z in degrees (counterclockwise)
        """
        t0 = +2.0 * (w * x + y * z)
        t1 = +1.0 - 2.0 * (x * x + y * y)
        roll_x = math.atan2(t0, t1)
     
        t2 = +2.0 * (w * y - z * x)
        t2 = +1.0 if t2 > +1.0 else t2
        t2 = -1.0 if t2 < -1.0 else t2
        pitch_y = math.asin(t2)
     
        t3 = +2.0 * (w * z + x * y)
        t4 = +1.0 - 2.0 * (y * y + z * z)
        yaw_z = math.atan2(t3, t4)

        roll_x = (roll_x * 180.0) / math.pi
        pitch_y = (pitch_y * 180.0) / math.pi
        yaw_z = (yaw_z * 180.0) / math.pi
     
        return roll_x, pitch_y, yaw_z # in degrees

@dataclass
class VelocityVector:
    """Represents a velocity vector in 3D space. Standard 3D right handed coordinate system.
    The vehicle is parallel to the xy plane, pointed to +y.
    yaw is about the z axis, pitch is about the x axis, roll is about the y axis.
    """

    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    yaw: float = 0.0
    pitch: float = 0.0
    roll: float = 0.0

    def __init__(self, vals: dict[str, float] | None = None):
        if vals is not None:
            for key, value in vals.items():
                setattr(self, key, value)

    def __getitem__(self, key):
        return asdict(self)[key]

    def __setitem__(self, key, value):
        asdict(self)[key] = value

    def keys(self):
        """Return keys."""
        return asdict(self).keys()

    def to_dict(self):
        """Return dict representation. Rounds values to 3 decimal places."""
        return {k: round(v, 3) for k, v in asdict(self).items()}


class PIDController:
    """Generic PID Controller"""

    def __init__(
        self,
        kp: float,
        ki: float,
        kd: float,
        max_output: float = 90,
        max_rate_of_change: float = 180,
    ):
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

class SlewRateLimiter:
    def __init__(self, max_rate, initial_value):
        self.max_rate = max_rate   # Maximum rate of change
        self.last_value = initial_value

    def update(self, target_value, dt):
        """Update the slew rate limiter.
        Args:
            target_value (float): target value to limit
            dt (float): time since last update (seconds)
        Returns:
            float: limited value
        """
        change = target_value - self.last_value
        max_change = self.max_rate * dt
        if abs(change) > max_change:
            change = max_change * (1 if change > 0 else -1)
        self.last_value += change
        
        return self.last_value