from datetime import date
import calendar

from PySide6.QtCore import QDate, Qt, Signal, QRect
from PySide6.QtGui import QPixmap, QColor, QPainter, QPen
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QComboBox,
    QMessageBox,
    QFrame,
    QScrollArea,
    QGridLayout,
    QCalendarWidget,
)

from core.session_manager import SessionManager
from core.toast import Toast
from services.booking_service import (
    create_booking,
    get_availability_for_trailer_and_date,
    get_availability_map_for_period,
)
from viewmodels.trailer_list_vm import TrailerListViewModel


class AvailabilityCalendar(QCalendarWidget):
    dayClicked = Signal(QDate)
    pageChangedManually = Signal(int, int)

    def __init__(self):
        super().__init__()
        self.availability_map = {}

        self.setGridVisible(True)
        self.clicked.connect(self.dayClicked.emit)
        self.currentPageChanged.connect(self._emit_page_changed)

        self.setStyleSheet("""
            QCalendarWidget QWidget {
                alternate-background-color: #111827;
                background-color: #111827;
                color: white;
                font-size: 11px;
            }
            QCalendarWidget QToolButton {
                color: white;
                font-weight: bold;
                background: transparent;
                margin: 2px;
                padding: 4px;
            }
            QCalendarWidget QMenu {
                background-color: #1f2937;
                color: white;
            }
            QCalendarWidget QSpinBox {
                color: white;
                background-color: #1f2937;
                selection-background-color: #16a34a;
            }
            QCalendarWidget QAbstractItemView:enabled {
                color: white;
                background-color: #111827;
                selection-background-color: transparent;
                selection-color: white;
                font-size: 11px;
            }
        """)

    def _emit_page_changed(self, year, month):
        self.pageChangedManually.emit(year, month)

    def set_availability_map(self, availability_map: dict):
        self.availability_map = availability_map
        self.updateCells()

    def paintCell(self, painter: QPainter, rect: QRect, qdate: QDate):
        py_date = date(qdate.year(), qdate.month(), qdate.day())
        today = date.today()
        state = self.availability_map.get(py_date, "free")

        painter.save()
        #ElMÚLT NAPOK → SZÜRKE
        if py_date <= today:
            painter.fillRect(rect.adjusted(2, 2, -2, -2), QColor("#6b7280"))
        
        diff = (py_date - today).days

        if diff <= 2:
            painter.fillRect(rect.adjusted(2, 2, -2, -2), QColor("#6b7280"))
        
        else:
            if state == "full":
                painter.fillRect(rect.adjusted(2, 2, -2, -2), QColor("#dc2626"))
            elif state == "partial":
                painter.fillRect(rect.adjusted(2, 2, -2, -2), QColor("#f59e0b"))
            else:
                painter.fillRect(rect.adjusted(2, 2, -2, -2), QColor("#16a34a"))

        # kijelölés kerete
        if qdate == self.selectedDate():
            pen = QPen(QColor("#ffffff"))
            pen.setWidth(2)
            painter.setPen(pen)
            painter.drawRect(rect.adjusted(1, 1, -2, -2))

        # szöveg szín
        painter.setPen(QColor("#e5e7eb"))
        painter.setPen(QColor("white"))
        painter.drawText(rect, Qt.AlignCenter, str(qdate.day()))

        painter.restore()


