from abc import ABC, abstractmethod
from typing import Generic, List, TypeVar

import pygame

from common import utils

VelocityVector = utils.VelocityVector

T = TypeVar("T")  # Generic type


class JoyItem(Generic[T], ABC):
    """Abstract joystick item class to represent any joystick item."""

    @abstractmethod
    def update(self, state: T) -> None:
        """update the joystick item based upon the input state"""

    @abstractmethod
    def get_joy_val(self) -> T:
        """get the value of the joystick item"""


class Button(JoyItem[bool]):
    """Represents a button and keeps track of it as False for up, True for down."""

    def __init__(self):
        self.button_pressed = False

    def update(self, state: bool) -> None:
        self.button_pressed = state

    def get_joy_val(self) -> bool:
        return self.button_pressed


class Toggle(Button):
    """Represents a toggle with False as off and True as on. Flips on toggle."""

    def __init__(self):
        super().__init__()
        self.button_pressed = False

    def update(self, state):
        if state:
            self.button_pressed = not self.button_pressed


class Axis(JoyItem[float]):
    """Represents an axis with a double for the value (triggers are axes) range [-1, 1]"""

    def __init__(self, val: float = 0.0):
        self.val = val

    def update(self, state: float) -> None:
        self.val = state

    def get_joy_val(self) -> float:
        return self.val


class Hat(JoyItem[tuple[float, float]]):
    """Represents the d-pad with 1 being (up/right)? -1 being (down/left)"""

    def __init__(self, up=0, right=0):
        self.up = up
        self.right = right

    def update(self, state):
        """update the hat values"""
        self.up = state[1]
        self.right = state[0]

    def get_joy_val(self):
        """get the hat values"""
        return (self.up, self.right)


class Controller(ABC):
    """Controller class to represent any joystick."""

    def __init__(self, joy_id: int, toggles: List[int] = []):
        pygame.init()  # safe to call multiple times
        pygame.joystick.init()  # safe to call multiple times
        self._joystick = pygame.joystick.Joystick(joy_id)
        self._joystick.init()
        self._axes: list[Axis] = [Axis() for _ in range(self._joystick.get_numaxes())]
        self._buttons: list[Button] = [Button() if i not in toggles else Toggle() 
                                       for i in range(self._joystick.get_numbuttons())]
        self._hats: list[Hat] = [Hat() for _ in range(self._joystick.get_numhats())]

    def update(self, event: pygame.event.EventType) -> None:
        """update the joystick with given event"""
        if event.type == pygame.JOYAXISMOTION:
            self._axes[event.axis].update(event.value)
        elif event.type == pygame.JOYBUTTONDOWN:
            self._buttons[event.button].update(True)
        elif event.type == pygame.JOYBUTTONUP:
            self._buttons[event.button].update(False)
        elif event.type == pygame.JOYHATMOTION:
            self._hats[event.hat].update(event.value)

    def _poll(self) -> None:
        """poll controller to get current values"""
        for i, item in enumerate(self._axes):
            item.update(self._joystick.get_axis(i))
        for i, item in enumerate(self._buttons):
            item.update(self._joystick.get_button(i))
        for i, item in enumerate(self._hats):
            item.update(self._joystick.get_hat(i))

    def get_joy_val(self) -> dict[str, list]:
        """get the value of the joystick"""
        return {
            "axes": [axis.get_joy_val() for axis in self._axes],
            "buttons": [button.get_joy_val() for button in self._buttons],
            "hats": [hat.get_joy_val() for hat in self._hats],
        }

    @abstractmethod
    def get_velocity_vector(self) -> VelocityVector:
        """get the desired velocity vector from joystick values"""


