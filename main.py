"""
main.py
-------
Belépési pont (entry point) az alkalmazáshoz.

- QApplication példányosítása
- MainWindow létrehozása
- Event loop indítása

Minden UI és üzleti logika külön modulokban van (core/, ui/, services/).
"""

from __future__ import annotations

import sys
from PySide6.QtWidgets import QApplication

from core.main_window import MainWindow


def main() -> int:
    """
    Az alkalmazás indítása.
    Visszatérési értéke az app.exec() exit kódja.
    """
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    # Event loop
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())