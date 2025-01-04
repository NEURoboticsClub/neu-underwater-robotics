# surface

This folder is responsible all code and assets related to the top-side machine,
in which there are three main parts:
- Controller: How input is read from a device, and sent to bottom-side to move
  the robot.
- GUI: A GUI app.
- Sturgeon: Parsing and rendering data via a diagram.

## CLI

To launch the controller,
```sh
python -m ./surface_client
```
(Or `python3` instead of `python` depending on your environment variables.)

To launch the surface GUI app,
```sh
./launch -p <PORT NUM> -n <NUM CAMERAS>
```
One can add `-s` flag to show surpressed messages. One can also add 
`-w <Widget Name>` which locates the surface central to be used in
`./gui/widgets/surface_central.py`.

Let `<PORT NUM>` and `<NUM CAERMAS>` be `p` and `n` respectively. Then, the
ports `p`, `p+1`, ..., `p+n-1` will be used for the cameras. If there exists an
invalid port, the program will shut down with a descriptive error message,
tellin you so.

## Directory Structure
- `common`: Contains code whose purpose cuts across the submodules present in this
  directory.
- `ESP32WifiTest`: Contains exploratory code for ESP32 Wifi.
- `__init__.py`: To make this directory a Python package. Do not delete.
- `tests`: Contains test for code in this directory.

### Controller
- `surface_client.py`: The entry point for the program to read user input from
  the controller and sends the movement data to the pi.
- `joystick.py`: Defines code that reads user input from XBox controller into numbers.
- `pygame_joystick_example.py`: Contains reference code for working with pygame.

### GUI
- `xgui`: The script to launch the GUI.
- `xgui.py`: The code which `xgui` calls into.
- `gui`: Responsible for defining PyQt5 GUI elements.
- `surpressed_qt_messages.txt`: Qt messages that should not be logged. Each line
  is one message.

### Sturgeon
- `sturgeon_test.csv`: Raw data for sturgeon.
- `sturgeon_test.py`: Exploratory code that parses the raw data into a visual diagram.

## Tests
Run
```sh
./xtest
```

## GUI

This is a UML activity diagram that summarizes the control flow `./xgui.py`.

![xgui.py diagram](xgui-diagram.jpg "xgui.py diagram")

You may modify the diagram in the link below, but be sure to download it as a
JPG and replace the current JPG under the same name. 
https://docs.google.com/drawings/d/1sxUdhup1p8CZiSeZzCpBNy8SAKoo_eIB_ZVpaZL_PD8/edit?usp=sharing

### Surpressed Warnings
```
QWidget::paintEngine: Should no longer be called
```
This spams the stderr port  when resizing video player widget while a
video is shown. According to [this forum
discussion](https://forum.qt.io/topic/122732/qwidget-paintengine-should-no-longer-be-called),
this is a bug and can be safely ignored. Once this bug has been fixed, we can
remove this.


## Regressions

The previous implementation was able to:
- Take a picture on a single camera and save it to the top-side's file system.
- Save a recording of a single camera and save it to the top-side's file system.
- Stream a cropped version of the video feed.

To see the previous implementation, go to this commit. (TODO(README): Add the commit.)
