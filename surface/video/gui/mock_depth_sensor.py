import json
import os
import socket
import time

class Depth_Sensor :

    HOST = "192.168.0.102"  # The server's hostname or IP address
    PORT = 2049  # The port used by the server
    CONTROL_LOOP_FREQ = 100  # Hz

    # Print readings
    def read_depth(self, sensor):     
        msg = {
            "Depth": "100 Leagues Under The Sea"
        }
        return msg
           