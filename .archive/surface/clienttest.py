import socket
import pygame

HOST = "192.168.0.103"  # The server's hostname or IP address
PORT = 2049  # The port used by the server


class button:
    def __init__(self, button_num):
        self.button_num = button_num
        self.button_pressed = False

    def update(self, state):
        self.button_pressed = state is 1
        self.pressed()

    def pressed(self):
        print("button pressed:", self.button_pressed)

    def calculate_values(self, precision):
        if self.button_pressed:
            return precision
        else:
            return 0


class toggle(button):
    def update(self, state):
        #print("toggle pressed",self.button_pressed,"state",state)
        if state is 1:
            self.button_pressed = not self.button_pressed
        self.pressed()

    def get_precision_val(self):
        if (self.button_pressed):
            return 0.2
        else:
            return 1

    def pressed(self):
        print("toggle :", self.button_pressed)


class axis:
    global axis_value1, axis_value2

    def __init__(self, axis_value1, axis_value2):
        self.axis_value1 = axis_value1
        self.axis_value2 = axis_value2

    def update(self, axis_num, value):
        if axis_num == self.axis_value1:
            self.axis_value1 = value
        else:
            self.axis_value2 = value
        #print("axis1: ",self.axis_value1," axis2 ",self.axis_value2)

    def calculate_values(self, precision):
        #print("calculate values",self.axis_value2,precision)
        # self.axis_value1," axis2 ",self.axis_value2)):
        return int((self.axis_value2*precision*55)+90)


class trigger:
    global trigger_val

    def __init__(self, trigger_val):
        self.trigger_val = trigger_val

    def update(self, axis_num, value):
        self.trigger_val = value
        print("trigger", self.trigger_val,
              (1+self.trigger_val)/2, (1+self.trigger_val)/2*1)
        self.calculate_values(1)

    def calculate_values(self, precision):
        return (1+self.trigger_val)/2*precision


class hat:
    global value1, value2

    def update(self, value_1, value_2):
        value1 = value_1
        value2 = value_2


class joystick:
    def __init__(self, back, start, centerButton, precisionToggle, buttonB, heightAdj,
                 override, leftAxis, rightAxis, dPad, leftBumper, rightBumper,
                 leftTrigger, rightTrigger):
        self.back = back
        self.start = start
        self.centerButton = centerButton
        self.precisionToggle = precisionToggle
        self.buttonB = buttonB
        self.heightAdj = heightAdj
        self.override = override
        self.leftAxis = leftAxis
        self.rightAxis = rightAxis
        self.dPad = dPad
        self.leftBumper = leftBumper
        self.rightBumper = rightBumper
        self.leftTrigger = leftTrigger
        self.rightTrigger = rightTrigger
        button_nums = [0, 1, 2, 3, 4, 5]
        button_obj = [precisionToggle, buttonB,
                      heightAdj, override, leftBumper, rightBumper]
        self.buttons_dict = dict(zip(button_nums, button_obj))
        axis_nums = [0, 1, 2, 3, 4, 5]
        axis_obj = [leftAxis, leftAxis, rightAxis,
                    rightAxis, leftTrigger, rightTrigger]
        self.axis_dict = dict(zip(axis_nums, axis_obj))
        print("start")

     # get the string to send to robot, format pin:val;
    def get_rov_input(self):
        precision_val = self.precisionToggle.get_precision_val()
        left_axis_val = self.leftAxis.calculate_values(precision_val)
        right_axis_val = self.rightAxis.calculate_values(precision_val)
        left_axis_val = ((left_axis_val - 90) * -1) + 90
