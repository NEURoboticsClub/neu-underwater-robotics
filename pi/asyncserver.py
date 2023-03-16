import asyncio

PI_IP = '192.168.0.103'
PI_PORT = 2049


class Server:
    lock = asyncio.Lock()

    def _init_conn(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        print(
            f"Ready to accept connection. Please start client.py {HOST=} {PORT=}")
        s.listen(5)
        conn, addr = s.accept()
        print(f"Connected by {addr}")
