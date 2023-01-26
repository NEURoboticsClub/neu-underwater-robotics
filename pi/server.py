from dataclasses import *
import socket
import pyfirmata
from time import sleep


# Initiate communication with Arduino
board = pyfirmata.ArduinoMega('/dev/ttyACM0')
print("Successfully connected to Arduino")

# Start iterator to receive input data
it = pyfirmata.util.Iterator(board)
it.start()

pins = []
pins.append('')
pins.append('')


@dataclass
class Stepper(object):
    pin: int
    direction: bool
    direction_pin: int


STEPPERS = [Stepper(2, True, 3)]  # list of pins that are used for steppers


for x in range(2, 14):
    pins.append(board.get_pin('d:'+str(x)+':s'))


# myservo = board.get_pin('d:10:s')

HOST = "192.168.0.101"  # Standard loopback interface address (localhost)
PORT = 2049  # Port to listen on (non-privileged ports are > 1023)


def writeToArduino(pin: int, val: int):
    if pin in [s.pin for s in STEPPERS]:
        stepper = filter(lambda x: x.pin == pin, STEPPERS)
        # stepper
        if val < 0 and stepper.direction:
            stepper.direction = False
            pins[stepper.direction_pin].write(1)
        elif val > 0 and not stepper.direction:
            stepper.direction = True
            pins[stepper.direction_pin].write(1)

        pins[stepper.pin].write(1)
        sleep(abs((1/val)/2))
        pins[stepper.pin].write(0)
        sleep(abs((1/val)/2))

        pins[stepper.direction_pin].write(0)

    # myservo.write(val)
    # board.digital[pin].write(float(val))
    pins[pin].write(val)


def parseInput(msg):
    ls = msg.split(';')
    for x in ls:
        writeToArduino(int(x.split(':')[0]), int(x.split(':')[1]))


while True:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    print(
        f"Ready to accept connection. Please start client.py {HOST=} {PORT=}")
    s.listen(5)
    conn, addr = s.accept()
    print(f"Connected by {addr}")
    while True:
        data = conn.recv(1024)
        if len(data) == 0:
            break
        print(f'{data=}')
        parseInput(data.decode("utf-8"))
    s.shutdown(2)
    s.close()
    s = None
    print("Connection closed. Re-opening server")
