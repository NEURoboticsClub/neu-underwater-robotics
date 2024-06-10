import time
import board
import busio
import adafruit_bno08x
from adafruit_bno08x.i2c import BNO08X_I2C
import json
import os
import socket
import serial
from adafruit_bno08x import (
    BNO_REPORT_ACCELEROMETER,
    BNO_REPORT_GYROSCOPE,
    BNO_REPORT_MAGNETOMETER,
    BNO_REPORT_ROTATION_VECTOR,
    BNO_REPORT_GAME_ROTATION_VECTOR,
    BNO_REPORT_LINEAR_ACCELERATION
)

HOST = "192.168.0.113"  # The server's hostname or IP address
PORT = 2049  # The port used by the server
CONTROL_LOOP_FREQ = 5  # Hz

# Print readings
def read_data(sensor):
        data_dict = {}
        accel_x, accel_y, accel_z = sensor.linear_acceleration  # pylint:disable=no-member
        data_dict["acceleration"] = ("X: %0.6f  Y: %0.6f Z: %0.6f  m/s^2" % (accel_x, accel_y, accel_z))

        # gyro_x, gyro_y, gyro_z = sensor.gyro  # pylint:disable=no-member
        # data_dict["gyro"] = ("X: %0.6f  Y: %0.6f Z: %0.6f rads/s" % (gyro_x, gyro_y, gyro_z))

        # mag_x, mag_y, mag_z = sensor.magnetic  # pylint:disable=no-member
        # data_dict["magnetometer"] = ("X: %0.6f  Y: %0.6f Z: %0.6f uT" % (mag_x, mag_y, mag_z))

        quat_i, quat_j, quat_k, quat_real = sensor.game_quaternion  # pylint:disable=no-member
        data_dict["rotation vector"] = (
            "I: %0.6f  J: %0.6f K: %0.6f  Real: %0.6f" % (quat_i, quat_j, quat_k, quat_real)
        )

        print(data_dict)
        return data_dict

def read_game(sensor):
        data_dict = {}
        

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    print(f"connecting to {HOST}:{PORT}")
    s.connect((HOST, PORT))
    last_time = time.time()
    i2c = busio.I2C(board.SCL, board.SDA, frequency=400000)
    # uart = serial.Serial("/dev/serial0", 115200)
    # uart = busio.UART(board.TX, board.RX, frequency=3000000, receiver_buffer_size=2048)
    bno = BNO08X_I2C(i2c)
    # bno.initialize()

    # while not (bno._calibration_complete and bno.get_calibration < 3):
    #     print("not yet")

    # bno.enable_feature(BNO_REPORT_ACCELEROMETER)
    # bno.enable_feature(BNO_REPORT_GYROSCOPE)
    # bno.enable_feature(BNO_REPORT_MAGNETOMETER)
    # bno.enable_feature(BNO_REPORT_ROTATION_VECTOR)
    bno.enable_feature(BNO_REPORT_GAME_ROTATION_VECTOR)
    bno.enable_feature(BNO_REPORT_LINEAR_ACCELERATION)

    print("features enabled")

    while True:
        # appends the newest depth to the depth list
        # pops off the oldest if there are enough values
        data = read_data(bno)

        msg = json.dumps(data)
        s.send(str.encode(msg))
        print(f"sent: {msg}")

        # sleep for remainder of loop
        if time.time() - last_time < 1 / CONTROL_LOOP_FREQ:
            time.sleep(1 / CONTROL_LOOP_FREQ - (time.time() - last_time))
        else:
            print("Warning: control loop took too long")
        last_time = time.time()

