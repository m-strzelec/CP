"""Main view for the file scheduling simulation."""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSpinBox,
    QDoubleSpinBox, QPushButton, QGroupBox, QProgressBar, QFormLayout,
)
from PySide6.QtCore import Qt, Slot
from simulator.viewmodels.simulation_vm import SimulationViewModel


class SimulationView(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("File Processing Simulation")
        self.resize(800, 600)
        self.view_model = SimulationViewModel()

        self.catalogs_group = None
        self.catalogs_layout = None

        self.view_model.catalogStatusChanged.connect(
            self.update_catalog_status
        )
        self.view_model.progressUpdated.connect(self.update_progress)
        self.view_model.simulationStateChanged.connect(self.update_ui_state)

        self._setup_ui()

    def _setup_ui(self):
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)

        settings_group = QGroupBox("Simulation Settings")
        settings_layout = QFormLayout(settings_group)

        # Config settings
        self.num_clients_spin = QSpinBox()
        self.num_clients_spin.setRange(1, 100)
        self.num_clients_spin.setValue(self.view_model.num_clients())
        self.num_clients_spin.valueChanged.connect(
            self._on_num_clients_changed
        )

        self.num_catalogs_spin = QSpinBox()
        self.num_catalogs_spin.setRange(1, 20)
        self.num_catalogs_spin.setValue(self.view_model.num_catalogs())
        self.num_catalogs_spin.valueChanged.connect(
            self._on_num_catalogs_changed
        )

        self.client_interval_spin = QDoubleSpinBox()
        self.client_interval_spin.setRange(0.1, 10.0)
        self.client_interval_spin.setSingleStep(0.1)
        self.client_interval_spin.setValue(self.view_model.client_interval())
        self.client_interval_spin.valueChanged.connect(
            self._on_client_interval_changed
        )

        self.min_size_spin = QDoubleSpinBox()
        self.min_size_spin.setRange(0.1, 100.0)
        self.min_size_spin.setSingleStep(0.1)
        self.min_size_spin.setValue(self.view_model.min_file_size())
        self.min_size_spin.valueChanged.connect(self._on_min_size_changed)

        self.max_size_spin = QDoubleSpinBox()
        self.max_size_spin.setRange(0.1, 100.0)
        self.max_size_spin.setSingleStep(0.1)
        self.max_size_spin.setValue(self.view_model.max_file_size())
        self.max_size_spin.valueChanged.connect(self._on_max_size_changed)

        self.m_param_spin = QDoubleSpinBox()
        self.m_param_spin.setRange(0.1, 50.0)
        self.m_param_spin.setSingleStep(0.1)
        self.m_param_spin.setValue(self.view_model.m_parameter())
        self.m_param_spin.valueChanged.connect(self._on_m_param_changed)

        self.k_param_spin = QDoubleSpinBox()
        self.k_param_spin.setRange(0.0, 50.0)
        self.k_param_spin.setSingleStep(0.1)
        self.k_param_spin.setValue(self.view_model.k_parameter())
        self.k_param_spin.valueChanged.connect(self._on_k_param_changed)

        # Add settings
        settings_layout.addRow("Number of Clients:", self.num_clients_spin)
        settings_layout.addRow("Number of Catalogs:", self.num_catalogs_spin)
        settings_layout.addRow(
            "Client Interval (s):", self.client_interval_spin
        )
        settings_layout.addRow("Min File Size:", self.min_size_spin)
        settings_layout.addRow("Max File Size:", self.max_size_spin)
        settings_layout.addRow("Parameter m:", self.m_param_spin)
        settings_layout.addRow("Parameter k:", self.k_param_spin)

        # Control buttons
        self.control_layout = QHBoxLayout()
        self.start_button = QPushButton("Start Simulation")
        self.start_button.clicked.connect(self.view_model.start_simulation)
        self.stop_button = QPushButton("Stop Simulation")
        self.stop_button.clicked.connect(self.view_model.stop_simulation)
        self.stop_button.setEnabled(False)

        self.control_layout.addWidget(self.start_button)
        self.control_layout.addWidget(self.stop_button)

        self.catalogs_group = QGroupBox("Catalog Status")
        self.catalogs_layout = QVBoxLayout(self.catalogs_group)

        self.catalog_widgets: dict[int, dict[str, QWidget]] = {}
        self._recreate_catalog_widgets()

        main_layout.addWidget(settings_group)
        main_layout.addLayout(self.control_layout)
        main_layout.addWidget(self.catalogs_group)
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
            catalog_box = QGroupBox(f"Catalog #{i}")
            catalog_layout = QVBoxLayout(catalog_box)

            status_label = QLabel("Idle")
            status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

            progress_bar = QProgressBar()
            progress_bar.setRange(0, 100)
            progress_bar.setValue(0)
            progress_bar.setTextVisible(True)

            catalog_layout.addWidget(status_label)
            catalog_layout.addWidget(progress_bar)
            self.catalogs_layout.addWidget(catalog_box)
            self.catalog_widgets[i] = {
                "group": catalog_box,
                "status": status_label,
                "progress": progress_bar
            }

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

    @Slot(bool)
    def update_ui_state(self, is_running: bool) -> None:
        """Update UI controls based on simulation state."""
        self.start_button.setEnabled(not is_running)
        self.stop_button.setEnabled(is_running)
        self.num_clients_spin.setEnabled(not is_running)
        self.num_catalogs_spin.setEnabled(not is_running)
        self.client_interval_spin.setEnabled(not is_running)
        self.min_size_spin.setEnabled(not is_running)
        self.max_size_spin.setEnabled(not is_running)
        self.m_param_spin.setEnabled(not is_running)
        self.k_param_spin.setEnabled(not is_running)

    @Slot(int)
    def _on_num_clients_changed(self, value: int) -> None:
        self.view_model.set_num_clients(value)

    @Slot(int)
    def _on_num_catalogs_changed(self, value: int) -> None:
        self.view_model.set_num_catalogs(value)
        self._recreate_catalog_widgets()

    @Slot(float)
    def _on_client_interval_changed(self, value: float) -> None:
        self.view_model.set_client_interval(value)

    @Slot(float)
    def _on_min_size_changed(self, value: float) -> None:
        self.view_model.set_min_file_size(value)
        if value > self.max_size_spin.value():
            self.max_size_spin.setValue(value)

    @Slot(float)
    def _on_max_size_changed(self, value: float) -> None:
        self.view_model.set_max_file_size(value)
        if value < self.min_size_spin.value():
            self.min_size_spin.setValue(value)

    @Slot(float)
    def _on_m_param_changed(self, value: float) -> None:
        self.view_model.set_m_parameter(value)

    @Slot(float)
    def _on_k_param_changed(self, value: float) -> None:
        self.view_model.set_k_parameter(value)
