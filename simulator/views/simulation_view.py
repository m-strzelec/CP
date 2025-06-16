"""Main view for the file scheduling simulation."""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSpinBox,
    QDoubleSpinBox, QPushButton, QGroupBox, QProgressBar, QFormLayout,
    QSplitter, QScrollArea, QCheckBox
)
from PySide6.QtCore import Qt, Slot

from simulator.viewmodels.simulation_vm import SimulationViewModel
from simulator.views.file_list_widget import FileListWidget


class SimulationView(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("File Processing Simulation")
        self.resize(1000, 700)
        self.view_model = SimulationViewModel()

        self.catalogs_group = None
        self.catalogs_layout = None
        self.file_list_widget = None

        self.view_model.catalogStatusChanged.connect(
            self.update_catalog_status
        )
        self.view_model.progressUpdated.connect(self.update_progress)
        self.view_model.simulationStateChanged.connect(self.update_ui_state)

        self.view_model.waitingClientsUpdated.connect(self.update_waiting_clients)
        self.view_model.processedFilesUpdated.connect(self.update_processed_files)

        self._setup_ui()

    def _setup_ui(self):
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)

        # Control panel at the top
        control_panel = QWidget()
        control_panel_layout = QVBoxLayout(control_panel)
        control_panel_layout.setContentsMargins(0, 0, 0, 0)
        control_panel_layout.setSpacing(5)

        # Settings and control area
        settings_and_control = QWidget()
        settings_and_control_layout = QHBoxLayout(settings_and_control)
        settings_and_control_layout.setSpacing(10)
        settings_group = QGroupBox("Simulation Settings")
        settings_layout = QFormLayout(settings_group)
        settings_layout.setVerticalSpacing(5)

        # Config settings
        self.num_catalogs_spin = QSpinBox()
        self.num_catalogs_spin.setRange(1, 20)
        self.num_catalogs_spin.setValue(self.view_model.num_catalogs())
        self.num_catalogs_spin.valueChanged.connect(
            self._on_num_catalogs_changed
        )

        self.client_interval_spin = QDoubleSpinBox()
        self.client_interval_spin.setRange(0.1, 100.0)
        self.client_interval_spin.setSingleStep(0.1)
        self.client_interval_spin.setValue(self.view_model.client_interval())
        self.client_interval_spin.valueChanged.connect(
            self._on_client_interval_changed
        )

        self.min_files_spin = QSpinBox()
        self.min_files_spin.setRange(1, 50)
        self.min_files_spin.setValue(self.view_model.min_files_per_client())
        self.min_files_spin.valueChanged.connect(self._on_min_files_changed)

        self.max_files_spin = QSpinBox()
        self.max_files_spin.setRange(1, 50)
        self.max_files_spin.setValue(self.view_model.max_files_per_client())
        self.max_files_spin.valueChanged.connect(self._on_max_files_changed)

        self.min_size_spin = QDoubleSpinBox()
        self.min_size_spin.setRange(0.1, 10000)
        self.min_size_spin.setSingleStep(1)
        self.min_size_spin.setValue(self.view_model.min_file_size())
        self.min_size_spin.valueChanged.connect(self._on_min_size_changed)

        self.max_size_spin = QDoubleSpinBox()
        self.max_size_spin.setRange(1, 10000)
        self.max_size_spin.setSingleStep(1)
        self.max_size_spin.setValue(self.view_model.max_file_size())
        self.max_size_spin.valueChanged.connect(self._on_max_size_changed)

        # Auto mode checkbox
        self.auto_mode_checkbox = QCheckBox("Auto Mode")
        self.auto_mode_checkbox.setChecked(self.view_model.auto_mode())
        self.auto_mode_checkbox.toggled.connect(self._on_auto_mode_changed)

        # Add settings
        settings_layout.addRow("Number of Catalogs:", self.num_catalogs_spin)
        settings_layout.addRow("Client Interval (s):", self.client_interval_spin)
        settings_layout.addRow("Min Files per Client:", self.min_files_spin)
        settings_layout.addRow("Max Files per Client:", self.max_files_spin)
        settings_layout.addRow("Min File Size:", self.min_size_spin)
        settings_layout.addRow("Max File Size:", self.max_size_spin)
        settings_layout.addRow("", self.auto_mode_checkbox)

        # Control buttons
        control_group = QGroupBox("Controls")
        control_layout = QVBoxLayout(control_group)
        control_layout.setSpacing(5)

        self.start_button = QPushButton("Start Simulation")
        self.start_button.clicked.connect(self.view_model.start_simulation)
        self.stop_button = QPushButton("Stop Simulation")
        self.stop_button.clicked.connect(self.view_model.stop_simulation)
        self.stop_button.setEnabled(False)

        # Manual client addition
        manual_layout = QHBoxLayout()
        self.manual_files_spin = QSpinBox()
        self.manual_files_spin.setRange(1, 50)
        self.manual_files_spin.setSingleStep(1)
        self.manual_files_spin.setValue(self.view_model.manual_files())
        self.manual_files_spin.valueChanged.connect(self._on_manual_files_changed)
        self.manual_files_spin.setEnabled(False)
        
        self.add_client_button = QPushButton("Add Client")
        self.add_client_button.clicked.connect(self.view_model.add_manual_client)
        self.add_client_button.setEnabled(False)

        manual_layout.addWidget(QLabel("Files:"))
        manual_layout.addWidget(self.manual_files_spin)
        manual_layout.addWidget(self.add_client_button)

        control_layout.addWidget(self.start_button)
        control_layout.addWidget(self.stop_button)
        control_layout.addLayout(manual_layout)

        settings_and_control_layout.addWidget(settings_group)
        settings_and_control_layout.addWidget(control_group)

        control_panel_layout.addWidget(settings_and_control)

        # Main content area with horizontal splitter
        content_splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left side - Catalog Status
        catalogs_scroll_area = QScrollArea()
        catalogs_scroll_area.setWidgetResizable(True)
        catalogs_scroll_area.setMaximumWidth(400)
        catalogs_container = QWidget()
        catalogs_container_layout = QVBoxLayout(catalogs_container)
        catalogs_container_layout.setContentsMargins(5, 5, 5, 5)

        self.catalogs_group = QGroupBox("Catalog Status")
        self.catalogs_layout = QVBoxLayout(self.catalogs_group)
        self.catalogs_layout.setSpacing(5)

        self.catalog_widgets: dict[int, dict[str, QWidget]] = {}
        self._recreate_catalog_widgets()

        catalogs_container_layout.addWidget(self.catalogs_group)
        catalogs_container_layout.addStretch()
        catalogs_scroll_area.setWidget(catalogs_container)

        # Right side - File Lists
        self.file_list_widget = FileListWidget()

        # Add widgets to content splitter
        content_splitter.addWidget(catalogs_scroll_area)
        content_splitter.addWidget(self.file_list_widget)
        content_splitter.setSizes([400, 600])
        vertical_splitter = QSplitter(Qt.Orientation.Vertical)
        vertical_splitter.addWidget(control_panel)
        vertical_splitter.addWidget(content_splitter)
        vertical_splitter.setSizes([100, 600])

        main_layout.addWidget(vertical_splitter)
        self.setCentralWidget(main_widget)

    def _recreate_catalog_widgets(self) -> None:
        """Create or recreate catalog status widgets."""
        if self.catalogs_layout:
            for i in reversed(range(self.catalogs_layout.count())):
                item = self.catalogs_layout.itemAt(i)
                if item and item.widget():
                    item.widget().setParent(None)

        self.catalog_widgets.clear()

        # Create widgets for each catalog
        for i in range(self.view_model.num_catalogs()):
            catalog_box = QGroupBox(f"Catalog #{i+1}")
            
            catalog_layout = QVBoxLayout(catalog_box)
            catalog_layout.setSpacing(2)

            status_label = QLabel("Idle")
            status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            status_label.setMaximumHeight(18)

            progress_bar = QProgressBar()
            progress_bar.setRange(0, 100)
            progress_bar.setValue(0)
            progress_bar.setTextVisible(True)
            progress_bar.setFormat("%p%")
            progress_bar.setMaximumHeight(18)

            catalog_layout.addWidget(status_label)
            catalog_layout.addWidget(progress_bar)
            self.catalogs_layout.insertWidget(i, catalog_box)
            self.catalog_widgets[i] = {
                "group": catalog_box,
                "status": status_label,
                "progress": progress_bar,
            }

    def update_processed_files(self, files: list) -> None:
        if self.file_list_widget:
            self.file_list_widget.update_processed_files(files)

    @Slot(int, str)
    def update_catalog_status(self, catalog_id: int, status: str) -> None:
        """Update status display for a catalog."""
        if catalog_id in self.catalog_widgets:
            label = self.catalog_widgets[catalog_id]["status"]
            if isinstance(label, QLabel):
                label.setText(status)

    @Slot(int, float)
    def update_progress(self, catalog_id: int, progress: float) -> None:
        """Update the progress bar for a catalog."""
        if catalog_id in self.catalog_widgets:
            progress_bar = self.catalog_widgets[catalog_id]["progress"]
            if isinstance(progress_bar, QProgressBar):
                progress_bar.setValue(int(progress))
                progress_bar.setFormat("%.1f%%" % progress)

    @Slot(list)
    def update_waiting_clients(self, clients: list) -> None:
        """Update the waiting clients files view."""
        if self.file_list_widget:
            self.file_list_widget.update_waiting_clients(clients)

    @Slot(bool)
    def update_ui_state(self, is_running: bool) -> None:
        """Update UI controls based on simulation state."""
        self.start_button.setEnabled(not is_running)
        self.stop_button.setEnabled(is_running)
        self.add_client_button.setEnabled(
            is_running and not self.auto_mode_checkbox.isChecked()
        )
        self.num_catalogs_spin.setEnabled(not is_running)
        self.client_interval_spin.setEnabled(not is_running)
        self.min_files_spin.setEnabled(not is_running)
        self.max_files_spin.setEnabled(not is_running)
        self.min_size_spin.setEnabled(not is_running)
        self.max_size_spin.setEnabled(not is_running)
        self.auto_mode_checkbox.setEnabled(not is_running)
        self.manual_files_spin.setEnabled(
            is_running and not self.auto_mode_checkbox.isChecked()
        )

    @Slot(int)
    def _on_num_catalogs_changed(self, value: int) -> None:
        self.view_model.set_num_catalogs(value)
        self._recreate_catalog_widgets()

    @Slot(float)
    def _on_client_interval_changed(self, value: float) -> None:
        self.view_model.set_client_interval(value)

    @Slot(int)
    def _on_min_files_changed(self, value: int) -> None:
        self.view_model.set_min_files_per_client(value)

    @Slot(int)
    def _on_max_files_changed(self, value: int) -> None:
        self.view_model.set_max_files_per_client(value)

    @Slot(float)
    def _on_min_size_changed(self, value: int) -> None:
        self.view_model.set_min_file_size(value)
        if value > self.max_size_spin.value():
            self.max_size_spin.setValue(value)

    @Slot(float)
    def _on_max_size_changed(self, value: int) -> None:
        self.view_model.set_max_file_size(value)
        if value < self.min_size_spin.value():
            self.min_size_spin.setValue(value)

    @Slot(bool)
    def _on_auto_mode_changed(self, checked: bool) -> None:
        self.view_model.set_auto_mode(checked)
        self.add_client_button.setEnabled(
            self.view_model.is_running() and not checked
        )
        
    @Slot(int)
    def _on_manual_files_changed(self, value: int) -> None:
        self.view_model.set_manual_files(value)
