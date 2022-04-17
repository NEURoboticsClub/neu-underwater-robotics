import socket

HOST = "raspberrypi.local"  # The server's hostname or IP address
PORT = 2048  # The port used by the server

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    while True:
        x = input()
        s.send(str.encode(x))
    # data = s.recv(1024)

# print(f"Received {data!r}")
