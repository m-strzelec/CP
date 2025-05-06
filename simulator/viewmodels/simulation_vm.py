"""ViewModel for the file scheduling simulation."""

from typing import Optional

from PySide6.QtCore import QObject, Signal, Slot

from simulator.models.file_model import FileModel
from simulator.models.simulation_manager import SimulationManager


class SimulationViewModel(QObject):
    catalogStatusChanged = Signal(int, str)
    progressUpdated = Signal(int, float)
    simulationStateChanged = Signal(bool)

    def __init__(self):
        super().__init__()

        # Settings
        self._num_clients: int = 3
        self._num_catalogs: int = 5
        self._client_interval: float = 1.0
        self._min_file_size: float = 1.0
        self._max_file_size: float = 1000.0
        self._m_parameter: float = 1.0
        self._k_parameter: float = 1.0

        self._simulation_manager: Optional[SimulationManager] = None
        self._is_running: bool = False
        self._catalog_statuses: dict[int, str] = {}
        self._catalog_progresses: dict[int, float] = {}

    def num_clients(self) -> int:
        return self._num_clients

    def set_num_clients(self, value: int) -> None:
        if value > 0:
            self._num_clients = value

    def num_catalogs(self) -> int:
        return self._num_catalogs

    def set_num_catalogs(self, value: int) -> None:
        if value > 0:
            self._num_catalogs = value

    def client_interval(self) -> float:
        return self._client_interval

    def set_client_interval(self, value: float) -> None:
        if value > 0:
            self._client_interval = value

    def min_file_size(self) -> float:
        return self._min_file_size

    def set_min_file_size(self, value: float) -> None:
        if 0 < value <= self._max_file_size:
            self._min_file_size = value

    def max_file_size(self) -> float:
        return self._max_file_size

    def set_max_file_size(self, value: float) -> None:
        if value >= self._min_file_size:
            self._max_file_size = value

    def m_parameter(self) -> float:
        return self._m_parameter

    def set_m_parameter(self, value: float) -> None:
        if value >= 0:
            self._m_parameter = value

    def k_parameter(self) -> float:
        return self._k_parameter

    def set_k_parameter(self, value: float) -> None:
        if value >= 0:
            self._k_parameter = value

    def is_running(self) -> bool:
        return self._is_running

    @Slot()
    def start_simulation(self) -> None:
        if self._is_running:
            return
        self._catalog_statuses = {i: "Idle" for i in range(self._num_catalogs)}
        self._catalog_progresses = {i: 0.0 for i in range(self._num_catalogs)}
        self._simulation_manager = SimulationManager(
            num_clients=self._num_clients,
            num_catalogs=self._num_catalogs,
            client_interval=self._client_interval,
            size_range=(self._min_file_size, self._max_file_size),
            m=self._m_parameter,
            k=self._k_parameter,
            dispatch_callback=self._catalog_callback
        )
        self._simulation_manager.start()
        self._is_running = True
        self.simulationStateChanged.emit(True)

    @Slot()
    def stop_simulation(self) -> None:
        if not self._is_running or self._simulation_manager is None:
            return
        self._simulation_manager.stop()
        self._is_running = False
        self.simulationStateChanged.emit(False)
        for catalog_id in range(self._num_catalogs):
            self._catalog_statuses[catalog_id] = "Stopped"
            self._catalog_progresses[catalog_id] = 0.0
            self.catalogStatusChanged.emit(catalog_id, "Stopped")
            self.progressUpdated.emit(catalog_id, 0.0)

    def _catalog_callback(
        self,
        catalog_id: int,
        file: Optional[FileModel]
    ) -> None:
        """Callback function for catalog status updates."""
        if file is None:
            status = "Idle"
            self._catalog_statuses[catalog_id] = status
            self._catalog_progresses[catalog_id] = 0.0
            self.catalogStatusChanged.emit(catalog_id, status)
            self.progressUpdated.emit(catalog_id, 0.0)
        else:
            elapsed = file.waiting_time
            estimated_total = file.size * 0.01
            progress = min(100.0, (elapsed / estimated_total) * 100.0) \
                if estimated_total > 0 else 0.0

            status = f"Processing File #{file.id} (Size: {file.size:.2f})"
            self._catalog_statuses[catalog_id] = status
            self._catalog_progresses[catalog_id] = progress
            self.catalogStatusChanged.emit(catalog_id, status)
            self.progressUpdated.emit(catalog_id, progress)
