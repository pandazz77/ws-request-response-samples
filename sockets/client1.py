from socklib import UDPclient, UDPRequestClient, rstr
from const import *
import time, random

# # simple udp message exchanging
# def main():
#     client = UDPclient(PORT1)
#     client.start()

#     while True:
#         client.send(rstr(15),PORT2)
#         time.sleep(random.randint(1,2))

def stub(*args):
    pass

def main():
    client = UDPRequestClient(PORT1,handler=stub)
    client.start()

    while True:
        request = {
            "message":rstr(13)
        }
        print("Request:",request)
        response = client.send_request(request,PORT2)
        print("Response:",response)
        time.sleep(random.randint(1,2))

if __name__ == "__main__":
    main()