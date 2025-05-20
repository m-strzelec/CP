"""ViewModel for the file scheduling simulation."""
import time
from typing import Optional

from PySide6.QtCore import QObject, Signal, Slot, QTimer

from simulator.models.file_model import FileModel
from simulator.models.simulation_manager import SimulationManager


class SimulationViewModel(QObject):
    catalogStatusChanged = Signal(int, str)
    progressUpdated = Signal(int, float)
    simulationStateChanged = Signal(bool)
    waitingFilesUpdated = Signal(list)
    processedFilesUpdated = Signal(list)

    def __init__(self):
        super().__init__()

        # Settings
        self._num_clients: int = 3
        self._num_catalogs: int = 5
        self._client_interval: float = 1.0
        self._min_file_size: float = 1.0
        self._max_file_size: float = 300.0

        self._simulation_manager: Optional[SimulationManager] = None
        self._is_running: bool = False
        self._catalog_statuses: dict[int, str] = {}
        self._catalog_progresses: dict[int, float] = {}

        self._waiting_files: list[FileModel] = []
        self._processed_files: list[FileModel] = []

        self._catalog_files: dict[int, int] = {}
        self._active_files: dict[int, dict] = {}

        self._progress_timer = QTimer(self)
        self._progress_timer.timeout.connect(self._update_progress)
        self._progress_timer.setInterval(100)

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
            self._catalog_statuses = {i: "Idle" for i in range(value)}
            self._catalog_progresses = {i: 0.0 for i in range(value)}

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

    def is_running(self) -> bool:
        return self._is_running

    def waiting_files(self) -> list[FileModel]:
        return self._waiting_files

    def processed_files(self) -> list[FileModel]:
        return self._processed_files

    @Slot()
    def start_simulation(self) -> None:
        if self._is_running:
            return
        self._catalog_statuses = {i: "Idle" for i in range(self._num_catalogs)}
        self._catalog_progresses = {i: 0.0 for i in range(self._num_catalogs)}
        self._catalog_files = {}
        self._waiting_files = []
        self._processed_files = []
        self._active_files = {}

        self.waitingFilesUpdated.emit([])
        self.processedFilesUpdated.emit([])

        self._simulation_manager = SimulationManager(
            num_clients=self._num_clients,
            num_catalogs=self._num_catalogs,
            client_interval=self._client_interval,
            size_range=(self._min_file_size, self._max_file_size),
            m=self._num_clients,
            k=self._num_catalogs,
            dispatch_callback=self._catalog_callback,
            file_creation_callback=self._file_created_callback,
            file_processed_callback=self._file_processed_callback
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

    def _file_created_callback(self, file: FileModel) -> None:
        self._waiting_files.append(file)
        self.waitingFilesUpdated.emit(self._waiting_files)

    def _file_processed_callback(self, file: FileModel) -> None:
        self._waiting_files = [
            f for f in self._waiting_files if f.id != file.id
        ]

        if file.id in self._catalog_files:
            file.catalog_id = self._catalog_files[file.id]

        self._processed_files.append(file)
        self.waitingFilesUpdated.emit(self._waiting_files)
        self.processedFilesUpdated.emit(self._processed_files)
