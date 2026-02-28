"""
ui/placeholder_view.py
----------------------
Egyszerű placeholder oldal a navigációhoz.

Később a valódi "Rólunk", "Szűrés", "Keresés" UI-t,
Ezeket lecserélni külön View-kra.
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QFrame


class PlaceholderView(QWidget):
    """
    Egy minimal oldal: cím + rövid szöveg.
    """

    def __init__(self, title: str, parent: QWidget | None = None):
        super().__init__(parent)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)

        frame = QFrame(self)
        frame.setObjectName("content")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(0, 40, 0, 0)

        label = QLabel(title, frame)
        label.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        label.setObjectName("pageTitle")

        hint = QLabel("Itt majd a tényleges tartalom lesz.", frame)
        hint.setAlignment(Qt.AlignHCenter | Qt.AlignTop)

        layout.addWidget(label)
        layout.addWidget(hint)
        root.addWidget(frame)

        # Alap stílus (külön QSS fájlba is kivehető később)
        self.setStyleSheet("""
            #content { background: white; }
            #pageTitle { font-size: 28px; font-weight: 800; }
        """)