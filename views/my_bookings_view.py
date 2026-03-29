from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QLabel, QHeaderView, QAbstractItemView, QPushButton, QHBoxLayout
)
from PySide6.QtCore import Qt

from database import SessionLocal
from models.booking import Booking
from core.session_manager import SessionManager
from datetime import date, timedelta
from services.booking_service import cancel_booking
from core.toast import Toast

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
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "Utánfutó", "Dátum", "Időszak", "Státusz", "Létrehozva", "Kaució", "Művelet"
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
            header.setSectionResizeMode(6, QHeaderView.ResizeToContents)   

            self.table.setColumnWidth(6, 220)

            for row, booking in enumerate(bookings):
                trailer_name = booking.trailer.name if booking.trailer else f"#{booking.trailer_id}"
                period_hu = PERIOD_TO_HU.get(booking.period, booking.period)
                status_hu = STATUS_TO_HU.get(booking.status, booking.status)
                created_at = str(booking.created_at)[:16] if booking.created_at else "-"
                deposit = f"{booking.trailer.deposit or 0} Ft" if booking.trailer else "-"

                self.table.setItem(row, 0, QTableWidgetItem(trailer_name))
                self.table.setItem(row, 1, QTableWidgetItem(str(booking.booking_date)))
                self.table.setItem(row, 2, QTableWidgetItem(period_hu))
                self.table.setItem(row, 3, QTableWidgetItem(status_hu))
                self.table.setItem(row, 4, QTableWidgetItem(created_at))
                self.table.setItem(row, 5, QTableWidgetItem(deposit))

                cancel_btn = QPushButton("Lemondás")
                cancel_btn.setFixedHeight(30)
                cancel_btn.setMinimumWidth(140)
                cancel_btn.setCursor(Qt.PointingHandCursor)
                cancel_btn.setStyleSheet("""
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

                # 5 napos szabály
                if booking.booking_date <= date.today() + timedelta(days=5):
                    cancel_btn.setEnabled(False)
                    cancel_btn.setText("Nem törölhető")

                cancel_btn.clicked.connect(
                    lambda _, bid=booking.id: self.handle_cancel(bid)
                )

                container = QWidget()
                container.setAttribute(Qt.WA_StyledBackground, False)
                container.setAutoFillBackground(False)
                container.setStyleSheet("background: transparent;")

                btn_layout = QHBoxLayout()
                btn_layout.setContentsMargins(10, 5, 10, 5)
                btn_layout.setSpacing(10)

                btn_layout.addWidget(cancel_btn)

                container.setLayout(btn_layout)
                
                self.table.setCellWidget(row, 6, cancel_btn)

        finally:
            session.close()
    def handle_cancel(self, booking_id):
        user = SessionManager.instance().get_user()

        try:
            cancel_booking(booking_id, user.id)

            Toast(self.main_window, "Foglalás lemondva", True).show_toast()
            self.load_data()

        except ValueError as e:
            Toast(self.main_window, str(e), False).show_toast()

        except Exception as e:
            Toast(self.main_window, "Hiba történt", False).show_toast()
            print(e)