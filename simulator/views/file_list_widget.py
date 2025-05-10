"""Widget for displaying lists of files."""

from typing import List, Optional
import time

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QTabWidget, QLineEdit, QHBoxLayout, QLabel
)
from PySide6.QtCore import Qt, Slot

from simulator.models.file_model import FileModel
from simulator.views.timer_widget import TimerWidget


class FilterableTableWidget(QWidget):
    """Table widget with filtering capabilities."""

    def __init__(self, columns: List[str], parent: Optional[QWidget] = None):
        super().__init__(parent)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        # Filter box
        filter_layout = QHBoxLayout()
        filter_label = QLabel("Filter:")
        self.filter_input = QLineEdit()
        self.filter_input.setPlaceholderText("Type to filter...")
        self.filter_input.textChanged.connect(self._apply_filter)
        filter_layout.addWidget(filter_label)
        filter_layout.addWidget(self.filter_input)

        self.layout.addLayout(filter_layout)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(len(columns))
        self.table.setHorizontalHeaderLabels(columns)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setAlternatingRowColors(True)
        self.table.setSortingEnabled(True)

        self.layout.addWidget(self.table)

        # Data storage - store raw data instead of QTableWidgetItems
        self.all_rows_data = []

    def clear_data(self):
        """Clear all data from the table."""
        self.table.setRowCount(0)
        self.all_rows_data = []

    def set_data(self, rows: List[List[QTableWidgetItem]]):
        """Set table data and apply any current filter.

        Takes a list of rows, where each row is a list of QTableWidgetItems.
        We extract and store the raw data to avoid referencing deleted Qt objects.
        """
        # Store the data in a format that doesn't reference Qt objects
        self.all_rows_data = []
        for row_data in rows:
            row_info = []
            for item in row_data:
                # Store text, edit flags, and sort data
                item_data = {
                    'text': item.text(),
                    'editable': bool(item.flags() & Qt.ItemFlag.ItemIsEditable),
                    'sort_data': item.data(Qt.ItemDataRole.UserRole) or item.data(Qt.ItemDataRole.DisplayRole)
                }
                row_info.append(item_data)
            self.all_rows_data.append(row_info)

        # Apply the filter with the new data
        self._apply_filter()

    def _apply_filter(self):
        """Filter table rows based on filter text."""
        filter_text = self.filter_input.text().lower()

        # Clear the table
        self.table.setRowCount(0)

        # Create QTableWidgetItems from our raw data
        filtered_rows = []
        for row_data in self.all_rows_data:
            # Check if this row matches the filter
            if not filter_text or any(filter_text in item['text'].lower() for item in row_data):
                # Create new QTableWidgetItems for this row
                row_items = []
                for item_data in row_data:
                    item = QTableWidgetItem(item_data['text'])
                    if not item_data['editable']:
                        item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    if item_data['sort_data'] is not None:
                        item.setData(Qt.ItemDataRole.UserRole, item_data['sort_data'])
                    row_items.append(item)
                filtered_rows.append(row_items)

        # Add filtered rows to the table
        self.table.setRowCount(len(filtered_rows))
        for row_idx, row_items in enumerate(filtered_rows):
            for col_idx, item in enumerate(row_items):
                self.table.setItem(row_idx, col_idx, item)


