# SPDX-FileCopyrightText: 2020 Bryan Siepert, written for Adafruit Industries
#
# SPDX-License-Identifier: Unlicense
import time
import board
import busio
import json
import socket

from adafruit_bno08x import (
    BNO_REPORT_ACCELEROMETER,
    BNO_REPORT_GYROSCOPE,
    BNO_REPORT_MAGNETOMETER,
    BNO_REPORT_ROTATION_VECTOR,
)
from adafruit_bno08x.i2c import BNO08X_I2C

try:
    i2c = busio.I2C(board.SCL, board.SDA, frequency=400000)
    bno = BNO08X_I2C(i2c)

    bno.enable_feature(BNO_REPORT_ACCELEROMETER)
    bno.enable_feature(BNO_REPORT_GYROSCOPE)
    bno.enable_feature(BNO_REPORT_MAGNETOMETER)
    bno.enable_feature(BNO_REPORT_ROTATION_VECTOR)
except Exception as e:
    raise RuntimeError("Could not initialize IMU")

HOST = "192.168.0.113"  # The server's hostname or IP address
PORT = 2049  # The port used by the server
CONTROL_LOOP_FREQ = 100  # Hz

def read_data() -> dict:
    data = {}
    # acceleration
    accel_x, accel_y, accel_z = bno.acceleration  # pylint:disable=no-member
    acceleration = {}
    acceleration["x"] = accel_x
    acceleration["y"] = accel_y
    acceleration["z"] = accel_z
    data["acceleration"] = acceleration

    # gyro
    gyro_x, gyro_y, gyro_z = bno.gyro  # pylint:disable=no-member
    gyroscope = {}
    gyroscope["x"] = gyro_x
    gyroscope["y"] = gyro_y
    gyroscope["z"] = gyro_z
    data["gyroscope"] = gyroscope

    # magnetometer
    mag_x, mag_y, mag_z = bno.magnetic  # pylint:disable=no-member
    magnetometer = {}
    magnetometer["x"] = mag_x
    magnetometer["y"] = mag_y
    magnetometer["z"] = mag_z
    data["magnetometer"] = magnetometer

    # quaternion
    quat_i, quat_j, quat_k, quat_real = bno.quaternion  # pylint:disable=no-member
    quaternion = {}
    quaternion["i"] = quat_i
    quaternion["j"] = quat_j
    quaternion["k"] = quat_k
    quaternion["real"] = quat_real
    data["quaternion"] = quaternion

    return data

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    print(f"connecting to {HOST}:{PORT}")
    s.connect((HOST, PORT))
    last_time = time.time()
    
    while True:
        data = read_data()
        msg = {
            "imu_data": json.dumps(data),
        }
        s.send(str.encode(json.dumps(msg)))

        print(f"sent: {msg}")

        # sleep for remainder of loop
        if time.time() - last_time < 1 / CONTROL_LOOP_FREQ:
            time.sleep(1 / CONTROL_LOOP_FREQ - (time.time() - last_time))
        else:
            print("Warning: control loop took too long")
        last_time = time.time()