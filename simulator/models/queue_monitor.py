"""Synchronizes access to the file queue."""

import threading
from typing import Optional, Deque
from collections import deque

from simulator.models.cost_function import compute_cost
from simulator.models.file_model import FileModel


class QueueMonitor:
    """Class that handles thread-safe access to the file queue."""
    def __init__(self, m: float, k: float) -> None:
        self.queue: Deque[FileModel] = deque()
        self.lock: threading.Lock = threading.Lock()
        self.condition: threading.Condition = threading.Condition(self.lock)
        self.m: float = m
        self.k: float = k

    def put_file(self, file: FileModel) -> None:
        """Add a file to the queue and notify waiting threads."""
        with self.condition:
            self.queue.append(file)
            self.condition.notify()

    def get_next_file(self, timeout: Optional[float] = None) -> Optional[FileModel]:
        """Get the next file based on cost function.

        Parameters
        ----------
        timeout : Optional[float]
                  Maximum time to wait for a file to become available.
                  If None, wait indefinitely.

        Returns
        -------
        FileModel | None
            The file with the lowest cost or None if no file is available.
        """
        with self.condition:
            # Wait if queue is empty
            if not self.queue and timeout is not None:
                self.condition.wait(timeout)
            # Check queue again
            if not self.queue:
                return None
            # No need to calculate cost if there is only one file
            if len(self.queue) == 1:
                return self.queue.popleft()

            pending: list[FileModel] = list(self.queue)
            self.queue.clear()

            # Pick lowest-cost file
            costs: list[tuple[float, FileModel]] = [
                (compute_cost(f.size, f.waiting_time, self.m, self.k), f)
                for f in pending
            ]
            cost: float
            chosen: FileModel
            cost, chosen = min(costs, key=lambda x: x[0])
            # Put back remaining files
            for _, f in costs:
                if f is not chosen:
                    self.queue.append(f)

            return chosen

    def has_files(self) -> bool:
        """Check if there are any files in the queue."""
        with self.lock:
            return len(self.queue) > 0
