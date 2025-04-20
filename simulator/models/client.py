"""Defines a client that generates files at random or configured intervals."""

import threading
import random
from simulator.models.file_model import FileModel


class Client(threading.Thread):
    """Class simulating client actions."""
    def __init__(
        self, client_id: int, queue_monitor, interval: float,
        size_range: tuple[float, float]
    ):
        super().__init__(daemon=True)
        self.client_id = client_id
        self.queue_monitor = queue_monitor
        self.interval = interval
        self.size_range = size_range
        self._stop_event = threading.Event()

    def run(self):
        while not self._stop_event.is_set():
            size = random.uniform(*self.size_range)
            file = FileModel(size=size)
            self.queue_monitor.put_file(file)
            self._stop_event.wait(timeout=self.interval)

    def stop(self):
        self._stop_event.set()
