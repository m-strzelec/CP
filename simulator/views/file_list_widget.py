"""Widget for displaying lists of files."""

from typing import Optional

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget,
    QTableWidgetItem, QHeaderView, QTabWidget
)
from PySide6.QtCore import Qt, Slot

from simulator.models.file_model import FileModel
from simulator.views.timer_widget import TimerWidget


class FileListWidget(QWidget):
    """Widget showing waiting and processed files."""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self.file_map = {}

        # Create timer updater for live wait time updates
        self.timer_updater = TimerWidget(self)
        self.timer_updater.update_waiting_times.connect(self.refresh_waiting_times)
        self.timer_updater.start()

        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        # Create tab widget
        self.tab_widget = QTabWidget()

        # Create waiting files table
        self.waiting_table = QTableWidget()
        self.waiting_table.setColumnCount(3)
        self.waiting_table.setHorizontalHeaderLabels(
            ["Client ID", "Size", "Waiting Time"]
        )
        self.waiting_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        # Enable sorting by clicking on headers
        self.waiting_table.setSortingEnabled(True)
        self.waiting_table.verticalHeader().setVisible(False)

        # Create processed files table
        self.processed_table = QTableWidget()
        self.processed_table.setColumnCount(6)
        self.processed_table.setHorizontalHeaderLabels([
            "Client ID", "Catalog ID", "Size",
            "Wait Time", "Processing Time", "Total Time"
        ])
        self.processed_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        # Enable sorting by clicking on headers
        self.processed_table.setSortingEnabled(True)
        self.processed_table.verticalHeader().setVisible(False)

        self.tab_widget.addTab(self.waiting_table, "Waiting Files")
        self.tab_widget.addTab(self.processed_table, "Processed Files")

        self.waiting_table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.waiting_table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.processed_table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.processed_table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        layout.addWidget(self.tab_widget)

    @Slot(list)
    def update_waiting_files(self, files: list[FileModel]):
        self.timer_updater.set_files(files)
        self._update_waiting_table(files)

    def _update_waiting_table(self, files: list[FileModel]):
        # Store current sort column and order
        sort_column = self.waiting_table.horizontalHeader().sortIndicatorSection()
        sort_order = self.waiting_table.horizontalHeader().sortIndicatorOrder()

        # Temporarily disable sorting to prevent slowdowns during update
        self.waiting_table.setSortingEnabled(False)

        self.file_map = {file.id: file for file in files}
        self.waiting_table.setRowCount(len(files))

        for row, file in enumerate(files):
            # Client ID
            client_id_item = QTableWidgetItem(f"#{file.client_id}")
            client_id_item.setFlags(client_id_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            client_id_item.setData(Qt.ItemDataRole.UserRole, file.client_id)
            self.waiting_table.setItem(row, 0, client_id_item)

            # Size
            size_item = QTableWidgetItem(f"{file.size:.2f}")
            size_item.setFlags(size_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.waiting_table.setItem(row, 1, size_item)

            # Waiting time
            wait_item = QTableWidgetItem(f"{file.waiting_time:.2f}s")
            wait_item.setFlags(wait_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.waiting_table.setItem(row, 2, wait_item)

        # Re-enable sorting
        self.waiting_table.setSortingEnabled(True)

        # Update tab title to show count
        self.tab_widget.setTabText(0, f"Waiting Files ({len(files)})")

        if sort_column >= 0:
            self.waiting_table.sortItems(sort_column, sort_order)

    @Slot(list)
    def refresh_waiting_times(self, files: list[FileModel]):
        # Disable sorting temporarily for better performance
        self.waiting_table.setSortingEnabled(False)
        id_to_file = {f.id: f for f in files}

        for row in range(self.waiting_table.rowCount()):
            id_item = self.waiting_table.item(row, 0)
            if not id_item:
                continue

            file_id = id_item.data(Qt.ItemDataRole.UserRole)
            file = id_to_file.get(file_id)

            if file:
                wait_item = self.waiting_table.item(row, 2)
                if wait_item:
                    wait_item.setText(f"{file.waiting_time:.2f}s")

        # Re-enable sorting
        self.waiting_table.setSortingEnabled(True)

    @Slot(list)
    def update_processed_files(self, files: list[FileModel]):
        # Store current sort column and order
        sort_column = self.processed_table.horizontalHeader().sortIndicatorSection()
        sort_order = self.processed_table.horizontalHeader().sortIndicatorOrder()

        # Temporarily disable sorting
        self.processed_table.setSortingEnabled(False)

        self.processed_table.setRowCount(len(files))

        for row, file in enumerate(files):
            if not all([file.arrival_time, file.start_time, file.end_time]):
                continue

            # Client ID
            client_id_item = QTableWidgetItem(f"#{file.client_id}")
            client_id_item.setFlags(client_id_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.processed_table.setItem(row, 0, client_id_item)

            catalog_id = getattr(file, "catalog_id", None)
            catalog_text = f"#{catalog_id}" if catalog_id is not None else "Unknown"
            catalog_item = QTableWidgetItem(catalog_text)
            catalog_item.setFlags(catalog_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.processed_table.setItem(row, 1, catalog_item)

            # Size
            size_item = QTableWidgetItem(f"{file.size:.2f}")
            size_item.setFlags(size_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.processed_table.setItem(row, 2, size_item)

            # Wait time
            wait_item = QTableWidgetItem(f"{file.waiting_time:.2f}s")
            wait_item.setFlags(wait_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.processed_table.setItem(row, 3, wait_item)

            # Processing time
            proc_item = QTableWidgetItem(f"{file.processing_time:.2f}s")
            proc_item.setFlags(proc_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.processed_table.setItem(row, 4, proc_item)

            # Total time
            total_time = file.end_time - file.arrival_time
            total_item = QTableWidgetItem(f"{total_time:.2f}s")
            total_item.setFlags(total_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.processed_table.setItem(row, 5, total_item)

        # Re-enable sorting
        self.processed_table.setSortingEnabled(True)

        # Update tab title to show count
        self.tab_widget.setTabText(1, f"Processed Files ({len(files)})")

        if sort_column >= 0:
            self.processed_table.sortItems(sort_column, sort_order)
