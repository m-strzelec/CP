"""Generates clients with files at specified intervals."""

import threading
import random

from simulator.models.queue_monitor import QueueMonitor
from simulator.models.client_model import ClientModel
from simulator.models.file_model import FileModel


class ClientGenerator(threading.Thread):
    """Generates clients with files at regular intervals."""
    def __init__(
        self,
        queue_monitor: QueueMonitor,
        interval: float,
        files_per_client_range: tuple[int, int],
        size_range: tuple[int, int]
    ) -> None:
        super().__init__(daemon=True)
        self.queue_monitor: QueueMonitor = queue_monitor
        self.interval: float = interval
        self.files_per_client_range: tuple[int, int] = files_per_client_range
        self.size_range: tuple[int, int] = size_range
        self._stop_event: threading.Event = threading.Event()

    def run(self) -> None:
        """Generate clients at regular intervals."""
        while not self._stop_event.is_set():
            # Generate a new client with random number of files
            num_files = random.randint(*self.files_per_client_range)
            files = []

            for _ in range(num_files):
                size = random.randint(*self.size_range)
                file = FileModel(client_id=0, size=size)
                files.append(file)

            client = ClientModel(files)
            self.queue_monitor.put_client(client)

            if self._stop_event.wait(self.interval):
                break

    def stop(self) -> None:
        self._stop_event.set()
        

