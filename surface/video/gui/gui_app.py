from asyncio import SendfileNotAvailableError
from asyncio.constants import _SendfileMode
from io import BytesIO
from flask import Flask, render_template, send_file, Response
from mock_camera import Camera  # Assuming your Camera class is defined in a file named camera.py
from PIL import Image
import io
from mock_depth_sensor import Depth_Sensor

app = Flask(__name__)

camera = Camera(port=8080)  # Adjust the port as needed


# sends camera bytes as a file 
@app.route('/image_route')
def image_route():
	return send_file(BytesIO(camera.get_frame()), mimetype='video/mp4')

@app.route('/')
def split_view() :
	depth_sensor = Depth_Sensor
	depth = depth_sensor.read_depth()
	return render_template('split_view.html', data=depth)


@app.route('/single_view/<int:camera_id>')
def single_view(camera_id):
	return render_template('single_view.html')

@app.route('/depth_route')
def depth_route() :
	depth_sensor = Depth_Sensor
	depth = depth_sensor.read_depth()
	print(depth)
	return render_template('split_view.html', data=depth)


if __name__ == '__main__':
    app.run(debug=True)

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

