import asyncio
import logging
import numpy as np

from common import utils

from .hardware import Actuator, Sensor, Thruster

PIDController = utils.PIDController
VelocityVector = utils.VelocityVector
SlewRateLimiter = utils.SlewRateLimiter
time_ms = utils.time_ms
linear_map = utils.linear_map


class ROVState:
    """State of ROV."""

    actuators: dict[str, Actuator]  # name: actuator  arm motors
    thrusters: dict[str, Actuator]  # name: actuator  thrusters
    sensors: dict[str, Sensor]  # name: sensor
    status_flags: dict[str, any] # name: status_flags

    def __init__(
        self,
        actuators: dict[str, Actuator],
        thrusters: dict[str, Actuator],
        sensors: dict[str, Sensor],
        status_flags: dict[str, any],
    ):
        self.actuators = actuators
        self.thrusters = thrusters
        self.sensors = sensors
        self.status_flags = status_flags
        self._current_velocity = VelocityVector()
        self._current_claw = {"extend": 0, "rotate": 90, "close_main": 90,
                              "close_side": 90, "sample": 0, "camera_servo": 90}
        self._target_velocity = VelocityVector()
        self._pid_controllers = {}  # axis: PIDController
        # TOASK: how are we using this and is it tuned? May explain some things
        for axis in self._current_velocity.keys():
            self._pid_controllers[axis] = PIDController(
                kp=1.0, ki=0.1, kd=0.01, max_output=90, max_rate_of_change=180
            )
        self._control_loop_frequency = 10.0  # Hz
        self._last_time = time_ms()  # time the last control loop iteration was executed in ms
        self._last_current_velocity_update = 0  # time of last current velocity update in ms
        self._last_current_claw_update = 0  # time of last current claw update in ms
        self._last_target_velocity_update = 0  # time of last target velocity update in ms
        self._current_depth = 0.0 # current depth of ROV
        self._target_depth = 0.0 # target depth for ROV
        self._current_imu_data = utils.init_imu_data()
        self._z_sensitivity = 0.0001 # how much the z changes with controller input
        self._bang_bang_radius = 0.02 # distance in meters from target depth before turning on
        self._p_factor = 1 # factor to scale the auto-depth by
        self._slew_limiters = {}
        for name, _ in self.thrusters.items():
            self._slew_limiters[name] = SlewRateLimiter(
                max_rate = (2.0 / 1.0), 
                initial_value = 0.0
            )

        # for axis in self._current_velocity.keys():
        #     self._slew_limiters[axis] = SlewRateLimiter(
        #         max_rate=500  # max rate of change of pwm per second
        #     )

    def get_tasks(self) -> list[asyncio.Task]:
        """Return tasks for all actuators"""
        tasks = []
        for actuator in self.actuators.values():
            tasks.append(actuator.run())
        for actuator in self.thrusters.values():
            tasks.append(actuator.run())
        return tasks
    

    def _translate_velocity_to_thruster_mix(
        self, target_velocity: VelocityVector, dt: float
    ) -> dict[str, float]:
        """
        Translate target velocity to thruster mix.
        Args:
            target_velocity (VelocityVector): target velocity
            dt (float): delta time (s)
        Returns:
            dict[str, float]: thruster mix
        """
        mix = {
            "front_left_horizontal": target_velocity.x + target_velocity.y + target_velocity.yaw,
            "front_right_horizontal": -target_velocity.x + target_velocity.y - target_velocity.yaw,
            "back_left_horizontal": -target_velocity.x + target_velocity.y + target_velocity.yaw,
            "back_right_horizontal": target_velocity.x + target_velocity.y + target_velocity.yaw,
            "front_left_vertical": target_velocity.z + target_velocity.pitch + target_velocity.roll,
            "front_right_vertical": target_velocity.z + target_velocity.pitch - target_velocity.roll,
            "back_left_vertical": target_velocity.z - target_velocity.pitch + target_velocity.roll,
            "back_right_vertical": target_velocity.z - target_velocity.pitch - target_velocity.roll,
        }
        if self.status_flags["agnes_mode"]:
            mix["front_left_vertical"] *= self.status_flags["agnes_factor"]
            mix["front_right_vertical"] *= self.status_flags["agnes_factor"]
            mix["back_left_vertical"] *= self.status_flags["agnes_factor"]
            mix["back_right_vertical"] *= self.status_flags["agnes_factor"]
        
        # apply slew rate limiters to thruster mix
        for name, value in mix.items():
            if name in self._slew_limiters:
                mix[name] = self._slew_limiters[name].update(value, dt)
            else:
                logging.warning(f"Slew rate limiter for {name} not found, using raw value.")

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
        self._current_depth = np.average(recent_depths)

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

    def set_status_flags(self, status_flags: dict):
        """
        Set current status flags.
        Args:
            status_flags (dict): current status flags
        """
        if status_flags["auto_depth"] and not self.status_flags["auto_depth"]:
            self._target_depth = self._current_depth
        self.status_flags = status_flags
    

    async def control_loop(self):
        """Control loop."""
        loop_period = 1000.0 / self._control_loop_frequency  # ms

        while True:
            dt = float(time_ms() - self._last_time) / 1000.0
            # update last time
            self._last_time = time_ms()

            if -0.1 < self._target_velocity.z < 0.1:
                self._target_depth -= self._target_velocity.z * self._z_sensitivity
                # test different sensitivities and potentially functions
                if self._target_depth > 1 and self._current_depth > 1:
                    self._target_velocity.z = (self._target_depth - self._current_depth) ** 3

            # Plan test these and either make them toggleable or keep the best one
            # Auto Depth V1 (Bang Bang P)
            # if self.status_flags["auto_depth"]:
            #     if abs(self._target_depth - self._current_depth) > self._bang_bang_radius:
            #         self._target_velocity.z = ((self._target_depth - self._current_depth) * 
            #                                    self._p_factor)
            #     else: 
            #         self._target_velocity.z = 0

            # Auto Depth V2 (Pure Bang Bang)
            # if self.status_flags["auto_depth"]:
            #     if self._target_depth - self._current_depth > self._bang_bang_radius:
            #         self._target_velocity.z = 1 
            #     elif self._current_depth - self._target_depth > self._bang_bang_radius:
            #         self._target_velocity.z = -1
            #     else: 
            #         self._target_velocity.z = 0

            # Auto Depth V3 (Altitude Mode w/ Bang Bang P)
            # if self.status_flags["auto_depth"]:
            #     z_radius = 0.1 # parameter for how far stick has to be to stop holding altitude
            #     if abs(self._target_velocity.z) > z_radius:
            #         self._target_depth += self._target_velocity.z * self._z_sensitivity
            #     if abs(self._target_depth - self._current_depth) > self._bang_bang_radius:
            #         self._target_velocity.z = ((self._target_depth - self._current_depth) *
            #                                    self._p_factor)
            #     else:
            #          self._target_velocity.z = 0

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
            thruster_mix = self._translate_velocity_to_thruster_mix(output_velocity, dt)
            # print(thruster_mix)
            # print(self._current_claw)
            set_val_tasks = []
            for name, value in thruster_mix.items():
                set_val_tasks.append(self.thrusters[name].set_val(value))
            for name, value in self._current_claw.items():
                set_val_tasks.append(self.actuators[name].set_val(value))
            
            for thruster_name, _ in self.thrusters.items():
                print(f"{thruster_name}: {thruster_mix[thruster_name]}")
            for actuator_name, _ in self.actuators.items():
                print(f"{actuator_name}: {self._current_claw[actuator_name]}")
            await asyncio.gather(*set_val_tasks)

            # sleep until next control loop iteration
            if (time_ms() - self._last_time) < loop_period:
                await asyncio.sleep(
                    (1 / self._control_loop_frequency) - (time_ms() - self._last_time) / 1000
                )
            else:
                logging.warning("Control loop iteration took too long.")
