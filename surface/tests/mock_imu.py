import math
import time
import json
import socket
import random

import numpy as np

HOST = "127.0.0.1"  # Use localhost for testing
PORT = 2049  # Same port as the GUI listener
CONTROL_LOOP_FREQ = 1  # Hz

"""
Mock IMU data emitter (in quaternions)
"""

r = -1
p = -1
y = 1
dx = 5

def generate_random_mock_data():
    """Generate random mock IMU data for testing."""
    data = {
        "rotation vector": f"I: {random.uniform(-1, 1):.2f}  "
                           f"J: {random.uniform(-1, 1):.2f}  "
                           f"K: {random.uniform(-1, 1):.2f}  "
                           f"Real: {random.uniform(-1, 1):.2f}",
        "acceleration": f"X: {random.uniform(-9.8, 9.8):.2f}  "
                        f"Y: {random.uniform(-9.8, 9.8):.2f}  "
                        f"Z: {random.uniform(-9.8, 9.8):.2f}"
    }
    return data

def generate_sliding_mock_data():
    """Generate sliding mock IMU data for testing."""
    global r, p, y, dx  
    r_rad = r*math.pi/180
    p_rad = p*math.pi/180
    y_rad = y*math.pi/180
    i, j, k, real = euler_to_quaternion(r_rad, p_rad, y_rad)

    if p == 89:
        dx = -dx
    if r == -1:
        p += dx
    if r == 89:
        dx = -dx
    if p == -1:
        r += dx


    data = {
        "rotation vector": f"I:    {i:.2f}  "
                           f"J:    {j:.2f}  "
                           f"K:    {k:.2f}  "
                           f"Real: {real:.2f}",
        "acceleration": f"X: {random.uniform(-9.8, 9.8):.2f}  "
                        f"Y: {random.uniform(-9.8, 9.8):.2f}  "
                        f"Z: {random.uniform(-9.8, 9.8):.2f}"
    }
    return data

def euler_to_quaternion(roll, pitch, yaw):

        qx = np.sin(roll/2) * np.cos(pitch/2) * np.cos(yaw/2) - np.cos(roll/2) * np.sin(pitch/2) * np.sin(yaw/2)
        qy = np.cos(roll/2) * np.sin(pitch/2) * np.cos(yaw/2) + np.sin(roll/2) * np.cos(pitch/2) * np.sin(yaw/2)
        qz = np.cos(roll/2) * np.cos(pitch/2) * np.sin(yaw/2) - np.sin(roll/2) * np.sin(pitch/2) * np.cos(yaw/2)
        qw = np.cos(roll/2) * np.cos(pitch/2) * np.cos(yaw/2) + np.sin(roll/2) * np.sin(pitch/2) * np.sin(yaw/2)

        return [qx, qy, qz, qw]

def run_mock_imu():
    """Run a mock IMU server that sends data over a socket."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen(1)
        print(f"Mock IMU listening on {HOST}:{PORT}")
        conn, addr = s.accept()
        print(f"Connection established with {addr}")

        last_time = time.time()
        try:
            while True:
                # Generate and send mock data
                data = generate_sliding_mock_data()
                msg = json.dumps(data)
                conn.sendall(msg.encode('utf-8'))
                print(f"Sent: {msg}")

                # Sleep to maintain CONTROL_LOOP_FREQ
                elapsed = time.time() - last_time
                sleep_time = max(1 / CONTROL_LOOP_FREQ - elapsed, 0)
                time.sleep(sleep_time)
                last_time = time.time()
        except (BrokenPipeError, ConnectionResetError):
            print("Connection closed.")
        except KeyboardInterrupt:
            print("Mock IMU server stopped.")

def main():
    """Main function to run the mock IMU server."""
    run_mock_imu()

if __name__ == "__main__":
    main()
