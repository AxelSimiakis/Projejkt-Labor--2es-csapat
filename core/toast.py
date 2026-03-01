from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QGraphicsOpacityEffect
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QPoint


class Toast(QWidget):
    def __init__(self, parent, message, success=True, duration=5000):
        super().__init__(parent)

        self.parent_window = parent
        self.duration = duration

        # NEM Tool flag!
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_StyledBackground, True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 12, 20, 12)

        self.label = QLabel(message)
        self.label.setAlignment(Qt.AlignCenter)

        if success:
            bg_color = "#16a34a"  # zöld
        else:
            bg_color = "#dc2626"  # piros

        self.setStyleSheet(f"""
            QWidget {{
                background-color: {bg_color};
                border-radius: 12px;
            }}
            QLabel {{
                color: white;
                font-size: 14px;
            }}
        """)

        layout.addWidget(self.label)
        self.adjustSize()

        # Fade effect
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)

    def show_toast(self):
        parent_rect = self.parent_window.rect()

        # Középre igazítás vízszintesen
        x = (parent_rect.width() - self.width()) // 2
        y = 20

        # Kezdő pozíció (kicsit feljebb)
        self.move(x, -self.height())
        self.show()

        # Slide animáció
        self.slide_anim = QPropertyAnimation(self, b"pos")
        self.slide_anim.setDuration(400)
        self.slide_anim.setStartValue(QPoint(x, -self.height()))
        self.slide_anim.setEndValue(QPoint(x, y))
        self.slide_anim.setEasingCurve(QEasingCurve.OutCubic)
        self.slide_anim.start()

        # Fade in
        self.fade_in = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_in.setDuration(400)
        self.fade_in.setStartValue(0)
        self.fade_in.setEndValue(1)
        self.fade_in.start()

        QTimer.singleShot(self.duration, self.hide_toast)

    def hide_toast(self):
        self.fade_out = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_out.setDuration(400)
        self.fade_out.setStartValue(1)
        self.fade_out.setEndValue(0)
        self.fade_out.finished.connect(self.close)
        self.fade_out.start()