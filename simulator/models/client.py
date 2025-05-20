"""Defines a client that generates files at random or configured intervals."""

import threading
import random
from simulator.models.file_model import FileModel
from simulator.models.queue_monitor import QueueMonitor


class Client(threading.Thread):
    """Class simulating client actions."""
    def __init__(
        self,
        client_id: int,
        queue_monitor: QueueMonitor,
        interval: float,
        size_range: tuple[float, float]
    ) -> None:
        super().__init__(daemon=True)
        self.client_id: int = client_id
        self.queue_monitor: QueueMonitor = queue_monitor
        self.interval: float = interval
        self.size_range: tuple[float, float] = size_range
        self._stop_event: threading.Event = threading.Event()

    def run(self) -> None:
        while not self._stop_event.is_set():
            size: float = random.uniform(*self.size_range)
            file: FileModel = FileModel(client_id=self.client_id, size=size)
            self.queue_monitor.put_file(file)
            self._stop_event.wait(timeout=self.interval)

    def stop(self) -> None:
        self._stop_event.set()
