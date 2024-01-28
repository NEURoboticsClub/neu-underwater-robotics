from asyncio import SendfileNotAvailableError
from asyncio.constants import _SendfileMode
from io import BytesIO
from flask import Flask, render_template, Response
from mock_camera import Camera  # Assuming your Camera class is defined in a file named camera.py

app = Flask(__name__)

camera = Camera(port=8080)  # Adjust the port as needed


@app.route('/')
def index():
    return render_template('split_view.html')

def generate_frame():
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frame(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/image_route')
def image_route():
    frame = camera.get_frame()
    return _SendfileMode(BytesIO(frame), mimetype='image/jpeg')

@app.route('/')
def split_view():
	return render_template('split_view.html')

@app.route('/single_view/<int:camera_id>')
def single_view(camera_id):
	return render_template('single_view.html')


if __name__ == '__main__':
    app.run(debug=True)