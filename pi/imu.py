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
            "imu data": json.dumps(data),
        }
        s.send(str.encode(json.dumps(msg)))
        print(f"sent: {msg}")

        # sleep for remainder of loop
        if time.time() - last_time < 1 / CONTROL_LOOP_FREQ:
            time.sleep(1 / CONTROL_LOOP_FREQ - (time.time() - last_time))
        else:
            print("Warning: control loop took too long")
        last_time = time.time()


# import time
# import board
# import adafruit_bno055


# i2c = board.I2C()  # uses board.SCL and board.SDA
# # i2c = board.STEMMA_I2C()  # For using the built-in STEMMA QT connector on a microcontroller
# sensor = adafruit_bno055.BNO055_I2C(i2c)

# # If you are going to use UART uncomment these lines
# # uart = board.UART()
# # sensor = adafruit_bno055.BNO055_UART(uart)

# last_val = 0xFFFF


# def temperature():
#     global last_val  # pylint: disable=global-statement
#     result = sensor.temperature
#     if abs(result - last_val) == 128:
#         result = sensor.temperature
#         if abs(result - last_val) == 128:
#             return 0b00111111 & result
#     last_val = result
#     return result


# while True:
#     print("Temperature: {} degrees C".format(sensor.temperature))
#     """
#     print(
#         "Temperature: {} degrees C".format(temperature())
#     )  # Uncomment if using a Raspberry Pi
#     """
#     print("Accelerometer (m/s^2): {}".format(sensor.acceleration))
#     print("Magnetometer (microteslas): {}".format(sensor.magnetic))
#     print("Gyroscope (rad/sec): {}".format(sensor.gyro))
#     print("Euler angle: {}".format(sensor.euler))
#     print("Quaternion: {}".format(sensor.quaternion))
#     print("Linear acceleration (m/s^2): {}".format(sensor.linear_acceleration))
#     print("Gravity (m/s^2): {}".format(sensor.gravity))
#     print()

#     time.sleep(1)
