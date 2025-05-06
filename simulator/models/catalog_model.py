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
            file: Optional[FileModel] = self.queue_monitor.get_next_file(0.5)
            if file and not self._stop_event.is_set():
                self.current_file = file
                file.mark_start()
                if self.dispatch_callback:
                    self.dispatch_callback(self.catalog_id, file)

                self.process_file(file)
                file.mark_end()
                self.current_file = None
                if self.dispatch_callback:
                    self.dispatch_callback(self.catalog_id, None)

    def process_file(self, file: FileModel) -> None:
        """Simulate file processing delay."""
        processing_time: float = file.size * 0.01
        end_time: float = time.monotonic() + processing_time
        while time.monotonic() < end_time and not self._stop_event.is_set():
            remaining: float = end_time - time.monotonic()
            if remaining <= 0:
                break
            time.sleep(min(0.1, remaining))

    def stop(self) -> None:
        self._stop_event.set()
