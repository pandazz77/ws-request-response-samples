import asyncio

from const import *
from socklib import WebSocketClient, RequestWebSocketClient, rstr

# async print func (just a stub)
async def aprint(*data):
    print(data)

async def stub(*data):
    pass

# Simple ws client <-> ws server message exchanging
# async def main():
#     wsc = WebSocketClient(wss_addr=SERVER_ADDR,wss_port=SERVER_PORT)
#     await wsc.connect()
#     while True:
#         data = rstr(15)
#         print(">>>",data)
#         await wsc.send(data)
#         resp = await wsc.recv()
#         print("<<<",resp)
#         await asyncio.sleep(1)

rwsc = RequestWebSocketClient(wss_addr=SERVER_ADDR,wss_port=SERVER_PORT,arhandler=stub)

async def sender():
    while True:
        data = rstr(15)
        print(">>>",data)
        response = await rwsc.send_request(data)
        print("<<<",response)
        await asyncio.sleep(1)

async def main():
    tasks = set()

    await rwsc.connect()
    tasks.add(asyncio.create_task(rwsc.listen()))
    tasks.add(asyncio.create_task(sender()))
    
    for task in tasks: await task

if __name__ == '__main__':
    asyncio.run(main())