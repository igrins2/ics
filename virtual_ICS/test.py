import threading
import time

class TestThread(threading.Thread):
    def __init__(self, message):
        threading.Thread.__init__(self)
        self.message = message
        self.daemon  = True
        self.event   = threading.Event()

    def run(self):
        while True:
            if self.event.is_set():
                break
            time.sleep(1)
            print('[class]', self.message)

threadList = []

for message in ["you", "need", "python"]:
    thread = TestThread(message)
    threadList.append(thread)
    thread.start()

for i in range(10):
    time.sleep(1)
    print('[for]', i)

for thread in threadList:
    thread.event.set()
    print('[thread for]', thread)

time.sleep(1)