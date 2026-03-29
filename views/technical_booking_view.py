from PySide6.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QComboBox, QDateEdit, QGridLayout
)
from PySide6.QtCore import QDate, Qt

from services.technical_booking_service import create_technical_booking
from core.toast import Toast


class TechnicalBooking(QDialog):
    def __init__(self, main_window, trailers):
        super().__init__()
        self.main_window = main_window
        self.trailers = trailers

        self.setWindowTitle("Technikai foglalás")
        self.setMinimumWidth(650)

        # ===== STYLE =====
        self.setStyleSheet("""
        QDialog {
            background-color: #1f2937;
            border-radius: 14px;
        }

        QLabel {
            color: #e5e7eb;
            font-size: 13px;
        }

        QLineEdit, QComboBox, QDateEdit {
            background-color: #111827;
            color: white;
            border: 1px solid #374151;
            border-radius: 8px;
            padding: 8px;
        }

        QLineEdit:focus, QComboBox:focus, QDateEdit:focus {
            border: 1px solid #16a34a;
        }

        QPushButton {
            border-radius: 8px;
            padding: 10px;
            font-weight: bold;
        }
        """)

        # ===== MAIN =====
        main_layout = QVBoxLayout()
        container = QWidget()
        container_layout = QVBoxLayout()
        container_layout.setContentsMargins(20, 20, 20, 20)
        container_layout.setSpacing(12)
        container.setLayout(container_layout)

        main_layout.addWidget(container)
        self.setLayout(main_layout)

        # ===== TITLE =====
        title = QLabel("Technikai foglalás")
        title.setStyleSheet("font-size:18px; font-weight:bold; color:white;")
        container_layout.addWidget(title)

        # ===== INPUTOK =====
        self.first_name_input = QLineEdit()
        self.last_name_input = QLineEdit()
        self.phone_input = QLineEdit()
        self.email_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)

        self.country_input = QLineEdit()
        self.zip_input = QLineEdit()
        self.city_input = QLineEdit()
        self.street_input = QLineEdit()
        self.house_number_input = QLineEdit()

        self.first_name_input.setPlaceholderText("Vezetéknév")
        self.last_name_input.setPlaceholderText("Keresztnév")
        self.phone_input.setPlaceholderText("+36 70 000 0000")
        self.email_input.setPlaceholderText("Email")
        self.password_input.setPlaceholderText("Jelszó")

        self.country_input.setPlaceholderText("Ország")
        self.zip_input.setPlaceholderText("Irányítószám")
        self.city_input.setPlaceholderText("Város")
        self.street_input.setPlaceholderText("Utca")
        self.house_number_input.setPlaceholderText("Házszám")

        # ===== FOGLALÁS =====
        self.trailer_combo = QComboBox()
        for t in trailers:
            self.trailer_combo.addItem(t.name, t.id)

        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(QDate.currentDate())

        self.period_combo = QComboBox()
        self.period_combo.addItems(["morning", "afternoon", "full_day"])

        # ===== GRID (2 OSZLOP) =====
        grid = QGridLayout()
        grid.setSpacing(10)

        def add(row, col, label, widget):
            grid.addWidget(QLabel(label), row, col)
            grid.addWidget(widget, row, col + 1)

        # BAL OSZLOP
        add(0, 0, "Vezetéknév", self.first_name_input)
        add(1, 0, "Keresztnév", self.last_name_input)
        add(2, 0, "Telefon", self.phone_input)
        add(3, 0, "Email", self.email_input)
        add(4, 0, "Jelszó", self.password_input)
        add(5, 0, "Ország", self.country_input)

        # JOBB OSZLOP
        add(0, 2, "Város", self.city_input)
        add(1, 2, "Utca", self.street_input)
        add(2, 2, "Házszám", self.house_number_input)
        add(3, 2, "Irányítószám", self.zip_input)
        add(4, 2, "Utánfutó", self.trailer_combo)
        add(5, 2, "Dátum", self.date_input)
        add(6, 2, "Időszak", self.period_combo)

        grid.setColumnStretch(1, 1)
        grid.setColumnStretch(3, 1)

        container_layout.addLayout(grid)

        # ===== GOMBOK =====
        btn_layout = QHBoxLayout()

        save_btn = QPushButton("Mentés")
        save_btn.setStyleSheet("""
        QPushButton {
            background-color: #16a34a;
            color: white;
        }
        QPushButton:hover {
            background-color: #15803d;
        }
        """)

        cancel_btn = QPushButton("Mégse")
        cancel_btn.setStyleSheet("""
        QPushButton {
            background-color: #374151;
            color: white;
        }
        QPushButton:hover {
            background-color: #4b5563;
        }
        """)

        save_btn.clicked.connect(self.handle_save)
        cancel_btn.clicked.connect(self.reject)

        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)

        container_layout.addLayout(btn_layout)

    # ===== SAVE =====
    def handle_save(self):
        try:
            create_technical_booking(
                first_name=self.first_name_input.text(),
                last_name=self.last_name_input.text(),
                phone=self.phone_input.text(),
                email=self.email_input.text(),
                password=self.password_input.text(),
                country=self.country_input.text(),
                zip_code=self.zip_input.text(),
                city=self.city_input.text(),
                street=self.street_input.text(),
                house_number=self.house_number_input.text(),
                trailer_id=self.trailer_combo.currentData(),
                booking_date=self.date_input.date().toPython(),
                period=self.period_combo.currentText()
            )

            Toast(self.main_window, "Foglalás sikeres", True).show_toast()
            self.accept()

        except ValueError as e:
            Toast(self.main_window, str(e), False).show_toast()

        except Exception as e:
            Toast(self.main_window, "Hiba történt", False).show_toast()
            print(e)