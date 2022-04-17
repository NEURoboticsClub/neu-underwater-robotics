import socket

HOST = "raspberrypi.local"  # Standard loopback interface address (localhost)
PORT = 2048  # Port to listen on (non-privileged ports are > 1023)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    conn, addr = s.accept()
    print(f"Connected by {addr}")
    while True:
        data = conn.recv(1024)
        if data:
            print(f'{data=}')


