import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst
from io import BytesIO
 
class Camera:
    def __init__(self):
        self.pipeline_str = f'gst-launch-1.0 v4l2src device=/dev/video2 ! videoconvert ! autovideosink'
        self.frame = None
        self.pipeline = None
 
        Gst.init(None)
        self.pipeline = Gst.parse_launch(self.pipeline_str)
        self.appsink = self.pipeline.get_by_name('appsink0')
        self.appsink.set_property('emit-signals', True)
        self.appsink.set_property('max-buffers', 1)
        self.appsink.set_property('drop', True)
        self.appsink.set_property('sync', False)
        self.appsink.connect('new-sample', self.on_new_buffer)
 
        self.pipeline.set_state(Gst.State.PLAYING)
 
    def __del__(self):
        self.pipeline.set_state(Gst.State.NULL)
 
    def on_new_buffer(self, sink):
        sample = sink.emit('pull-sample')
        buffer = sample.get_buffer()
        self.frame = buffer.extract_dup(0, buffer.get_size())
        return Gst.FlowReturn.OK
 
    def get_frame(self) -> bytes:
        if self.frame is not None:
            file_object = BytesIO()
            file_object.write(self.frame)
            file_object.seek(0)
            return file_object.read()
        return b''
