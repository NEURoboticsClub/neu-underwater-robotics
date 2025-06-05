import ms5837
import json
import os
import socket
import time

HOST = "192.168.0.102"  # The server's hostname or IP address
PORT = 2049  # The port used by the server
CONTROL_LOOP_FREQ = 10  # Hz

# Print readings
def read_depth(sensor):        
        if sensor.read():
                print(("P: %0.1f mbar  %0.3f psi\tDepth: %0.3f\tT: %0.2f C  %0.2f F") % (
                sensor.pressure(), # Default is mbar (no arguments)
                sensor.pressure(ms5837.UNITS_psi), # Request psi
                sensor.depth(),
                sensor.temperature(), # Default is degrees C (no arguments)
                sensor.temperature(ms5837.UNITS_Farenheit))) # Request Farenheit
                return sensor.depth()
        else:
                print("Sensor read failed!")
                exit(1)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    print(f"connecting to {HOST}:{PORT}")
    s.connect((HOST, PORT))
    last_time = time.time()
    sensor = ms5837.MS5837_02BA() # Default I2C bus is 1 (Raspberry Pi 3)

    # We must initialize the sensor before reading it
    if not sensor.init():
        print("Sensor could not be initialized")
        exit(1)

    # TODO: Rewrite this to standard
    # store target height as a variable
    # come up with target velocity based on current velocity, 
    # target height and target depth
    # hardcode velocity scalar proportional to where we are and
    # where we want to be, in rov_state.py
    # might have to store a couple of depth values
    # pop off end and stack with list- queue, need to be able to 
    # average the whole thing
    # init param! 
    # send over to rov_state, rov_state only has the height setpoint
    # get vector down from top, pick some scalar (whatever speaks to you emotionally)
    # change it by that much based on the message you get

    depth_list = []
    depth_list_length = 10

    while True:
        # appends the newest depth to the depth list
        # pops off the oldest if there are enough values
        depth = read_depth(sensor)
        depth_list.append(depth)
        if len(depth_list) >= depth_list_length:
            depth_list.pop(0)

        msg = {
            "depth": json.dumps(depth_list),
        }
        s.send(str.encode(json.dumps(msg)))
        print(f"sent: {msg}")

        # sleep for remainder of loop
        if time.time() - last_time < 1 / CONTROL_LOOP_FREQ:
            time.sleep(1 / CONTROL_LOOP_FREQ - (time.time() - last_time))
        else:
            print("Warning: control loop took too long")
        last_time = time.time()
