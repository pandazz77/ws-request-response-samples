import asyncio

from const import *
from socklib import WebSocketClient, rstr


# Simple ws client <-> ws server message exchanging
async def main():
    wsc = WebSocketClient(wss_addr=SERVER_ADDR,wss_port=SERVER_PORT)
    await wsc.connect()
    while True:
        data = rstr(15)
        print(">>>",data)
        await wsc.send(data)
        resp = await wsc.recv()
        print("<<<",resp)
        await asyncio.sleep(1)

if __name__ == '__main__':
    asyncio.run(main())