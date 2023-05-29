import time

from flask import Flask, render_template, Response

# from camera import Camera
from mock_camera import Camera

import random, threading, webbrowser

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

# camera = Camera(5600)

def gen(port):
    camera = Camera(port)
    time.sleep(1)
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed/<port>')
def video_feed(port):
    return Response(gen(port),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':

    #threading.Timer(1.25, lambda:webbrowser.open_new('http://0.0.0.0:5000/'))
    #app.run(host='0.0.0.0', use_reloader=False, debug=True)
    app.run(host='127.0.0.1', use_reloader=False, debug=True)
