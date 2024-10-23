# import time
# import json
# import socket

# from Adafruit_BNO055 import BNO055

# HOST = "192.168.0.112"  # The server's hostname or IP address
# PORT = 2049  # The port used by the server
# CONTROL_LOOP_FREQ = 100  # Hz

# bno = BNO055.BNO055(serial_port='/dev/serial0', rst=18)

# def read_data():
#     # Read the Euler angles for heading, roll, pitch (all in degrees).
#     heading, roll, pitch = bno.read_euler()
#     # Read the calibration status, 0=uncalibrated and 3=fully calibrated.
#     sys, gyro, accel, mag = bno.get_calibration_status()
#     # Print everything out.
#     return ('Heading: {0:0.2F} Roll: {1:0.2F} Pitch: {2:0.2F}\tSys_cal: {3} Gyro_cal: {4} Accel_cal: {5} Mag_cal: {6}'.format(
#           heading, roll, pitch, sys, gyro, accel, mag))
#     # Other values you can optionally read:
#     # Orientation as a quaternion:
#     #x,y,z,w = bno.read_quaterion()
#     # Sensor temperature in degrees Celsius:
#     #temp_c = bno.read_temp()
#     # Magnetometer data (in micro-Teslas):
#     #x,y,z = bno.read_magnetometer()
#     # Gyroscope data (in degrees per second):
#     #x,y,z = bno.read_gyroscope()
#     # Accelerometer data (in meters per second squared):
#     #x,y,z = bno.read_accelerometer()
#     # Linear acceleration data (i.e. acceleration from movement, not gravity--
#     # returned in meters per second squared):
#     #x,y,z = bno.read_linear_acceleration()
#     # Gravity acceleration data (i.e. acceleration just from gravity--returned
#     # in meters per second squared):
#     #x,y,z = bno.read_gravity()

# with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
#     print(f"connecting to {HOST}:{PORT}")
#     s.connect((HOST, PORT))
#     last_time = time.time()

#     # Initialize the BNO055 and stop if something went wrong.
#     if not bno.begin():
#         raise RuntimeError('Failed to initialize BNO055! Is the sensor connected?')
    
#     # Print out an error if system status is in error mode.
#     status, self_test, error = bno.get_system_status()
#     if status == 0x01:
#         print('System error: {0}'.format(error))
#         print('See datasheet section 4.3.59 for the meaning.')
        
#     while True:
#         data = read_data()
#         msg = {
#             "imu data": json.dumps(data.to_dict()),
#         }
#         s.send(str.encode(json.dumps(msg)))
#         print(f"sent: {msg}")

#         # sleep for remainder of loop
#         if time.time() - last_time < 1 / CONTROL_LOOP_FREQ:
#             time.sleep(1 / CONTROL_LOOP_FREQ - (time.time() - last_time))
#         else:
#             print("Warning: control loop took too long")
#         last_time = time.time()

# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

import time
import board
import adafruit_bno055


i2c = board.I2C()  # uses board.SCL and board.SDA
# i2c = board.STEMMA_I2C()  # For using the built-in STEMMA QT connector on a microcontroller
sensor = adafruit_bno055.BNO055_I2C(i2c)

# If you are going to use UART uncomment these lines
# uart = board.UART()
# sensor = adafruit_bno055.BNO055_UART(uart)

last_val = 0xFFFF


def temperature():
    global last_val  # pylint: disable=global-statement
    result = sensor.temperature
    if abs(result - last_val) == 128:
        result = sensor.temperature
        if abs(result - last_val) == 128:
            return 0b00111111 & result
    last_val = result
    return result


while True:
    print("Temperature: {} degrees C".format(sensor.temperature))
    """
    print(
        "Temperature: {} degrees C".format(temperature())
    )  # Uncomment if using a Raspberry Pi
    """
    print("Accelerometer (m/s^2): {}".format(sensor.acceleration))
    print("Magnetometer (microteslas): {}".format(sensor.magnetic))
    print("Gyroscope (rad/sec): {}".format(sensor.gyro))
    print("Euler angle: {}".format(sensor.euler))
    print("Quaternion: {}".format(sensor.quaternion))
    print("Linear acceleration (m/s^2): {}".format(sensor.linear_acceleration))
    print("Gravity (m/s^2): {}".format(sensor.gravity))
    print()

    time.sleep(1)
