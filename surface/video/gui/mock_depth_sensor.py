import json
import os
import socket
import time

class Depth_Sensor :

    def __init__(self):
        
        self.whichDepth = True

        self.depth1 = {"Depth": 99999}
        self.depth2 = {"Depth": 00000}

    def read_depth(self):

         if self.whichDepth:
             self.whichDepth = not self.whichDepth
             return json.dumps(self.depth1)
         else:
             self.whichDepth = not self.whichDepth
             return json.dumps(self.depth2)

        
        
   
           