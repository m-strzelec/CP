"""Manages a processing thread (catalog) and its own scheduling queue."""

import threading
import time
from queue import Empty
from simulator.models.cost_function import compute_cost


class CatalogModel(threading.Thread):
    """Class representing processing slot that pulls the-lowest-cost file."""
    def __init__(
        self, catalog_id: int, input_queue, m: float,
        k: float, dispatch_callback=None
    ):
        super().__init__(daemon=True)
        self.catalog_id = catalog_id
        self.input_queue = input_queue
        self.m = m
        self.k = k
        self.current_file = None
        self.dispatch_callback = dispatch_callback
        self._running = False

    def run(self):
        self._running = True
        while self._running:
            pending = []
            try:
                pending.append(self.input_queue.get(timeout=1))
                while True:
                    pending.append(self.input_queue.get_nowait())
            except Empty:
                pass

            if pending:
                # pick lowest-cost file
                costs = [
                    (compute_cost(f.size, f.waiting_time, self.m, self.k), f)
                    for f in pending
                ]
                cost, chosen = min(costs, key=lambda x: x[0])
                for _, f in costs:
                    if f is not chosen:
                        self.input_queue.put(f)
                # process chosen file
                self.current_file = chosen
                chosen.mark_start()
                if self.dispatch_callback:
                    self.dispatch_callback(self.catalog_id, chosen)
                self.process_file(chosen)
                chosen.mark_end()
                self.current_file = None
                if self.dispatch_callback:
                    self.dispatch_callback(self.catalog_id, None)

    def process_file(self, file_item):
        """Simulate file processing delay."""
        time.sleep(file_item.size * 0.01)

    def stop(self):
        self._running = False
