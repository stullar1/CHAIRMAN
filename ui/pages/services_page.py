from PySide6.QtWidgets import QWidget, QVBoxLayout, QListWidget
from core.app_state import AppState


class ServicesPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        self.list = QListWidget()
        layout.addWidget(self.list)
        self.load()

    def load(self):
        self.list.clear()
        for s in AppState.services.all():
            self.list.addItem(f"{s.name} — ${s.price} ({s.duration_minutes}m)")
