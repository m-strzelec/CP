"""Coordinates simulation loop."""

from queue import Queue
from simulator.models.client import Client
from simulator.models.catalog_model import CatalogModel


class SimulationManager:
    """Class that runs the full simulation for set up clients and catalogs."""
    def __init__(
        self, num_clients: int, num_catalogs: int, client_interval: float,
        size_range: tuple[float, float], m: float, k: float,
        dispatch_callback=None
    ):
        self.queue = Queue()
        self.clients = [
            Client(i, self.queue, client_interval, size_range)
            for i in range(num_clients)
        ]
        self.catalogs = [
            CatalogModel(i, self.queue, m, k, dispatch_callback)
            for i in range(num_catalogs)
        ]

    def start(self):
        for c in self.catalogs:
            c.start()
        for cl in self.clients:
            cl.start()

    def stop(self):
        for cl in self.clients:
            cl.stop()
        for c in self.catalogs:
            c.stop()