class FileListWidget(QWidget):
    """Widget showing waiting and processed files."""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        # Create timer updater for live wait time updates
        self.timer_updater = TimerWidget(self)
        self.timer_updater.update_waiting_times.connect(self.refresh_waiting_times)
        self.timer_updater.start()

        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Create tab widget
        self.tab_widget = QTabWidget()

        # Create waiting files table
        waiting_columns = ["File ID", "Size", "Arrival Time", "Waiting Time"]
        self.waiting_table_widget = FilterableTableWidget(waiting_columns)

        # Create processed files table
        processed_columns = [
            "File ID", "Size", "Arrival Time", "Wait Time",
            "Processing Time", "Total Time"
        ]
        self.processed_table_widget = FilterableTableWidget(processed_columns)

        # Add tables to tabs
        self.tab_widget.addTab(self.waiting_table_widget, "Waiting Files")
        self.tab_widget.addTab(self.processed_table_widget, "Processed Files")

        layout.addWidget(self.tab_widget)

    @Slot(list)
    def update_waiting_files(self, files: List[FileModel]):
        self.timer_updater.set_files(files)
        self._update_waiting_table(files)

    def _update_waiting_table(self, files: List[FileModel]):
        rows = []

        for file in files:
            row_items = []

            # File ID
            id_item = QTableWidgetItem(str(file.id))
            id_item.setFlags(id_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            row_items.append(id_item)

            # Size
            size_item = QTableWidgetItem(f"{file.size:.2f}")
            size_item.setFlags(size_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            size_item.setData(Qt.ItemDataRole.DisplayRole, file.size)  # For sorting
            row_items.append(size_item)

            # Arrival time
            arrival_time = time.strftime(
                "%H:%M:%S",
                time.localtime(file.arrival_time)
            )
            arrival_item = QTableWidgetItem(arrival_time)
            arrival_item.setFlags(arrival_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            arrival_item.setData(Qt.ItemDataRole.UserRole, file.arrival_time)  # For sorting
            row_items.append(arrival_item)

            # Waiting time
            wait_time = time.monotonic() - file.arrival_time
            wait_item = QTableWidgetItem(f"{wait_time:.2f}s")
            wait_item.setFlags(wait_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            wait_item.setData(Qt.ItemDataRole.UserRole, wait_time)  # For sorting
            row_items.append(wait_item)

            rows.append(row_items)

        self.waiting_table_widget.set_data(rows)

        # Update tab title to show count
        self.tab_widget.setTabText(0, f"Waiting Files ({len(files)})")

    @Slot(list)
    def refresh_waiting_times(self, files: List[FileModel]):
        """Update waiting times for all files in the waiting list."""
        # First, create a safer way to track files by recreating the entire data structure
        file_map = {file.id: file for file in files}
        rows = []

        # Get all rows directly from the table widget to ensure we're accessing valid objects
        for row in range(self.waiting_table_widget.table.rowCount()):
            id_item = self.waiting_table_widget.table.item(row, 0)
            if id_item is None:
                continue

            try:
                file_id = int(id_item.text())

                # Find the corresponding file
                if file_id in file_map:
                    file = file_map[file_id]

                    # Create a new row with updated data
                    row_items = []

                    # File ID (same)
                    new_id_item = QTableWidgetItem(str(file_id))
                    new_id_item.setFlags(new_id_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    row_items.append(new_id_item)

                    # Size (same)
                    size_text = self.waiting_table_widget.table.item(row, 1).text()
                    size_value = float(size_text)
                    size_item = QTableWidgetItem(size_text)
                    size_item.setFlags(size_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    size_item.setData(Qt.ItemDataRole.DisplayRole, size_value)
                    row_items.append(size_item)

                    # Arrival time (same)
                    arrival_item = QTableWidgetItem(self.waiting_table_widget.table.item(row, 2).text())
                    arrival_item.setFlags(arrival_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    arrival_item.setData(Qt.ItemDataRole.UserRole, file.arrival_time)
                    row_items.append(arrival_item)

                    # Waiting time (updated)
                    wait_time = time.monotonic() - file.arrival_time
                    wait_item = QTableWidgetItem(f"{wait_time:.2f}s")
                    wait_item.setFlags(wait_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    wait_item.setData(Qt.ItemDataRole.UserRole, wait_time)
                    row_items.append(wait_item)

                    rows.append(row_items)
            except (ValueError, AttributeError, IndexError):
                # Skip any rows with invalid data
                continue

        # Update the table with the new data
        if rows:
            self.waiting_table_widget.set_data(rows)

    @Slot(list)
    def update_processed_files(self, files: List[FileModel]):
        # Sort files by end time, newest first
        sorted_files = sorted(
            files,
            key=lambda f: f.end_time if f.end_time is not None else 0,
            reverse=True
        )

        rows = []
        for file in sorted_files:
            if file.end_time is None or file.start_time is None:
                continue

            row_items = []

            # File ID
            id_item = QTableWidgetItem(str(file.id))
            id_item.setFlags(id_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            row_items.append(id_item)

            # Size
            size_item = QTableWidgetItem(f"{file.size:.2f}")
            size_item.setFlags(size_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            size_item.setData(Qt.ItemDataRole.DisplayRole, file.size)  # For sorting
            row_items.append(size_item)

            # Arrival time (formatted)
            arrival_time = time.strftime(
                "%H:%M:%S",
                time.localtime(file.arrival_time)
            )
            arrival_item = QTableWidgetItem(arrival_time)
            arrival_item.setFlags(arrival_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            arrival_item.setData(Qt.ItemDataRole.UserRole, file.arrival_time)  # For sorting
            row_items.append(arrival_item)

            # Wait time
            wait_time = file.start_time - file.arrival_time
            wait_item = QTableWidgetItem(f"{wait_time:.2f}s")
            wait_item.setFlags(wait_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            wait_item.setData(Qt.ItemDataRole.UserRole, wait_time)  # For sorting
            row_items.append(wait_item)

            # Processing time
            proc_time = file.end_time - file.start_time
            proc_item = QTableWidgetItem(f"{proc_time:.2f}s")
            proc_item.setFlags(proc_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            proc_item.setData(Qt.ItemDataRole.UserRole, proc_time)  # For sorting
            row_items.append(proc_item)

            # Total time
            total_time = file.end_time - file.arrival_time
            total_item = QTableWidgetItem(f"{total_time:.2f}s")
            total_item.setFlags(total_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            total_item.setData(Qt.ItemDataRole.UserRole, total_time)  # For sorting
            row_items.append(total_item)

            rows.append(row_items)

        self.processed_table_widget.set_data(rows)

        # Update tab title to show count
        self.tab_widget.setTabText(1, f"Processed Files ({len(files)})")
