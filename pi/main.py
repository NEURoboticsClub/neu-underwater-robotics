import pyfirmata
import time

if __name__ == '__main__':
    # Initiate communication with Arduino
    board = pyfirmata.Arduino('/dev/ttyACM0 (Arduino Mega or Mega 2560)')
    print("Communication Successfully started")

    # Create bunch of useful variables
    myservo = board.digital[10]

    # Start iterator to receive input data
    it = pyfirmata.util.Iterator(board)
    it.start()
    # Setup LEDs and button

    myservo.write(180)
    time.sleep(2)
    myservo.write(0)
    time.sleep(1)
    myservo.write(180)

    while True:
        for pos in range(180):
            myservo.write(pos)
            print(pos)
            time.sleep(0.015)
