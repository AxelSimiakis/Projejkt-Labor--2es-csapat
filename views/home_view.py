from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt


class HomeView(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()

        label = QLabel("Foglaláshoz, regisztráljon vagy lépjen be!")
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("font-size: 20px; margin-top: 100px;")

        layout.addWidget(label)
        self.setLayout(layout)