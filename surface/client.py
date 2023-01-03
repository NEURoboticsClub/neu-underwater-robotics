import socket
import pygame
from abc import abstractmethod
HOST = "192.168.0.101"  # The server's hostname or IP address
PORT = 2049  # The port used by the server


# abstract class to represent nany joystick item. promises the ability
# to get a value and to update based upon an input value.
class joy_item:
    @abstractmethod
    def update(self, state):
        pass

    @abstractmethod
    def get_joy_val(self):
        pass

# represents a button and keeps track of it as 0 for up, 1 for down.
class button(joy_item):
    def __init__(self):
        self.button_pressed = 0

    def update(self, state):
        self.button_pressed = state

    def get_joy_val(self):
        return self.button_pressed


# represents a toggle with 0 as off and 1 as on. Flips on toggle.
class toggle(button):
    def __init__(self):
        super()
        self.button_pressed = 0

    def update(self, state):
        if state == 1:
            self.button_pressed = (self.button_pressed + 1) % 2

# defines an axis with a double for the value (triggers are axes) range [-1, 1]
class axis(joy_item):
    def __init__(self, trigger_val):
        self.trigger_val = trigger_val

    def update(self, state):
        self.trigger_val = state

    def get_joy_val(self):
        return self.trigger_val

# represents the d-pad with 1 being (up/right)? -1 being (down/left)
class hat():
    def __init__(self, up, right):
        self.up = up
        self.right = right

    def update(self, up, right):
        self.up = up
        self.right = right

    def get_joy_val(self):
        return [self.up, self.right]

# class representing a full joystick with dictionarys for buttons and axes.
class joystick:
    # we use a list of toggle_vals for all values that behave like toggles not buttons
    # buttons is number of buttons and axes is number of axes
    def __init__(self, buttons, axes, toggle_vals):
        self.buttons_dict = {}
        for i in range(buttons):
            if i in toggle_vals:
                self.buttons_dict[i] = toggle()
            else:
                self.buttons_dict[i] = button()
        self.axis_dict = {k:axis(0) for k in range(axes)}
        self.hat = hat(0, 0)

     # get the string to send to robot, format pin:val;
    def get_rov_input(self):
        output = ""
        for button in self.buttons_dict:
            output += f"{button}:{self.buttons_dict[button].get_joy_val()};"

        output += "\n"
        for axis in self.axis_dict:
            output += f"{axis}:{self.axis_dict[axis].get_joy_val()};"
        return output


    def detect_event(self):
        for event in pygame.event.get():
            if event.type == pygame.JOYAXISMOTION:
                self.axis_dict[event.axis].update(event.value)

            elif event.type == pygame.JOYBALLMOTION:
                print("ball motions")

            elif event.type == pygame.JOYBUTTONDOWN:
                self.buttons_dict[event.button].update(1)

            elif event.type == pygame.JOYBUTTONUP:
                self.buttons_dict[event.button].update(0)

            elif event.type == pygame.JOYHATMOTION:
                value = event.value
                self.hat.update(value[0], value[1])

            print(self.get_rov_input())

    def setup(self):
        pygame.joystick.init()
        joysticks = [pygame.joystick.Joystick(
            x) for x in range(pygame.joystick.get_count())]
        pygame.init()
        j = pygame.joystick.Joystick(0)
        j.init()


j1 = joystick(11, 6, [0, 2])



j1.setup()


while True:
    j1.detect_event()
    j1.get_rov_input()

# with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
#     s.connect((HOST, PORT))
#     print(f'connecting to {HOST}:{PORT}')
#     old = ''
#     while True:
#         j1.detect_event()
#         x = j1.get_rov_input()
#         if not x == old:
#             s.send(str.encode(x))
#             old = x

    # data = s.recv(1024)

# print(f"Received {data!r}")
