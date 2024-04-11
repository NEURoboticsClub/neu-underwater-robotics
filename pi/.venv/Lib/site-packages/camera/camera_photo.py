class Camera:
    def __init__(self):
        self.camera = 'camera'

    def begin(self):
        from picamera import PiCamera
        from time import sleep

        CAMERA = PiCamera()

    def previewFor(self,secs):
        CAMERA.start_preview()
        sleep(secs)
        CAMERA.stop_preview()

    def takeVideoFor(self,file,secs):
        CAMERA.start_recording(file)
        sleep(secs)
        CAMERA.stop_recording()

    def takePhoto(self,file):
        CAMERA.capture(file)

    def previewAndVideoFor(self,file,secs):
        CAMERA.start_preview()
        CAMERA.start_recording(file)
        sleep(secs)
        CAMERA.stop_recording()
        CAMERA.stop_preview()

    def video(self,file):
        CAMERA.start_recording(file)

    def noVideo(self):
        CAMERA.stop_recording()

    def preview(self):
        CAMERA.start_preview()

    def noPreview(self):
        CAMERA.stop_preview()

    def previewAndVideo(self,file):
        CAMERA.start_preview()
        CAMERA.start_recording(file)

    def noPreviewAndVideo(self):
        CAMERA.stop_recording()
        CAMERA.stop_preview()

    def set_rotation(self, rotation):
        CAMERA.rotation = rotation
