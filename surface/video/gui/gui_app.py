from asyncio import SendfileNotAvailableError
from asyncio.constants import _SendfileMode
from io import BytesIO
import math
from flask import Flask, render_template, Response
from mock_camera import Camera  # Assuming your Camera class is defined in a file named camera.py
from mock_depth_sensor import Depth_Sensor
from PIL import Image
import io
import json
import random


app = Flask(__name__)

depth_sensor = Depth_Sensor()
camera = Camera(port=8080)  # Adjust the port as needed

def genImg():
    while True:
       frame = camera.get_frame()
       yield (b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n")

# def genArtHoriz():
#     while True:
#         pitch = 50
#         yield f"data: {pitch}\n\n"
            
# @app.route('/arthoriz_route')
# def arthoriz_route():
#     return Response(genArtHoriz(), mimetype='text/event-stream')

def genArtHoriz():
    while True:

        pitchCoeff = random.randrange(20, 70)
        pitchDeg = random.randrange(20, 70)

        rollCoeff = random.randrange(20, 70)
        rollDeg = random.randrange(20, 70)

        yawCoeff = random.randrange(20, 70)
        yawDeg = random.randrange(20, 70)

        pitch = pitchCoeff * math.sin(pitchDeg) 
        roll = rollCoeff * math.sin(rollDeg)  
        yaw = yawCoeff * math.sin(yawDeg)
        return {'pitch': pitch, 'roll': roll, 'yaw': yaw}

@app.route('/arthoriz_route')
def arthoriz_route():
    return genArtHoriz()


# sends camera bytes as a file 
@app.route('/image_route')
def image_route():
    return Response(genImg(), mimetype="multipart/x-mixed-replace; boundary=frame")

def genDepth():
    while True:
       depth = depth_sensor.read_depth()
       yield f"data: {depth}\n\n"

@app.route('/depth_route')
def depth_route() :
	return Response(genDepth(), mimetype='text/event-stream')

@app.route('/')
def split_view() :
	return render_template('split_view.html')

@app.route('/single_view/<int:camera_id>')
def single_view(camera_id):
	return render_template('single_view.html')



if __name__ == '__main__':
    app.run(host="localhost", port=3000, debug=False)


# sends camera bytes as a file 
#@app.route('/image_route')
#def image_route():
   # while True:
       # frame = camera.get_frame()
       #yield (b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n")

#@app.route('/')
#def index():
    #return render_template('split_view.html')


#def generate_frame():
    #while True:
       # frame = camera.get_frame()
       # yield (b'--frame\r\n'
              # b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


#@app.route('/video_feed')
#def video_feed():
   # return Response(generate_frame(),
                    #mimetype='multipart/x-mixed-replace; boundary=frame')

