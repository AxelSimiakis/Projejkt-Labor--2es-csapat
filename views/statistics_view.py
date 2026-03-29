from collections import Counter
from datetime import date, timedelta

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QFrame,
    QGridLayout, QSizePolicy, QTabWidget, QHBoxLayout
)
from PySide6.QtCore import QTimer

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from database import SessionLocal
from models.booking import Booking
from models.trailer import Trailer
from models.user import User


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


class StatsCard(QFrame):
    def __init__(self, title: str, value: str):
        super().__init__()
        self.setStyleSheet("""
        QFrame {
            background-color: #1f2937;
            border: 1px solid #374151;
            border-radius: 12px;
        }
        """)

        self.card_layout = QVBoxLayout(self)
        self.card_layout.setContentsMargins(16, 16, 16, 16)
        self.card_layout.setSpacing(6)

        self.title_label = QLabel(title)
        self.title_label.setStyleSheet("""
            color: #9ca3af;
            font-size: 13px;
            background: transparent;
            border: none;
        """)

        self.value_label = QLabel(value)
        self.value_label.setStyleSheet("""
            color: white;
            font-size: 24px;
            font-weight: bold;
            background: transparent;
            border: none;
        """)

        self.card_layout.addWidget(self.title_label)
        self.card_layout.addWidget(self.value_label)


class ChartCard(QFrame):
    def __init__(self, title: str):
        super().__init__()
        self.setStyleSheet("""
        QFrame {
            background-color: #1f2937;
            border: 1px solid #374151;
            border-radius: 12px;
        }
        """)

        self.card_layout = QVBoxLayout(self)
        self.card_layout.setContentsMargins(12, 12, 12, 12)
        self.card_layout.setSpacing(10)

        self.title_label = QLabel(title)
        self.title_label.setStyleSheet("""
            color: white;
            font-size: 16px;
            font-weight: bold;
            background: transparent;
            border: none;
        """)
        self.card_layout.addWidget(self.title_label)

        self.canvas = FigureCanvas(Figure(figsize=(6.0, 3.6)))
        self.canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.card_layout.addWidget(self.canvas)

    def get_ax(self):
        fig = self.canvas.figure
        fig.clear()
        fig.patch.set_facecolor("#1f2937")

        ax = fig.add_subplot(111)
        ax.set_facecolor("#111827")

        ax.tick_params(colors="white", labelsize=10)
        ax.title.set_color("white")
        ax.xaxis.label.set_color("white")
        ax.yaxis.label.set_color("white")

        for spine in ax.spines.values():
            spine.set_color("#6b7280")

        return ax

    def can_draw(self) -> bool:
        return self.canvas.width() > 10 and self.canvas.height() > 10

    def draw(self):
        self.canvas.draw()


