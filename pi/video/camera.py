import cv2


class Camera:
    def __init__(self):
        self.video = cv2.VideoCapture(
            'v4l2src device=/dev/video0 ! video/x-raw,width=1920,height=1080 ! videoconvert ! appsink', cv2.CAP_GSTREAMER)
    
    def get_frame(self):
        ret, image = self.video.read()
        ret, jpeg = cv2.imencode('.jpg', image)
        return jpeg.tobytes()
        