class TrailerCard(QFrame):
    clicked = Signal(object)

    def __init__(self, trailer):
        super().__init__()
        self.trailer = trailer
        self.setCursor(Qt.PointingHandCursor)
        self.setObjectName("trailerCard")
        self.setStyleSheet("""
            QFrame#trailerCard {
                background-color: #1f2937;
                border: 1px solid #374151;
                border-radius: 14px;
            }
            QFrame#trailerCard:hover {
                border: 1px solid #16a34a;
                background-color: #243042;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        self.image_label = QLabel()
        self.image_label.setFixedHeight(140)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("""
            background-color: #111827;
            border-radius: 10px;
            color: #9ca3af;
        """)

        pixmap = QPixmap(getattr(trailer, "image_path", "") or "")
        if not pixmap.isNull():
            self.image_label.setPixmap(
                pixmap.scaled(
                    260,
                    140,
                    Qt.KeepAspectRatioByExpanding,
                    Qt.SmoothTransformation
                )
            )
        else:
            self.image_label.setText("Nincs kép")

        self.name_label = QLabel(trailer.name)
        self.name_label.setStyleSheet("font-size: 16px; font-weight: bold; color: white;")

        self.desc_label = QLabel((trailer.description or "Nincs leírás.")[:70])
        self.desc_label.setWordWrap(True)
        self.desc_label.setStyleSheet("color: #d1d5db; font-size: 12px;")

        self.price_label = QLabel(
            f"Délelőtt: {trailer.price_morning} Ft\n"
            f"Délután: {trailer.price_afternoon} Ft\n"
            f"Egész nap: {trailer.price_full_day} Ft"
        )
        self.price_label.setStyleSheet("color: #f3f4f6; font-size: 12px;")

        layout.addWidget(self.image_label)
        layout.addWidget(self.name_label)
        layout.addWidget(self.desc_label)
        layout.addWidget(self.price_label)

    def mousePressEvent(self, event):
        self.clicked.emit(self.trailer)
        super().mousePressEvent(event)


class TrailerListView(QWidget):
    def __init__(self, main_window=None):
        super().__init__()
        self.main_window = main_window
        self.viewmodel = TrailerListViewModel()
        self.trailers = []
        self.selected_trailer = None

        self.setWindowTitle("Elérhető utánfutók")

        root = QHBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(20)

        # Bal oldal - csempék
        left_wrapper = QFrame()
        left_wrapper.setStyleSheet("""
            QFrame {
                background-color: transparent;
                border-radius: 12px;
            }
        """)
        left_layout = QVBoxLayout(left_wrapper)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(12)

        left_title = QLabel("Elérhető utánfutók")
        left_title.setStyleSheet("font-size: 28px; font-weight: bold; color: white;")
        left_layout.addWidget(left_title)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
        """)

        self.cards_container = QWidget()
        self.cards_layout = QGridLayout(self.cards_container)
        self.cards_layout.setSpacing(16)
        self.cards_layout.setContentsMargins(0, 0, 0, 0)

        self.scroll.setWidget(self.cards_container)
        left_layout.addWidget(self.scroll)

        root.addWidget(left_wrapper, 3)

        # Jobb oldal - scrollozható részletek panel
        self.right_scroll = QScrollArea()
        self.right_scroll.setWidgetResizable(True)
        self.right_scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
        """)

        self.right_panel = QFrame()
        self.right_panel.setStyleSheet("""
            QFrame {
                background-color: #1f2937;
                border-radius: 16px;
                color: white;
            }
        """)
        self.right_panel.setMinimumWidth(430)

        right_layout = QVBoxLayout(self.right_panel)
        right_layout.setContentsMargins(18, 18, 18, 18)
        right_layout.setSpacing(8)

        self.image_label = QLabel("Válassz egy utánfutót")
        self.image_label.setFixedHeight(220)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("""
            background-color: #111827;
            border: 1px solid #374151;
            border-radius: 12px;
            color: #9ca3af;
            font-size: 16px;
        """)
        right_layout.addWidget(self.image_label)

        self.name_label = QLabel("Nincs kiválasztott utánfutó")
        self.name_label.setStyleSheet("font-size: 22px; font-weight: bold; color: white;")
        right_layout.addWidget(self.name_label)

        self.description_label = QLabel("Kattints a bal oldali csempék egyikére.")
        self.description_label.setWordWrap(True)
        self.description_label.setStyleSheet("color: #d1d5db; font-size: 14px;")
        right_layout.addWidget(self.description_label)

        self.price_label = QLabel("-")
        self.price_label.setStyleSheet("color: white; font-size: 14px;")
        right_layout.addWidget(self.price_label)

        legend = QLabel("Jelmagyarázat: zöld = szabad, sárga = részben foglalt, piros = teljesen foglalt")
        legend.setWordWrap(True)
        legend.setStyleSheet("color: #d1d5db; font-size: 12px;")
        right_layout.addWidget(legend)

        self.calendar = AvailabilityCalendar()
        self.calendar.setFixedHeight(280)
        self.calendar.setMinimumHeight(280)
        self.calendar.setMaximumHeight(280)
        self.calendar.dayClicked.connect(self.on_calendar_day_selected)
        self.calendar.pageChangedManually.connect(self.refresh_calendar_month)
        right_layout.addWidget(self.calendar)

        self.selected_date_label = QLabel("Kiválasztott dátum: -")
        self.selected_date_label.setStyleSheet("color: white; font-size: 14px;")
        right_layout.addWidget(self.selected_date_label)

        self.availability_morning = QLabel("Délelőtt: -")
        self.availability_afternoon = QLabel("Délután: -")
        self.availability_full_day = QLabel("Egész nap: -")

        for label in [self.availability_morning, self.availability_afternoon, self.availability_full_day]:
            label.setStyleSheet("color: white; font-size: 14px;")
            right_layout.addWidget(label)

        self.period_combo = QComboBox()
        self.period_combo.addItem("Délelőtt", "morning")
        self.period_combo.addItem("Délután", "afternoon")
        self.period_combo.addItem("Egész nap", "full_day")
        self.period_combo.setStyleSheet("""
            QComboBox {
                background-color: #111827;
                color: white;
                padding: 8px;
                border-radius: 8px;
                border: 1px solid #374151;
            }
        """)
        right_layout.addWidget(self.period_combo)

        self.book_button = QPushButton("Foglalás")
        self.book_button.clicked.connect(self.book_selected_trailer)
        self.book_button.setStyleSheet("""
            QPushButton {
                background-color: #16a34a;
                color: white;
                padding: 10px;
                border: none;
                border-radius: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #15803d;
            }
        """)
        right_layout.addWidget(self.book_button)

        self.login_hint = QLabel("")
        self.login_hint.setWordWrap(True)
        self.login_hint.setStyleSheet("color: #fbbf24;")
        right_layout.addWidget(self.login_hint)

        right_layout.addStretch()

        self.right_scroll.setWidget(self.right_panel)
        root.addWidget(self.right_scroll, 2)

        self.load_trailers()
        self.refresh_auth_state()

    def clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def load_trailers(self):
        self.trailers = self.viewmodel.get_all_trailers()
        self.clear_layout(self.cards_layout)

        columns = 2
        row = 0
        col = 0

        for trailer in self.trailers:
            card = TrailerCard(trailer)
            card.clicked.connect(self.select_trailer)
            self.cards_layout.addWidget(card, row, col)

            col += 1
            if col >= columns:
                col = 0
                row += 1

        if self.trailers:
            self.select_trailer(self.trailers[0])
        else:
            self.selected_trailer = None
            self.name_label.setText("Nincs elérhető utánfutó")
            self.description_label.setText("A listában jelenleg nincs aktív utánfutó.")
            self.price_label.setText("-")
            self.image_label.setPixmap(QPixmap())
            self.image_label.setText("Nincs kép")
            self.selected_date_label.setText("Kiválasztott dátum: -")
            self.clear_availability_labels()

    def refresh(self):
        self.load_trailers()
        self.refresh_auth_state()

    def refresh_auth_state(self):
        is_logged_in = SessionManager.instance().is_authenticated()
        self.book_button.setVisible(is_logged_in)
        self.period_combo.setVisible(is_logged_in)

        if is_logged_in:
            self.login_hint.setText("")
        else:
            self.login_hint.setText("Foglalni csak bejelentkezés után lehet.")

    def select_trailer(self, trailer):
        self.selected_trailer = trailer
        self.name_label.setText(trailer.name)
        self.description_label.setText(trailer.description or "Nincs leírás.")
        self.price_label.setText(
            f"Délelőtt: {trailer.price_morning} Ft | "
            f"Délután: {trailer.price_afternoon} Ft | "
            f"Egész nap: {trailer.price_full_day} Ft | "
            f"Kaució: {trailer.deposit} Ft"
        )

        self.load_trailer_image(getattr(trailer, "image_path", None))

        selected_qdate = self.calendar.selectedDate()
        self.selected_date_label.setText(
            f"Kiválasztott dátum: {selected_qdate.toString('yyyy.MM.dd.')}"
        )

        self.refresh_calendar_month(selected_qdate.year(), selected_qdate.month())
        self.refresh_day_availability()

    def load_trailer_image(self, image_path):
        if not image_path:
            self.image_label.setPixmap(QPixmap())
            self.image_label.setText("Nincs kép")
            return

        pixmap = QPixmap(image_path)
        if pixmap.isNull():
            self.image_label.setPixmap(QPixmap())
            self.image_label.setText("Kép nem található")
            return

        scaled = pixmap.scaled(
            self.image_label.width(),
            self.image_label.height(),
            Qt.KeepAspectRatioByExpanding,
            Qt.SmoothTransformation
        )
        self.image_label.setPixmap(scaled)
        self.image_label.setText("")

    def on_calendar_day_selected(self, qdate: QDate):
        self.selected_date_label.setText(f"Kiválasztott dátum: {qdate.toString('yyyy.MM.dd.')}")
        self.refresh_day_availability()

    def get_selected_booking_date(self) -> date:
        qdate = self.calendar.selectedDate()
        return date(qdate.year(), qdate.month(), qdate.day())

    def refresh_calendar_month(self, year: int, month: int):
        if not self.selected_trailer:
            return

        first_day = date(year, month, 1)
        last_day_num = calendar.monthrange(year, month)[1]
        last_day = date(year, month, last_day_num)

        availability_map = get_availability_map_for_period(
            self.selected_trailer.id,
            first_day,
            last_day
        )
        self.calendar.set_availability_map(availability_map)
        
        self.calendar.updateCells()
        self.calendar.repaint()

    def clear_availability_labels(self):
        self.availability_morning.setText("Délelőtt: -")
        self.availability_afternoon.setText("Délután: -")
        self.availability_full_day.setText("Egész nap: -")

    def refresh_day_availability(self):
        if not self.selected_trailer:
            self.clear_availability_labels()
            return

        booking_date = self.get_selected_booking_date()
        availability = get_availability_for_trailer_and_date(self.selected_trailer.id, booking_date)

        self.availability_morning.setText(
            f"Délelőtt: {'Szabad' if availability['morning'] else 'Foglalt'}"
        )
        self.availability_afternoon.setText(
            f"Délután: {'Szabad' if availability['afternoon'] else 'Foglalt'}"
        )
        self.availability_full_day.setText(
            f"Egész nap: {'Szabad' if availability['full_day'] else 'Foglalt'}"
        )

    def book_selected_trailer(self):
        if self.selected_trailer is None:
            toast = Toast(self.main_window or self, "Először válassz utánfutót.", success=False)
            toast.show_toast()
            return

        user = SessionManager.instance().get_user()
        if not user:
            toast = Toast(self.main_window or self, "Foglaláshoz be kell jelentkezni.", success=False)
            toast.show_toast()
            return

        booking_date = self.get_selected_booking_date()
        period = self.period_combo.currentData()

        today = date.today()

        #USER KORLÁTOZÁS
        if user.role == "user":
            diff = (booking_date - today).days

            # múlt tiltás
            if booking_date <= today:
                Toast(
                    self.main_window or self,
                    "Múltbeli dátum nem választható!",
                    success=False
                ).show_toast()
                return
            # 3 napos limit
            
            if diff <= 2:
                Toast(
                    self.main_window or self,
                    "Csak a helyszínen személyesen, telefonon érdeklődjön!",
                    success=False
                ).show_toast()
                return

        try:
            create_booking(user.id, self.selected_trailer.id, booking_date, period)

            self.refresh_calendar_month(booking_date.year, booking_date.month)
            self.refresh_day_availability()

            toast = Toast(
                self.main_window or self,
                f"Sikeres foglalás: {self.selected_trailer.name} - {booking_date.strftime('%Y.%m.%d.')}",
                success=True
            )
            toast.show_toast()

        except ValueError as exc:
            toast = Toast(self.main_window or self, str(exc), success=False)
            toast.show_toast()

        except Exception as exc:
            toast = Toast(self.main_window or self, f"Váratlan hiba történt: {exc}", success=False)
            toast.show_toast()