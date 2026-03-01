from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QScrollArea, QSizePolicy, QSpacerItem, QGridLayout, QPushButton
)
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt


class HomeView(QWidget):
    def __init__(self):
        super().__init__()

        # --- Színek (maradnak a jelenlegi zöld + szürke árnyalatok) ---
        self.colors = {
            "bg": "#5b5b5b",
            "card": "#4b4b4b",
            "card_soft": "#474747",
            "border": "#3f3f3f",
            "text": "#f5f5f5",
            "muted": "#d6d6d6",
            "primary": "#16a34a"
        }

        self.setStyleSheet(f"background-color: {self.colors['bg']};")

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("QScrollArea{border:none;}")

        content = QWidget()
        root = QVBoxLayout(content)
        root.setContentsMargins(0, 40, 0, 40)

        # középre igazított konténer
        row = QHBoxLayout()
        row.addItem(QSpacerItem(10, 10, QSizePolicy.Expanding, QSizePolicy.Minimum))

        container = QWidget()
        container.setMaximumWidth(1100)
        container_layout = QVBoxLayout(container)
        container_layout.setSpacing(40)
        container_layout.setContentsMargins(30, 0, 30, 0)

        row.addWidget(container)
        row.addItem(QSpacerItem(10, 10, QSizePolicy.Expanding, QSizePolicy.Minimum))

        root.addLayout(row)
        scroll.setWidget(content)
        outer.addWidget(scroll)

        # =====================================================
        # HERO SZEKCIÓ
        # =====================================================

        hero = QWidget()
        hero_layout = QVBoxLayout(hero)
        hero_layout.setSpacing(16)

        title = QLabel("Pótkocsi kölcsönzés")
        title.setStyleSheet(f"""
            color: {self.colors["text"]};
            font-size: 34px;
            font-weight: 800;
            text-align: center;
        """)

        subtitle = QLabel(
            "A PótkocsiPont egy letisztult és átlátható rendszer, "
            "amely megkönnyíti az utánfutók bérlését és kezelését."
        )
        subtitle.setWordWrap(True)
        subtitle.setStyleSheet(f"""
            color: {self.colors["muted"]};
            font-size: 15px;
        """)

        cta = QPushButton("Utánfutók megtekintése")
        cta.setCursor(Qt.PointingHandCursor)
        cta.setFixedHeight(42)
        cta.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.colors["primary"]};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 0 18px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: #1db954;
            }}
        """)

        hero_layout.addWidget(title)
        hero_layout.addWidget(subtitle)
        hero_layout.addWidget(cta)
        hero_layout.addSpacing(10)

        container_layout.addWidget(hero)

        # =====================================================
        # HIGHLIGHT BOXOK (3 egy sorban)
        # =====================================================

        highlight_grid = QGridLayout()
        highlight_grid.setHorizontalSpacing(20)

        highlight_grid.addWidget(
            self.create_info_box("🚚", "Többféle pótkocsi",
                                 "Különböző méretű és típusú utánfutók egy helyen."), 0, 0)

        highlight_grid.addWidget(
            self.create_info_box("🕒", "Gyors ügyintézés",
                                 "Egyszerű foglalási és adminisztrációs rendszer."), 0, 1)

        highlight_grid.addWidget(
            self.create_info_box("✅", "Átlátható működés",
                                 "Követhető bérlési adatok és stabil rendszer."), 0, 2)

        highlight_grid.setColumnStretch(0, 1)
        highlight_grid.setColumnStretch(1, 1)
        highlight_grid.setColumnStretch(2, 1)

        container_layout.addLayout(highlight_grid)

        # =====================================================
        # SZOLGÁLTATÁSOK (3 kép kártya)
        # =====================================================

        section_title = QLabel("Szolgáltatásaink")
        section_title.setStyleSheet(f"""
            color: {self.colors["text"]};
            font-size: 20px;
            font-weight: 700;
        """)

        container_layout.addWidget(section_title)

        image_grid = QGridLayout()
        image_grid.setHorizontalSpacing(20)

        image_grid.addWidget(
            self.create_image_card("assets/kulonbozo_meretu_utanfutok.png", "Különböző méretű utánfutók"), 0, 0)
        image_grid.addWidget(
            self.create_image_card("assets/biztonsagos_kolcsonzes.png", "Biztonságos kölcsönzés"), 0, 1)
        image_grid.addWidget(
            self.create_image_card("assets/gyors_atvetel.png", "Gyors átvétel"), 0, 2)

        image_grid.setColumnStretch(0, 1)
        image_grid.setColumnStretch(1, 1)
        image_grid.setColumnStretch(2, 1)

        container_layout.addLayout(image_grid)

        # =====================================================
        # FOOTER
        # =====================================================

        footer = QLabel("© 2026 PótkocsiPont – Modern pótkocsi kölcsönzés")
        footer.setAlignment(Qt.AlignCenter)
        footer.setStyleSheet(f"""
            color: {self.colors["muted"]};
            font-size: 12px;
            margin-top: 40px;
        """)

        container_layout.addWidget(footer)

    # =====================================================
    # KOMPONENSEK
    # =====================================================

    def create_info_box(self, icon, title, text):
        box = QFrame()
        box.setStyleSheet(f"""
            QFrame {{
                background-color: {self.colors["card"]};
                border-radius: 10px;
                padding: 20px;
            }}
        """)

        layout = QVBoxLayout(box)
        layout.setSpacing(10)
        layout.setAlignment(Qt.AlignCenter)

        icon_label = QLabel(icon)
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet("font-size: 24px;")
        layout.addWidget(icon_label)

        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet(f"""
            color: {self.colors["text"]};
            font-size: 16px;
            font-weight: 700;
        """)
        layout.addWidget(title_label)

        text_label = QLabel(text)
        text_label.setAlignment(Qt.AlignCenter)
        text_label.setWordWrap(True)
        text_label.setStyleSheet(f"""
            color: {self.colors["muted"]};
            font-size: 13px;
        """)
        layout.addWidget(text_label)

        return box

    def create_image_card(self, path, caption):
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {self.colors["card"]};
                border-radius: 10px;
                padding: 14px;
            }}
        """)

        layout = QVBoxLayout(card)
        layout.setSpacing(12)
        layout.setAlignment(Qt.AlignCenter)

        image = QLabel()
        image.setMinimumHeight(140)
        image.setAlignment(Qt.AlignCenter)

        pix = QPixmap(path)
        if not pix.isNull():
            image.setPixmap(pix.scaled(
                400, 200,
                Qt.KeepAspectRatioByExpanding,
                Qt.SmoothTransformation
            ))
        else:
            image.setText("Kép helye")
            image.setStyleSheet(f"color:{self.colors['muted']};")

        layout.addWidget(image)

        caption_label = QLabel(caption)
        caption_label.setAlignment(Qt.AlignCenter)
        caption_label.setStyleSheet(f"""
            color: {self.colors["text"]};
            font-size: 13px;
            font-weight: 600;
        """)
        layout.addWidget(caption_label)

        return card