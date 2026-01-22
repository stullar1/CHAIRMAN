"""
CHAIRMAN - Client Management Page
Clean, modern design with color accents
"""
from __future__ import annotations

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel, QLineEdit,
    QScrollArea, QTextEdit, QPushButton, QDialog, QMessageBox, QGridLayout,
    QGraphicsBlurEffect
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QColor, QPainter

from core.app_state import AppState
from core.logging_config import get_logger

logger = get_logger(__name__)

# Color palette for cards
CARD_COLORS = ["#5865F2", "#22C55E", "#F59E0B", "#EF4444", "#8B5CF6", "#EC4899", "#06B6D4", "#10B981"]


class ClientDialog(QDialog):
    """Dialog for adding/editing clients with overlay background."""

    def __init__(self, parent=None, client_data=None):
        super().__init__(parent)
        self.client_data = client_data
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setModal(True)
        self._setup_ui()

    def showEvent(self, event):
        """Position dialog to cover entire parent window."""
        super().showEvent(event)
        if self.parent():
            # Get the main window and its geometry
            main_window = self.parent().window()
            self.setGeometry(main_window.geometry())

    def paintEvent(self, event):
        """Draw semi-transparent dark overlay background."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.fillRect(self.rect(), QColor(0, 0, 0, 180))

    def mousePressEvent(self, event):
        """Close dialog when clicking outside the form."""
        if hasattr(self, 'container'):
            # Get container position in dialog coordinates
            container_geo = self.container.geometry()
            if not container_geo.contains(event.pos()):
                self.reject()
        super().mousePressEvent(event)

    def _setup_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setAlignment(Qt.AlignCenter)

        self.container = QFrame()
        self.container.setObjectName("dialog_container")
        self.container.setFixedSize(420, 480)
        self.container.setStyleSheet("""
            QFrame#dialog_container {
                background-color: #1A1A1A;
                border-radius: 12px;
                border: 1px solid #333333;
            }
            QFrame#dialog_container QLabel {
                border: none;
                background: transparent;
            }
        """)

        layout = QVBoxLayout(self.container)
        layout.setContentsMargins(32, 28, 32, 32)
        layout.setSpacing(0)

        # Header
        header = QHBoxLayout()
        title = QLabel("Edit Client" if self.client_data else "New Client")
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: #FFFFFF;")
        header.addWidget(title)
        header.addStretch()

        close_btn = QPushButton("x")
        close_btn.setFixedSize(28, 28)
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                color: #555555;
                font-size: 16px;
                border-radius: 14px;
            }
            QPushButton:hover {
                background-color: #EF4444;
                color: #FFFFFF;
            }
        """)
        close_btn.clicked.connect(self.reject)
        header.addWidget(close_btn)
        layout.addLayout(header)

        layout.addSpacing(28)

        # Form styling
        label_style = "font-size: 11px; font-weight: 600; color: #666666; letter-spacing: 1px;"
        input_style = """
            QLineEdit {
                background-color: #252525;
                border: none;
                border-radius: 8px;
                padding: 14px 16px;
                color: #FFFFFF;
                font-size: 14px;
            }
            QLineEdit:focus {
                background-color: #2A2A2A;
            }
            QLineEdit::placeholder {
                color: #555555;
            }
        """

        # Name
        name_label = QLabel("CLIENT NAME")
        name_label.setStyleSheet(label_style)
        layout.addWidget(name_label)
        layout.addSpacing(8)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter client name...")
        self.name_input.setMinimumHeight(48)
        self.name_input.setStyleSheet(input_style)
        if self.client_data:
            self.name_input.setText(self.client_data.name)
        layout.addWidget(self.name_input)

        layout.addSpacing(20)

        # Phone
        phone_label = QLabel("PHONE NUMBER")
        phone_label.setStyleSheet(label_style)
        layout.addWidget(phone_label)
        layout.addSpacing(8)

        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("(555) 123-4567")
        self.phone_input.setMinimumHeight(48)
        self.phone_input.setStyleSheet(input_style)
        if self.client_data and self.client_data.phone:
            self.phone_input.setText(self.client_data.phone)
        layout.addWidget(self.phone_input)

        layout.addSpacing(20)

        # Notes
        notes_label = QLabel("NOTES")
        notes_label.setStyleSheet(label_style)
        layout.addWidget(notes_label)
        layout.addSpacing(8)

        self.notes_input = QTextEdit()
        self.notes_input.setPlaceholderText("Preferences, allergies, etc...")
        self.notes_input.setFixedHeight(80)
        self.notes_input.setStyleSheet("""
            QTextEdit {
                background-color: #252525;
                border: none;
                border-radius: 8px;
                padding: 12px 14px;
                color: #FFFFFF;
                font-size: 14px;
            }
            QTextEdit:focus {
                background-color: #2A2A2A;
            }
        """)
        if self.client_data and self.client_data.notes:
            self.notes_input.setPlainText(self.client_data.notes)
        layout.addWidget(self.notes_input)

        layout.addSpacing(32)

        # Buttons
        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setMinimumHeight(48)
        cancel_btn.setCursor(Qt.PointingHandCursor)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #252525;
                border: none;
                border-radius: 8px;
                color: #AAAAAA;
                font-weight: 600;
                font-size: 14px;
                padding: 0 24px;
            }
            QPushButton:hover {
                background-color: #333333;
                color: #FFFFFF;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(cancel_btn)

        save_btn = QPushButton("Save Client" if self.client_data else "Add Client")
        save_btn.setMinimumHeight(48)
        save_btn.setCursor(Qt.PointingHandCursor)
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #5865F2;
                border: none;
                border-radius: 8px;
                color: #FFFFFF;
                font-weight: 600;
                font-size: 14px;
                padding: 0 32px;
            }
            QPushButton:hover {
                background-color: #4752C4;
            }
        """)
        save_btn.clicked.connect(self.accept)
        btn_row.addWidget(save_btn)

        layout.addLayout(btn_row)
        outer.addWidget(self.container)

    def get_data(self):
        return {
            "name": self.name_input.text().strip(),
            "phone": self.phone_input.text().strip(),
            "notes": self.notes_input.toPlainText().strip()
        }


class ClientCard(QFrame):
    """Modern client card with color accent line."""

    def __init__(self, client, color: str, on_edit, on_delete, parent=None):
        super().__init__(parent)
        self.client = client
        self.color = color
        self.on_edit = on_edit
        self.on_delete = on_delete
        self._setup_ui()

    def _setup_ui(self):
        self.setObjectName("client_card")
        self.setStyleSheet(f"""
            QFrame#client_card {{
                background-color: #1A1A1A;
                border: none;
                border-left: 3px solid {self.color};
                border-radius: 0px;
            }}
            QFrame#client_card:hover {{
                background-color: #1E1E1E;
            }}
            QFrame#client_card QLabel {{
                border: none;
            }}
        """)
        self.setMinimumHeight(90)
        self.setMaximumHeight(110)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(16)

        # Left: Info
        info_col = QVBoxLayout()
        info_col.setSpacing(4)

        name = QLabel(self.client.name)
        name.setStyleSheet("font-size: 15px; font-weight: 600; color: #FFFFFF; background: transparent;")
        info_col.addWidget(name)

        # Phone with color accent
        if self.client.phone:
            phone = QLabel(self.client.phone)
            phone.setStyleSheet(f"font-size: 12px; color: {self.color}; background: transparent;")
            info_col.addWidget(phone)

        # Notes preview
        if self.client.notes:
            notes_text = self.client.notes[:45] + "..." if len(self.client.notes) > 45 else self.client.notes
            notes = QLabel(notes_text)
            notes.setStyleSheet("font-size: 11px; color: #666666; background: transparent;")
            info_col.addWidget(notes)

        # No-show badge
        if self.client.no_show_count > 0:
            no_show = QLabel(f"{self.client.no_show_count} no-show{'s' if self.client.no_show_count > 1 else ''}")
            no_show.setStyleSheet("font-size: 10px; color: #F59E0B; background: transparent;")
            info_col.addWidget(no_show)

        layout.addLayout(info_col, 1)

        # Right: Actions
        action_col = QVBoxLayout()
        action_col.setSpacing(6)

        edit_btn = QPushButton("Edit")
        edit_btn.setFixedSize(60, 28)
        edit_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #252525;
                border: none;
                border-radius: 6px;
                color: #AAAAAA;
                font-size: 11px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {self.color};
                color: #FFFFFF;
            }}
            QPushButton:pressed {{
                padding-top: 1px;
            }}
        """)
        edit_btn.setCursor(Qt.PointingHandCursor)
        edit_btn.clicked.connect(lambda: self.on_edit(self.client))
        action_col.addWidget(edit_btn)

        delete_btn = QPushButton("Delete")
        delete_btn.setFixedSize(60, 28)
        delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #252525;
                border: none;
                border-radius: 6px;
                color: #AAAAAA;
                font-size: 11px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #EF4444;
                color: #FFFFFF;
            }
            QPushButton:pressed {
                padding-top: 1px;
            }
        """)
        delete_btn.setCursor(Qt.PointingHandCursor)
        delete_btn.clicked.connect(lambda: self.on_delete(self.client))
        action_col.addWidget(delete_btn)

        action_col.addStretch()
        layout.addLayout(action_col)


class ClientPage(QWidget):
    """Modern client management page."""

    def __init__(self):
        super().__init__()
        self._color_index = 0
        self._setup_ui()
        self._load_clients()

    def _get_next_color(self) -> str:
        color = CARD_COLORS[self._color_index % len(CARD_COLORS)]
        self._color_index += 1
        return color

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Main content area
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(32, 32, 32, 32)
        content_layout.setSpacing(24)

        # Header
        header = QHBoxLayout()

        title_col = QVBoxLayout()
        title_col.setSpacing(4)

        title = QLabel("Clients")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #FFFFFF;")
        title_col.addWidget(title)

        subtitle = QLabel("Manage your client database")
        subtitle.setStyleSheet("font-size: 13px; color: #666666;")
        title_col.addWidget(subtitle)

        header.addLayout(title_col)
        header.addStretch()

        # Client count badge
        self.count_label = QLabel("0")
        self.count_label.setFixedSize(44, 44)
        self.count_label.setAlignment(Qt.AlignCenter)
        self.count_label.setStyleSheet("""
            background-color: #252525;
            border-radius: 22px;
            font-size: 16px;
            font-weight: bold;
            color: #FFFFFF;
        """)
        header.addWidget(self.count_label)

        header.addSpacing(12)

        # Add button
        add_btn = QPushButton("+ Add Client")
        add_btn.setFixedHeight(44)
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #5865F2;
                border: none;
                border-radius: 10px;
                color: #FFFFFF;
                font-weight: bold;
                padding: 0 24px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #4752C4;
            }
            QPushButton:pressed {
                background-color: #3C45A5;
                padding-top: 2px;
            }
        """)
        add_btn.setCursor(Qt.PointingHandCursor)
        add_btn.clicked.connect(self._add_client)
        header.addWidget(add_btn)

        content_layout.addLayout(header)

        # Search bar
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search clients...")
        self.search_input.setMinimumHeight(48)
        self.search_input.setStyleSheet("""
            QLineEdit {
                background-color: #1A1A1A;
                border: 1px solid #252525;
                border-radius: 12px;
                padding: 0 20px;
                font-size: 14px;
                color: #FFFFFF;
            }
            QLineEdit:focus {
                border-color: #5865F2;
            }
            QLineEdit::placeholder {
                color: #555555;
            }
        """)
        self.search_input.textChanged.connect(self._on_search)
        content_layout.addWidget(self.search_input)

        # Clients list in scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")

        self.list_container = QWidget()
        self.list_container.setStyleSheet("background: transparent;")
        self.list_layout = QVBoxLayout(self.list_container)
        self.list_layout.setSpacing(8)
        self.list_layout.setContentsMargins(0, 0, 0, 0)
        self.list_layout.setAlignment(Qt.AlignTop)

        scroll.setWidget(self.list_container)
        content_layout.addWidget(scroll, 1)

        layout.addWidget(content)

    def _load_clients(self, search_text=""):
        # Clear existing
        while self.list_layout.count():
            item = self.list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        self._color_index = 0

        try:
            all_clients = AppState.client_service.all()

            # Filter
            if search_text:
                search_lower = search_text.lower()
                clients = [c for c in all_clients if search_lower in c.name.lower() or (c.phone and search_lower in c.phone)]
            else:
                clients = all_clients

            self.count_label.setText(str(len(clients)))

            if not clients:
                empty = QLabel("No clients found" if search_text else "No clients yet")
                empty.setAlignment(Qt.AlignCenter)
                empty.setStyleSheet("color: #555555; font-size: 15px; padding: 60px;")
                self.list_layout.addWidget(empty)
            else:
                for client in clients:
                    color = self._get_next_color()
                    card = ClientCard(client, color, self._edit_client, self._delete_client)
                    self.list_layout.addWidget(card)

        except Exception as e:
            logger.error(f"Error loading clients: {e}")
            error = QLabel("Error loading clients")
            error.setStyleSheet("color: #EF4444; padding: 40px;")
            self.list_layout.addWidget(error)

    def _on_search(self, text):
        self._load_clients(text)

    def _add_client(self):
        dialog = ClientDialog(self)
        if dialog.exec() == QDialog.Accepted:
            data = dialog.get_data()
            if not data["name"]:
                QMessageBox.warning(self, "Error", "Please enter a client name")
                return
            try:
                AppState.client_service.create(data["name"], data["phone"], data["notes"])
                self._load_clients(self.search_input.text())
            except Exception as e:
                logger.error(f"Error adding client: {e}")
                QMessageBox.critical(self, "Error", "Failed to add client")

    def _edit_client(self, client):
        dialog = ClientDialog(self, client)
        if dialog.exec() == QDialog.Accepted:
            data = dialog.get_data()
            if not data["name"]:
                QMessageBox.warning(self, "Error", "Please enter a client name")
                return
            try:
                AppState.client_service.update(client.id, data["name"], data["phone"], data["notes"])
                self._load_clients(self.search_input.text())
            except Exception as e:
                logger.error(f"Error updating client: {e}")
                QMessageBox.critical(self, "Error", "Failed to update client")

    def _delete_client(self, client):
        reply = QMessageBox.question(
            self, "Delete Client",
            f"Delete '{client.name}'?\n\nThis cannot be undone.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            try:
                AppState.client_service.delete(client.id)
                self._load_clients(self.search_input.text())
            except Exception as e:
                logger.error(f"Error deleting client: {e}")
                QMessageBox.critical(self, "Error", "Failed to delete client")
