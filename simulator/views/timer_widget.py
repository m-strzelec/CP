"""Timer for updating waiting time displays."""

from typing import Optional

from PySide6.QtCore import QObject, QTimer, Signal, Slot
from simulator.models.file_model import FileModel


class TimerWidget(QObject):
    """Timer for updating file waiting times in UI."""
    update_waiting_times = Signal(list)

    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)
        self._timer = QTimer()
        self._timer.setInterval(800)
        self._timer.timeout.connect(self._update_times)
        self._waiting_files: list[FileModel] = []

    def start(self) -> None:
        self._timer.start()

    def stop(self) -> None:
        self._timer.stop()

    @Slot(list)
    def set_files(self, files: list[FileModel]) -> None:
        """Set the list of files to track."""
        self._waiting_files = files

    def _update_times(self) -> None:
        """Update the waiting times and emit signal."""
        if self._waiting_files:
            self.update_waiting_times.emit(self._waiting_files)
