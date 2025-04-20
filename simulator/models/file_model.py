"""Defines a file model with metadata for simulation."""

import threading
import time
from typing import Optional


class FileModel:
    """Class representing a file to be sent by a client."""
    _counter: int = 0
    _counter_lock: threading.Lock = threading.Lock()

    def __init__(self, size: float) -> None:
        with FileModel._counter_lock:
            FileModel._counter += 1
            self.id: int = FileModel._counter
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
        now: float = time.monotonic()
        if self.start_time is None:
            return now - self.arrival_time
        return self.start_time - self.arrival_time
