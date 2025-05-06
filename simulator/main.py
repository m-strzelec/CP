import sys
from PySide6.QtWidgets import QApplication
from simulator.views.simulation_view import SimulationView


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SimulationView()
    window.show()
    sys.exit(app.exec())
