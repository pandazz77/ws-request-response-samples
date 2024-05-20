import socket, json, threading, random, string
import time

REQUEST_ID_FIELD = "_rid"
REQUEST_TYPE_FIELD = "_type"
REQUEST_REQVAL = "REQUEST"
REQUEST_RESVAL = "RESPONSE"
REQUEST_ID_LENGTH = 10

# random string generator
def rstr(N:int):
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(N))

# Simple udp socket client
class UDPclient(threading.Thread):
    def __init__(self,port:int,address:str="localhost",input_handler=None, output_handler=None):
        super().__init__()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((address,port))

        if input_handler  is None: self.input_handler  = self._iprinter
        else: self.input_handler = input_handler

        if output_handler is None: self.output_handler = self._oprinter
        else: self.output_handler = output_handler

    def run(self):
        while True:
            try:
                data, addr = self.sock.recvfrom(1024)
                self.input_handler(data.decode(),addr)
            except ConnectionError:
                pass

    def send(self,msg:str,port:int,address:str="localhost"):
        self.sock.sendto(msg.encode(),(address,port))
        self.output_handler(msg,(address,port))

    def _iprinter(self,data,addr):
        print(addr,"<<",data)

    def _oprinter(self,data,addr):
        print(addr,">>",data)


class UDPRequestClient(UDPclient):
    def __init__(self,port:int,address:str="localhost",handler=None):
        super().__init__(port,address,input_handler=self._input_handler)
        
        if handler is None: self.handler = self._echo
        else: self.handler = handler

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

    def _input_handler(self,data:str,addr:tuple):
        data = json.loads(data)
        if REQUEST_ID_FIELD not in data: raise Exception("Invalid body(doesnt contain id):",data)
        if REQUEST_TYPE_FIELD not in data: raise Exception("Invalid body(doesnt contain type):",data)
        self.incoming_messages[data[REQUEST_ID_FIELD]] = data
        data = self.wrap_message(data,False)
        self._send_response(data,addr)


    def send_request(self,msg:dict,port:int,address:str="localhost") -> dict:
        wrapped_msg = self.wrap_message(msg,True)
        id = wrapped_msg.get(REQUEST_ID_FIELD)

        self.send(json.dumps(wrapped_msg),port,address)
        while id not in self.incoming_messages:
            time.sleep(0.1)
        response = self.incoming_messages.pop(id)
        if response[REQUEST_TYPE_FIELD] == REQUEST_RESVAL:
            return response
        else:
            raise Exception("Response is not response :)")
        
    def _send_response(self,data:dict,addr:tuple):
        handled_data = self.handler(data)
        if handled_data is None: return
        self.send(json.dumps(handled_data),addr[1],addr[0])

    def _echo(self,data:dict) -> dict:
        return data