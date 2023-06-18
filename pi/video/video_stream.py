import time

from flask import Flask, render_template, Response

from io import BytesIO
from base64 import b64encode
from PIL import Image

from camera import Camera
# from mock_camera import Camera

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


INDEX_TO_DEVICE = {
    "0": "0",  # /dev/video0
    "1": "4",  # /dev/video4
}

cameras = {
    "0": Camera(INDEX_TO_DEVICE.get("0")),
    "1": Camera(INDEX_TO_DEVICE.get("1")),
}


def gen(index):
    camera = cameras.get(str(index))
    while True:
        frame = camera.get_frame()
        yield (b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n")


@app.route("/raw_frame/<index>")
def raw_frame(index):
    camera = cameras.get(str(index))
    img = Image.open(BytesIO(camera.get_frame()))
    image_io = BytesIO()
    img.save(image_io, 'PNG')
    dataurl = 'data:image/png;base64,' + b64encode(image_io.getvalue()).decode('ascii')
    return render_template('image.html', image_data=dataurl)


@app.route("/video_feed/<index>")
def video_feed(index):
    return Response(gen(index), mimetype="multipart/x-mixed-replace; boundary=frame")


if __name__ == "__main__":
    app.run(host="0.0.0.0", use_reloader=False, debug=True, port=9000)
