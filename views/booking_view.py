from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QTableWidget,
    QTableWidgetItem, QHBoxLayout, QHeaderView,
    QLabel, QAbstractItemView, QDialog, 
    QFormLayout, QComboBox, QDateEdit
)
from PySide6.QtCore import Qt, QDate

from database import SessionLocal
from models.booking import Booking
from core.toast import Toast


class BookingView(QWidget):

    def __init__(self, main_window):
        super().__init__()

        self.main_window = main_window

        layout = QVBoxLayout()

        # ======================
        # TOOLBAR
        # ======================
        toolbar = QHBoxLayout()

        title = QLabel("Foglalások")
        title.setStyleSheet("color: white; font-size: 18px; font-weight: bold;")

        toolbar.addWidget(title)
        toolbar.addStretch()

        layout.addLayout(toolbar)

        # ======================
        # TABLE
        # ======================
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Név", "Telefon", "Utánfutó", "Dátum", "Időszak", "Művelet"
        ])

        # STYLE
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

    # ======================
    # ADAT BETÖLTÉS
    # ======================

    def load_data(self):
        session = SessionLocal()
        bookings = session.query(Booking).all()

        # ===== ÜRES ÁLLAPOT =====
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

        # ==== TABLE ====
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "Név", "Telefon", "Utánfutó", "Foglalás", "Időszak", "Létrehozva", "Művelet"
        ])

        # ======================
        # OSZLOP MÉRETEZÉS
        # ======================
        header = self.table.horizontalHeader()
        for i in range(6):
            header.setSectionResizeMode(i, QHeaderView.Stretch)

        header.setSectionResizeMode(6, QHeaderView.Fixed)
        self.table.setColumnWidth(6, 220)

        self.table.setRowCount(len(bookings))

        for row, b in enumerate(bookings):

            # USER / TECHNIKAI
            if b.user:
                name = f"{b.user.first_name} {b.user.last_name}"
                phone = b.user.phone or "-"
            else:
                name = getattr(b, "name", "Technikai")
                phone = getattr(b, "phone", "-")

            trailer = b.trailer.name if b.trailer else str(b.trailer_id)

            self.table.setItem(row, 0, QTableWidgetItem(name))
            self.table.setItem(row, 1, QTableWidgetItem(phone))
            self.table.setItem(row, 2, QTableWidgetItem(trailer))
            self.table.setItem(row, 3, QTableWidgetItem(str(b.booking_date)))
            self.table.setItem(row, 4, QTableWidgetItem(b.period))
            self.table.setItem(row, 5, QTableWidgetItem(str(b.created_at)[:16]))
            

            # ======================
            # GOMBOK
            # ======================

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
            edit_btn.clicked.connect(
                lambda _, bid=b.id: self.edit_booking(bid)
            )

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

            delete_btn.clicked.connect(
                lambda _, bid=b.id: self.delete_booking(bid)
            )

            container = QWidget()
            container.setAttribute(Qt.WA_StyledBackground, False)
            container.setAutoFillBackground(False)
            container.setStyleSheet("background: transparent; ")
            
            btn_layout = QHBoxLayout()
            btn_layout.setContentsMargins(10, 5, 10, 5)
            btn_layout.setSpacing(10)

            btn_layout.addWidget(edit_btn)
            btn_layout.addWidget(delete_btn)

            container.setLayout(btn_layout)

            self.table.setCellWidget(row, 6, container)

        session.close()

    # ======================
    # TÖRLÉS
    # ======================

    def delete_booking(self, booking_id):
        session = SessionLocal()

        booking = session.get(Booking, booking_id)

        if booking:
            session.delete(booking)
            session.commit()
            Toast(self.main_window, "Foglalás törölve", False).show_toast()

        session.close()
        self.load_data()

    # ======================
    # Szerkesztés
    # ======================
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
            color: #d1d5db;
        }

        QComboBox, QDateEdit {
            background-color: #111827;
            color: white;
            padding: 6px;
            border-radius: 6px;
            border: 1px solid #374151;
        }

        QPushButton {
            border-radius: 8px;
            padding: 8px;
        }
        """)

        layout = QFormLayout()

        # ===== DÁTUM =====
        date_edit = QDateEdit()
        date_edit.setCalendarPopup(True)
        date_edit.setDate(QDate.fromString(str(booking.booking_date), "yyyy-MM-dd"))

        # ===== IDŐSZAK =====
        period_select = QComboBox()
        period_select.addItems(["morning", "afternoon", "full_day"])
        period_select.setCurrentText(booking.period)

        layout.addRow("Dátum:", date_edit)
        layout.addRow("Időszak:", period_select)

        # ===== GOMBOK =====
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
        
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)

        layout.addRow(btn_layout)

        dialog.setLayout(layout)

        # ===== Mentés =====
        def save():
            booking.booking_date = date_edit.date().toPython()
            booking.period = period_select.currentText()

            session.commit()
            session.close()

            Toast(self.main_window, "Foglalás frissítve", True).show_toast()
            dialog.accept()
            self.load_data()

        save_btn.clicked.connect(save)
        cancel_btn.clicked.connect(dialog.reject)

        dialog.exec()