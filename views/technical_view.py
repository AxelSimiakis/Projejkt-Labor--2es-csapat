from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QHBoxLayout, QHeaderView, QDialog,
    QFormLayout, QLineEdit, QLabel, QAbstractItemView
)
from PySide6.QtCore import Qt

from database import SessionLocal
from models.trailer import Trailer
from core.toast import Toast


class TechnicalView(QWidget):

    def __init__(self, main_window):
        super().__init__()

        self.main_window = main_window
        layout = QVBoxLayout()

        # ===== HEADER =====
        toolbar = QHBoxLayout()

        title = QLabel("Utánfutók kezelése")
        title.setStyleSheet("color: white; font-size: 18px; font-weight: bold;")

        add_btn = QPushButton("+ Új utánfutó")
        add_btn.clicked.connect(self.create_trailer)
        add_btn.setCursor(Qt.PointingHandCursor)
        add_btn.setStyleSheet("""
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
        
        toolbar.addWidget(title)
        toolbar.addStretch()
        toolbar.addWidget(add_btn)

        layout.addLayout(toolbar)

        # ===== TABLE =====
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "Név", "Leírás", "Délelőtt", "Délután", "Egész nap","Kaukció", "Művelet"
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
        self.table.setWordWrap(True)

        layout.addWidget(self.table)
        self.setLayout(layout)

        self.load_data()

    def _apply_dialog_style(self, dialog):
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

            QLineEdit, QComboBox {
                background-color: #111827;
                color: white;
                padding: 8px;
                border-radius: 8px;
                border: 1px solid #374151;
                min-height: 18px;
            }

            QLineEdit:focus, QComboBox:focus {
                border: 1px solid #16a34a;
            }

            QPushButton {
                border-radius: 8px;
                padding: 8px 12px;
                min-height: 18px;
            }
            """)

    def _primary_button_style(self):
            return """
            QPushButton {
                background-color: #16a34a;
                color: white;
                border: none;
                font-weight: bold;
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
                border: none;
            }
            QPushButton:hover {
                background-color: #4b5563;
            }
            """
    
    # ======================
    # Frissités
    # ======================
    def refresh(self):
        self.load_data()

    # ======================
    # Adatokok kezelése
    # ======================
    def load_data(self):
        session = SessionLocal()
        trailers = session.query(Trailer).all()

        self.table.clearContents()
        self.table.setRowCount(len(trailers))

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)            # Név
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)   # Leírás
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)            # Délelőtt
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)            # Délután
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)            # Egésznap
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)            #  kció
        header.setSectionResizeMode(6, QHeaderView.Fixed)              # Művelet

        self.table.setColumnWidth(2, 300)
        self.table.setColumnWidth(3, 120)
        self.table.setColumnWidth(4, 120)
        self.table.setColumnWidth(5, 120)
        self.table.setColumnWidth(6, 230)

        for row, t in enumerate(trailers):

            self.table.setItem(row, 0, QTableWidgetItem(t.name))
            self.table.setItem(row, 1, QTableWidgetItem(t.description or ""))
            self.table.setItem(row, 2, QTableWidgetItem(str(t.price_morning)))
            self.table.setItem(row, 3, QTableWidgetItem(str(t.price_afternoon)))
            self.table.setItem(row, 4, QTableWidgetItem(str(t.price_full_day)))
            self.table.setItem(row, 5, QTableWidgetItem(str(t.deposit)))

            # ===== GOMBOK =====
            edit_btn = QPushButton("Szerkesztés")
            edit_btn.setFixedHeight(32)
            edit_btn.setMinimumWidth(110)
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
            edit_btn.clicked.connect(lambda _, tid=t.id: self.edit_trailer(tid))
            
            delete_btn = QPushButton("Törlés")
            delete_btn.setFixedHeight(32)
            delete_btn.setMinimumWidth(90)
            edit_btn.setCursor(Qt.PointingHandCursor)
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
            
            delete_btn.clicked.connect(lambda _, tid=t.id: self.delete_trailer(tid))

            container = QWidget()
            container.setStyleSheet("background: transparent;")

            btn_layout = QHBoxLayout(container)
            btn_layout.setContentsMargins(6, 0, 6, 0)
            btn_layout.setSpacing(8)

            btn_layout.addWidget(edit_btn)
            btn_layout.addWidget(delete_btn)

            self.table.setCellWidget(row, 6, container)

        session.close()

    # ======================
    # Új Utánfutó
    # ======================
    def create_trailer(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Új utánfutó")
        dialog.resize(420, 360)
        self._apply_dialog_style(dialog)

        layout = QFormLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 16)

        name = QLineEdit()
        desc = QLineEdit()
        price_m = QLineEdit()
        price_a = QLineEdit()
        price_f = QLineEdit()
        deposit = QLineEdit()

        layout.addRow("Név:", name)
        layout.addRow("Leírás:", desc)
        layout.addRow("Délelőtt ár:", price_m)
        layout.addRow("Délután ár:", price_a)
        layout.addRow("Egész nap ár:", price_f)
        layout.addRow("Kaukció:", deposit)

        save = QPushButton("Mentés")
        save.setStyleSheet("""
        QPushButton {
            background-color: #16a34a;
            color: white;
        }
        QPushButton:hover {
            background-color: #15803d;
        }
        """)

        cancel = QPushButton("Mégse")
        cancel.setStyleSheet("""
        QPushButton {
            background-color: #374151;
            color: white;
        }
        QPushButton:hover {
            background-color: #4b5563;
        }
        """)

        btns = QHBoxLayout()
        btns.addWidget(save)
        btns.addWidget(cancel)

        layout.addRow(btns)
        dialog.setLayout(layout)

        def do_save():
            try:
                session = SessionLocal()

                new = Trailer(
                    name=name.text(),
                    description=desc.text(),
                    price_morning=int(price_m.text()),
                    price_afternoon=int(price_a.text()),
                    price_full_day=int(price_f.text()),
                    deposit=int(price_f.text())
                )

                session.add(new)
                session.commit()
                session.close()

                Toast(self.main_window, "Utánfutó létrehozva", True).show_toast()

                dialog.accept()
                self.load_data()

            except Exception:
                Toast(self.main_window, "Hibás adat!", False).show_toast()

        save.clicked.connect(do_save)
        cancel.clicked.connect(dialog.reject)

        dialog.exec()

    # ======================
    # Törlés
    # ======================
    def delete_trailer(self, trailer_id):
        session = SessionLocal()
        trailer = session.get(Trailer, trailer_id)

        if trailer:
            session.delete(trailer)
            session.commit()

        session.close()
        Toast(self.main_window, "Utánfutó törölve", False).show_toast()
        self.load_data()

    # ======================
    # Szerkesztés
    # ======================
    def edit_trailer(self, trailer_id):
        session = SessionLocal()
        t = session.get(Trailer, trailer_id)

        dialog = QDialog(self)
        dialog.setWindowTitle("Utánfutó szerkesztése")
        dialog.resize(420, 360)
        self._apply_dialog_style(dialog)

        layout = QFormLayout()
        layout.setSpacing(8)
        layout.setContentsMargins(16, 16, 16, 16)

        name = QLineEdit(t.name)
        desc = QLineEdit(t.description or "")
        price_m = QLineEdit(str(t.price_morning))
        price_a = QLineEdit(str(t.price_afternoon))
        price_f = QLineEdit(str(t.price_full_day))
        deposit = QLineEdit(str(t.deposit))


        layout.addRow("Név:", name)
        layout.addRow("Leírás:", desc)
        layout.addRow("Délelőtt ár:", price_m)
        layout.addRow("Délután ár:", price_a)
        layout.addRow("Egész nap ár:", price_f)
        layout.addRow("Kaukció:", deposit)

        save = QPushButton("Mentés")
        save.setStyleSheet(self._primary_button_style())

        cancel = QPushButton("Mégse")
        cancel.setStyleSheet(self._secondary_button_style())
        
        btns = QHBoxLayout()
        btns.addWidget(save)
        btns.addWidget(cancel)

        layout.addRow(btns)

        def do_save():
            try:
                t.name = name.text()
                t.description = desc.text()
                t.price_morning = int(price_m.text())
                t.price_afternoon = int(price_a.text())
                t.price_full_day = int(price_f.text())
                t.deposit = int(deposit.text())

                session.commit()
                session.close()

                Toast(self.main_window, "Utánfutó frissítve", True).show_toast()

                dialog.accept()
                self.load_data()

            except Exception:
                Toast(self.main_window, "Hibás adat!", False).show_toast()

        save.clicked.connect(do_save)
        cancel.clicked.connect(lambda: (session.close(), dialog.reject()))

        dialog.setLayout(layout)
        dialog.exec()