class StatisticsTab(QWidget):
    def __init__(self):
        super().__init__()

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(16)

        self.cards_layout = QHBoxLayout()
        self.cards_layout.setSpacing(12)
        root.addLayout(self.cards_layout)

        self.card_total_bookings = StatsCard("Összes foglalás", "0")
        self.card_active_users = StatsCard("Felhasználók száma", "0")
        self.card_active_trailers = StatsCard("Aktív utánfutók", "0")
        self.card_estimated_revenue = StatsCard("Becsült bevétel", "0 Ft")

        self.cards_layout.addWidget(self.card_total_bookings)
        self.cards_layout.addWidget(self.card_active_users)
        self.cards_layout.addWidget(self.card_active_trailers)
        self.cards_layout.addWidget(self.card_estimated_revenue)

        charts_grid = QGridLayout()
        charts_grid.setSpacing(16)
        root.addLayout(charts_grid)

        self.time_chart = ChartCard("Foglalások idő szerint")
        self.period_chart = ChartCard("Foglalások napszak szerint")
        self.status_chart = ChartCard("Foglalások státusz szerint")
        self.trailer_chart = ChartCard("Legnépszerűbb utánfutók")

        charts_grid.addWidget(self.time_chart, 0, 0)
        charts_grid.addWidget(self.period_chart, 0, 1)
        charts_grid.addWidget(self.status_chart, 1, 0)
        charts_grid.addWidget(self.trailer_chart, 1, 1)

    def _set_card_value(self, card: StatsCard, value: str):
        card.value_label.setText(value)

    def populate(self, bookings, users_count, trailers_count, estimated_revenue, mode: str):
        total_bookings = len(bookings)

        period_counter = Counter()
        status_counter = Counter()
        trailer_counter = Counter()
        time_counter = Counter()

        month_labels_map = {
            1: "Jan", 2: "Feb", 3: "Már", 4: "Ápr", 5: "Máj", 6: "Jún",
            7: "Júl", 8: "Aug", 9: "Szep", 10: "Okt", 11: "Nov", 12: "Dec",
        }

        for booking in bookings:
            booking_date = booking["booking_date"]
            if booking_date:
                if mode == "weekly":
                    time_counter[booking_date.weekday()] += 1
                elif mode == "monthly":
                    time_counter[booking_date.day] += 1
                elif mode == "yearly":
                    time_counter[booking_date.month] += 1
                else:
                    time_counter[booking_date.year] += 1

            period_counter[PERIOD_TO_HU.get(booking["period"], booking["period"])] += 1
            status_counter[STATUS_TO_HU.get(booking["status"], booking["status"])] += 1
            trailer_counter[booking["trailer_name"]] += 1

        self._set_card_value(self.card_total_bookings, str(total_bookings))
        self._set_card_value(self.card_active_users, str(users_count))
        self._set_card_value(self.card_active_trailers, str(trailers_count))
        self._set_card_value(
            self.card_estimated_revenue,
            f"{estimated_revenue:,} Ft".replace(",", " ")
        )

        self._draw_time_chart(time_counter, month_labels_map, mode)
        self._draw_period_chart(period_counter)
        self._draw_status_chart(status_counter)
        self._draw_trailer_chart(trailer_counter)

    def _draw_time_chart(self, time_counter, month_labels_map, mode: str):
        ax = self.time_chart.get_ax()
        fig = self.time_chart.canvas.figure

        if not time_counter:
            ax.text(0.5, 0.5, "Nincs adat", ha="center", va="center", color="white")
            fig.subplots_adjust(left=0.12, right=0.96, top=0.86, bottom=0.22)
            if self.time_chart.can_draw():
                self.time_chart.draw()
            return

        sorted_items = sorted(time_counter.items())

        if mode == "weekly":
            weekday_map = {
                0: "Hétfő",
                1: "Kedd",
                2: "Szerda",
                3: "Csütörtök",
                4: "Péntek",
                5: "Szombat",
                6: "Vasárnap",
            }
            labels = [weekday_map[d] for d, _ in sorted_items]
            values = [count for _, count in sorted_items]
            ax.bar(labels, values)
            ax.set_title("Foglalások napokra bontva", fontsize=11, color="white")
            ax.set_xlabel("Nap")
            ax.tick_params(axis="x", rotation=20)
            fig.subplots_adjust(left=0.12, right=0.96, top=0.86, bottom=0.30)

        elif mode == "monthly":
            labels = [str(day) for day, _ in sorted_items]
            values = [count for _, count in sorted_items]
            ax.bar(labels, values)
            ax.set_title("Foglalások napokra bontva", fontsize=11, color="white")
            ax.set_xlabel("Nap")
            ax.tick_params(axis="x", rotation=25)
            fig.subplots_adjust(left=0.12, right=0.96, top=0.86, bottom=0.26)

        elif mode == "yearly":
            labels = [month_labels_map[m] for m, _ in sorted_items]
            values = [count for _, count in sorted_items]
            ax.bar(labels, values)
            ax.set_title("Foglalások hónapokra bontva", fontsize=11, color="white")
            ax.set_xlabel("Hónap")
            ax.tick_params(axis="x", rotation=0)
            fig.subplots_adjust(left=0.12, right=0.96, top=0.86, bottom=0.18)

        else:
            labels = [str(year) for year, _ in sorted_items]
            values = [count for _, count in sorted_items]
            ax.bar(labels, values)
            ax.set_title("Foglalások évekre bontva", fontsize=11, color="white")
            ax.set_xlabel("Év")
            ax.tick_params(axis="x", rotation=0)
            fig.subplots_adjust(left=0.12, right=0.96, top=0.86, bottom=0.18)

        ax.set_ylabel("Db")
        if self.time_chart.can_draw():
            self.time_chart.draw()

    def _draw_period_chart(self, period_counter):
        ax = self.period_chart.get_ax()
        fig = self.period_chart.canvas.figure

        if not period_counter:
            ax.text(0.5, 0.5, "Nincs adat", ha="center", va="center", color="white")
            fig.subplots_adjust(left=0.12, right=0.96, top=0.86, bottom=0.20)
            if self.period_chart.can_draw():
                self.period_chart.draw()
            return

        labels = list(period_counter.keys())
        values = list(period_counter.values())

        ax.bar(labels, values)
        ax.set_ylabel("Db")
        ax.set_title("Foglalások napszak szerint", fontsize=11, color="white")
        fig.subplots_adjust(left=0.12, right=0.96, top=0.86, bottom=0.20)
        if self.period_chart.can_draw():
            self.period_chart.draw()

    def _draw_status_chart(self, status_counter):
        fig = self.status_chart.canvas.figure
        fig.clear()
        fig.patch.set_facecolor("#1f2937")

        if not self.status_chart.can_draw():
            return

        ax = fig.add_subplot(111)
        ax.set_facecolor("#111827")

        if not status_counter:
            ax.text(0.5, 0.5, "Nincs adat", ha="center", va="center", color="white")
            fig.subplots_adjust(left=0.10, right=0.90, top=0.84, bottom=0.10)
            self.status_chart.canvas.draw()
            return

        labels = list(status_counter.keys())
        values = list(status_counter.values())

        wedges, texts, autotexts = ax.pie(
            values,
            labels=labels,
            autopct="%1.0f%%",
            startangle=90,
            radius=1.0,
            textprops={"color": "white", "fontsize": 11},
            wedgeprops={"linewidth": 1, "edgecolor": "#1f2937"}
        )

        for text in texts:
            text.set_color("white")
            text.set_fontsize(11)

        for autotext in autotexts:
            autotext.set_color("white")
            autotext.set_fontsize(10)

        ax.set_title("Foglalások státusz szerint", fontsize=12, color="white")
        fig.subplots_adjust(left=0.10, right=0.90, top=0.84, bottom=0.10)
        self.status_chart.canvas.draw()

    def _draw_trailer_chart(self, trailer_counter):
        ax = self.trailer_chart.get_ax()
        fig = self.trailer_chart.canvas.figure

        if not trailer_counter:
            ax.text(0.5, 0.5, "Nincs adat", ha="center", va="center", color="white")
            fig.subplots_adjust(left=0.20, right=0.96, top=0.86, bottom=0.18)
            if self.trailer_chart.can_draw():
                self.trailer_chart.draw()
            return

        most_used = trailer_counter.most_common(5)
        labels = [name for name, _ in most_used]
        values = [count for _, count in most_used]

        short_labels = [label if len(label) <= 18 else label[:15] + "..." for label in labels]

        ax.barh(short_labels, values)
        ax.set_xlabel("Foglalások száma")
        ax.set_title("Top 5 utánfutó", fontsize=11, color="white")
        fig.subplots_adjust(left=0.28, right=0.96, top=0.86, bottom=0.18)
        if self.trailer_chart.can_draw():
            self.trailer_chart.draw()


