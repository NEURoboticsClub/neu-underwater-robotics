# To be deprecated in favour of PyQt5.
# Features yet to be moved out:
# - Show continuous video data.
# - Start/stop saving of video data streaming in from one particular port.
#   - When is_saving is true, every frame is saved as an image in the Images folder.
#   - Maybe better to just save as a video?
# - Save one frame to an image file.

import time

from flask import Flask, render_template, Response, redirect, url_for #hosts webserver on localhost

from io import BytesIO
from base64 import b64encode
from PIL import Image

from camera import Camera
# from mock_camera import Camera

app = Flask(__name__)

cameras = {
    "5600": Camera(5600),
    "5601": Camera(5601),
}

PORT_TO_SAVE = 5600

# ImageData. To be used as as the src field of the <image> tag.
SAVED_FRAME = None

@app.route("/")
def index():
    if SAVED_FRAME is not None:
        return render_template("index.html", is_saving=cameras.get(str(PORT_TO_SAVE)).is_saving, image_data=SAVED_FRAME)
    return render_template("index.html", is_saving=cameras.get(str(PORT_TO_SAVE)).is_saving)

def gen(port, crop=False): ## python generator (only calculated when needed)- gets a frame and puts in html tag
    global counter
    camera = cameras.get(str(port))
    while True:
        if not crop:
            frame = camera.get_frame()
        else:
            frame = camera.get_cropped_frame()
        yield (b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n")


@app.route("/raw_frame/<port>")
def raw_frame(port): ## save as jpeg then open and save as png on webpage
    camera = cameras.get(str(port))
    img = Image.open(BytesIO(camera.get_frame()))
    image_io = BytesIO()
    img.save(image_io, 'PNG')
    dataurl = 'data:image/png;base64,' + b64encode(image_io.getvalue()).decode('ascii')
    return render_template('image.html', image_data=dataurl)

@app.route("/start_saving")
def start_saving(): 
    camera = cameras.get(str(PORT_TO_SAVE))
    camera.start_saving()
    return redirect(url_for('index'))

@app.route("/stop_saving")
def stop_saving():
    camera = cameras.get(str(PORT_TO_SAVE))
    camera.stop_saving()
    return redirect(url_for('index'))

@app.route("/video_feed/<port>")
def video_feed(port): ## gen response here
    return Response(gen(port), mimetype="multipart/x-mixed-replace; boundary=frame")

@app.route("/cropped_video_feed/<port>")
def cropped_video_feed(port):
    return Response(gen(port, crop=True), mimetype="multipart/x-mixed-replace; boundary=frame")

@app.route("/save_frame")
def save_frame(): ## saving images for photogrammetry
    global SAVED_FRAME
    camera = cameras.get(str(PORT_TO_SAVE))
    img = Image.open(BytesIO(camera.get_frame()))
    image_io = BytesIO()
    img.save(image_io, 'PNG')
    dataurl = 'data:image/png;base64,' + b64encode(image_io.getvalue()).decode('ascii')
    SAVED_FRAME = dataurl
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(host="0.0.0.0", use_reloader=False, debug=True)
