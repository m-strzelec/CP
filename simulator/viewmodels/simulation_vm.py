"""ViewModel for the file scheduling simulation."""
import time
from typing import Optional

from PySide6.QtCore import QObject, Signal, Slot, QTimer

from simulator.models.file_model import FileModel
from simulator.models.client_model import ClientModel
from simulator.models.simulation_manager import SimulationManager


class SimulationViewModel(QObject):
    catalogStatusChanged = Signal(int, str)
    progressUpdated = Signal(int, float)
    simulationStateChanged = Signal(bool)
    waitingClientsUpdated = Signal(list)
    processedFilesUpdated = Signal(list)

    def __init__(self):
        super().__init__()

        # Settings
        self._num_catalogs: int = 5
        self._client_interval: float = 2.0
        self._min_files_per_client: int = 1
        self._max_files_per_client: int = 5
        self._min_file_size: int = 1
        self._max_file_size: int = 1000
        self._auto_mode: bool = True
        self._manual_files: int = 3

        self._simulation_manager: Optional[SimulationManager] = None
        self._is_running: bool = False
        self._catalog_statuses: dict[int, str] = {}
        self._catalog_progresses: dict[int, float] = {}

        self._waiting_clients: list[ClientModel] = []
        self._processed_files: list[FileModel] = []

        self._catalog_files: dict[int, int] = {}
        self._active_files: dict[int, dict] = {}

        self._progress_timer = QTimer(self)
        self._progress_timer.timeout.connect(self._update_progress)
        self._progress_timer.setInterval(100)

    def num_catalogs(self) -> int:
        return self._num_catalogs

    def set_num_catalogs(self, value: int) -> None:
        if value > 0:
            self._num_catalogs = value
            self._catalog_statuses = {i: "Idle" for i in range(value)}
            self._catalog_progresses = {i: 0.0 for i in range(value)}

    def client_interval(self) -> float:
        return self._client_interval

    def set_client_interval(self, value: float) -> None:
        if value > 0:
            self._client_interval = value

    def min_files_per_client(self) -> int:
        return self._min_files_per_client

    def set_min_files_per_client(self, value: int) -> None:
        if 1 <= value <= self._max_files_per_client:
            self._min_files_per_client = value

    def max_files_per_client(self) -> int:
        return self._max_files_per_client

    def set_max_files_per_client(self, value: int) -> None:
        if value >= self._min_files_per_client:
            self._max_files_per_client = value

    def min_file_size(self) -> int:
        return self._min_file_size

    def set_min_file_size(self, value: int) -> None:
        if 0 < value <= self._max_file_size:
            self._min_file_size = value

    def max_file_size(self) -> int:
        return self._max_file_size

    def set_max_file_size(self, value: int) -> None:
        if value >= self._min_file_size:
            self._max_file_size = value

    def auto_mode(self) -> bool:
        return self._auto_mode

    def set_auto_mode(self, value: bool) -> None:
        self._auto_mode = value
        
    def manual_files(self) -> int:
        return self._manual_files
    
    def set_manual_files(self, value: int) -> None:
        self._manual_files = value

    def is_running(self) -> bool:
        return self._is_running

    def waiting_clients(self) -> list[ClientModel]:
        return self._waiting_clients

    def processed_files(self) -> list[FileModel]:
        return self._processed_files

    @Slot()
    def start_simulation(self) -> None:
        if self._is_running:
            return
        self._catalog_statuses = {i: "Idle" for i in range(self._num_catalogs)}
        self._catalog_progresses = {i: 0.0 for i in range(self._num_catalogs)}
        self._catalog_files = {}
        self._waiting_clients = []
        self._processed_files = []
        self._active_files = {}

        self.waitingClientsUpdated.emit([])
        self.processedFilesUpdated.emit([])

        self._simulation_manager = SimulationManager(
            num_catalogs=self._num_catalogs,
            client_interval=self._client_interval,
            files_per_client_range=(self._min_files_per_client, self._max_files_per_client),
            size_range=(self._min_file_size, self._max_file_size),
            m=self._num_catalogs,
            k=self._num_catalogs,
            dispatch_callback=self._catalog_callback,
            client_creation_callback=self._client_created_callback,
            file_processed_callback=self._file_processed_callback,
            auto_mode=self._auto_mode
        )
        self._simulation_manager.start()
        self._is_running = True
        self._progress_timer.start()
        self.simulationStateChanged.emit(True)

    @Slot()
    def stop_simulation(self) -> None:
        if not self._is_running or self._simulation_manager is None:
            return
        self._simulation_manager.stop()
        self._is_running = False
        self._progress_timer.stop()
        self._active_files = {}
        self.simulationStateChanged.emit(False)
        for catalog_id in range(self._num_catalogs):
            self._catalog_statuses[catalog_id] = "Stopped"
            self._catalog_progresses[catalog_id] = 0.0
            self.catalogStatusChanged.emit(catalog_id, "Stopped")
            self.progressUpdated.emit(catalog_id, 0.0)

    @Slot()
    def add_manual_client(self) -> None:
        if self._is_running and self._simulation_manager:
            self._simulation_manager.add_manual_client(self._manual_files)

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
            if catalog_id in self._active_files:
                del self._active_files[catalog_id]
            self.catalogStatusChanged.emit(catalog_id, status)
            self.progressUpdated.emit(catalog_id, 0.0)
        else:
            self._catalog_files[file.id] = catalog_id
            file.catalog_id = catalog_id

            self._active_files[catalog_id] = {
                'file': file,
                'start_time': time.monotonic(),
                'estimated_total': file.size * 0.01
            }

            status = f"Processing File #{file.id} (Size: {file.size:.2f})"
            self._catalog_statuses[catalog_id] = status
            self._catalog_progresses[catalog_id] = 0.0
            self.catalogStatusChanged.emit(catalog_id, status)
            self.progressUpdated.emit(catalog_id, 0.0)

    def _update_progress(self) -> None:
        """Update progress for all active file processing tasks."""
        current_time = time.monotonic()
        for catalog_id, file_info in list(self._active_files.items()):
            elapsed = current_time - file_info['start_time']
            estimated_total = file_info['estimated_total']

            progress = min(100.0, (elapsed / estimated_total) * 100.0) \
                if estimated_total > 0 else 0.0

            self._catalog_progresses[catalog_id] = progress
            self.progressUpdated.emit(catalog_id, progress)

        # Update waiting clients list
        if self._simulation_manager:
            self._waiting_clients = self._simulation_manager.get_waiting_clients()
            self.waitingClientsUpdated.emit(self._waiting_clients)

    def _client_created_callback(self, client: ClientModel) -> None:
        if self._simulation_manager:
            self._waiting_clients = self._simulation_manager.get_waiting_clients()
            self.waitingClientsUpdated.emit(self._waiting_clients)

    def _file_processed_callback(self, file: FileModel) -> None:
        # Update waiting clients list
        if self._simulation_manager:
            self._waiting_clients = self._simulation_manager.get_waiting_clients()

        if file.id in self._catalog_files:
            file.catalog_id = self._catalog_files[file.id]

        self._processed_files.append(file)
        self.waitingClientsUpdated.emit(self._waiting_clients)
        self.processedFilesUpdated.emit(self._processed_files)
