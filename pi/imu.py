import time
import board
import busio
import adafruit_bno08x
from adafruit_bno08x.i2c import BNO08X_I2C
import json
import socket
from adafruit_bno08x import (
    BNO_REPORT_GAME_ROTATION_VECTOR,
    BNO_REPORT_LINEAR_ACCELERATION
)

HOST = "192.168.0.102"  # The server's hostname or IP address
PORT = 2049  # The port used by the server
CONTROL_LOOP_FREQ = 5  # Hz

# read acceleration and rotation
def read_data(sensor):
        data_dict = {}
        accel_x, accel_y, accel_z = sensor.linear_acceleration  # pylint:disable=no-member
        data_dict["acceleration"] = ("X: %0.6f  Y: %0.6f Z: %0.6f  m/s^2" % (accel_x, accel_y, accel_z))

        quat_i, quat_j, quat_k, quat_real = sensor.game_quaternion  # pylint:disable=no-member
        data_dict["rotation vector"] = (
            "I: %0.6f  J: %0.6f K: %0.6f  Real: %0.6f" % (quat_i, quat_j, quat_k, quat_real)
        )

        return data_dict

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    print(f"connecting to {HOST}:{PORT}")
    s.connect((HOST, PORT))
    last_time = time.time()
    # initialize sensor
    i2c = busio.I2C(board.SCL, board.SDA, frequency=400000)
    bno = BNO08X_I2C(i2c)

    # leave these in in case we switch to uart:
    # uart = serial.Serial("/dev/serial0", 115200)
    # uart = busio.UART(board.TX, board.RX, frequency=3000000, receiver_buffer_size=2048)

    bno.enable_feature(BNO_REPORT_GAME_ROTATION_VECTOR)
    bno.enable_feature(BNO_REPORT_LINEAR_ACCELERATION)

    while True:
        data = read_data(bno)

        # send to async server as json
        msg = json.dumps(data)
        s.send(str.encode(msg))
        print(f"sent: {msg}")

        # sleep for remainder of loop
        if time.time() - last_time < 1 / CONTROL_LOOP_FREQ:
            time.sleep(1 / CONTROL_LOOP_FREQ - (time.time() - last_time))
        else:
            print("Warning: control loop took too long")
        last_time = time.time()

