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



STEPPERS = [Stepper(26, True, 28, 1, float(time.time())), \
            Stepper(36, True, 34, 1, float(time.time()))]  # list of pins that are used for steppers


for stepper in STEPPERS:
    pins[stepper.pin] = board.get_pin('d:'+str(stepper.pin)+':o')
    pins[stepper.direction_pin] = board.get_pin('d:'+str(stepper.direction_pin)+':o')



# myservo = board.get_pin('d:10:s')

HOST = "192.168.0.101"  # Standard loopback interface address (localhost)
PORT = 2049  # Port to listen on (non-privileged ports are > 1023)


def writeToArduino(pin: int, val: int):
    if pin in [s.pin for s in STEPPERS]:
        stepper = None
        for step in STEPPERS:
            if step.pin == pin:
                stepper = step
                break
        
        if stepper is None:
            raise Exception("error no stepper found")
        
        if val < 0 and stepper.direction:
            stepper.direction = False
            pins[stepper.direction_pin].write(1)
        elif val > 0 and not stepper.direction:
            stepper.direction = True
            pins[stepper.direction_pin].write(0)



        # pins[stepper.pin].write(1)
        # time.sleep(abs((1/val)/2))
        # pins[stepper.pin].write(0)
        # time.sleep(abs((1/val)/2))

        writeIfAble(stepper, val, pins)

    # myservo.write(val)
    # board.digital[pin].write(float(val))
    
def writeIfAble(stepper, val, pins):
    print(stepper, val, val > 2 or val < -2)
    if val > 2 or val < -2:
        rest_time = 0.1 / val
    
        if (stepper.lastTime < time.time() - rest_time):
            stepper.on = (stepper.on + 1) % 2
            pins[stepper.pin].write(stepper.on)
            print(time.time() - stepper.lastTime, stepper.on)
            stepper.lastTime = time.time()
    

def parseInput(msg):
    msg = msg.split("&")[0]
    if len(msg) > 0:
        ls = msg.split(';')
        for x in ls:
            if len(x) > 0:
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
        print(f'{data=}')
        parseInput(data.decode("utf-8"))
    s.shutdown(2)
    s.close()
    s = None
    print("Connection closed. Re-opening server")

# while True:
#     data = input()
#     while True:
#        parseInput(str(data))
