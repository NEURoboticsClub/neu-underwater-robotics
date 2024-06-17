import io
import json
import math
import random
from asyncio import SendfileNotAvailableError
from asyncio.constants import _SendfileMode
from io import BytesIO

from camera import Camera  # Assuming your Camera class is defined in a file named camera.py
from flask import Flask, Response, render_template
from mock_depth_sensor import Depth_Sensor
from PIL import Image

app = Flask(__name__)

depth_sensor = Depth_Sensor()
cameras = {
    1: Camera(port=5600),
    2: Camera(port=5601),
}


def genImg(camera_id):
    while True:
        frame = cameras.get(camera_id).get_frame()
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
        return {"pitch": pitch, "roll": roll, "yaw": yaw}


@app.route("/arthoriz_route")
def arthoriz_route():
    return genArtHoriz()


# sends camera bytes as a file
@app.route("/image_route/<int:camera_id>")
def image_route(camera_id):
    return Response(genImg(camera_id), mimetype="multipart/x-mixed-replace; boundary=frame")


def genDepth(temp):
    while True:
        yield f"data: {temp}\n\n"


@app.route("/depth_route/<temp>", methods=['POST'])
def depth_route(temp):
    form_data = request.form.get('temp')
    processed_data = f"Processed data: {form_data}"
    return render_template('split_view.html', path_variable=temp, processed_data=processed_data)


@app.route("/")
def split_view():
    return render_template("split_view.html")


@app.route("/single_view/<int:camera_id>")
def single_view(camera_id):
    return render_template("single_view.html", camera_id=camera_id)


if __name__ == "__main__":
    app.run(host="localhost", port=3000, debug=False)


# sends camera bytes as a file
# @app.route('/image_route')
# def image_route():
# while True:
# frame = camera.get_frame()
# yield (b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n")

# @app.route('/')
# def index():
# return render_template('split_view.html')


# def generate_frame():
# while True:
# frame = camera.get_frame()
# yield (b'--frame\r\n'
# b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


# @app.route('/video_feed')
# def video_feed():
# return Response(generate_frame(),
# mimetype='multipart/x-mixed-replace; boundary=frame')
