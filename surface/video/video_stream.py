import time

from flask import Flask, render_template, Response

# from camera import Camera
from mock_camera import Camera

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


cameras = {
    "5600": Camera(5600),
    "5601": Camera(5601),
}


def gen(port):
    camera = cameras.get(str(port))
    time.sleep(1)
    while True:
        frame = camera.get_frame()
        yield (b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n")


@app.route("/raw_frame/<port>")
def raw_frame(port):
    camera = cameras.get(str(port))
    return Response(camera.get_frame())


@app.route("/video_feed/<port>")
def video_feed(port):
    return Response(gen(port), mimetype="multipart/x-mixed-replace; boundary=frame")


if __name__ == "__main__":
    app.run(host="0.0.0.0", use_reloader=False, debug=True)
