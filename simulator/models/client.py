"""Defines a client that generates files at random or configured intervals."""

import threading
import random
import time
from simulator.models.file_model import FileModel


class Client(threading.Thread):
    """Class simulating client actions"""
    def __init__(
        self, client_id: int, out_queue, interval: float,
        size_range: tuple[float, float]
    ):
        super().__init__(daemon=True)
        self.client_id = client_id
        self.out_queue = out_queue
        self.interval = interval
        self.size_range = size_range
        self._running = False

    def run(self):
        self._running = True
        while self._running:
            size = random.uniform(*self.size_range)
            file = FileModel(size=size)
            self.out_queue.put(file)
            time.sleep(self.interval)

    def stop(self):
        self._running = False
