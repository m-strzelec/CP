"""Manages a processing thread (catalog) and its own scheduling queue."""

import threading
import time


class CatalogModel(threading.Thread):
    """Class representing processing slot that pulls the-lowest-cost file."""
    def __init__(self, catalog_id: int, queue_monitor, dispatch_callback=None):
        super().__init__(daemon=True)
        self.catalog_id = catalog_id
        self.queue_monitor = queue_monitor
        self.current_file = None
        self.dispatch_callback = dispatch_callback
        self._stop_event = threading.Event()

    def run(self):
        while not self._stop_event.is_set():
            file = self.queue_monitor.get_next_file()
            if file:
                self.current_file = file
                file.mark_start()
                if self.dispatch_callback:
                    self.dispatch_callback(self.catalog_id, file)

                self.process_file(file)
                file.mark_end()
                self.current_file = None
                if self.dispatch_callback:
                    self.dispatch_callback(self.catalog_id, None)
            else:
                # Wait before checking again if any file is available
                time.sleep(0.1)

    def process_file(self, file_item):
        """Simulate file processing delay."""
        time.sleep(file_item.size * 0.01)

    def stop(self):
        self._stop_event.set()
