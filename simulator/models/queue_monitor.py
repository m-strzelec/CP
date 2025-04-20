"""Synchronizes access to the file queue."""

import threading
from queue import Queue, Empty
from simulator.models.cost_function import compute_cost


class QueueMonitor:
    """Class that handles thread-safe access to the file queue."""
    def __init__(self, m: float, k: float):
        self.queue = Queue()
        self.lock = threading.Lock()
        self.m = m
        self.k = k

    def put_file(self, file):
        """Add a file to the queue."""
        self.queue.put(file)

    def get_next_file(self):
        """Get the next file based on cost function."""
        with self.lock:
            pending = []
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
            costs = [
                (compute_cost(f.size, f.waiting_time, self.m, self.k), f)
                for f in pending
            ]
            cost, chosen = min(costs, key=lambda x: x[0])
            # Put back remaining files
            for _, f in costs:
                if f is not chosen:
                    self.queue.put(f)

            return chosen
