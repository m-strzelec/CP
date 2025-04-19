"""Defines a file model with metadata for simulation."""

import time


class FileModel:
    """Class representing a file to be sent by a client."""
    _counter = 0

    def __init__(self, size: float):
        FileModel._counter += 1
        self.id = FileModel._counter
        self.size = size
        self.arrival_time = time.monotonic()
        self.start_time = None
        self.end_time = None

    def mark_start(self):
        """Mark the time when file begins processing."""
        self.start_time = time.monotonic()

    def mark_end(self):
        """Mark the time when file has finished processing."""
        self.end_time = time.monotonic()

    @property
    def waiting_time(self) -> float:
        """Compute how long file has waited in the queue."""
        now = time.monotonic()
        if self.start_time is None:
            return now - self.arrival_time
        return self.start_time - self.arrival_time
