from socklib import UDPclient, UDPRequestClient, rstr
from const import *
import time, random

# # simple udp message exchanging
# def main():
#     client = UDPclient(PORT2)
#     client.start()

#     while True:
#         client.send(rstr(15),PORT1)
#         time.sleep(random.randint(1,2))

# echo client
def main():
    client = UDPRequestClient(PORT2)
    client.start()

if __name__ == "__main__":
    main()