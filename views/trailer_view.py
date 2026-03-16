from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QListWidget, QListWidgetItem,
    QPushButton, QComboBox, QMessageBox
)

from datetime import date

from viewmodels.trailer_vm import TrailerViewModel
from services.booking_service import create_booking, is_trailer_available


class TrailerView(QWidget):

    def __init__(self, user=None):
        super().__init__()

        self.user = user
        self.trailers = []

        self.setWindowTitle("Elérhető utánfutók")
        self.setMinimumSize(400, 400)

        self.viewmodel = TrailerViewModel()

        layout = QVBoxLayout()

        title = QLabel("Utánfutóink")
        layout.addWidget(title)

        # utánfutó lista
        self.list_widget = QListWidget()
        layout.addWidget(self.list_widget)

        # időszak választó
        self.period_combo = QComboBox()
        self.period_combo.addItems([
            "morning",
            "afternoon",
            "fullday"
        ])
        layout.addWidget(self.period_combo)

        # foglalás gomb
        self.book_button = QPushButton("Foglalás")
        self.book_button.clicked.connect(self.book_trailer)
        layout.addWidget(self.book_button)

        self.setLayout(layout)

        self.load_trailers()

    # ----------------------------
    # utánfutók betöltése
    # ----------------------------
    def load_trailers(self):

        self.trailers = self.viewmodel.get_trailers()

        for t in self.trailers:
            item_text = f"{t['name']} - {t['price_full_day']} Ft/nap"
            item = QListWidgetItem(item_text)
            self.list_widget.addItem(item)

    # ----------------------------
    # foglalás
    # ----------------------------
    def book_trailer(self):

        # kiválasztott utánfutó
        selected_row = self.list_widget.currentRow()

        if selected_row == -1:
            QMessageBox.warning(self, "Hiba", "Válassz utánfutót!")
            return

        # vendég ellenőrzés
        if not self.user:
            QMessageBox.warning(
                self,
                "Hiba",
                "Foglaláshoz be kell jelentkezni!"
            )
            return

        trailer = self.trailers[selected_row]

        period = self.period_combo.currentText()
        today = date.today()

        # elérhetőség ellenőrzése
        available = is_trailer_available(
            trailer["id"],
            today,
            period
        )

        if not available:
            QMessageBox.warning(
                self,
                "Hiba",
                "Az utánfutó már foglalt!"
            )
            return

        # foglalás létrehozása
        create_booking(
            self.user["id"],
            trailer["id"],
            today,
            period
        )

        QMessageBox.information(
            self,
            "Siker",
            "Foglalás sikeres!"
        )