"""Synchronizes access to the file queue."""

import threading
from queue import Queue, Empty
from typing import Optional

from simulator.models.cost_function import compute_cost
from simulator.models.file_model import FileModel


class QueueMonitor:
    """Class that handles thread-safe access to the file queue."""
    def __init__(self, m: float, k: float) -> None:
        self.queue: Queue[FileModel] = Queue()
        self.lock: threading.Lock = threading.Lock()
        self.m: float = m
        self.k: float = k

    def put_file(self, file: FileModel) -> None:
        """Add a file to the queue."""
        self.queue.put(file)

    def get_next_file(self) -> Optional[FileModel]:
        """Get the next file based on cost function.

        Returns
        -------
        FileModel | None
            The file with the lowest cost or None if no file is available.
        """
        with self.lock:
            pending: list[FileModel] = []
            try:
                # Try to get at least one item
                pending.append(self.queue.get_nowait())
                # Try to get more items without blocking
                while True:
                    pending.append(self.queue.get_nowait())
            except Empty:
                if not pending:
                    return None
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
                    self.queue.put(f)

            return chosen
