import asyncio

HOST = "localhost"  # raspberry pi ip
PORT = 2049


class Client:
    def __init__(self):
        self.loop = asyncio.get_event_loop()

    def __del__(self):
        self.loop.close()

    async def run(self):
        reader, writer = await asyncio.open_connection(HOST, PORT)
        for i in range(1000):
            print(f"send message: {i}")
            writer.write(f"message: {i}".encode("utf-8"))
            await writer.drain()
            await asyncio.sleep(1)

        writer.close()
        await writer.wait_closed()


if __name__ == "__main__":
    client = Client()
    client.loop.run_until_complete(client.run())
