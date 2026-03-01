from PySide6.QtGui import QPixmap, QPainter, QPainterPath
from PySide6.QtCore import Qt


def create_round_avatar(image_path, size=40):
    original = QPixmap(image_path)

    if original.isNull():
        return QPixmap()

    # ===== CENTER CROP (négyzet) =====
    width = original.width()
    height = original.height()
    side = min(width, height)

    x = (width - side) // 2
    y = (height - side) // 2

    square = original.copy(x, y, side, side)

    # ===== SKÁLÁZÁS =====
    square = square.scaled(
        size,
        size,
        Qt.KeepAspectRatioByExpanding,
        Qt.SmoothTransformation
    )

    # ===== KÖR MASZK =====
    rounded = QPixmap(size, size)
    rounded.fill(Qt.transparent)

    painter = QPainter(rounded)
    painter.setRenderHint(QPainter.Antialiasing)

    path = QPainterPath()
    path.addEllipse(0, 0, size, size)
    painter.setClipPath(path)

    painter.drawPixmap(0, 0, square)
    painter.end()

    return rounded