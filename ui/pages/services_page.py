"""
CHAIRMAN - Services Management Page
Clean design with color-coded cards
"""
from __future__ import annotations

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel, QLineEdit,
    QScrollArea, QPushButton, QDialog, QMessageBox, QGridLayout,
    QSpinBox, QDoubleSpinBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPainter

from core.app_state import AppState
from core.logging_config import get_logger

logger = get_logger(__name__)

# Color palette for service cards
SERVICE_COLORS = ["#22C55E", "#5865F2", "#F59E0B", "#EC4899", "#8B5CF6", "#06B6D4", "#EF4444", "#10B981"]


class ServiceDialog(QDialog):
    """Dialog for adding/editing services with overlay background."""

    def __init__(self, parent=None, service_data=None):
        super().__init__(parent)
        self.service_data = service_data
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setModal(True)
        self._setup_ui()

    def showEvent(self, event):
        """Position dialog to cover entire parent window."""
        super().showEvent(event)
        if self.parent():
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
        self.container.setFixedSize(420, 520)
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
        title = QLabel("Edit Service" if self.service_data else "New Service")
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

        # Form styles
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
        """
        spin_style = """
            QSpinBox, QDoubleSpinBox {
                background-color: #252525;
                border: none;
                border-radius: 8px;
                padding: 14px 16px;
                color: #FFFFFF;
                font-size: 14px;
            }
            QSpinBox:focus, QDoubleSpinBox:focus {
                background-color: #2A2A2A;
            }
            QSpinBox::up-button, QDoubleSpinBox::up-button {
                subcontrol-origin: border;
                subcontrol-position: top right;
                width: 32px;
                border: none;
                background-color: #333333;
                border-top-right-radius: 8px;
            }
            QSpinBox::up-button:hover, QDoubleSpinBox::up-button:hover {
                background-color: #22C55E;
            }
            QSpinBox::down-button, QDoubleSpinBox::down-button {
                subcontrol-origin: border;
                subcontrol-position: bottom right;
                width: 32px;
                border: none;
                background-color: #333333;
                border-bottom-right-radius: 8px;
            }
            QSpinBox::down-button:hover, QDoubleSpinBox::down-button:hover {
                background-color: #22C55E;
            }
            QSpinBox::up-arrow, QDoubleSpinBox::up-arrow {
                width: 0;
                height: 0;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-bottom: 6px solid #888888;
            }
            QSpinBox::down-arrow, QDoubleSpinBox::down-arrow {
                width: 0;
                height: 0;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 6px solid #888888;
            }
        """

        # Name
        name_label = QLabel("SERVICE NAME")
        name_label.setStyleSheet(label_style)
        layout.addWidget(name_label)
        layout.addSpacing(8)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Haircut, Beard Trim, etc.")
        self.name_input.setMinimumHeight(48)
        self.name_input.setStyleSheet(input_style)
        if self.service_data:
            self.name_input.setText(self.service_data.name)
        layout.addWidget(self.name_input)

        layout.addSpacing(20)

        # Price
        price_label = QLabel("PRICE")
        price_label.setStyleSheet(label_style)
        layout.addWidget(price_label)
        layout.addSpacing(8)

        self.price_input = QDoubleSpinBox()
        self.price_input.setRange(0.0, 9999.99)
        self.price_input.setDecimals(2)
        self.price_input.setPrefix("$ ")
        self.price_input.setValue(self.service_data.price if self.service_data else 30.00)
        self.price_input.setMinimumHeight(48)
        self.price_input.setStyleSheet(spin_style)
        layout.addWidget(self.price_input)

        layout.addSpacing(20)

        # Duration
        duration_label = QLabel("DURATION")
        duration_label.setStyleSheet(label_style)
        layout.addWidget(duration_label)
        layout.addSpacing(8)

        self.duration_input = QSpinBox()
        self.duration_input.setRange(5, 480)
        self.duration_input.setSingleStep(5)
        self.duration_input.setSuffix(" minutes")
        self.duration_input.setValue(self.service_data.duration_minutes if self.service_data else 30)
        self.duration_input.setMinimumHeight(48)
        self.duration_input.setStyleSheet(spin_style)
        layout.addWidget(self.duration_input)

        layout.addSpacing(20)

        # Buffer
        buffer_label = QLabel("BUFFER TIME")
        buffer_label.setStyleSheet(label_style)
        layout.addWidget(buffer_label)
        layout.addSpacing(8)

        self.buffer_input = QSpinBox()
        self.buffer_input.setRange(0, 60)
        self.buffer_input.setSingleStep(5)
        self.buffer_input.setSuffix(" minutes")
        self.buffer_input.setValue(self.service_data.buffer_minutes if self.service_data else 10)
        self.buffer_input.setMinimumHeight(48)
        self.buffer_input.setStyleSheet(spin_style)
        layout.addWidget(self.buffer_input)

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

        save_btn = QPushButton("Save Service" if self.service_data else "Add Service")
        save_btn.setMinimumHeight(48)
        save_btn.setCursor(Qt.PointingHandCursor)
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #22C55E;
                border: none;
                border-radius: 8px;
                color: #FFFFFF;
                font-weight: 600;
                font-size: 14px;
                padding: 0 32px;
            }
            QPushButton:hover {
                background-color: #16A34A;
            }
        """)
        save_btn.clicked.connect(self.accept)
        btn_row.addWidget(save_btn)

        layout.addLayout(btn_row)
        outer.addWidget(self.container)

    def get_data(self):
        return {
            "name": self.name_input.text().strip(),
            "price": self.price_input.value(),
            "duration": self.duration_input.value(),
            "buffer": self.buffer_input.value()
        }