class StatisticsView(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        self.weekly_payload = None
        self.monthly_payload = None
        self.yearly_payload = None
        self.overall_payload = None

        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(16)

        title = QLabel("Statisztika")
        title.setStyleSheet("""
            color:white;
            font-size:22px;
            font-weight:bold;
            background: transparent;
            border: none;
        """)
        root.addWidget(title)

        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
        QTabWidget::pane {
            border: none;
            background: transparent;
        }
        QTabBar::tab {
            background: #1f2937;
            color: white;
            padding: 10px 18px;
            margin-right: 4px;
            border-top-left-radius: 8px;
            border-top-right-radius: 8px;
        }
        QTabBar::tab:selected {
            background: #16a34a;
            font-weight: bold;
        }
        QTabBar::tab:!selected {
            background: #374151;
        }
        """)

        self.week_tab = StatisticsTab()
        self.month_tab = StatisticsTab()
        self.year_tab = StatisticsTab()
        self.overall_tab = StatisticsTab()

        self.tabs.addTab(self.week_tab, "Heti")
        self.tabs.addTab(self.month_tab, "Havi")
        self.tabs.addTab(self.year_tab, "Éves")
        self.tabs.addTab(self.overall_tab, "Összesített")
        self.tabs.currentChanged.connect(self._render_current_tab)

        root.addWidget(self.tabs)

        QTimer.singleShot(0, self.refresh_data)

    def showEvent(self, event):
        super().showEvent(event)
        QTimer.singleShot(0, self._render_current_tab)

    def refresh_data(self):
        session = SessionLocal()
        try:
            today = date.today()

            all_users_count = session.query(User).count()
            active_trailers_count = session.query(Trailer).filter(Trailer.is_active == True).count()

            week_start = today - timedelta(days=today.weekday())
            week_end = week_start + timedelta(days=7)

            if today.month == 12:
                next_month_first = date(today.year + 1, 1, 1)
            else:
                next_month_first = date(today.year, today.month + 1, 1)

            weekly_bookings_raw = (
                session.query(Booking)
                .filter(
                    Booking.booking_date.isnot(None),
                    Booking.booking_date >= week_start,
                    Booking.booking_date < week_end
                )
                .all()
            )

            monthly_bookings_raw = (
                session.query(Booking)
                .filter(
                    Booking.booking_date.isnot(None),
                    Booking.booking_date >= date(today.year, today.month, 1),
                    Booking.booking_date < next_month_first
                )
                .all()
            )

            yearly_bookings_raw = (
                session.query(Booking)
                .filter(
                    Booking.booking_date.isnot(None),
                    Booking.booking_date >= date(today.year, 1, 1),
                    Booking.booking_date < date(today.year + 1, 1, 1)
                )
                .all()
            )

            overall_bookings_raw = (
                session.query(Booking)
                .filter(Booking.booking_date.isnot(None))
                .all()
            )

            weekly_bookings = [self._serialize_booking(b) for b in weekly_bookings_raw]
            monthly_bookings = [self._serialize_booking(b) for b in monthly_bookings_raw]
            yearly_bookings = [self._serialize_booking(b) for b in yearly_bookings_raw]
            overall_bookings = [self._serialize_booking(b) for b in overall_bookings_raw]

            self.weekly_payload = {
                "bookings": weekly_bookings,
                "users_count": all_users_count,
                "trailers_count": active_trailers_count,
                "estimated_revenue": self._calculate_revenue(weekly_bookings),
                "mode": "weekly",
            }

            self.monthly_payload = {
                "bookings": monthly_bookings,
                "users_count": all_users_count,
                "trailers_count": active_trailers_count,
                "estimated_revenue": self._calculate_revenue(monthly_bookings),
                "mode": "monthly",
            }

            self.yearly_payload = {
                "bookings": yearly_bookings,
                "users_count": all_users_count,
                "trailers_count": active_trailers_count,
                "estimated_revenue": self._calculate_revenue(yearly_bookings),
                "mode": "yearly",
            }

            self.overall_payload = {
                "bookings": overall_bookings,
                "users_count": all_users_count,
                "trailers_count": active_trailers_count,
                "estimated_revenue": self._calculate_revenue(overall_bookings),
                "mode": "overall",
            }

        finally:
            session.close()

        QTimer.singleShot(0, self._render_current_tab)

    def _serialize_booking(self, booking):
        trailer = booking.trailer
        trailer_name = trailer.name if trailer else f"#{booking.trailer_id}"

        price = 0
        if trailer and booking.status in ["active", "completed"]:
            if booking.period == "morning":
                price = trailer.price_morning
            elif booking.period == "afternoon":
                price = trailer.price_afternoon
            elif booking.period == "full_day":
                price = trailer.price_full_day

        return {
            "booking_date": booking.booking_date,
            "period": booking.period,
            "status": booking.status,
            "trailer_name": trailer_name,
            "price": price,
        }

    def _render_current_tab(self):
        if not self.isVisible():
            return

        current_index = self.tabs.currentIndex()

        if current_index == 0 and self.weekly_payload:
            self.week_tab.populate(
                self.weekly_payload["bookings"],
                self.weekly_payload["users_count"],
                self.weekly_payload["trailers_count"],
                self.weekly_payload["estimated_revenue"],
                self.weekly_payload["mode"],
            )

        elif current_index == 1 and self.monthly_payload:
            self.month_tab.populate(
                self.monthly_payload["bookings"],
                self.monthly_payload["users_count"],
                self.monthly_payload["trailers_count"],
                self.monthly_payload["estimated_revenue"],
                self.monthly_payload["mode"],
            )

        elif current_index == 2 and self.yearly_payload:
            self.year_tab.populate(
                self.yearly_payload["bookings"],
                self.yearly_payload["users_count"],
                self.yearly_payload["trailers_count"],
                self.yearly_payload["estimated_revenue"],
                self.yearly_payload["mode"],
            )

        elif current_index == 3 and self.overall_payload:
            self.overall_tab.populate(
                self.overall_payload["bookings"],
                self.overall_payload["users_count"],
                self.overall_payload["trailers_count"],
                self.overall_payload["estimated_revenue"],
                self.overall_payload["mode"],
            )

    def _calculate_revenue(self, bookings):
        return sum(item["price"] for item in bookings)