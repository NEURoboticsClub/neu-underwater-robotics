import ms5837
import json
import os
import socket
import time

HOST = "192.168.0.102"  # The server's hostname or IP address
PORT = 2049  # The port used by the server
CONTROL_LOOP_FREQ = 100  # Hz

# Print readings
def read_depth(self, sensor):        
        if sensor.read():
                print(("P: %0.1f mbar  %0.3f psi\tT: %0.2f C  %0.2f F") % (
                sensor.pressure(), # Default is mbar (no arguments)
                sensor.pressure(ms5837.UNITS_psi), # Request psi
                sensor.temperature(), # Default is degrees C (no arguments)
                sensor.temperature(ms5837.UNITS_Farenheit))) # Request Farenheit
        else:
                print("Sensor read failed!")
                exit(1)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    print(f"connecting to {HOST}:{PORT}")
    s.connect((HOST, PORT))
    last_time = time.time()
    sensor = ms5837.MS5837_02BA(21) # Default I2C bus is 1 (Raspberry Pi 3)

    # We must initialize the sensor before reading it
    if not sensor.init():
        print("Sensor could not be initialized")
        exit(1)
        
    while True:
        depth = read_depth(sensor)
        msg = {
            "depth": json.dumps(depth.to_dict()),
        }
        s.send(str.encode(json.dumps(msg)))
        print(f"sent: {msg}")

        # sleep for remainder of loop
        if time.time() - last_time < 1 / CONTROL_LOOP_FREQ:
            time.sleep(1 / CONTROL_LOOP_FREQ - (time.time() - last_time))
        else:
            print("Warning: control loop took too long")
        last_time = time.time()