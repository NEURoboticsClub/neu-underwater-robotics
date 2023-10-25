import json
import socket
import time

from joystick import XBoxDriveController

HOST = "192.168.0.102"  # The server's hostname or IP address
PORT = 2049  # The port used by the server
CONTROL_LOOP_FREQ = 100  # Hz

drive_controller = XBoxDriveController(joy_id=0)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    print(f"connecting to {HOST}:{PORT}")
    last_time = time.time()
    while True:
        vec = drive_controller.get_velocity_vector()
        msg = json.dumps(
            {
                "target_velocity": json.dumps(vec.__dict__),
            }
        )
        s.send(str.encode(msg))
        print(f"sent: {msg}")

        # sleep for remainder of loop
        time.sleep(1 / CONTROL_LOOP_FREQ - (time.time() - last_time))
        last_time = time.time()
