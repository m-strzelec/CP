"""Coordinates simulation loop."""

import time
from typing import Optional

from simulator.models.client import Client
from simulator.models.catalog_model import CatalogModel, DispatchCallbackType
from simulator.models.queue_monitor import QueueMonitor


class SimulationManager:
    """Class that runs the full simulation for set up clients and catalogs."""
    def __init__(
        self,
        num_clients: int,
        num_catalogs: int,
        client_interval: float,
        size_range: tuple[float, float],
        m: float,
        k: float,
        dispatch_callback: Optional[DispatchCallbackType] = None
    ) -> None:
        self.queue_monitor: QueueMonitor = QueueMonitor(m=m, k=k)
        self.catalogs: list[CatalogModel] = [
            CatalogModel(i, self.queue_monitor, dispatch_callback)
            for i in range(num_catalogs)
        ]
        self.clients: list[Client] = [
            Client(i, self.queue_monitor, client_interval, size_range)
            for i in range(num_clients)
        ]

    def start(self) -> None:
        for c in self.catalogs:
            c.start()
        for cl in self.clients:
            cl.start()

    def stop(self) -> None:
        for cl in self.clients:
            cl.stop()
        time.sleep(0.5)
        for c in self.catalogs:
            c.stop()
        # Wait for threads to finish
        for thread in self.clients + self.catalogs:
            if thread.is_alive():
                thread.join(timeout=1.0)
