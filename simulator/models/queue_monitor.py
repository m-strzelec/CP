"""Synchronizes access to the file queue of each client."""

import threading
from typing import Optional, Callable

from simulator.models.cost_function import compute_cost
from simulator.models.client_model import ClientModel
from simulator.models.file_model import FileModel


class QueueMonitor:
    """Class that handles thread-safe access to the file queue."""
    def __init__(
        self,
        m: float,
        k: float,
        client_creation_callback: Optional[Callable[[ClientModel], None]] = None
    ) -> None:
        self.clients: list[ClientModel] = []
        self.lock: threading.Lock = threading.Lock()
        self.condition: threading.Condition = threading.Condition(self.lock)
        self.m: float = m
        self.k: float = k
        self.client_creation_callback = client_creation_callback

    def put_client(self, client: ClientModel) -> None:
        """Add a client to the queue and notify waiting threads."""
        with self.condition:
            self.clients.append(client)
            self.condition.notify()

        if self.client_creation_callback:
            self.client_creation_callback(client)

    def get_next_file(self, timeout: Optional[float] = None) -> Optional[FileModel]:
        """Get the next file based on cost function from client files.

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
            # Wait if no clients have pending files
            if not self._has_pending_files() and timeout is not None:
                self.condition.wait(timeout)

            # Check again after waiting
            if not self._has_pending_files():
                return None

            # Get current files from all clients
            current_files = []
            for client in self.clients:
                current_file = client.current_file
                if current_file is not None:
                    current_files.append(current_file)

            if not current_files:
                return None

            # If only one file, return it
            if len(current_files) == 1:
                chosen_file = current_files[0]
                chosen_file.mark_start()
                return chosen_file

            # Calculate costs for current files
            costs = [
                (compute_cost(f.size, f.waiting_time, self.m, self.k), f)
                for f in current_files
            ]

            # Choose file with lowest cost
            _, chosen_file = min(costs, key=lambda x: x[0])
            chosen_file.mark_start()

            return chosen_file

    def mark_file_completed(self, file: FileModel) -> None:
        """Mark a file as completed and remove client if no more files."""
        with self.lock:
            file.mark_end()

            # Find the client that owns this file
            for client in self.clients[:]:
                if file.client_id == client.id:
                    client.mark_file_processed(file.id)
                    if not client.has_pending_files:
                        self.clients.remove(client)
                    break

    def get_waiting_clients(self) -> list[ClientModel]:
        """Get a list of all clients currently in the queue."""
        with self.lock:
            return [client for client in self.clients if client.has_pending_files]

    def get_all_waiting_files(self) -> list[FileModel]:
        """Get all files from all waiting clients."""
        with self.lock:
            files = []
            for client in self.clients:
                files.extend([f for f in client.files if f.start_time is None])
            return files

    def _has_pending_files(self) -> bool:
        """Check if any client has pending files."""
        return any(client.has_pending_files for client in self.clients)
