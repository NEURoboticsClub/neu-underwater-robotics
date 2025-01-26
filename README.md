# neu-underwater-robotics
Repo for the Northeastern underwater robotics team.

### For setting up this repo for the first time, please see the [software setup guide](software_setup.md)
### For best practices for software development, please see the [best practices guide](best_practices.md)


## Software Overview:
> To be updated

We currently use a sockets based system to achieve two-way communication with a raspberry pi. On the surface, a USB controller is used to generate a 6-way velocity vector (x, y, z, yaw, pitch, roll) wich is sent to the ROV. We use a standard right-hand coordinate system, with the ROV's heading along +y. See more in the defintion of [VelocityVector](common/utils.py)  The ROV then translates that to the appropriate thruster control values with a PID controller (work in progress).

## Running instructions

### ROV:
- ssh into the ROV's RaspberryPi: `ssh pi@192.168.0.102`
- navigate to `neu-underwater-robotics`: `cd ~/neu-underwater-robotics`
- run `python -m pi.async_server`

### On surface laptop:
- setup environment described in [software_setup.md](software_setup.md)
- navigate to the `neu-underwater-robotics` directory (this directory)
- activate venv if using (`source ./activate.sh`)
- run `python -m surface/surface_client`
- for how to run the surface's gui app, read [this](./surface/README.md).

## Testing on local machine
- setup environment described in [software_setup.md](software_setup.md)
- navigate to the `neu-underwater-robotics` directory (this directory)
- activate venv if using (`source ./activate.sh`)
- set environment variable `SIM`: `export SIM='TRUE'`
- run server first `python -m pi.async_server`
- open a new terminal, and navigate to `neu-underwater-robotics`, activate venv if using
- run client second `python -m surface.surface_client`