class ServiceCard(QFrame):
    """Service card with color accent and price highlight."""

    def __init__(self, service, color: str, on_edit, on_delete, parent=None):
        super().__init__(parent)
        self.service = service
        self.color = color
        self.on_edit = on_edit
        self.on_delete = on_delete
        self._setup_ui()

    def _setup_ui(self):
        self.setObjectName("service_card")
        self.setStyleSheet(f"""
            QFrame#service_card {{
                background-color: #1A1A1A;
                border: none;
                border-left: 3px solid {self.color};
                border-radius: 0px;
            }}
            QFrame#service_card:hover {{
                background-color: #1E1E1E;
            }}
            QFrame#service_card QLabel {{
                border: none;
            }}
        """)
        self.setMinimumHeight(100)
        self.setMaximumHeight(120)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(16)

        # Left: Info
        info_col = QVBoxLayout()
        info_col.setSpacing(6)

        name = QLabel(self.service.name)
        name.setStyleSheet("font-size: 15px; font-weight: 600; color: #FFFFFF; background: transparent;")
        info_col.addWidget(name)

        # Duration and buffer
        details = QLabel(f"{self.service.duration_minutes} min")
        if self.service.buffer_minutes > 0:
            details.setText(f"{self.service.duration_minutes} min  ·  +{self.service.buffer_minutes} buffer")
        details.setStyleSheet("font-size: 12px; color: #666666; background: transparent;")
        info_col.addWidget(details)

        layout.addLayout(info_col, 1)

        # Middle: Price
        price = QLabel(f"${self.service.price:.2f}")
        price.setStyleSheet(f"font-size: 22px; font-weight: bold; color: {self.color}; background: transparent;")
        layout.addWidget(price)

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
        edit_btn.clicked.connect(lambda: self.on_edit(self.service))
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
        delete_btn.clicked.connect(lambda: self.on_delete(self.service))
        action_col.addWidget(delete_btn)

        layout.addLayout(action_col)


