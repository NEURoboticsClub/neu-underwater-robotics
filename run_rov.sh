#!/bin/bash

trap 'killall' INT

killall() {
    trap '' INT TERM # ignore INT and TERM while shutting down
    kill -TERM 0
    wait # wait for child processes to complete
    echo DONE
}

# run the async server and all clients
python -m pi.async_server &
sleep 6
python -m pi.imu &
sleep 1
python -m pi.depth-sensor &
cat # wait forever
