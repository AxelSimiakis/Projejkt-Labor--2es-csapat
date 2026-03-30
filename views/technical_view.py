from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QHBoxLayout, QHeaderView, QLabel, QDialog,
    QFormLayout, QLineEdit, QAbstractItemView, QMessageBox,
    QDateEdit
)
from PySide6.QtCore import Qt, QDate

from database import SessionLocal
from models.trailer import Trailer
from core.toast import Toast
from services.trailer_service import TrailerService


STATUS_TO_HU = {
    "available": "Elérhető",
    "service": "Szerviz",
    "inactive": "Inaktív"
}


class TechnicalView(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        layout = QVBoxLayout()

        top = QHBoxLayout()

        title = QLabel("Utánfutók kezelése")
        title.setStyleSheet("color:white; font-size:18px; font-weight:bold;")

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

        top.addWidget(title)
        top.addStretch()
        top.addWidget(add_btn)
        layout.addLayout(top)

        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "Név", "Státusz", "Leírás", "Délelőtt", "Délután", "Egész nap", "Kaució", "Művelet"
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

        QLineEdit, QDateEdit {
            background-color: #111827;
            color: white;
            padding: 8px;
            border-radius: 8px;
            border: 1px solid #374151;
            min-height: 18px;
        }

        QLineEdit:focus, QDateEdit:focus {
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

    def _danger_button_style(self):
        return """
        QPushButton {
            background-color: #b91c1c;
            color: white;
            border: none;
            border-radius: 6px;
            padding: 6px 12px;
            font-size: 13px;
        }
        QPushButton:hover {
            background-color: #991b1b;
        }
        """

    def load_data(self):
        session = SessionLocal()
        try:
            trailers = session.query(Trailer).order_by(Trailer.name.asc()).all()

            self.table.clearContents()
            self.table.setRowCount(len(trailers))

            header = self.table.horizontalHeader()
            header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
            header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
            header.setSectionResizeMode(2, QHeaderView.Stretch)
            header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
            header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
            header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
            header.setSectionResizeMode(6, QHeaderView.ResizeToContents)
            header.setSectionResizeMode(7, QHeaderView.Fixed)

            self.table.setColumnWidth(7, 520)

            for row, t in enumerate(trailers):
                self.table.setItem(row, 0, QTableWidgetItem(t.name))
                self.table.setItem(row, 1, QTableWidgetItem(STATUS_TO_HU.get(t.status or "available", "Elérhető")))
                self.table.setItem(row, 2, QTableWidgetItem(t.description or ""))
                self.table.setItem(row, 3, QTableWidgetItem(f"{t.price_morning} Ft"))
                self.table.setItem(row, 4, QTableWidgetItem(f"{t.price_afternoon} Ft"))
                self.table.setItem(row, 5, QTableWidgetItem(f"{t.price_full_day} Ft"))
                self.table.setItem(row, 6, QTableWidgetItem(f"{t.deposit} Ft"))

                edit_btn = QPushButton("Szerkesztés")
                edit_btn.setFixedHeight(32)
                edit_btn.setMinimumWidth(95)
                edit_btn.setCursor(Qt.PointingHandCursor)
                edit_btn.setStyleSheet("""
                QPushButton {
                    background-color: #374151;
                    color: white;
                    border-radius: 6px;
                    padding: 6px 12px;
                    font-size: 13px;
                    border: none;
                }
                QPushButton:hover {
                    background-color: #4b5563;
                }
                """)
                edit_btn.clicked.connect(lambda _, tid=t.id: self.edit_trailer(tid))

                service_btn = QPushButton("Szerviz")
                service_btn.setFixedHeight(32)
                service_btn.setMinimumWidth(80)
                service_btn.setCursor(Qt.PointingHandCursor)
                service_btn.setStyleSheet("""
                QPushButton {
                    background-color: #d97706;
                    color: white;
                    border-radius: 6px;
                    padding: 6px 12px;
                    font-size: 13px;
                    border: none;
                }
                QPushButton:hover {
                    background-color: #b45309;
                }
                """)
                service_btn.clicked.connect(lambda _, tid=t.id: self.open_service_dialog(tid))

                inactive_btn = QPushButton("Inaktív")
                inactive_btn.setFixedHeight(32)
                inactive_btn.setMinimumWidth(80)
                inactive_btn.setCursor(Qt.PointingHandCursor)
                inactive_btn.setStyleSheet("""
                QPushButton {
                    background-color: #b91c1c;
                    color: white;
                    border-radius: 6px;
                    padding: 6px 12px;
                    font-size: 13px;
                    border: none;
                }
                QPushButton:hover {
                    background-color: #991b1b;
                }
                """)
                inactive_btn.clicked.connect(lambda _, tid=t.id: self.set_inactive(tid))

                activate_btn = QPushButton("Aktív")
                activate_btn.setFixedHeight(32)
                activate_btn.setMinimumWidth(70)
                activate_btn.setCursor(Qt.PointingHandCursor)
                activate_btn.setStyleSheet("""
                QPushButton {
                    background-color: #16a34a;
                    color: white;
                    border-radius: 6px;
                    padding: 6px 12px;
                    font-size: 13px;
                    border: none;
                }
                QPushButton:hover {
                    background-color: #15803d;
                }
                """)
                activate_btn.clicked.connect(lambda _, tid=t.id: self.set_available(tid))

                delete_btn = QPushButton("Törlés")
                delete_btn.setFixedHeight(32)
                delete_btn.setMinimumWidth(75)
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
                delete_btn.clicked.connect(lambda _, tid=t.id: self.delete_trailer(tid))

                container = QWidget()
                container.setStyleSheet("background: transparent; border: none;")
                btn_layout = QHBoxLayout(container)
                btn_layout.setContentsMargins(6, 0, 6, 0)
                btn_layout.setSpacing(8)
                btn_layout.addWidget(edit_btn)
                btn_layout.addWidget(service_btn)
                btn_layout.addWidget(inactive_btn)
                btn_layout.addWidget(activate_btn)
                btn_layout.addWidget(delete_btn)
                btn_layout.addStretch()

                self.table.setCellWidget(row, 7, container)
        finally:
            session.close()

    def create_trailer(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Új utánfutó")
        dialog.resize(460, 580)
        self._apply_dialog_style(dialog)

        layout = QFormLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 16)

        name = QLineEdit()
        description = QLineEdit()

        length_cm = QLineEdit()
        width_cm = QLineEdit()
        max_weight = QLineEdit()

        price_morning = QLineEdit()
        price_afternoon = QLineEdit()
        price_full_day = QLineEdit()
        deposit = QLineEdit()
        late_fee = QLineEdit()
        image_path = QLineEdit()

        layout.addRow("Név:", name)
        layout.addRow("Leírás:", description)
        layout.addRow("Hossz (cm):", length_cm)
        layout.addRow("Szélesség (cm):", width_cm)
        layout.addRow("Max teherbírás (kg):", max_weight)
        layout.addRow("Délelőtt ár:", price_morning)
        layout.addRow("Délután ár:", price_afternoon)
        layout.addRow("Egész nap ár:", price_full_day)
        layout.addRow("Kaució:", deposit)
        layout.addRow("Késedelmi díj:", late_fee)
        layout.addRow("Kép útvonala:", image_path)

        save = QPushButton("Mentés")
        save.setStyleSheet(self._primary_button_style())

        cancel = QPushButton("Mégse")
        cancel.setStyleSheet(self._secondary_button_style())

        btns = QHBoxLayout()
        btns.addWidget(save)
        btns.addWidget(cancel)
        layout.addRow(btns)

        dialog.setLayout(layout)

        def do_save():
            session = SessionLocal()
            try:
                new_trailer = Trailer(
                    name=name.text().strip(),
                    description=description.text().strip(),
                    length_cm=int(length_cm.text() or 0),
                    width_cm=int(width_cm.text() or 0),
                    max_weight=int(max_weight.text() or 0),
                    price_morning=int(price_morning.text() or 0),
                    price_afternoon=int(price_afternoon.text() or 0),
                    price_full_day=int(price_full_day.text() or 0),
                    deposit=int(deposit.text() or 0),
                    late_fee=int(late_fee.text() or 0),
                    image_path=image_path.text().strip(),
                    status="available",
                    is_active=True
                )

                session.add(new_trailer)
                session.commit()

                Toast(self.main_window, "Utánfutó létrehozva", True).show_toast()
                dialog.accept()
                self.load_data()

            except Exception as e:
                session.rollback()
                Toast(self.main_window, f"Hiba: {e}", False).show_toast()
            finally:
                session.close()

        save.clicked.connect(do_save)
        cancel.clicked.connect(dialog.reject)
        dialog.exec()

    def edit_trailer(self, trailer_id):
        session = SessionLocal()
        trailer = session.get(Trailer, trailer_id)

        if not trailer:
            session.close()
            Toast(self.main_window, "Az utánfutó nem található", False).show_toast()
            return

        dialog = QDialog(self)
        dialog.setWindowTitle("Utánfutó szerkesztése")
        dialog.resize(460, 580)
        self._apply_dialog_style(dialog)

        layout = QFormLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 16)

        name = QLineEdit(trailer.name or "")
        description = QLineEdit(trailer.description or "")

        length_cm = QLineEdit(str(trailer.length_cm or 0))
        width_cm = QLineEdit(str(trailer.width_cm or 0))
        max_weight = QLineEdit(str(trailer.max_weight or 0))

        price_morning = QLineEdit(str(trailer.price_morning or 0))
        price_afternoon = QLineEdit(str(trailer.price_afternoon or 0))
        price_full_day = QLineEdit(str(trailer.price_full_day or 0))
        deposit = QLineEdit(str(trailer.deposit or 0))
        late_fee = QLineEdit(str(trailer.late_fee or 0))
        image_path = QLineEdit(trailer.image_path or "")

        layout.addRow("Név:", name)
        layout.addRow("Leírás:", description)
        layout.addRow("Hossz (cm):", length_cm)
        layout.addRow("Szélesség (cm):", width_cm)
        layout.addRow("Max teherbírás (kg):", max_weight)
        layout.addRow("Délelőtt ár:", price_morning)
        layout.addRow("Délután ár:", price_afternoon)
        layout.addRow("Egész nap ár:", price_full_day)
        layout.addRow("Kaució:", deposit)
        layout.addRow("Késedelmi díj:", late_fee)
        layout.addRow("Kép útvonala:", image_path)

        save = QPushButton("Mentés")
        save.setStyleSheet(self._primary_button_style())

        cancel = QPushButton("Mégse")
        cancel.setStyleSheet(self._secondary_button_style())

        btns = QHBoxLayout()
        btns.addWidget(save)
        btns.addWidget(cancel)
        layout.addRow(btns)

        dialog.setLayout(layout)

        def do_save():
            try:
                trailer.name = name.text().strip()
                trailer.description = description.text().strip()

                trailer.length_cm = int(length_cm.text() or 0)
                trailer.width_cm = int(width_cm.text() or 0)
                trailer.max_weight = int(max_weight.text() or 0)

                trailer.price_morning = int(price_morning.text() or 0)
                trailer.price_afternoon = int(price_afternoon.text() or 0)
                trailer.price_full_day = int(price_full_day.text() or 0)

                trailer.deposit = int(deposit.text() or 0)
                trailer.late_fee = int(late_fee.text() or 0)

                trailer.image_path = image_path.text().strip()

                session.commit()
                Toast(self.main_window, "Utánfutó frissítve", True).show_toast()

                dialog.accept()
                self.load_data()

            except Exception as e:
                session.rollback()
                Toast(self.main_window, f"Hiba: {e}", False).show_toast()

        save.clicked.connect(do_save)

        def close_dialog():
            session.close()
            dialog.reject()

        cancel.clicked.connect(close_dialog)
        dialog.exec()

        if session.is_active:
            session.close()

    def open_service_dialog(self, trailer_id):
        dialog = QDialog(self)
        dialog.setWindowTitle("Szerviz időszak beállítása")
        dialog.resize(360, 180)
        self._apply_dialog_style(dialog)

        layout = QFormLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 16)

        service_until = QDateEdit()
        service_until.setCalendarPopup(True)
        service_until.setDate(QDate.currentDate())
        service_until.setMinimumDate(QDate.currentDate())

        layout.addRow("Szerviz vége:", service_until)

        save = QPushButton("Mentés")
        save.setStyleSheet(self._primary_button_style())

        cancel = QPushButton("Mégse")
        cancel.setStyleSheet(self._secondary_button_style())

        btns = QHBoxLayout()
        btns.addWidget(save)
        btns.addWidget(cancel)
        layout.addRow(btns)

        dialog.setLayout(layout)

        def do_save():
            try:
                selected_date = service_until.date().toPython()

                result = TrailerService.set_trailer_service_until(
                    trailer_id=trailer_id,
                    service_until=selected_date
                )

                if result["cancelled_count"] > 0:
                    Toast(
                        self.main_window,
                        f"Szerviz beállítva, {result['cancelled_count']} foglalás lemondva",
                        True
                    ).show_toast()
                else:
                    Toast(self.main_window, "Szerviz státusz beállítva", True).show_toast()

                dialog.accept()
                self.load_data()

            except Exception as e:
                Toast(self.main_window, f"Hiba: {e}", False).show_toast()

        save.clicked.connect(do_save)
        cancel.clicked.connect(dialog.reject)
        dialog.exec()

    def set_inactive(self, trailer_id):
        reply = QMessageBox.question(
            self,
            "Inaktívvá tétel",
            "Biztosan inaktívvá teszed az utánfutót?\n\nAz összes jövőbeli foglalás lemondásra kerül.",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply != QMessageBox.Yes:
            return

        try:
            result = TrailerService.set_trailer_inactive(trailer_id)

            if result["cancelled_count"] > 0:
                Toast(
                    self.main_window,
                    f"Utánfutó inaktív, {result['cancelled_count']} jövőbeli foglalás lemondva",
                    True
                ).show_toast()
            else:
                Toast(self.main_window, "Utánfutó inaktív állapotba került", True).show_toast()

            self.load_data()

        except Exception as e:
            Toast(self.main_window, f"Hiba: {e}", False).show_toast()

    def set_available(self, trailer_id):
        try:
            TrailerService.set_trailer_available(trailer_id)
            Toast(self.main_window, "Utánfutó ismét elérhető", True).show_toast()
            self.load_data()

        except Exception as e:
            Toast(self.main_window, f"Hiba: {e}", False).show_toast()

    def delete_trailer(self, trailer_id):
        reply = QMessageBox.question(
            self,
            "Törlés",
            "Biztosan törölni szeretnéd ezt az utánfutót?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply != QMessageBox.Yes:
            return

        session = SessionLocal()
        try:
            trailer = session.get(Trailer, trailer_id)
            if trailer:
                session.delete(trailer)
                session.commit()
                Toast(self.main_window, "Utánfutó törölve", False).show_toast()
                self.load_data()
        except Exception as e:
            session.rollback()
            Toast(self.main_window, f"Hiba törlés közben: {e}", False).show_toast()
        finally:
            session.close()