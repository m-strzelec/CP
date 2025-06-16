"""Defines a client model with a list of files."""

import time
import threading
from typing import Optional
from simulator.models.file_model import FileModel


class ClientModel:
    """Class representing a client with a list of files."""
    _counter: int = 0
    _counter_lock: threading.Lock = threading.Lock()

    def __init__(self, files: list[FileModel]) -> None:
        with ClientModel._counter_lock:
            ClientModel._counter += 1
            self.id: int = ClientModel._counter
        # Sort files by size
        self.files: list[FileModel] = sorted(files, key=lambda f: f.size)
        self.arrival_time: float = time.time()
        # Update client_id for all files
        for file in self.files:
            file.client_id = self.id

    @property
    def current_file(self) -> Optional[FileModel]:
        """Get the next file that hasn't been processed yet."""
        for file in self.files:
            if file.start_time is None:  # Not yet processed
                return file
        return None

    @property
    def file_sizes_str(self) -> str:
        """Get comma-separated string of file sizes."""
        return ", ".join(f"{file.size}" for file in self.files)

    @property
    def has_pending_files(self) -> bool:
        """Check if client has any unprocessed files."""
        return self.current_file is not None

    def mark_file_processed(self, file_id: int) -> None:
        """Mark a file as processed."""
        for file in self.files:
            if file.id == file_id:
                if file.start_time is None:
                    file.mark_start()
                file.mark_end()
                break
