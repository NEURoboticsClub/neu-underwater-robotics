import json
import os
import socket
import time

class Depth_Sensor :

    def read_depth():
        
        msg = {
            "Depth": 10000
        }
        return msg

   
           