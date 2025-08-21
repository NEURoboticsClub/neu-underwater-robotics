#!/bin/bash

trap 'killall' INT

killall() {
    trap '' INT TERM # ignore INT and TERM while shutting down
    kill -TERM 0
    wait # wait for child processes to complete
    echo DONE
}

rm -f async_server_log.txt
rm -f imu_log.txt
rm -f depth_sensor_log.txt

# run the async server and all clients
python -u -m pi.async_server > async_server_log.txt &
sleep 6
python -u -m pi.imu > imu_log.txt &
sleep 1
python -u -m pi.depth-sensor > depth_sensor_log.txt &
multitail async_server_log.txt imu_log.txt depth_sensor_log.txt # wait forever
