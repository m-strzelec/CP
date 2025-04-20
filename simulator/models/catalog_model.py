"""Manages a processing thread (catalog) and its own scheduling queue."""

import threading
import time
from typing import Optional
from collections.abc import Callable

from simulator.models.file_model import FileModel
from simulator.models.queue_monitor import QueueMonitor


DispatchCallbackType = Callable[[int, Optional[FileModel]], None]


class CatalogModel(threading.Thread):
    """Class representing processing slot that pulls the-lowest-cost file."""
    def __init__(
        self,
        catalog_id: int,
        queue_monitor: QueueMonitor,
        dispatch_callback: Optional[DispatchCallbackType] = None
    ) -> None:
        super().__init__(daemon=True)
        self.catalog_id: int = catalog_id
        self.queue_monitor: QueueMonitor = queue_monitor
        self.current_file: Optional[FileModel] = None
        self.dispatch_callback: Optional[DispatchCallbackType] = (
            dispatch_callback
        )
        self._stop_event: threading.Event = threading.Event()

    def run(self) -> None:
        while not self._stop_event.is_set():
            file: Optional[FileModel] = self.queue_monitor.get_next_file()
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

    def process_file(self, file: FileModel) -> None:
        """Simulate file processing delay."""
        time.sleep(file.size * 0.01)

    def stop(self) -> None:
        self._stop_event.set()
