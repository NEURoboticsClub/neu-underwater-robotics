# neu-underwater-robotics
Repo for the Northeastern underwater robotics team.

### For setting up this repo for the first time, please see the [software setup guide](software_setup.md)
### For best practices for software development, please see the [best practices guide](best_practices.md)


## Software Overview:
> To be updated

We currently use a sockets based system to communicate two ways with a raspberry pi.
All of our data is streamed down using tcp as a string in the form:
```
pin:val;pin:val;
```
### Surface
* We currently use client.py to control our ROV using a drone control mode 1 scheme.
* We can use clienttest.py for a seaperch control scheme.

### Pi
* We use async_server.py for read input from the surface and control thrusters/motors.
* We run video_stream.py to stream video from the pi to the surface.

