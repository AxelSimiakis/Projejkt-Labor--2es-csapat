from PySide6.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QComboBox, QDateEdit, QGridLayout
)
from PySide6.QtCore import QDate

from core.toast import Toast
from services.staff_booking_service import create_staff_booking
from services.technical_booking_service import create_technical_booking


PERIOD_LABELS = {
    "morning": "Délelőtt",
    "afternoon": "Délután",
    "full_day": "Egész nap",
}


class ManagedBookingDialog(QDialog):
    def __init__(self, main_window, trailers, booking_kind="technical"):
        super().__init__()
        self.main_window = main_window
        self.trailers = trailers
        self.booking_kind = booking_kind

        is_staff_booking = booking_kind == "employee"
        self.setWindowTitle("Alkalmazotti foglalás" if is_staff_booking else "Technikai foglalás")
        self.setMinimumWidth(650)

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

        main_layout = QVBoxLayout()
        container = QWidget()
        container_layout = QVBoxLayout()
        container_layout.setContentsMargins(20, 20, 20, 20)
        container_layout.setSpacing(12)
        container.setLayout(container_layout)

        main_layout.addWidget(container)
        self.setLayout(main_layout)

        title = QLabel("Alkalmazotti foglalás" if is_staff_booking else "Technikai foglalás")
        title.setStyleSheet("font-size:18px; font-weight:bold; color:white;")
        container_layout.addWidget(title)

        subtitle_text = (
            "Utcáról érkező ügyfél foglalásának rögzítése dolgozó által."
            if is_staff_booking else
            "Szervizelés vagy belső kizárás miatt nem foglalható időszak rögzítése."
        )
        subtitle = QLabel(subtitle_text)
        subtitle.setWordWrap(True)
        subtitle.setStyleSheet("color:#9ca3af; font-size:12px;")
        container_layout.addWidget(subtitle)

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

        self.trailer_combo = QComboBox()
        for t in trailers:
            self.trailer_combo.addItem(t.name, t.id)

        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(QDate.currentDate())
        self.date_input.setMinimumDate(QDate.currentDate())

        self.period_combo = QComboBox()
        self.period_combo.addItem(PERIOD_LABELS["morning"], "morning")
        self.period_combo.addItem(PERIOD_LABELS["afternoon"], "afternoon")
        self.period_combo.addItem(PERIOD_LABELS["full_day"], "full_day")

        grid = QGridLayout()
        grid.setSpacing(10)

        def add(row, col, label, widget):
            grid.addWidget(QLabel(label), row, col)
            grid.addWidget(widget, row, col + 1)

        add(0, 0, "Vezetéknév", self.first_name_input)
        add(1, 0, "Keresztnév", self.last_name_input)
        add(2, 0, "Telefon", self.phone_input)
        add(3, 0, "Email", self.email_input)
        add(4, 0, "Jelszó", self.password_input)
        add(5, 0, "Ország", self.country_input)

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

    def handle_save(self):
        try:
            payload = dict(
                first_name=self.first_name_input.text().strip(),
                last_name=self.last_name_input.text().strip(),
                phone=self.phone_input.text().strip(),
                email=self.email_input.text().strip(),
                password=self.password_input.text().strip(),
                country=self.country_input.text().strip(),
                zip_code=self.zip_input.text().strip(),
                city=self.city_input.text().strip(),
                street=self.street_input.text().strip(),
                house_number=self.house_number_input.text().strip(),
                trailer_id=self.trailer_combo.currentData(),
                booking_date=self.date_input.date().toPython(),
                period=self.period_combo.currentData(),
            )

            if self.booking_kind == "employee":
                create_staff_booking(**payload)
                success_message = "Alkalmazotti foglalás sikeresen létrehozva"
            else:
                create_technical_booking(**payload)
                success_message = "Technikai foglalás sikeresen létrehozva"

            Toast(self.main_window, success_message, True).show_toast()
            self.accept()

        except ValueError as e:
            Toast(self.main_window, str(e), False).show_toast()
        except Exception as e:
            Toast(self.main_window, "Hiba történt", False).show_toast()
            print(e)


class TechnicalBooking(ManagedBookingDialog):
    def __init__(self, main_window, trailers):
        super().__init__(main_window, trailers, booking_kind="technical")


class EmployeeBooking(ManagedBookingDialog):
    def __init__(self, main_window, trailers):
        super().__init__(main_window, trailers, booking_kind="employee")
