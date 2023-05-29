from socket import *

HOST = "raspberrypi.local"
PORT = 20488

sock = socket(AF_INET, SOCK_DGRAM)

sock.bind((HOST, PORT))

while True:
	data, addr = sock.recvfrom(1024)
	print(f'{addr=} | {data=}')

