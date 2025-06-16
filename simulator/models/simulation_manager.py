"""Coordinates simulation loop."""

import time
from typing import Optional, Callable

from simulator.models.client_generator import ClientGenerator
from simulator.models.catalog_model import CatalogModel, DispatchCallbackType
from simulator.models.queue_monitor import QueueMonitor
from simulator.models.file_model import FileModel
from simulator.models.client_model import ClientModel


class SimulationManager:
    """Class that runs the full simulation"""
    def __init__(
        self,
        num_catalogs: int,
        client_interval: float,
        files_per_client_range: tuple[int, int],
        size_range: tuple[float, float],
        m: float,
        k: float,
        dispatch_callback: Optional[DispatchCallbackType] = None,
        client_creation_callback: Optional[Callable[[ClientModel], None]] = None,
        file_processed_callback: Optional[Callable[[FileModel], None]] = None,
        auto_mode: bool = True
    ) -> None:
        self.queue_monitor: QueueMonitor = QueueMonitor(
            m=m,
            k=k,
            client_creation_callback=client_creation_callback
        )
        self.catalogs: list[CatalogModel] = [
            CatalogModel(
                i,
                self.queue_monitor,
                dispatch_callback,
                file_processed_callback
            )
            for i in range(num_catalogs)
        ]

        self.client_generator: Optional[ClientGenerator] = None
        self.auto_mode = auto_mode

        if auto_mode:
            self.client_generator = ClientGenerator(
                self.queue_monitor,
                client_interval,
                files_per_client_range,
                size_range
            )

        # Store settings for manual mode
        self.files_per_client_range = files_per_client_range
        self.size_range = size_range

    def start(self) -> None:
        for c in self.catalogs:
            c.start()
        if self.client_generator:
            self.client_generator.start()

    def stop(self) -> None:
        if self.client_generator:
            self.client_generator.stop()
        time.sleep(0.5)
        for c in self.catalogs:
            c.stop()
        # Wait for threads to finish
        threads_to_join = self.catalogs[:]
        if self.client_generator:
            threads_to_join.append(self.client_generator)
        for thread in threads_to_join:
            if thread.is_alive():
                thread.join(timeout=1.0)

    def add_manual_client(self, num_files: int) -> ClientModel:
        """Manually add a client with specified number of files."""
        import random
        files: list[FileModel] = []

        for _ in range(num_files):
            size = random.uniform(*self.size_range)
            file = FileModel(client_id=0, size=size)
            files.append(file)

        client = ClientModel(files)
        self.queue_monitor.put_client(client)
        return client

    def get_waiting_clients(self) -> list[ClientModel]:
        """Get list of waiting clients."""
        return self.queue_monitor.get_waiting_clients()
