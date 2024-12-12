import json
import os
import socket
import time

from joystick import XBoxDriveController

HOST = "192.168.0.102"  # The server's hostname or IP address
PORT = 2049  # The port used by the server
CONTROL_LOOP_FREQ = 100  # Hz

if os.environ.get("SIM"):
    print(f"{'='*10} SIMULATION MODE. Type YES to continue {'='*10}")
    if input() != "YES":
        raise RuntimeError("Simulation mode not confirmed")
    HOST = "127.0.0.1"

drive_controller = XBoxDriveController(joy_id=0, toggle_indices=[2])
claw_controller = XBoxDriveController(joy_id=1)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    print(f"connecting to {HOST}:{PORT}")
    s.connect((HOST, PORT))
    last_time = time.time()
    while True:
        vec = drive_controller.get_velocity_vector()
        claw_vec = claw_controller.get_claw_vector()
        msg = {
            "target_velocity": json.dumps(vec.to_dict()),
            "claw_movement": json.dumps(claw_vec),
        }
        s.send(str.encode(json.dumps(msg)))
        print(f"sent: {msg}")

        # sleep for remainder of loop
        if time.time() - last_time < 1 / CONTROL_LOOP_FREQ:
            time.sleep(1 / CONTROL_LOOP_FREQ - (time.time() - last_time))
        else:
            print("Warning: control loop took too long")
        last_time = time.time()
