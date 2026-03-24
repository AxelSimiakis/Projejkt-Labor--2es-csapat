from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QLabel, QHeaderView, QAbstractItemView
)
from PySide6.QtCore import Qt

from database import SessionLocal
from models.booking import Booking
from core.session_manager import SessionManager


PERIOD_TO_HU = {
    "morning": "Délelőtt",
    "afternoon": "Délután",
    "full_day": "Egész nap",
}

STATUS_TO_HU = {
    "active": "Aktív",
    "completed": "Lezárt",
    "cancelled": "Törölt",
    "technical": "Technikai",
}


class MyBookingsView(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        layout = QVBoxLayout()

        title = QLabel("Saját foglalások")
        title.setStyleSheet("color:white; font-size:18px; font-weight:bold;")
        layout.addWidget(title)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Utánfutó", "Dátum", "Időszak", "Státusz", "Létrehozva", "Kaució"
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
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setDefaultSectionSize(52)
        self.table.setWordWrap(True)

        layout.addWidget(self.table)
        self.setLayout(layout)

        self.load_data()

    def load_data(self):
        user = SessionManager.instance().get_user()

        if not user:
            self.table.clearContents()
            self.table.setRowCount(0)
            return

        session = SessionLocal()
        try:
            bookings = (
                session.query(Booking)
                .filter(Booking.user_id == user.id)
                .order_by(Booking.booking_date.desc(), Booking.created_at.desc())
                .all()
            )

            self.table.clearContents()
            self.table.setRowCount(len(bookings))

            header = self.table.horizontalHeader()
            header.setSectionResizeMode(0, QHeaderView.Stretch)            # Utánfutó
            header.setSectionResizeMode(1, QHeaderView.ResizeToContents)   # Dátum
            header.setSectionResizeMode(2, QHeaderView.ResizeToContents)   # Időszak
            header.setSectionResizeMode(3, QHeaderView.ResizeToContents)   # Státusz
            header.setSectionResizeMode(4, QHeaderView.ResizeToContents)   # Létrehozva
            header.setSectionResizeMode(5, QHeaderView.ResizeToContents)   # Kaució

            for row, booking in enumerate(bookings):
                trailer_name = booking.trailer.name if booking.trailer else f"#{booking.trailer_id}"
                period_hu = PERIOD_TO_HU.get(booking.period, booking.period)
                status_hu = STATUS_TO_HU.get(booking.status, booking.status)
                created_at = str(booking.created_at)[:16] if booking.created_at else "-"
                deposit = f"{booking.trailer.deposit} Ft" if booking.trailer else "-"

                self.table.setItem(row, 0, QTableWidgetItem(trailer_name))
                self.table.setItem(row, 1, QTableWidgetItem(str(booking.booking_date)))
                self.table.setItem(row, 2, QTableWidgetItem(period_hu))
                self.table.setItem(row, 3, QTableWidgetItem(status_hu))
                self.table.setItem(row, 4, QTableWidgetItem(created_at))
                self.table.setItem(row, 5, QTableWidgetItem(deposit))

        finally:
            session.close()