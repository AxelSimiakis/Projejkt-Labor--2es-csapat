from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QHBoxLayout, QHeaderView, QLabel, QAbstractItemView
)
from PySide6.QtCore import Qt

from core.session_manager import SessionManager
from core.toast import Toast
from services.favorite_service import get_user_favorite_trailers, remove_favorite


class FavoriteView(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        layout = QVBoxLayout()

        top = QHBoxLayout()

        title = QLabel("Kedvencek")
        title.setStyleSheet("color:white; font-size:18px; font-weight:bold;")

        top.addWidget(title)
        top.addStretch()

        layout.addLayout(top)

        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "Név", "Leírás", "Délelőtt", "Délután", "Egész nap", "Kaució", "Művelet"
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
            self.table.clearContents()
            self.table.setRowCount(0)
            return

        trailers = get_user_favorite_trailers(user.id)

        self.table.clearContents()
        self.table.setRowCount(len(trailers))

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)   # Név
        header.setSectionResizeMode(1, QHeaderView.Stretch)            # Leírás
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)   # Délelőtt
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)   # Délután
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)   # Egész nap
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)   # Kaució
        header.setSectionResizeMode(6, QHeaderView.Fixed)              # Művelet

        self.table.setColumnWidth(6, 120)

        for row, trailer in enumerate(trailers):
            self.table.setItem(row, 0, QTableWidgetItem(trailer.name))
            self.table.setItem(row, 1, QTableWidgetItem(trailer.description or "-"))
            self.table.setItem(row, 2, QTableWidgetItem(f"{trailer.price_morning} Ft"))
            self.table.setItem(row, 3, QTableWidgetItem(f"{trailer.price_afternoon} Ft"))
            self.table.setItem(row, 4, QTableWidgetItem(f"{trailer.price_full_day} Ft"))
            self.table.setItem(row, 5, QTableWidgetItem(f"{trailer.deposit} Ft"))

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
                lambda _, tid=trailer.id: self.remove_from_favorites(tid)
            )

            container = QWidget()
            container.setStyleSheet("background: transparent;")

            btn_layout = QHBoxLayout(container)
            btn_layout.setContentsMargins(6, 0, 6, 0)
            btn_layout.setSpacing(8)
            btn_layout.addWidget(delete_btn)
            btn_layout.addStretch()

            self.table.setCellWidget(row, 6, container)

    def remove_from_favorites(self, trailer_id):
        user = SessionManager.instance().get_user()
        if not user:
            return

        removed = remove_favorite(user.id, trailer_id)

        if removed:
            Toast(self.main_window, "Eltávolítva a kedvencekből", False).show_toast()
        else:
            Toast(self.main_window, "Ez az utánfutó nincs a kedvencek között", False).show_toast()

        if hasattr(self.main_window, "trailer_page"):
            self.main_window.trailer_page.refresh()

        self.load_data()