class ServicesPage(QWidget):
    """Services management page with color-coded cards."""

    def __init__(self):
        super().__init__()
        self._color_index = 0
        self._setup_ui()
        self._load_services()

    def _get_next_color(self) -> str:
        color = SERVICE_COLORS[self._color_index % len(SERVICE_COLORS)]
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

        title = QLabel("Services")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #FFFFFF;")
        title_col.addWidget(title)

        subtitle = QLabel("Manage your service menu and pricing")
        subtitle.setStyleSheet("font-size: 13px; color: #666666;")
        title_col.addWidget(subtitle)

        header.addLayout(title_col)
        header.addStretch()

        # Service count badge
        self.count_label = QLabel("0")
        self.count_label.setFixedSize(44, 44)
        self.count_label.setAlignment(Qt.AlignCenter)
        self.count_label.setStyleSheet("""
            background-color: #22C55E;
            border-radius: 22px;
            font-size: 16px;
            font-weight: bold;
            color: #FFFFFF;
        """)
        header.addWidget(self.count_label)

        header.addSpacing(12)

        # Add button
        add_btn = QPushButton("+ Add Service")
        add_btn.setFixedHeight(44)
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #22C55E;
                border: none;
                border-radius: 10px;
                color: #FFFFFF;
                font-weight: bold;
                padding: 0 24px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #16A34A;
            }
            QPushButton:pressed {
                background-color: #15803D;
                padding-top: 2px;
            }
        """)
        add_btn.setCursor(Qt.PointingHandCursor)
        add_btn.clicked.connect(self._add_service)
        header.addWidget(add_btn)

        content_layout.addLayout(header)

        # Search bar
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search services...")
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
                border-color: #22C55E;
            }
            QLineEdit::placeholder {
                color: #555555;
            }
        """)
        self.search_input.textChanged.connect(self._on_search)
        content_layout.addWidget(self.search_input)

        # Services list in scroll area
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

    def _load_services(self, search_text=""):
        # Clear existing
        while self.list_layout.count():
            item = self.list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        self._color_index = 0

        try:
            all_services = AppState.service_manager.all()

            # Filter
            if search_text:
                search_lower = search_text.lower()
                services = [s for s in all_services if search_lower in s.name.lower()]
            else:
                services = all_services

            self.count_label.setText(str(len(services)))

            if not services:
                empty = QLabel("No services found" if search_text else "No services yet")
                empty.setAlignment(Qt.AlignCenter)
                empty.setStyleSheet("color: #555555; font-size: 15px; padding: 60px;")
                self.list_layout.addWidget(empty)
            else:
                for service in services:
                    color = self._get_next_color()
                    card = ServiceCard(service, color, self._edit_service, self._delete_service)
                    self.list_layout.addWidget(card)

        except Exception as e:
            logger.error(f"Error loading services: {e}")
            error = QLabel("Error loading services")
            error.setStyleSheet("color: #EF4444; padding: 40px;")
            self.list_layout.addWidget(error)

    def _on_search(self, text):
        self._load_services(text)

    def _add_service(self):
        dialog = ServiceDialog(self)
        if dialog.exec() == QDialog.Accepted:
            data = dialog.get_data()
            if not data["name"]:
                QMessageBox.warning(self, "Error", "Please enter a service name")
                return
            try:
                AppState.service_manager.create(data["name"], data["price"], data["duration"], data["buffer"])
                self._load_services(self.search_input.text())
            except Exception as e:
                logger.error(f"Error adding service: {e}")
                QMessageBox.critical(self, "Error", str(e))

    def _edit_service(self, service):
        dialog = ServiceDialog(self, service)
        if dialog.exec() == QDialog.Accepted:
            data = dialog.get_data()
            if not data["name"]:
                QMessageBox.warning(self, "Error", "Please enter a service name")
                return
            try:
                AppState.service_manager.update(
                    service.id,
                    name=data["name"],
                    price=data["price"],
                    duration_minutes=data["duration"],
                    buffer_minutes=data["buffer"]
                )
                self._load_services(self.search_input.text())
            except Exception as e:
                logger.error(f"Error updating service: {e}")
                QMessageBox.critical(self, "Error", str(e))

    def _delete_service(self, service):
        reply = QMessageBox.question(
            self, "Delete Service",
            f"Delete '{service.name}'?\n\nThis cannot be undone.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            try:
                AppState.service_manager.delete(service.id)
                self._load_services(self.search_input.text())
            except Exception as e:
                logger.error(f"Error deleting service: {e}")
                QMessageBox.critical(self, "Error", str(e))
