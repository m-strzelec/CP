"""Generates clients with files at random or configured intervals."""

import threading
import random

from simulator.models.file_model import FileModel
from simulator.models.client_model import ClientModel
from simulator.models.queue_monitor import QueueMonitor


class ClientGenerator(threading.Thread):
    """Class that generates clients with files."""
    def __init__(
            self,
            queue_monitor: QueueMonitor,
            interval: float,
            files_per_client_range: tuple[int, int],
            size_range: tuple[float, float]
    ) -> None:
        super().__init__(daemon=True)
        self.queue_monitor: QueueMonitor = queue_monitor
        self.interval: float = interval
        self.files_per_client_range: tuple[int, int] = files_per_client_range
        self.size_range: tuple[float, float] = size_range
        self._stop_event: threading.Event = threading.Event()

    def run(self) -> None:
        while not self._stop_event.is_set():
            self.generate_client()
            self._stop_event.wait(timeout=self.interval)

    def generate_client(self) -> ClientModel:
        """Generate a new client with random files."""
        num_files = random.randint(*self.files_per_client_range)
        files: list[FileModel] = []

        for _ in range(num_files):
            size = random.uniform(*self.size_range)
            file = FileModel(client_id=0, size=size)
            files.append(file)

        client = ClientModel(files)
        self.queue_monitor.put_client(client)
        return client

    def stop(self) -> None:
        self._stop_event.set()
