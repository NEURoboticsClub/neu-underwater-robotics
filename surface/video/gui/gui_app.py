from flask import Flask, render_template,  Response
from camera import Camera  # Assuming your Camera class is defined in a file named camera.py
from mock_depth_sensor import Depth_Sensor
from PIL import Image
import io
import json


app = Flask(__name__)

depth_sensor = Depth_Sensor()
camera1 = Camera(port=5600)  # Adjust the port as needed
camera2 = Camera(port=5601)
camera3 = Camera(port=5602)
camera4 = Camera(port=5603)


def genImg(camera_id):
    while True:
       if camera_id == 5600 :
        frame = camera1.get_frame()
       elif camera_id == 5601:
        frame = camera2.get_frame()
       elif camera_id == 5602: 
         frame = camera3.get_frame()
       else :
        frame = camera4.get_frame()
       yield (b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n")

# sends camera bytes as a file 
@app.route('/image_route<int:camera_id>')
def image_route(camera_id):
    return Response(genImg(camera_id), mimetype="multipart/x-mixed-replace; boundary=frame")

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
	return render_template('single_view.html', {"camera_id": camera_id})



if __name__ == '__main__':
    app.run(host="0.0.0.0", port=3000, debug=False)


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

