import asyncio

from const import *
from socklib import WebsocketServer, RequestWebSocketServer

# Simple websocket handler function
async def echo(websocket):
    async for message in websocket:
        print("Received:",message)
        await websocket.send(message)
        print("Sent:",message)

# request echo
async def r_echo(data:dict) -> dict:
    print("Sent:",data)
    return data

# Simple websocket echo server
# async def main():
#     wss = WebsocketServer(SERVER_ADDR,SERVER_PORT,echo)
#     return await wss.listen()

rwss = RequestWebSocketServer(SERVER_ADDR,SERVER_PORT,r_echo)

async def main():
    task = asyncio.create_task(rwss.listen())
    await task

if __name__ == "__main__":
    asyncio.run(main())