from flask import Flask, render_template, Response
import cv2
import sys
import numpy
import base64

app = Flask(__name__)

def get_cams():
    cams = []
    for i in range(10):
        cam = cv2.VideoCapture(i)
        if cam is not None and cam.isOpened():
            print(f'added cam: {i}')
            cams.append(i)
        del(cam)
    print(f'total cams detected: {len(cams)}')
    return cams

camera_mapping = get_cams()

def get_frame(cam_idx):
    cam = cv2.VideoCapture(cam_idx)
    while True:
        retval, im = cam.read()
        imgencode=cv2.imencode('.jpg',im)[1]
        stringData=imgencode.tostring()
        # yield f'<body><img src="data:image/jpg;base64, {str(stringData)[2:-1]}"</body>'
        yield (b'--frame\r\nContent-Type: text/plain\r\n\r\n'+stringData+b'\r\n')
    # del(cam)

@app.route('/vid/raw/<cam>')
def vid(cam):
    return Response(get_frame(camera_mapping[int(cam)]),mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/vid/view/<cam>')
def view(cam):
    return Response(f"<img src='/vid/raw/{cam}'>")

if __name__ == '__main__':
    app.run(host='192.168.0.101',port=5000, debug=True, threaded=True)