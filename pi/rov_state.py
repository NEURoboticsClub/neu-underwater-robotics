import asyncio

from hardware import Actuator, Sensor
from utils import PIDController, VelocityVector, linear_map, time_ms


class ROVState:
    """State of ROV."""

    actuators: dict[str, Actuator]  # name: actuator  arm motors
    thrusters: dict[str, Actuator]  # name: actuator  thrusters
    sensors: dict[str, Sensor]  # name: sensor
    current_velocity: VelocityVector
    target_veolocity: VelocityVector
    pid_controllers: dict[str, PIDController]  # name: pid controller
    last_time: int  # time of last update in ms

    def __init__(
        self,
        actuators: dict[str, Actuator],
        thrusters: dict[str, Actuator],
        sensors: dict[str, Sensor],
    ):
        self.actuators = actuators
        self.thrusters = thrusters
        self.sensors = sensors
        self.current_velocity = VelocityVector()
        self.target_velocity = VelocityVector()
        self.pid_controllers = {}
        for axis in self.current_velocity.keys():
            self.pid_controllers[axis] = PIDController(
                kp=1.0, ki=0.1, kd=0.01, max_output=90, max_rate_of_change=180
            )
        self.control_loop_frequency = 10  # Hz
        self.last_time = time_ms()

    def _translate_velocity_to_thruster_mix(
        self, target_velocity: VelocityVector
    ) -> dict[str, float]:
        """Translate target velocity to thruster mix.

        Args:
            target_velocity (VelocityVector): target velocity
        Returns:
            dict[str, float]: thruster mix
        """
        mix = {
            "front_left_horizontal": target_velocity.x + target_velocity.y + target_velocity.yaw,
            "front_right_horizontal": target_velocity.x - target_velocity.y - target_velocity.yaw,
            "back_left_horizontal": target_velocity.x - target_velocity.y + target_velocity.yaw,
            "back_right_horizontal": target_velocity.x + target_velocity.y - target_velocity.yaw,
            "left_vertical": target_velocity.z + target_velocity.roll,
            "right_vertical": target_velocity.z - target_velocity.roll,
        }

        # normalize mix, map it to [-1, 1]
        for name, value in mix.items():
            mix[name] = linear_map(value, -3, -3, -1, 1)

        return mix

    async def control_loop(self):
        """Control loop."""
        # get current velocity
        # TODO: get current velocity from sensors

        dt = time_ms() - self.last_time
        # sleep until next control loop iteration
        await asyncio.sleep(1 / self.control_loop_frequency - dt / 1000)

        output_velocity = VelocityVector()
        for axis, controller in self.pid_controllers.items():
            # get error
            error = self.target_velocity[axis] - self.current_velocity[axis]
            # get output
            output_velocity[axis] = controller.update(error, dt)

        # translate output velocity to thruster mix
        thruster_mix = self._translate_velocity_to_thruster_mix(output_velocity)
        for name, value in thruster_mix.items():
            await self.thrusters[name].set_val(value)

        # update last time
        self.last_time = time_ms()
