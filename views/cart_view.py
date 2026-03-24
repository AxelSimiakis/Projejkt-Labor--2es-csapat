from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QTableWidget, QTableWidgetItem, QPushButton, QHeaderView,
    QAbstractItemView
)
from PySide6.QtCore import Qt

from core.session_manager import SessionManager
from core.toast import Toast
from services.cart_service import (
    get_user_cart_items,
    remove_cart_item,
    checkout_cart,
)


class CartView(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        layout = QVBoxLayout()

        top = QHBoxLayout()

        title = QLabel("Kosár")
        title.setStyleSheet("color:white; font-size:18px; font-weight:bold;")

        self.checkout_btn = QPushButton("Kosár jóváhagyása")
        self.checkout_btn.setCursor(Qt.PointingHandCursor)
        self.checkout_btn.setStyleSheet("""
        QPushButton {
            background-color: #16a34a;
            color: white;
            border-radius: 8px;
            padding: 8px 14px;
            font-size: 13px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #15803d;
        }
        """)
        self.checkout_btn.clicked.connect(self.handle_checkout)

        top.addWidget(title)
        top.addStretch()
        top.addWidget(self.checkout_btn)

        layout.addLayout(top)

        self.summary_label = QLabel("")
        self.summary_label.setStyleSheet("color: white; font-size: 14px;")
        layout.addWidget(self.summary_label)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Utánfutó", "Dátum", "Időszak", "Ár", "Művelet", ""
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
        self.table.verticalHeader().setDefaultSectionSize(56)
        self.table.setWordWrap(True)

        layout.addWidget(self.table)
        self.setLayout(layout)

        self.load_data()

    def load_data(self):
        user = SessionManager.instance().get_user()
        if not user:
            self.table.setRowCount(0)
            self.summary_label.setText("A kosár csak bejelentkezés után érhető el.")
            self.checkout_btn.setVisible(False)
            return

        items = get_user_cart_items(user.id)

        self.checkout_btn.setVisible(True)
        self.table.clearContents()
        self.table.setRowCount(len(items))

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.Fixed)
        header.setSectionResizeMode(5, QHeaderView.Fixed)

        self.table.setColumnWidth(4, 110)
        self.table.setColumnWidth(5, 10)

        total = 0

        for row, item in enumerate(items):
            total += item["price"]

            self.table.setItem(row, 0, QTableWidgetItem(item["trailer_name"]))
            self.table.setItem(row, 1, QTableWidgetItem(str(item["booking_date"])))
            self.table.setItem(row, 2, QTableWidgetItem(item["period_hu"]))
            self.table.setItem(row, 3, QTableWidgetItem(f'{item["price"]} Ft'))

            delete_btn = QPushButton("Törlés")
            delete_btn.setFixedHeight(32)
            delete_btn.setMinimumWidth(90)
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
                lambda _, cid=item["id"]: self.remove_item(cid)
            )

            self.table.setCellWidget(row, 4, delete_btn)

        self.summary_label.setText(f"Tételek száma: {len(items)} | Összesen: {total} Ft")

    def remove_item(self, cart_item_id):
        user = SessionManager.instance().get_user()
        if not user:
            return

        success = remove_cart_item(cart_item_id, user.id)
        if success:
            Toast(self.main_window, "Tétel eltávolítva a kosárból", False).show_toast()
        else:
            Toast(self.main_window, "A tétel nem található", False).show_toast()

        if hasattr(self.main_window, "trailer_page"):
            self.main_window.trailer_page.refresh()

        self.load_data()

    def handle_checkout(self):
        user = SessionManager.instance().get_user()
        if not user:
            return

        try:
            checkout_cart(user.id)
            Toast(self.main_window, "A kosár jóváhagyása sikeres, a foglalások létrejöttek.", True).show_toast()

            if hasattr(self.main_window, "trailer_page"):
                self.main_window.trailer_page.refresh()

            if hasattr(self.main_window, "booking_page"):
                self.main_window.booking_page.load_data()

            self.load_data()

        except ValueError as exc:
            Toast(self.main_window, str(exc), False).show_toast()
        except Exception as exc:
            Toast(self.main_window, f"Hiba történt: {exc}", False).show_toast()