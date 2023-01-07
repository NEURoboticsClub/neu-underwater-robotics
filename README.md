# neu-underwater-robotics
Repo for the Northeastern underwater robotics team.
We currently use a sockets based system to communicate two ways with a raspberry pi.
All of our data is streamed down using tcp as a string in the form:
```
pin:val;pin:val;
```
## Surface
* We currently use client.py to control our ROV using a drone control 1 scheme.
* We can use clienttest.py for a seaperch control scheme.
* We use camera.py to recieve camera feed.

## Pi
* We use server.py for read input from the surface and control thrusters/motors.
* We have various flask options all starting with webcam for different camera feeds.

