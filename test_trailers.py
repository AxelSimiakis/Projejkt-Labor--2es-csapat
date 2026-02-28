import sys
from PySide6.QtWidgets import QApplication
from views.trailer_list_view import TrailerListView

app = QApplication(sys.argv)
window = TrailerListView()
window.show()
sys.exit(app.exec())