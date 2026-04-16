import threading
import time

balance = 1000
lock = threading.Lock() # mutex --> thread locks


def withdraw_without_lock(amount):
    global balance
    temp = balance
    time.sleep(0.1)
    balance = temp - amount

def withdraw_with_lock(amount):
    global balance
    with lock:
        temp = balance
        time.sleep(0.1)
        balance = temp - amount
    

# Without coordination
balance = 1000
t1 = threading.Thread(target=withdraw_without_lock, args=(100,))
t2 = threading.Thread(target=withdraw_without_lock, args=(100,))
t1.start()
t2.start()
t1.join()
t2.join()
print("Without lock balance:", balance)

# With coordination
balance = 1000
t1 = threading.Thread(target=withdraw_with_lock, args=(100,))
t2 = threading.Thread(target=withdraw_with_lock, args=(100,))
t1.start()
t2.start()
t1.join()
t2.join()
print("With lock balance:", balance)

# do not sharememory, instead share memory by comminicating 