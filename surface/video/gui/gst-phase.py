"""This module is responsible for being able to take in video
information from any source of choice, including the intended bytes
from the network, as well as producing vide information in a
representation that can be understood by our app.


Call order:
setup -> connect_sink_listener* -> teardown -> ...
setup must be called after teardown.


- setup(String pipeline_description) -> Void
  - Initializes the module by creating a new pipeline based on the given pipeline description. Raises an error if Gstreamer is unable to parse or launch with the given pipline description.

- connect_sink_listener([AppSink -> Void]) -> Void
  - Accepts a callback for the module pass on the app sink into.

- teardown() -> Void
  - Cleanly shuts down gstreamer. It may be possible to not call this at all and allow the OS to clean up for you. If this is called, must call `setup` again.

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

# TODO(gst-phase): Defensive code (the ifs at the start of each function body) could be replaced with decorators maybe?

APP_SINK_NAME = "appsink0"

setup_called = False
pipeline = None  # Gst.Pipeline | Gst.Element | None
appsink = None  # AppSink | None

def setup(pipeline_description):
    if setup_called:
        print("gst-phase.py: setup has already been called! Ignoring call.")
        return

    try:
        pipeline = Gst.parse_launch(pipeline_description)
    except GLib.Error as inst:
        print("gst-phase.py: Gst.parse_launch raised an error. Setup failed.")
        print(type(inst))
        print(inst)
        return

    if pipeline is None:
        print("gst-phase.py: Gst.parse_launch returned None. There is no pipeline... Setup failed.")
        return

    # TODO(marvin): Can't find this function on the internet?
    appsink = pipeline.get_by_name(APP_SINK_NAME)

    if appsink is None:
        print("gst-phase.py: appsink in the pipeline could not be found. Setup failed.")

    appsink.set_property('emit-signals', True)
    appsink.set_property('max-buffers', 1)
    appsink.set_property('drop', True)
    appsink.set_property('sync', False)

    pipeline.set_state(Gst.State.PLAYING)
    setup_called = True

def connect_sink_listener(sink_listener):
    if not setup_called:
        print("gst-phase.py: cannot connect sink listener if setup has not been called. Ignoring request.")
        return

    appsink.connect('new-sample', sink_listener)

def teardown():
    if not setup_called:
        print("gst-phase.py: cannot teardown if setup has not been called. Ignoring request.")
        return

    pipeline.set_state(Gst.State.NULL)
    appsink = None
    pipeline = None
    setup_called = False
