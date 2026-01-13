from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QListWidget
)
from core.app_state import AppState


class ClientPage(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        title = QLabel("Clients")
        title.setObjectName("page_title")
        layout.addWidget(title)

        form = QHBoxLayout()
        self.name = QLineEdit()
        self.name.setPlaceholderText("Client name")

        self.phone = QLineEdit()
        self.phone.setPlaceholderText("Phone number")

        add_btn = QPushButton("Add Client")
        add_btn.setObjectName("primary")
        add_btn.clicked.connect(self.add_client)

        form.addWidget(self.name)
        form.addWidget(self.phone)
        form.addWidget(add_btn)

        layout.addLayout(form)

        self.list = QListWidget()
        layout.addWidget(self.list)

        self.refresh()

    def refresh(self):
        self.list.clear()
        for c in AppState.clients.all():
            self.list.addItem(f"{c.name}  •  {c.phone}")

    def add_client(self):
        name = self.name.text().strip()
        phone = self.phone.text().strip()
        if not name:
            return

        AppState.clients.create(name, phone)
        self.name.clear()
        self.phone.clear()
        self.refresh()
