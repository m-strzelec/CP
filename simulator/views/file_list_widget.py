"""Widget for displaying lists of clients and their files."""

from typing import Optional
from datetime import datetime

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget,
    QTableWidgetItem, QHeaderView, QTabWidget
)
from PySide6.QtCore import Qt, Slot

from simulator.models.file_model import FileModel
from simulator.models.client_model import ClientModel


class FileListWidget(QWidget):
    """Widget showing waiting clients and processed files."""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.client_map = {}
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        # Create tab widget
        self.tab_widget = QTabWidget()

        # Create waiting clients table
        self.waiting_table = QTableWidget()
        self.waiting_table.setColumnCount(3)
        self.waiting_table.setHorizontalHeaderLabels(
            ["Client ID", "File Sizes", "Arrival Time"]
        )
        self.waiting_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.waiting_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.waiting_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
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

        self.tab_widget.addTab(self.waiting_table, "Waiting Clients")
        self.tab_widget.addTab(self.processed_table, "Processed Files")

        self.waiting_table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.waiting_table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.processed_table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.processed_table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        layout.addWidget(self.tab_widget)

    @Slot(list)
    def update_waiting_clients(self, clients: list[ClientModel]):
        self._update_waiting_table(clients)

    def _update_waiting_table(self, clients: list[ClientModel]):
        # Store current sort column and order
        sort_column = self.waiting_table.horizontalHeader().sortIndicatorSection()
        sort_order = self.waiting_table.horizontalHeader().sortIndicatorOrder()

        # Temporarily disable sorting to prevent slowdowns during update
        self.waiting_table.setSortingEnabled(False)

        self.client_map = {client.id: client for client in clients}
        self.waiting_table.setRowCount(len(clients))

        for row, client in enumerate(clients):
            # Client ID
            client_id_item = QTableWidgetItem(f"#{client.id}")
            client_id_item.setFlags(client_id_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            client_id_item.setData(Qt.ItemDataRole.UserRole, client.id)
            self.waiting_table.setItem(row, 0, client_id_item)

            # File sizes (comma-separated)
            sizes_item = QTableWidgetItem(client.file_sizes_str)
            sizes_item.setFlags(sizes_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.waiting_table.setItem(row, 1, sizes_item)

            # Arrival time (formatted)
            arrival_time = datetime.fromtimestamp(client.arrival_time).strftime("%H:%M:%S")
            arrival_item = QTableWidgetItem(arrival_time)
            arrival_item.setFlags(arrival_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.waiting_table.setItem(row, 2, arrival_item)

        # Re-enable sorting
        self.waiting_table.setSortingEnabled(True)

        # Update tab title to show count
        self.tab_widget.setTabText(0, f"Waiting Clients ({len(clients)})")

        if sort_column >= 0:
            self.waiting_table.sortItems(sort_column, sort_order)

    @Slot(list)
    def update_processed_files(self, files: list[FileModel]):
        """Update the processed files table."""
        # Store current sort column and order
        sort_column = self.processed_table.horizontalHeader().sortIndicatorSection()
        sort_order = self.processed_table.horizontalHeader().sortIndicatorOrder()

        # Temporarily disable sorting to prevent slowdowns during update
        self.processed_table.setSortingEnabled(False)

        self.processed_table.setRowCount(len(files))

        for row, file in enumerate(files):
            # Client ID
            client_id_item = QTableWidgetItem(f"#{file.client_id}")
            client_id_item.setFlags(client_id_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.processed_table.setItem(row, 0, client_id_item)

            # Catalog ID
            catalog_id_item = QTableWidgetItem(f"#{file.catalog_id}" if file.catalog_id is not None else "N/A")
            catalog_id_item.setFlags(catalog_id_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.processed_table.setItem(row, 1, catalog_id_item)

            # Size
            size_item = QTableWidgetItem(f"{file.size}")
            size_item.setFlags(size_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.processed_table.setItem(row, 2, size_item)

            # Wait time
            wait_time = file.waiting_time if file.start_time else 0.0
            wait_item = QTableWidgetItem(f"{wait_time:.2f}s")
            wait_item.setFlags(wait_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.processed_table.setItem(row, 3, wait_item)

            # Processing time
            proc_time = file.processing_time
            proc_item = QTableWidgetItem(f"{proc_time:.2f}s")
            proc_item.setFlags(proc_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.processed_table.setItem(row, 4, proc_item)

            # Total time
            total_time = wait_time + proc_time
            total_item = QTableWidgetItem(f"{total_time:.2f}s")
            total_item.setFlags(total_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.processed_table.setItem(row, 5, total_item)

        # Re-enable sorting
        self.processed_table.setSortingEnabled(True)

        # Update tab title to show count
        self.tab_widget.setTabText(1, f"Processed Files ({len(files)})")

        if sort_column >= 0:
            self.processed_table.sortItems(sort_column, sort_order)
