import socket
import pygame

HOST = "192.168.1.200"  # The server's hostname or IP address
PORT = 2049  # The port used by the server

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    while True:
        x = input()
        s.send(str.encode(x))
    # data = s.recv(1024)

# print(f"Received {data!r}")

class button:
    def __init__(self, button_num):
        self.button_num = button_num
        button_pressed = False

    def pressed(self):
        self.button_pressed = not self.button_pressed
        print("button pressed")




class axis:
    global axis_value1, axis_value2

    def __init__(self, axis_num1, axis_num2):
        self.axis_num1 = axis_num1
        self.axis_num2 = axis_num2

    def update(self, axis_num, value):
        if axis_num == self.axis_num1:
            axis_value1 = value
        else:
            axis_value2 = value



class hat:
    global value1, value2

    def update(self, value_1, value_2):
        value1 = value_1
        value2 = value_2


class joystick:
    joystick = 0
    axis = 0
    ball = 0
    button = 0
    hat = 0
    value = 0
    rel = 0
    pressed = 0

    def __init__(self, button3, button5, button6, buttonA, buttonB, buttonX, buttonY, axis1, axis4, hat2):
        self.button3 = button3
        self.button5 = button5
        self.button6 = button6
        self.buttonA = buttonA
        self.buttonB = buttonB
        self.buttonX = buttonX
        self.buttonY = buttonY
        self.axis1 = axis1
        self.axis4 = axis4
        self.hat2 = hat2
        print("start")

    def setup(self):
        pygame.joystick.init()
        print(pygame.joystick.get_count())
        joysticks = [pygame.joystick.Joystick(
            x) for x in range(pygame.joystick.get_count())]
        pygame.init()
        j = pygame.joystick.Joystick(0)
        j.init()

    def detect_event(self):
        for event in pygame.event.get():
            if event.type == pygame.JOYAXISMOTION:
                # print(event.dict, event.joy, event.axis, event.value)
                joystick = event.joy
                axis = event.axis
                value = event.value
                print("JOYAXISMOTION", "joystick", joystick, "axis", axis, "value", value)

            elif event.type == pygame.JOYBALLMOTION:
                joystick = event.joy
                ball = event.ball
                rel = event.rel
                # print(event.dict, event.joy, event.ball, event.rel)
                print("JOYBALLMOTION", "joystick", joystick, "ball", ball, "rel", rel)
            elif event.type == pygame.JOYBUTTONDOWN:
                joystick = event.joy
                button = event.button
                pressed = 1
                print("JOYBUTTONDOWN", "joystick", joystick, "button", button, "pressed", pressed)
                # print(event.dict, event.joy, event.button, 'pressed')
            elif event.type == pygame.JOYBUTTONUP:
                joystick = event.joy
                button = event.button
                pressed = 0
                print("JOYBUTTONUP", "joystick", joystick, "button", button, "pressed", pressed)
                # print(event.dict, event.joy, event.button, 'released')
            elif event.type == pygame.JOYHATMOTION:
                joystick = event.joy
                hat = event.hat
                value = event.value




button3 = button(6)
button5 = button(7)
button6 = button(8)
buttonA = button(0)
buttonB = button(1)
buttonX = button(2)
buttonY = button(3)
axis1 = axis(1, 0)
axis4 = axis(3, 4)
hat2 = hat()
j1 = joystick(button3, button5, button6, buttonA, buttonB, buttonX, buttonY, axis1, axis4, hat)
j1.setup()
while True:
    j1.detect_event()