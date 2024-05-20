import asyncio

from const import *
from socklib import WebsocketServer, _echo

# Simple websocket echo server
async def main():
    wss = WebsocketServer(SERVER_ADDR,SERVER_PORT,_echo)
    return await wss.run()

if __name__ == "__main__":
    asyncio.run(main())