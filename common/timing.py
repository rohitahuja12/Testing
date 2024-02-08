import threading

class RepeatAction(threading.Thread):

    stopped = threading.Event()

    def __init__(self, interval, f):
        threading.Thread.__init__(self)
        self.interval = interval
        self.f = f

    def run(self):
        while not self.stopped.wait(self.interval):
            self.f()
