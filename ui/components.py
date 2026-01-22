"""
CHAIRMAN - Reusable UI Components

This module provides reusable, professional UI components used throughout the application.
"""
from __future__ import annotations

from PySide6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QComboBox, QTextEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QMessageBox, QFrame, QTimeEdit, QDateEdit
)
from PySide6.QtCore import Qt, Signal, QTime, QDate
from PySide6.QtGui import QFont

from config import UIConfig


class ModernCard(QFrame):
    """A modern card container with subtle shadow effect."""

    def __init__(self, title: str = "", parent: QWidget | None = None):
        super().__init__(parent)
        self.setObjectName("modern_card")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        if title:
            title_label = QLabel(title)
            title_label.setObjectName("card_title")
            title_font = QFont()
            title_font.setPointSize(15)
            title_font.setBold(True)
            title_label.setFont(title_font)
            layout.addWidget(title_label)

        self.content_layout = layout

    def add_widget(self, widget: QWidget) -> None:
        """Add a widget to the card."""
        self.content_layout.addWidget(widget)

    def add_layout(self, layout) -> None:
        """Add a layout to the card."""
        self.content_layout.addLayout(layout)


class FormField(QWidget):
    """A labeled form field with consistent styling."""

    def __init__(
        self,
        label: str,
        widget: QWidget,
        required: bool = False,
        helper_text: str = "",
        parent: QWidget | None = None
    ):
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        # Label
        label_widget = QLabel(label + (" *" if required else ""))
        label_widget.setObjectName("form_label")
        label_font = QFont()
        label_font.setPointSize(10)
        label_font.setBold(True)
        label_widget.setFont(label_font)
        layout.addWidget(label_widget)

        # Input widget
        widget.setObjectName("form_input")
        widget.setMinimumHeight(36)
        layout.addWidget(widget)

        # Helper text
        if helper_text:
            helper = QLabel(helper_text)
            helper.setObjectName("helper_text")
            layout.addWidget(helper)

        self.input_widget = widget


class ModernButton(QPushButton):
    """A modern styled button."""

    def __init__(
        self,
        text: str,
        button_type: str = "primary",
        parent: QWidget | None = None
    ):
        super().__init__(text, parent)
        self.setObjectName(f"btn_{button_type}")
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumHeight(36)

        font = QFont()
        font.setPointSize(13)
        font.setBold(True if button_type == "primary" else False)
        font.setWeight(QFont.Bold if button_type == "primary" else QFont.DemiBold)
        self.setFont(font)


class ErrorDialog:
    """Show error messages to the user."""

    @staticmethod
    def show(title: str, message: str, parent: QWidget | None = None) -> None:
        """Show an error dialog."""
        msg_box = QMessageBox(parent)
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec()


class SuccessDialog:
    """Show success messages to the user."""

    @staticmethod
    def show(title: str, message: str, parent: QWidget | None = None) -> None:
        """Show a success dialog."""
        msg_box = QMessageBox(parent)
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec()


class ConfirmDialog:
    """Show confirmation dialogs."""

    @staticmethod
    def ask(title: str, message: str, parent: QWidget | None = None) -> bool:
        """
        Ask for user confirmation.

        Returns:
            True if user clicked Yes, False otherwise
        """
        msg_box = QMessageBox(parent)
        msg_box.setIcon(QMessageBox.Question)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setDefaultButton(QMessageBox.No)
        return msg_box.exec() == QMessageBox.Yes


class SearchBar(QWidget):
    """A modern search bar with icon."""

    search_changed = Signal(str)

    def __init__(self, placeholder: str = "Search...", parent: QWidget | None = None):
        super().__init__(parent)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(placeholder)
        self.search_input.setObjectName("search_bar")
        self.search_input.setMinimumHeight(40)
        self.search_input.textChanged.connect(self.search_changed.emit)

        layout.addWidget(self.search_input)

    def text(self) -> str:
        """Get the current search text."""
        return self.search_input.text()

    def clear(self) -> None:
        """Clear the search text."""
        self.search_input.clear()