class XBoxDriveController(Controller):
    """Represents a joystick with buttons and axes."""

    def __init__(self, joy_id: int):
        toggles = [2, 3] # indices treated as toggles
        super().__init__(joy_id, toggles)
        self.buttons_dict = {
            "A": self._buttons[0],
            "B": self._buttons[1],
            "X": self._buttons[2],
            "Y": self._buttons[3],
            "LB": self._buttons[4],
            "RB": self._buttons[5],
            "back": self._buttons[6],
            "start": self._buttons[7],
            "left_stick": self._buttons[8],
            "right_stick": self._buttons[9],
        }
        self.hat_dict = {
            "hat": self._hats[0]
        }
        self.axis_dict = {
            "left_x": self._axes[0],
            "left_y": self._axes[1],
            "right_x": self._axes[3],
            "right_y": self._axes[4],
            "left_trigger": self._axes[2],
            "right_trigger": self._axes[5],
        }
        self.velocity_vec = VelocityVector()
        self.status_flags = {
            "agnes_factor":0.3,
            "agnes_mode":False,
            "auto_depth":False,
        }
        self.claw_vec = {"camera_servo": 90}
        self.agnes_factor_scale = 0.002

    def get_velocity_vector(self) -> VelocityVector:
        """get the desired velocity vector from joystick values"""
        pygame.event.get()  # clear events to get current values (not sure why this is needed)
        self._poll()  # get current joystick values
        self.velocity_vec.x = utils.deadzone_retrict(self.axis_dict["left_x"].get_joy_val()) * -1
        self.velocity_vec.y = utils.deadzone_retrict(self.axis_dict["left_y"].get_joy_val())
        self.velocity_vec.z = utils.deadzone_retrict(self.axis_dict["right_y"].get_joy_val())
        self.velocity_vec.yaw = utils.deadzone_retrict(self.axis_dict["right_x"].get_joy_val()) * -1
        self.velocity_vec.pitch = (((utils.deadzone_retrict(self.axis_dict["left_trigger"].get_joy_val()) + 1) / 2) - 
                    ((utils.deadzone_retrict(self.axis_dict["right_trigger"].get_joy_val()) + 1) / 2))
        self.velocity_vec.roll = (int(self.buttons_dict["RB"].get_joy_val()) - \
                                 int(self.buttons_dict["LB"].get_joy_val())) * 0.5
        
        return self.velocity_vec
    
    def get_status_flags(self) -> dict:
        self.status_flags["agnes_factor"] += self.hat_dict["hat"].get_joy_val()[0] * self.agnes_factor_scale
        self.status_flags["agnes_mode"] = self.buttons_dict["Y"].get_joy_val()
        self.status_flags["auto_depth"] = self.buttons_dict["X"].get_joy_val()

        return self.status_flags


    def get_claw_vector(self) -> dict:
        """get the desired claw vector from joystick values"""
        pygame.event.get()  # clear events to get current values (not sure why this is needed)
        self._poll()  # get current joystick values
        # TODO: control scheme goes here     
        self.claw_vec["extend"] = utils.deadzone_retrict(self.axis_dict["left_y"].get_joy_val())
        self.claw_vec["rotate"] = utils.deadzone_retrict(self.axis_dict["right_x"].get_joy_val()) * -90 + 90
        self.claw_vec["close_main"] = (utils.deadzone_retrict(self.axis_dict["right_trigger"].get_joy_val()) + 1) * -4 + \
                        (utils.deadzone_retrict(self.axis_dict["left_trigger"].get_joy_val()) + 1) * 4 + 92
        self.claw_vec["close_side"] = int(self.buttons_dict["LB"].get_joy_val()) * 6 + \
                        int(self.buttons_dict["RB"].get_joy_val()) * -4 + 92
        self.claw_vec["sample"] = (int(self.buttons_dict["B"].get_joy_val()) - 
                         int(self.buttons_dict["A"].get_joy_val()))
        self.claw_vec["camera_servo"] = max(min(self.claw_vec["camera_servo"] + (self.hat_dict["hat"].get_joy_val()[0] / 2.0), 180), 0)

        return self.claw_vec
    
    def update_sensor_reading(self, sensor_dict):
        # TODO: implement sensor dict in surface client
        self.sensor_dict = sensor_dict
