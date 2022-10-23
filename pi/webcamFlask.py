from flask import Flask, render_template, Response
import cv2
import sys
import numpy
import base64
import time

class Cameras:
    cameras = []
    frames = []

    @classmethod
    def init_cams(cls):
        print(f'init_cams called')
        if cls.cameras:
            print(f'cameras already instantiated. Please use Cameras.clear_cams().')
            return
        for i in range(10):
            cam = cv2.VideoCapture(i)
            if cam is not None and cam.isOpened():
                print(f'added cam: {i}')
                cls.cameras.append(cam)
        print(f'total cams detected: {len(cls.cameras)}')
        cls.frames = []
        for c in cls.cameras:
            retval, im = c.read()
            cls.frames.append((time.time(), cv2.imencode('.jpg',im)[1].tostring()))
    
    @classmethod
    def clear_cams(cls):
        for c in cls.cameras:
            del c
    
    @classmethod
    def get_cam_frame(cls, cam_idx):
        if cls.frames[cam_idx][0] < time.time() - 0.017:
            retval, im = cls.cameras[cam_idx].read()
            if im is None:
                print(f'image empty')
            else:
                cls.frames[cam_idx] = (time.time(), cv2.imencode('.jpg',im)[1].tostring())
        
        return cls.frames[cam_idx][1]




app = Flask(__name__)

# def get_cams():
#     cams = []
#     for i in range(10):
#         cam = cv2.VideoCapture(i)
#         if cam is not None and cam.isOpened():
#             print(f'added cam: {i}')
#             cams.append(i)
#         del(cam)
#     print(f'total cams detected: {len(cams)}')
#     return cams

# camera_mapping = get_cams()

def get_frame(cam_idx):
    # cam = cv2.VideoCapture(cam_idx)
    # cam = Cameras.cameras[cam_idx]
    while True:
        # retval, im = cam.read()
        # imgencode=cv2.imencode('.jpg',im)[1]
        # stringData=imgencode.tostring()
        # yield f'<body><img src="data:image/jpg;base64, {str(stringData)[2:-1]}"</body>'
        yield (b'--frame\r\nContent-Type: text/plain\r\n\r\n'+Cameras.get_cam_frame(cam_idx)+b'\r\n')
    # del(cam)

@app.route('/vid/raw/<cam>')
def vid(cam):
    if not Cameras.cameras:
        Cameras.clear_cams()
        Cameras.init_cams()
    return Response(get_frame(int(cam)),mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/vid/view/<cam>')
def view(cam):
    return Response(f"<img src='/vid/raw/{cam}'>")

if __name__ == '__main__':
    app.run(host='192.168.0.101',port=5000, debug=True, threaded=True)