#         vert_front_val = 90 + (55 * (self.leftBumper.calculate_values(
#             precision_val) - self.leftTrigger.calculate_values(precision_val)))
# #         print("left",precision_val,self.leftTrigger.calculate_values(precision_val))
#         vert_back_val = 90 + (55 * self.rightBumper.calculate_values(
#             precision_val)) - self.rightTrigger.calculate_values(precision_val)

        vert_front_val = 90 + (55 * self.rightTrigger.calculate_values(
            precision_val)) - (55 * self.leftTrigger.calculate_values(precision_val))
        vert_back_val = 90 + (55 * self.leftTrigger.calculate_values(
            precision_val)) - (55 * self.rightTrigger.calculate_values(precision_val))
        # print("right",self.rightBumper.calculate_values(precision_val), self.rightTrigger.calculate_values(precision_val))self.pin_dict = {4:left_axis_val,5:right_axis_val,6:left_axis_val,7:right_axis_val,8:int(vert_front_val),9:int(vert_back_val),10:"",11:"",12:"",13:""}
        pin_dict = {4: left_axis_val, 5: right_axis_val, 6: left_axis_val, 7: right_axis_val, 8: int(
            vert_front_val), 9: "0", 10: int(vert_back_val), 11: "0", 12: "0", 13: "0"}
        # return left_axis_val,right_axis_val,int(vert_front_val),int(vert_back_val)
        output = ""
        for pin in pin_dict:
            output += f"{pin}:{pin_dict[pin]};"
        return output[:-1]
#     def write_string(self):
#         output = ""
#         for pin, var in  self.pin_dict:
#             output += f"{pin}:{var};"
#         return output

    def detect_event(self):
        for event in pygame.event.get():
            if event.type == pygame.JOYAXISMOTION:
                #print(event.dict, event.joy, event.axis, event.value)
                joystick = event.joy
                axis = event.axis
                value = event.value
                self.axis_dict[axis].update(axis, value)

                # print("JOYAXISMOTION","joystick",joystick,"axis",axis,"value",value)

#             elif event.type == pygame.JOYBALLMOTION:
#                 joystick = event.joy
#                 ball = event.ball
#                 rel = event.rel
#                 #print(event.dict, event.joy, event.ball, event.rel)
#                 print("JOYBALLMOTION","joystick",joystick,"ball",ball,"rel",rel)
            elif event.type == pygame.JOYBUTTONDOWN:
                # print("dict",self.buttons_dict[0])
                joystick = event.joy
                button = event.button
                pressed = 1
                print("JOYBUTTONDOWN", "joystick", joystick,
                      "button", button, "pressed", pressed)
                if button < 6:
                    self.buttons_dict[int(button)].update(1)

                #print(event.dict, event.joy, event.button, 'pressed')
#             elif event.type == pygame.JOYBUTTONUP:
#                 joystick = event.joy
#                 button = event.button
#                 pressed = 0
#                 print("JOYBUTTONUP","joystick",joystick,"button",button,"pressed",pressed)
                #print(event.dict, event.joy, event.button, 'released')
            elif event.type == pygame.JOYHATMOTION:
                joystick = event.joy
                hat = event.hat
                value = event.value
                print("JOYBUTTONUP", "joystick", joystick,
                      "hat", hat, "value", value)
                #print(event.dict, event.joy, event.hat, event.value)
            print(self.get_rov_input())

    def setup(self):
        pygame.joystick.init()
        joysticks = [pygame.joystick.Joystick(
            x) for x in range(pygame.joystick.get_count())]
        pygame.init()
        j = pygame.joystick.Joystick(0)
        j.init()


button3 = button(6)
button5 = button(7)
button6 = button(8)
buttonA = toggle(0)
buttonB = button(1)
buttonX = toggle(2)
buttonY = button(3)
axis1 = axis(0, 0)
axis4 = axis(0, 0)
lb = button(0)
rb = button(0)
lt = trigger(-1)
rt = trigger(-1)
hat2 = hat()
j1 = joystick(button3, button5, button6, buttonA, buttonB,
              buttonX, buttonY, axis1, axis4, hat, lb, rb, lt, rt)


j1.setup()


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
        if not x == old:
            s.send(str.encode(x))
            old = x

    # data = s.recv(1024)

# print(f"Received {data!r}")
