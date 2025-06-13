     #!/bin/bash

     # run the async server and all clients
     python -m pi.async_server &
     python -m pi.imu &
     python -m pi.depth-sensor &
     wait