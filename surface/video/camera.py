import cv2
import numpy as np
from PIL import Image
from io import BytesIO

import get_image
import video_pipeline

FRAMES_TO_SAVE = 2  # save a frame every x frames

class Camera:
    def __init__(self, port):
        self._frame = None
        gst_str = f'udpsrc port={port} ! application/x-rtp ! rtpjitterbuffer ! rtph264depay ! avdec_h264 ! videoconvert ! video/x-raw,width=1280,height=720,format=RGB ! appsink name=appsink0'
        print(gst_str)
        video_pipeline.setup(gst_str)
        video_pipeline.connect_sink_listener(self.on_new_buffer)
        
        self.is_saving = False
        self.frame_counter = 0
        self.last_saved_frame = 0

    def __del__(self):
        video_pipeline.teardown()

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

        
