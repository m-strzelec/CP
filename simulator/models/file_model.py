"""Defines a file model with metadata for simulation."""

import threading
import time
from typing import Optional


class FileModel:
    """Class representing a file to be sent by a client."""
    _counter: int = 0
    _counter_lock: threading.Lock = threading.Lock()

    def __init__(self, client_id, size: float) -> None:
        with FileModel._counter_lock:
            FileModel._counter += 1
            self.id: int = FileModel._counter
        self.client_id: int = client_id
        self.catalog_id: Optional[int] = None
        self.size: float = size
        self.arrival_time: float = time.monotonic()
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None

    def mark_start(self) -> None:
        """Mark the time when file begins processing."""
        self.start_time = time.monotonic()

    def mark_end(self) -> None:
        """Mark the time when file has finished processing."""
        self.end_time = time.monotonic()

    @property
    def waiting_time(self) -> float:
        """Compute how long file has waited in the queue."""
        if self.start_time is None:
            now: float = time.monotonic()
            return now - self.arrival_time
        return self.start_time - self.arrival_time

    @property
    def processing_time(self) -> float:
        """Compute how long file was processed."""
        if self.start_time is None:
            return 0.0
        if self.end_time is None:
            now: float = time.monotonic()
            return now - self.start_time
        return self.end_time - self.start_time
