import time

from flask import Flask, render_template, Response

from camera import Camera

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
    app.run(host='0.0.0.0', use_reloader=False, debug=True)