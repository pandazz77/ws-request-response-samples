import threading
from client1 import main as client1_main
from client2 import main as client2_main

if __name__ == "__main__":
    thr1 = threading.Thread(target=client1_main)
    thr2 = threading.Thread(target=client2_main)

    thr1.start()
    thr2.start()

    thr1.join()
    thr2.join()