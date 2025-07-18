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
    BNO_REPORT_LINEAR_ACCELERATION,
    BNO_REPORT_GYROSCOPE,
    BNO_REPORT_MAGNETOMETER,
    BNO_REPORT_GAME_ROTATION_VECTOR,
)
from adafruit_bno08x.i2c import BNO08X_I2C
# from adafruit_bno08x.uart import BNO08X_UART

from common import utils

try:
    i2c = I2C(8)
    bno = BNO08X_I2C(i2c)

    # uart = busio.UART(board.TX, board.RX, baudrate=3000000, receiver_buffer_size=2048)
    # uart = serial.Serial("/dev/serial0", 115200)
    # bno = BNO08X_UART(uart)

    bno.enable_feature(BNO_REPORT_LINEAR_ACCELERATION)
    bno.enable_feature(BNO_REPORT_GYROSCOPE)
    bno.enable_feature(BNO_REPORT_MAGNETOMETER)
    bno.enable_feature(BNO_REPORT_GAME_ROTATION_VECTOR)
except Exception as e:
    raise RuntimeError("Could not initialize IMU")

HOST = "192.168.0.102"  # The server's hostname or IP address
PORT = 2049  # The port used by the server
CONTROL_LOOP_FREQ = 10  # Hz

# Global variables to store velocity
# These are initialized to 0 and will be updated in the read_data function
vel_x = 0.0
vel_y = 0.0
vel_z = 0.0

"""Reads data from the IMU sensor and returns as a dictionary.

Returns:
    dict: a dictionary of dictionaries, each one containing a set of data from the IMU
        (accelerometer, gyroscope, magnetometer, or quaternion)
"""
def read_data() -> dict:
    data = {}
    # acceleration
    accel_x, accel_y, accel_z = bno.linear_acceleration  # pylint:disable=no-member
    data["acceleration"] = utils.make_xyz_dict(accel_x, accel_y, accel_z)

    # velocity
    global vel_x, vel_y, vel_z
    vel_x = vel_x + accel_x / CONTROL_LOOP_FREQ
    vel_y = vel_y + accel_y / CONTROL_LOOP_FREQ
    vel_z = vel_z + accel_z / CONTROL_LOOP_FREQ
    data["velocity"] = utils.make_xyz_dict(vel_x, vel_y, vel_z)

    # gyro
    # gyro_x, gyro_y, gyro_z = bno.gyro  # pylint:disable=no-member
    # data["gyroscope"] = utils.make_xyz_dict(gyro_x, gyro_y, gyro_z)

    # magnetometer
    mag_x, mag_y, mag_z = bno.magnetic  # pylint:disable=no-member
    data["magnetometer"] = utils.make_xyz_dict(mag_x, mag_y, mag_z)

    # quaternion
    quat_i, quat_j, quat_k, quat_real = bno.game_quaternion  # pylint:disable=no-member
    quaternion = {}
    quaternion["i"] = quat_i
    quaternion["j"] = quat_j
    quaternion["k"] = quat_k
    quaternion["real"] = quat_real
    data["game_quaternion"] = quaternion

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
            
            s.send(str.encode(json.dumps(msg) + "~"))

            print(f"sent: {msg}")
        except RuntimeError as err:
            print(f"Fatal error: {err=}. Resetting.")
            bno.hard_reset()
            time.sleep(5)
        except BrokenPipeError:
            print("Connection closed.")
            break
        except Exception as err:
            print(f"Transient error: {err=}.")

        # sleep for remainder of loop
        if time.time() - last_time < 1 / CONTROL_LOOP_FREQ:
            time.sleep(1 / CONTROL_LOOP_FREQ - (time.time() - last_time))
        else:
            print("Warning: control loop took too long")
        last_time = time.time()
