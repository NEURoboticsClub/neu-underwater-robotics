import pyfirmata
import time
import asyncio



if __name__ == '__main__':
    # Initiate communication with Arduino
    board = pyfirmata.Arduino('/dev/ttyACM0')
    print("Communication Successfully started")

    # Create bunch of useful variables
    # myservo = board.digital[10]
    myservo = board.get_pin('d:9:s')

    # Start iterator to receive input data
    it = pyfirmata.util.Iterator(board)
    it.start()
    # Setup LEDs and button

    # step = board.digital[3]
    # board.digital[2].write(1)
    # time.sleep(1)
    # board.digital[2].write(0)

    # while True:
    #     step.write(1.0)
    #     time.sleep(0.0005)
    #     step.write(0.0)
    #     time.sleep(0.0005)

    myservo.write(180)
    time.sleep(2)
    myservo.write(0)
    time.sleep(1)
    myservo.write(180)

    while True:
        for pos in range(180):
            myservo.write(pos)
            print(pos)
            time.sleep(0.05)