class AppointmentCard(QFrame):
    """A card displaying appointment information."""

    delete_clicked = Signal(int)
    toggle_paid_clicked = Signal(int)

    def __init__(
        self,
        appointment_data: dict,
        parent: QWidget | None = None
    ):
        super().__init__(parent)
        self.setObjectName("appointment_card")
        self.appointment_id = appointment_data["appointment_id"]

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(8)

        # Time and status row
        top_row = QHBoxLayout()

        # Time
        from datetime import datetime
        start = datetime.fromisoformat(appointment_data["start_time"])
        end = datetime.fromisoformat(appointment_data["end_time"])
        time_label = QLabel(f"{start.strftime('%I:%M %p')} - {end.strftime('%I:%M %p')}")
        time_label.setObjectName("appointment_time")
        top_row.addWidget(time_label)

        top_row.addStretch()

        # Paid status
        if appointment_data["paid"]:
            paid_label = QLabel("Paid")
            paid_label.setObjectName("paid_badge")
            paid_label.setStyleSheet("color: #10b981; font-weight: bold;")
        else:
            paid_label = QLabel("Unpaid")
            paid_label.setObjectName("unpaid_badge")
            paid_label.setStyleSheet("color: #ef4444; font-weight: bold;")
        top_row.addWidget(paid_label)

        layout.addLayout(top_row)

        # Client and service
        client_label = QLabel(appointment_data['client'])
        client_label.setObjectName("appointment_client")
        layout.addWidget(client_label)

        service_label = QLabel(f"{appointment_data['service']} - ${appointment_data['service_price']:.2f}")
        service_label.setObjectName("appointment_service")
        layout.addWidget(service_label)

        # Notes (if any)
        if appointment_data.get("notes"):
            notes_label = QLabel(appointment_data['notes'])
            notes_label.setObjectName("appointment_notes")
            notes_label.setWordWrap(True)
            notes_label.setStyleSheet("color: rgba(255, 255, 255, 0.7); font-size: 11px;")
            layout.addWidget(notes_label)

        # Action buttons
        button_row = QHBoxLayout()
        button_row.setSpacing(8)

        toggle_btn = ModernButton(
            "Mark Paid" if not appointment_data["paid"] else "Mark Unpaid",
            "secondary"
        )
        toggle_btn.clicked.connect(lambda: self.toggle_paid_clicked.emit(self.appointment_id))
        button_row.addWidget(toggle_btn)

        delete_btn = ModernButton("Delete", "danger")
        delete_btn.clicked.connect(lambda: self.delete_clicked.emit(self.appointment_id))
        button_row.addWidget(delete_btn)

        layout.addLayout(button_row)


class ClientCard(QFrame):
    """A card displaying client information."""

    clicked = Signal(int)

    def __init__(self, client_data: dict, parent: QWidget | None = None):
        super().__init__(parent)
        self.setObjectName("client_card")
        self.client_id = client_data["id"]
        self.setCursor(Qt.PointingHandCursor)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 12, 15, 12)
        layout.setSpacing(6)

        # Name
        name_label = QLabel(client_data["name"])
        name_label.setObjectName("client_name")
        name_font = QFont()
        name_font.setPointSize(12)
        name_font.setBold(True)
        name_label.setFont(name_font)
        layout.addWidget(name_label)

        # Phone
        if client_data.get("phone"):
            phone_label = QLabel(client_data['phone'])
            phone_label.setObjectName("client_phone")
            layout.addWidget(phone_label)

        # No-show count (if any)
        if client_data.get("no_show_count", 0) > 0:
            no_show_label = QLabel(f"{client_data['no_show_count']} no-show(s)")
            no_show_label.setStyleSheet("color: #f59e0b; font-size: 11px;")
            layout.addWidget(no_show_label)

    def mousePressEvent(self, event):
        """Emit clicked signal when card is clicked."""
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.client_id)
        super().mousePressEvent(event)


class ServiceCard(QFrame):
    """A card displaying service information."""

    def __init__(self, service_data: dict, parent: QWidget | None = None):
        super().__init__(parent)
        self.setObjectName("service_card")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 12, 15, 12)
        layout.setSpacing(6)

        # Name
        name_label = QLabel(service_data["name"])
        name_label.setObjectName("service_name")
        name_font = QFont()
        name_font.setPointSize(12)
        name_font.setBold(True)
        name_label.setFont(name_font)
        layout.addWidget(name_label)

        # Price and duration row
        info_row = QHBoxLayout()

        price_label = QLabel(f"${service_data['price']:.2f}")
        price_label.setObjectName("service_price")
        info_row.addWidget(price_label)

        duration_label = QLabel(f"{service_data['duration_minutes']} min")
        duration_label.setObjectName("service_duration")
        info_row.addWidget(duration_label)

        info_row.addStretch()

        layout.addLayout(info_row)

        # Buffer time (if any)
        if service_data.get("buffer_minutes", 0) > 0:
            buffer_label = QLabel(f"Buffer: {service_data['buffer_minutes']} min")
            buffer_label.setStyleSheet("color: rgba(255, 255, 255, 0.6); font-size: 11px;")
            layout.addWidget(buffer_label)


class EmptyState(QWidget):
    """Display an empty state message."""

    def __init__(
        self,
        icon: str,
        title: str,
        message: str,
        parent: QWidget | None = None
    ):
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(12)

        # Icon
        icon_label = QLabel(icon)
        icon_label.setAlignment(Qt.AlignCenter)
        icon_font = QFont()
        icon_font.setPointSize(48)
        icon_label.setFont(icon_font)
        layout.addWidget(icon_label)

        # Title
        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)

        # Message
        message_label = QLabel(message)
        message_label.setAlignment(Qt.AlignCenter)
        message_label.setWordWrap(True)
        message_label.setStyleSheet("color: rgba(255, 255, 255, 0.7);")
        layout.addWidget(message_label)
