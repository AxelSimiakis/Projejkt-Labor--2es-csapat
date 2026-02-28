from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QListWidget
)
from viewmodels.trailer_list_vm import TrailerListViewModel


class TrailerListView(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Elérhető utánfutók")
        self.setMinimumWidth(400)

        self.viewmodel = TrailerListViewModel()

        layout = QVBoxLayout()

        self.list_widget = QListWidget()

        trailers = self.viewmodel.get_all_trailers()
        for trailer in trailers:
            self.list_widget.addItem(
                f"{trailer.name} | "
                f"Délelőtt: {trailer.price_morning} Ft | "
                f"Délután: {trailer.price_afternoon} Ft | "
                f"Egész nap: {trailer.price_full_day} Ft"
    )

        layout.addWidget(QLabel("Elérhető utánfutók:"))
        layout.addWidget(self.list_widget)

        self.setLayout(layout)