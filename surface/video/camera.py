import cv2
import numpy as np
from PIL import Image
from io import BytesIO
import gi
gi.require_version('Gst', '1.0')
gi.require_version('GstApp', '1.0')
from gi.repository import Gst, GstApp

import get_image

FRAMES_TO_SAVE = 2  # save a frame every x frames

class Camera:
    def __init__(self, port):
        self._frame = None
        Gst.init(None)
        gst_str = f'udpsrc port={port} ! application/x-rtp ! rtpjitterbuffer ! rtph264depay ! avdec_h264 ! videoconvert ! video/x-raw,width=1280,height=720,format=RGB ! appsink name=appsink0'
        print(gst_str)
        self.pipeline = Gst.parse_launch(gst_str)
        self.appsink = self.pipeline.get_by_name('appsink0')
        self.appsink.set_property('emit-signals', True)
        self.appsink.set_property('max-buffers', 1)
        self.appsink.set_property('drop', True)
        self.appsink.set_property('sync', False)
        self.appsink.connect('new-sample', self.on_new_buffer)

        self.is_saving = False
        self.frame_counter = 0
        self.last_saved_frame = 0

        self.pipeline.set_state(Gst.State.PLAYING)

    def __del__(self):
        self.pipeline.set_state(Gst.State.NULL)

    def start_saving(self):
        self.is_saving = True
        # get_image.make_folder()
    
    def stop_saving(self):
        self.is_saving = False

    def on_new_buffer(self, sink): ## everytime it gets a new frame, pull sample signal -> stored in buffer, reshapes into numpy array
        sample = sink.emit('pull-sample')
        buffer = sample.get_buffer()
        self._frame = np.ndarray(
            shape=(720, 1280, 3), # 720 by 1280 resolution
            buffer=buffer.extract_dup(0, buffer.get_size()),
            dtype=np.uint8,
        )
        self.frame_counter += 1
        return Gst.FlowReturn.OK

    def get_frame(self) -> bytes: ## makes image from array of values and stores as jpeg
        if self._frame is not None and self._frame.any():
            file_object = BytesIO()
            img = Image.fromarray(self._frame)
            if self.is_saving and self.frame_counter - self.last_saved_frame >= FRAMES_TO_SAVE:
                get_image.save_image(img, str(self.frame_counter))
                self.last_saved_frame = self.frame_counter
            img.save(file_object, 'JPEG')
            file_object.seek(0)
            return file_object.read()
        return b''

    def get_cropped_frame(self) -> bytes:
        if self._frame is not None and self._frame.any():
            file_object = BytesIO()
            img = Image.fromarray(self._frame)
            cropped_img = img.crop((1280*0.3, 0, 1280-(1280*0.3), 720))
            cropped_img.save(file_object, 'JPEG')
            file_object.seek(0)
            return file_object.read()

        