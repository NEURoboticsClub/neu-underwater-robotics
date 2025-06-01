import asyncio
import logging
import numpy as np

from common import utils

from .hardware import Actuator, Sensor

PIDController = utils.PIDController
VelocityVector = utils.VelocityVector
time_ms = utils.time_ms
linear_map = utils.linear_map


class ROVState:
    """State of ROV."""

    actuators: dict[str, Actuator]  # name: actuator  arm motors
    thrusters: dict[str, Actuator]  # name: actuator  thrusters
    sensors: dict[str, Sensor]  # name: sensor

    def __init__(
        self,
        actuators: dict[str, Actuator],
        thrusters: dict[str, Actuator],
        sensors: dict[str, Sensor],
    ):
        self.actuators = actuators
        self.thrusters = thrusters
        self.sensors = sensors
        self._current_velocity = VelocityVector()
        self._current_claw = {"extend": 0, "rotate": 90, "close": 90}
        self._target_velocity = VelocityVector()
        self._pid_controllers = {}  # axis: PIDController
        for axis in self._current_velocity.keys():
            self._pid_controllers[axis] = PIDController(
                kp=1.0, ki=0.1, kd=0.01, max_output=90, max_rate_of_change=180
            )
        self._control_loop_frequency = 10  # Hz
        self._last_time = time_ms()  # time the last control loop iteration was executed in ms
        self._last_current_velocity_update = 0  # time of last current velocity update in ms
        self._last_current_claw_update = 0  # time of last current claw update in ms
        self._last_target_velocity_update = 0  # time of last target velocity update in ms
        self._current_depth = 0 # current depth of ROV
        self._target_depth = 0 # target depth for ROV
        self._current_imu_data = utils.init_imu_data()
        self._z_sensitivity = 0.0001 # how much the z changes with controller input

    def get_tasks(self) -> list[asyncio.Task]:
        """Return tasks for all actuators"""
        tasks = []
        for actuator in self.actuators.values():
            tasks.append(actuator.run())
        for actuator in self.thrusters.values():
            tasks.append(actuator.run())
        return tasks
    

    def _translate_velocity_to_thruster_mix(
        self, target_velocity: VelocityVector
    ) -> dict[str, float]:
        """
        Translate target velocity to thruster mix.
        Args:
            target_velocity (VelocityVector): target velocity
        Returns:
            dict[str, float]: thruster mix
        """
        mix = {
            "front_left_horizontal": -target_velocity.x + target_velocity.y + target_velocity.yaw,
            "front_right_horizontal": target_velocity.x + target_velocity.y - target_velocity.yaw,
            "back_left_horizontal": -target_velocity.x - target_velocity.y - target_velocity.yaw,
            "back_right_horizontal": target_velocity.x - target_velocity.y + target_velocity.yaw,
            "front_left_vertical": target_velocity.z + target_velocity.pitch - target_velocity.roll,
            "front_right_vertical": target_velocity.z + target_velocity.pitch + target_velocity.roll,
            "back_left_vertical": target_velocity.z - target_velocity.pitch - target_velocity.roll,
            "back_right_vertical": target_velocity.z - target_velocity.pitch + target_velocity.roll,
        }

        # cap value to [-1, 1]
        for name, value in mix.items():
            mix[name] = max(min(value, 1), -1)

        return mix

    def set_current_velocity(self, velocity: VelocityVector):
        """
        Set current velocity.
        Args:
            velocity (VelocityVector): current velocity
        """
        self._current_velocity = velocity
        self._last_current_velocity_update = time_ms()
    
    def set_claw_movement(self, claw: dict):
        """
        Set current claw movement values.
        Args:
            claw (dict): current claw movement values
        """
        self._current_claw = claw
        self._last_current_claw_update = time_ms()

    def set_current_depth(self, recent_depths):
        """
        Set current depth by averaging previous 10 values
        Args: 
            recent_depths (List[float]): Lsit of the most recent depths
        """
        self._current_depth = np.avg(recent_depths)

    def set_current_imu_data(self, imu_data):
        """
        Set current imu data.
        Args:
            imu_data (dict): current imu data
        """
        self._current_imu_data = imu_data

    def set_target_velocity(self, velocity: VelocityVector):
        """Set target velocity.

        Args:
            velocity (VelocityVector): target velocity
        """
        self._target_velocity = velocity
        self._last_target_velocity_update = time_ms()
    

    async def control_loop(self):
        """Control loop."""
        loop_period = 1000 / self._control_loop_frequency  # ms

        while True:
            dt = (time_ms() - self._last_time) / 1000
            # update last time
            self._last_time = time_ms()

            if -0.1 < self._target_velocity.z < 0.1:
                self._target_depth -= self._target_velocity.z * self._z_sensitivity
                # test different sensitivities and potentially functions
                if self._target_depth > 1 and self._current_depth > 1:
                    self._target_velocity.z = (self._target_depth - self._current_depth) ** 3

            if time_ms() - self._last_target_velocity_update > 2 * loop_period:
                # target velocity is stale, stop ROV
                self._target_velocity = VelocityVector()

            if time_ms() - self._last_current_velocity_update <= 2 * loop_period:
                # current velocity is not stale, use PID controller
                output_velocity = VelocityVector()
                for axis, controller in self._pid_controllers.items():
                    error = self._target_velocity[axis] - self._current_velocity[axis]
                    output_velocity[axis] = controller.update(error, dt)
            else:
                # controller bypass. uses target velocity directly.
                # logging.warning("Current velocity is stale, using target velocity directly.")
                output_velocity = self._target_velocity
            

            # translate output velocity to thruster mix
            thruster_mix = self._translate_velocity_to_thruster_mix(output_velocity)
            print(thruster_mix)
            # print(self._current_claw)
            set_val_tasks = []
            for name, value in thruster_mix.items():
                set_val_tasks.append(self.thrusters[name].set_val(value))
            for name, value in self._current_claw.items():
                set_val_tasks.append(self.actuators[name].set_val(value))
            
            for thruster_name, thruster in self.thrusters.items():
                print(f"{thruster_name}: {thruster_mix[thruster_name]}")
            for actuator_name, actuator in self.actuators.items():
                print(f"{actuator_name}: {self._current_claw[actuator_name]}")
            await asyncio.gather(*set_val_tasks)

            # sleep until next control loop iteration
            if (time_ms() - self._last_time) < loop_period:
                await asyncio.sleep(
                    (1 / self._control_loop_frequency) - (time_ms() - self._last_time) / 1000
                )
            else:
                logging.warning("Control loop iteration took too long.")
