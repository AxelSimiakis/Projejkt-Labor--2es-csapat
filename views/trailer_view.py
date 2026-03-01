from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QListWidget, QListWidgetItem
)
from viewmodels.trailer_vm import TrailerViewModel


class TrailerView(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Elérhető utánfutók")
        self.setMinimumSize(400, 300)

        self.viewmodel = TrailerViewModel()

        layout = QVBoxLayout()

        title = QLabel("Utánfutóink")
        layout.addWidget(title)

        self.list_widget = QListWidget()
        layout.addWidget(self.list_widget)

        self.setLayout(layout)

        self.load_trailers()

    def load_trailers(self):
        trailers = self.viewmodel.get_trailers()

        for t in trailers:
            item_text = f"{t['name']} - {t['price_full_day']} Ft/nap"
            item = QListWidgetItem(item_text)
            self.list_widget.addItem(item)