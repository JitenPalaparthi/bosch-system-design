import queue
import threading
import time

q = queue.Queue(10)  # bounded queue → backpressure

def producer():
    i = 0
    while True:
        print(f"[Producer] Producing {i}")
        q.put(i)  # blocks when queue is full → BACKPRESSURE
        i += 1
       # time.sleep(0.1)  # fast producer

def consumer():
    while True:
        item = q.get()
        print(f"    [Consumer] Consuming {item}")
        time.sleep(1)  # slow consumer

t1 = threading.Thread(target=producer)
t2 = threading.Thread(target=consumer)

t1.start()
t2.start()