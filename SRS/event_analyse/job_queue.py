import threading
import Queue


class JobQueue(threading.Thread):
    """
    Job Queue,FIFO using one single thread.
    """
    def __init__(self):
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self.queue = Queue.Queue()  # FIFO

    def run(self):
        while True:
            items = self.queue.get()
            func = items[0]
            args = items[1:]
            func(*args)
            self.queue.task_done()

    def put(self, item):
        self.queue.put(item)

    def finish(self):
        """
        Wait all operations have been executed
        """
        self.queue.join()