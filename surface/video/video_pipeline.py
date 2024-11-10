"""Defines the entry point for the video pipeline.

Using the GStreamer framework, we can create a pipeline for streaming
raw video data. This pipeline supports applying data transformations
to the video stream and then streaming the transformed data to a
sink. GStreamer enables us to leverage pre-existing data
transformations for these processes.

Call order:
Begins with `setup`.
 ┌─► setup ─► connect_sink_listener* ─► teardown ─┐
 │                                                │
 └────────────────────────────────────────────────┘

API:
- setup(String pipeline_description) -> Void
  - Creating a new pipeline based on the given pipeline description,
    which must include the source of the video data, the
    transformations to be applied, and the sink. Raises an error if
    Gstreamer is unable to parse or launch with the given pipeline
    description.

- connect_sink_listener([AppSink -> Void]) -> Void
  - Accepts a callback for where the data would sink into.

- teardown() -> Void
  - Cleanly shuts down gstreamer. It may be possible to not call this
    at all and allow the OS to clean up for you.

gi.repository API reference:
https://lazka.github.io/pgi-docs/Gst-1.0/index.html

I have no idea who that guy is, but some reason, this is the only
source of information on the internet that has everything nicely
organized in one website with easy navigation. If you find something
better and more official, please replace it.

"""
import gi
gi.require_version('Gst', '1.0')
gi.require_version('GstApp', '1.0')
from gi.repository import Gst, GstApp

# TODO(gst-phase): Defensive code (the ifs at the start of each
# function body) could be replaced with decorators maybe?

APP_SINK_NAME = "appsink0"

setup_called = False
pipeline = None  # Gst.Pipeline | Gst.Element | None
appsink = None  # AppSink | None

def setup(pipeline_description):
    if setup_called:
        print("video_pipeline.py: setup has already been called! Ignoring call.")
        return

    Gst.init(None)

    try:
        pipeline = Gst.parse_launch(pipeline_description)
    except GLib.Error as inst:
        print("video_pipeline.py: Gst.parse_launch raised an error. Setup failed.")
        print(type(inst))
        print(inst)
        return

    if pipeline is None:
        print("video_pipeline.py: Gst.parse_launch returned None. There is no pipeline... Setup failed.")
        return

    # TODO(marvin): Can't find this function on the internet?
    appsink = pipeline.get_by_name(APP_SINK_NAME)

    if appsink is None:
        print("video_pipeline.py: appsink in the pipeline could not be found. Setup failed.")

    appsink.set_property('emit-signals', True)
    appsink.set_property('max-buffers', 1)
    appsink.set_property('drop', True)
    appsink.set_property('sync', False)

    pipeline.set_state(Gst.State.PLAYING)
    setup_called = True

def connect_sink_listener(sink_listener):
    if not setup_called:
        print("video_pipeline.py: cannot connect sink listener if setup has not been called. Ignoring request.")
        return

    # Wraps the given sink_listener by return Gst.FlowReturn values
    def listener_wrapper(sink):
        try:
            sink_listener(sink)
            return Gst.FlowReturn.OK
        except Exception as e:
            return Gst.FlowReturn.ERROR
            

    appsink.connect('new-sample', listener_wrapper)

def teardown():
    if not setup_called:
        print("video_pipeline.py: cannot teardown if setup has not been called. Ignoring request.")
        return

    pipeline.set_state(Gst.State.NULL)
    appsink = None
    pipeline = None
    setup_called = False
