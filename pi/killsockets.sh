#!/bin/bash

kill -kill "$(sudo netstat -anp | grep 2048 | grep -o '[0-9][0-9][0-9][0-9]/python' | egrep -o '[0-9]{4}')"
