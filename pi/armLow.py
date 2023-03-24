from dataclasses import *
import socket
import pyfirmata
import time


# Initiate communication with Arduino
board = pyfirmata.ArduinoMega('/dev/ttyACM0')
print("Successfully connected to Arduino")

# Start iterator to receive input data
it = pyfirmata.util.Iterator(board)
it.start()

pins = {}

@dataclass
class Stepper(object):
    pin: int
    direction: bool
    direction_pin: int
    on: int
    lastTime: float



STEPPERS = [Stepper(26, True, 28, 1, float(time.time()))]  # list of pins that are used for steppers


for step in STEPPERS:
    pins[step.pin] = board.get_pin('d:'+str(step.pin)+':o')
    pins[step.direction_pin] = board.get_pin('d:'+str(step.direction_pin)+':o')
    


while True:
    step_pin = 26
    dir_pin = 28

    pins[step_pin].write(1)
    time.sleep(1/500)
    pins[step_pin].write(0)
    time.sleep(1/500)
