from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QTableWidget,
    QTableWidgetItem, QHBoxLayout, QHeaderView,
    QLabel, QAbstractItemView, QDialog,
    QFormLayout, QComboBox, QDateEdit
)
from PySide6.QtCore import Qt, QDate

from database import SessionLocal
from models.booking import Booking
from models.trailer import Trailer
from core.toast import Toast
from views.technical_booking_view import TechnicalBooking, EmployeeBooking

PERIOD_TO_HU = {
    "morning": "Délelőtt",
    "afternoon": "Délután",
    "full_day": "Egész nap",
}

STATUS_TO_HU = {
    "active": "Normál",
    "employee": "Alkalmazotti",
    "completed": "Lezárt",
    "cancelled": "Törölt",
    "technical": "Technikai",
}


class BookingView(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        layout = QVBoxLayout()
        toolbar = QHBoxLayout()

        title = QLabel("Foglalások")
        title.setStyleSheet("color: white; font-size: 18px; font-weight: bold;")

        self.new_technical_booking_btn = QPushButton("+ Új technikai foglalás")
        self.new_technical_booking_btn.setCursor(Qt.PointingHandCursor)
        self.new_technical_booking_btn.setStyleSheet(self._secondary_button_style())
        self.new_technical_booking_btn.clicked.connect(self.open_technical_booking)

        toolbar.addWidget(title)
        toolbar.addStretch()
        toolbar.addWidget(self.new_technical_booking_btn)
        layout.addLayout(toolbar)

        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "Típus", "Név", "Telefon", "Utánfutó", "Foglalás", "Időszak", "Létrehozva", "Művelet"
        ])
        self.table.setStyleSheet("""
        QTableWidget {
            background-color: #1f2937;
            color: white;
            gridline-color: #374151;
            border: none;
            border-radius: 10px;
        }

        QHeaderView::section {
            background-color: #111827;
            color: #9ca3af;
            padding: 8px;
            border: none;
        }

        QTableWidget::item {
            padding: 6px;
        }

        QTableWidget::item:selected {
            background-color: #16a34a;
        }
        """)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setDefaultSectionSize(50)

        layout.addWidget(self.table)
        self.setLayout(layout)
        self.load_data()

    def _primary_button_style(self):
        return """
        QPushButton {
            background-color: #16a34a;
            color: white;
            border-radius: 8px;
            padding: 8px 14px;
            font-size: 13px;
            font-weight: bold;
            border: none;
        }
        QPushButton:hover {
            background-color: #15803d;
        }
        """

    def _secondary_button_style(self):
        return """
        QPushButton {
            background-color: #374151;
            color: white;
            border-radius: 8px;
            padding: 8px 14px;
            font-size: 13px;
            font-weight: bold;
            border: none;
        }
        QPushButton:hover {
            background-color: #4b5563;
        }
        """

    def load_data(self):
        session = SessionLocal()
        bookings = session.query(Booking).order_by(Booking.booking_date.desc(), Booking.created_at.desc()).all()

        if not bookings:
            self.table.setRowCount(0)
            self.table.setColumnCount(1)
            self.table.setHorizontalHeaderLabels([""])
            self.table.setRowCount(1)
            item = QTableWidgetItem("Nincs foglalás")
            item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(0, 0, item)
            session.close()
            return

        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "Típus", "Név", "Telefon", "Utánfutó", "Foglalás", "Időszak", "Létrehozva", "Művelet"
        ])

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        for i in range(1, 7):
            header.setSectionResizeMode(i, QHeaderView.Stretch)
        header.setSectionResizeMode(7, QHeaderView.Fixed)
        self.table.setColumnWidth(7, 220)
        self.table.setRowCount(len(bookings))

        for row, b in enumerate(bookings):
            if b.user:
                name = f"{b.user.first_name} {b.user.last_name}"
                phone = b.user.phone or "-"
            else:
                name = getattr(b, "name", "-")
                phone = getattr(b, "phone", "-")

            trailer = b.trailer.name if b.trailer else str(b.trailer_id)
            booking_type = STATUS_TO_HU.get(b.status, b.status)
            period = PERIOD_TO_HU.get(b.period, b.period)

            self.table.setItem(row, 0, QTableWidgetItem(booking_type))
            self.table.setItem(row, 1, QTableWidgetItem(name))
            self.table.setItem(row, 2, QTableWidgetItem(phone))
            self.table.setItem(row, 3, QTableWidgetItem(trailer))
            self.table.setItem(row, 4, QTableWidgetItem(str(b.booking_date)))
            self.table.setItem(row, 5, QTableWidgetItem(period))
            self.table.setItem(row, 6, QTableWidgetItem(str(b.created_at)[:16]))

            edit_btn = QPushButton("Szerkesztés")
            edit_btn.setFixedHeight(30)
            edit_btn.setMinimumWidth(100)
            edit_btn.setCursor(Qt.PointingHandCursor)
            edit_btn.setStyleSheet("""
            QPushButton {
                background-color: #374151;
                color: white;
                border-radius: 6px;
                padding: 6px 12px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #4b5563;
            }
            """)
            edit_btn.clicked.connect(lambda _, bid=b.id: self.edit_booking(bid))

            delete_btn = QPushButton("Törlés")
            delete_btn.setFixedHeight(30)
            delete_btn.setMinimumWidth(80)
            delete_btn.setCursor(Qt.PointingHandCursor)
            delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #1f2937;
                color: #d1d5db;
                border: 1px solid #374151;
                border-radius: 6px;
                padding: 6px 12px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #374151;
                color: white;
            }
            """)
            delete_btn.clicked.connect(lambda _, bid=b.id: self.delete_booking(bid))

            container = QWidget()
            container.setAttribute(Qt.WA_StyledBackground, False)
            container.setAutoFillBackground(False)
            container.setStyleSheet("background: transparent;")
            btn_layout = QHBoxLayout()
            btn_layout.setContentsMargins(10, 5, 10, 5)
            btn_layout.setSpacing(10)
            btn_layout.addWidget(edit_btn)
            btn_layout.addWidget(delete_btn)
            container.setLayout(btn_layout)
            self.table.setCellWidget(row, 7, container)

        session.close()

    def _load_trailers(self):
        session = SessionLocal()
        trailers = session.query(Trailer).all()
        session.close()
        return trailers

    def open_technical_booking(self):
        dialog = TechnicalBooking(self.main_window, self._load_trailers())
        if dialog.exec():
            self.load_data()

    def open_employee_booking(self):
        dialog = EmployeeBooking(self.main_window, self._load_trailers())
        if dialog.exec():
            self.load_data()

    def delete_booking(self, booking_id):
        session = SessionLocal()
        booking = session.get(Booking, booking_id)

        if booking:
            session.delete(booking)
            session.commit()
            Toast(self.main_window, "Foglalás törölve", False).show_toast()

        session.close()
        self.load_data()

    def edit_booking(self, booking_id):
        session = SessionLocal()
        booking = session.get(Booking, booking_id)
        if not booking:
            session.close()
            return

        dialog = QDialog(self)
        dialog.setWindowTitle("Foglalás szerkesztése")
        dialog.setFixedWidth(320)
        dialog.setStyleSheet("""
        QDialog {
            background-color: #1f2937;
            color: white;
            border-radius: 12px;
        }

        QLabel {
            color: white;
            font-size: 13px;
            background: transparent;
        }

        QComboBox, QDateEdit {
            background-color: #111827;
            color: white;
            padding: 8px;
            border-radius: 8px;
            border: 1px solid #374151;
        }

        QPushButton {
            border-radius: 8px;
            padding: 8px 12px;
            min-height: 18px;
        }
        """)

        form = QFormLayout(dialog)
        date_input = QDateEdit()
        date_input.setCalendarPopup(True)
        date_input.setDate(QDate(booking.booking_date.year, booking.booking_date.month, booking.booking_date.day))

        period_input = QComboBox()
        for key, label in PERIOD_TO_HU.items():
            period_input.addItem(label, key)
        index = max(0, period_input.findData(booking.period))
        period_input.setCurrentIndex(index)

        status_input = QComboBox()
        for key, label in STATUS_TO_HU.items():
            status_input.addItem(label, key)
        index = max(0, status_input.findData(booking.status))
        status_input.setCurrentIndex(index)

        form.addRow("Dátum:", date_input)
        form.addRow("Időszak:", period_input)
        form.addRow("Típus:", status_input)

        save_btn = QPushButton("Mentés")
        save_btn.setStyleSheet(self._primary_button_style())
        save_btn.clicked.connect(
            lambda: self._save_booking_edit(dialog, session, booking, date_input, period_input, status_input)
        )
        form.addRow(save_btn)
        dialog.exec()

    def _save_booking_edit(self, dialog, session, booking, date_input, period_input, status_input):
        booking.booking_date = date_input.date().toPython()
        booking.period = period_input.currentData()
        booking.status = status_input.currentData()
        session.commit()
        session.close()
        dialog.accept()
        self.load_data()
