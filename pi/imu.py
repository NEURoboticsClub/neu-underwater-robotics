# SPDX-FileCopyrightText: 2020 Bryan Siepert, written for Adafruit Industries
#
# SPDX-License-Identifier: Unlicense
import time
import board
import busio
import json
import socket
from adafruit_extended_bus import ExtendedI2C as I2C
# import serial

from adafruit_bno08x import (
    BNO_REPORT_ACCELEROMETER,
    BNO_REPORT_GYROSCOPE,
    BNO_REPORT_MAGNETOMETER,
    BNO_REPORT_ROTATION_VECTOR,
)
from adafruit_bno08x.i2c import BNO08X_I2C
# from adafruit_bno08x.uart import BNO08X_UART

try:
    i2c = I2C(8)
    bno = BNO08X_I2C(i2c)

    # uart = busio.UART(board.TX, board.RX, baudrate=3000000, receiver_buffer_size=2048)
    # uart = serial.Serial("/dev/serial0", 115200)
    # bno = BNO08X_UART(uart)

    bno.enable_feature(BNO_REPORT_ACCELEROMETER)
    bno.enable_feature(BNO_REPORT_GYROSCOPE)
    bno.enable_feature(BNO_REPORT_MAGNETOMETER)
    bno.enable_feature(BNO_REPORT_ROTATION_VECTOR)
except Exception as e:
    raise RuntimeError("Could not initialize IMU")

HOST = "192.168.0.102"  # The server's hostname or IP address
PORT = 2049  # The port used by the server
CONTROL_LOOP_FREQ = 4  # Hz

"""Creates a dictionary with the given x, y, and z arguments.

Args:
    x: the value to set dict["x"] to
    y: the value to set dict["y"] to
    z: the value to set dict["z"] to

Returns:
    dict: a dictionary with the given values as "x", "y", and "z"
"""
def make_xyz_dict(x, y, z) -> dict:
    diction = {}
    diction["x"] = x
    diction["y"] = y
    diction["z"] = z

    return diction

"""Reads data from the IMU sensor and returns as a dictionary.

Returns:
    dict: a dictionary of dictionaries, each one containing a set of data from the IMU
        (accelerometer, gyroscope, magnetometer, or quaternion)
"""
def read_data() -> dict:
    data = {}
    # acceleration
    accel_x, accel_y, accel_z = bno.acceleration  # pylint:disable=no-member
    data["acceleration"] = make_xyz_dict(accel_x, accel_y, accel_z)

    # gyro
    gyro_x, gyro_y, gyro_z = bno.gyro  # pylint:disable=no-member
    data["gyroscope"] = make_xyz_dict(gyro_x, gyro_y, gyro_z)

    # magnetometer
    mag_x, mag_y, mag_z = bno.magnetic  # pylint:disable=no-member
    data["magnetometer"] = make_xyz_dict(mag_x, mag_y, mag_z)

    # quaternion
    quat_i, quat_j, quat_k, quat_real = bno.quaternion  # pylint:disable=no-member
    quaternion = {}
    quaternion["i"] = quat_i
    quaternion["j"] = quat_j
    quaternion["k"] = quat_k
    quaternion["real"] = quat_real
    data["quaternion"] = quaternion

    return data

"""
Starts the client. Connects to async_server, then reads and
publishes IMU data to the server at the rate defined above until manually terminated.
"""
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    print(f"connecting to {HOST}:{PORT}")
    s.connect((HOST, PORT))
    last_time = time.time()
    
    while True:
        try:
            data = read_data()
            msg = {
                "imu_data": json.dumps(data),
            }
            
            s.send(str.encode(json.dumps(msg)))

            print(f"sent: {msg}")
        except RuntimeError as err:
            print(f"Fatal error: {err=}. Resetting.")
            bno.hard_reset()
            time.sleep(5)
        except Exception as err:
            print(f"Transient error: {err=}.")

        # sleep for remainder of loop
        if time.time() - last_time < 1 / CONTROL_LOOP_FREQ:
            time.sleep(1 / CONTROL_LOOP_FREQ - (time.time() - last_time))
        else:
            print("Warning: control loop took too long")
        last_time = time.time()
