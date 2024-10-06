import socket
import pygame
from abc import abstractmethod
HOST = "192.168.0.103"  # The server's hostname or IP address
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
    def __init__(self, buttons, axes, toggle_vals, trigger_vals, center, radius, ratio):
        self.buttons_dict = {}
        for i in range(buttons):
            if i in toggle_vals:
                self.buttons_dict[i] = toggle()
            else:
                self.buttons_dict[i] = button()

        self.axis_dict = {}
        for i in range(axes):
            if i in trigger_vals:
                self.axis_dict[i] = axis(-1)
            else:
                self.axis_dict[i] = axis(0)

        self.hat = hat(0, 0)
        self.center = center
        self.radius = radius
        self.ratio = ratio

     # get the string to send to robot, format pin:val;
    def get_rov_input(self):
        # output = ""
        # for button in self.buttons_dict:
        #     output += f"{button}:{self.buttons_dict[button].get_joy_val()};"

        # output += "\n"
        # for axis in self.axis_dict:
        #     output += f"{axis}:{self.axis_dict[axis].get_joy_val()};"
        # return output

        # max is up right
        right = self.axis_dict[0].get_joy_val()
        forward = self.axis_dict[1].get_joy_val() * -1
        yaw = self.axis_dict[3].get_joy_val()
        height = self.axis_dict[4].get_joy_val() * -1
        
        front_tilt = (self.axis_dict[2].get_joy_val() + 1) / 2
        back_tilt = (self.axis_dict[5].get_joy_val() + 1) / 2

        precision = self.buttons_dict[0].get_joy_val() + 1.0

        if precision > 1.1:
            precision = self.ratio
        
        depth_hold = self.buttons_dict[2].get_joy_val() # for auto depth

        front_left = self.radius * precision * (forward + right + yaw) / 3.0 + self.center
        back_left = self.radius * precision * (forward - right + yaw) / 3.0 + self.center
        front_right = self.radius * precision * (forward - right - yaw) / 3.0 + self.center
        back_right = self.radius * precision * (forward + right - yaw) / 3.0 + self.center

        front_vert = max(self.center - self.radius, min(self.center + self.radius, 
            precision * (self.radius * height + self.radius * front_tilt) + self.center))
        back_vert = max(self.center - self.radius, min(self.center + self.radius, 
            precision * (self.radius * height + self.radius * back_tilt) + self.center))


        pin_dict = {4: int(front_left), 5: int(front_right), 6: int(back_left), 
                    7: int(back_right), 8: int(front_vert), 9: int(back_vert)}

        output = ""
        for pin in pin_dict:
            output += f"{pin}:{pin_dict[pin]};"
        return output[:-1]


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

    def setup(self, joy_num):
        pygame.joystick.init()
        joysticks = [pygame.joystick.Joystick(
            x) for x in range(pygame.joystick.get_count())]
        pygame.init()
        j = pygame.joystick.Joystick(joy_num)
        j.init()
        
        
j1 = joystick(11, 6, [0, 2], [2, 5], 90, 55, 0.2)


j1.setup(1)

# while True:
#     j1.detect_event()
#     j1.get_rov_input()

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    print(f'connecting to {HOST}:{PORT}')
    old = ''
    while True:
        j1.detect_event()
        x = j1.get_rov_input()
        out = x
        if not out == old:
            s.send(str.encode(out))
            old = out

    data = s.recv(1024)

print(f"Received {data!r}")
