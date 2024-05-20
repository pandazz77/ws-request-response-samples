import websockets, asyncio, json, random, string

REQUEST_ID_FIELD = "_rid"
REQUEST_TYPE_FIELD = "_type"
REQUEST_REQVAL = "REQUEST"
REQUEST_RESVAL = "RESPONSE"
REQUEST_ID_LENGTH = 10

# request echo
async def _r_echo(data:dict) -> dict:
    return data

# random string generator
def rstr(N:int):
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(N))

# Simple websocket handler function
async def _echo(websocket, path):
    async for message in websocket:
        print("Received:",message)
        await websocket.send(message)
        print("Sent:",message)


# Simple websocket server
class WebsocketServer:
    def __init__(self,addr:str,port:int,handler):
        self.addr = addr
        self.port = port
        self.handler = handler

    async def run(self):
        async with websockets.serve(self.handler, self.addr, self.port) as server:
            await asyncio.Future()

    async def send(self, data, websocket):
        await websocket.send(data)

# Simple websocket client
class WebSocketClient:
    def __init__(self,uri:str=None,wss_addr:str=None,wss_port:int=None):
        if uri is not None:
            self.uri = uri
        else:
            if wss_addr is None or wss_port is None:
                raise Exception("Invalid connection")
            self.uri = f"ws://{wss_addr}:{wss_port}"

        self.websocket: None

    async def connect(self):
        self.websocket = await websockets.connect(self.uri)
    
    async def send(self,data):
        await self.websocket.send(data)

    async def recv(self):
        return await self.websocket.recv()

    @staticmethod
    async def send_to(data,uri:str):
        async with websockets.connect(uri) as websocket:
            await websocket.send(data)

    @staticmethod
    async def recv_from(uri:str):
        async with websockets.connect(uri) as websocket:
            return await websocket.recv()


class RequestWebSocketServer(WebsocketServer):
    def __init__(self,addr:str,port:int,handler):
        super().__init__(addr,port,self._input_handler)
        self.handler = handler # мб будет ошибка из-за одного имени с родителем

        self.incoming_messages = {}

    @staticmethod
    def wrap_message(msg:dict|str,isRequest:bool=True) -> dict:
        if type(msg) is str:
            msg = {"message":msg}

        if REQUEST_ID_FIELD not in msg:
            msg[REQUEST_ID_FIELD] = rstr(REQUEST_ID_LENGTH)

        if isRequest: msg[REQUEST_TYPE_FIELD] = REQUEST_REQVAL
        else: msg[REQUEST_TYPE_FIELD] = REQUEST_RESVAL

        return msg

    async def _input_handler(self,websocket):
        async for message in websocket:
            message = json.loads(message)
            if REQUEST_ID_FIELD not in message: raise Exception("Invalid body(doesnt contain id):",message)
            if REQUEST_TYPE_FIELD not in message: raise Exception("Invalid body(doesnt contain type):",message)
            self.incoming_messages[message[REQUEST_ID_FIELD]] = message
            message = self.wrap_message(message,False)
            self._send_response(message,websocket)

    async def send_request(self,data:dict,websocket):
        wrapped_msg = self.wrap_message(data)
        id = wrapped_msg.get(REQUEST_ID_FIELD)

        self.send(json.dumps(wrapped_msg),websocket)
        while id not in self.incoming_messages:
            await asyncio.sleep(0.1)
        response = self.incoming_messages.pop(id)
        if response[REQUEST_TYPE_FIELD] == REQUEST_RESVAL:
            return response
        else:
            raise Exception("Response is not response :)")

    async def _send_response(self,data:dict,websocket):
        handled_data = self.handler(data)
        if handled_data is None: return
        self.send(handled_data,websocket)


class RequestWebSocketClient(WebSocketClient):
    def __init__(self,uri:str=None,wss_addr:str=None,wss_port:int=None,handler=None):
        super().__init__(uri,wss_addr,wss_port)
        self.handler = handler

        self.incoming_messages = {}

    async def run(self):
        while True:
            await self._input_handler(await self.recv())

    async def _input_handler(self,message):
        message = json.loads(message)
        if REQUEST_ID_FIELD not in message: raise Exception("Invalid body(doesnt contain id):",message)
        if REQUEST_TYPE_FIELD not in message: raise Exception("Invalid body(doesnt contain type):",message)
        self.incoming_messages[message[REQUEST_ID_FIELD]] = message
        message = RequestWebSocketServer.wrap_message(message,False)
        self._send_response(message)

    async def send_request(self, data:dict):
        wrapped_msg = RequestWebSocketServer.wrap_message(data)
        id = wrapped_msg.get(REQUEST_ID_FIELD)

        self.send(json.dumps(wrapped_msg))
        while id not in self.incoming_messages:
            await asyncio.sleep(0.1)
        response = self.incoming_messages.pop(id)
        if response[REQUEST_TYPE_FIELD] == REQUEST_RESVAL:
            return response
        else:
            raise Exception("Response is not response :)")
        
    async def _send_response(self,data:dict):
        handled_data = self.handler(data)
        if handled_data is None: return
        return await self.send(handled_data)
