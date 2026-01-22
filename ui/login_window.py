"""
CHAIRMAN - Login Window
Modern authentication screen
"""
from __future__ import annotations

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFrame
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont


class LoginWindow(QWidget):
    """
    Modern login window.

    Emits:
        login_successful: Signal emitted when login is successful
    """

    login_successful = Signal()

    def __init__(self):
        """Initialize the login window."""
        super().__init__()

        # Remove title bar and make frameless
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.setFixedSize(420, 520)

        # Center the window
        self._center_on_screen()

        self._setup_ui()

    def _center_on_screen(self):
        """Center the window on the screen."""
        from PySide6.QtGui import QGuiApplication
        screen = QGuiApplication.primaryScreen().geometry()
        x = (screen.width() - 420) // 2
        y = (screen.height() - 520) // 2
        self.move(x, y)

    def _setup_ui(self):
        """Setup the login UI."""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Container with rounded corners
        container = QFrame()
        container.setObjectName("login_container")
        container.setStyleSheet("""
            QFrame#login_container {
                background-color: #1A1A1A;
                border-radius: 16px;
                border: 1px solid #2A2A2A;
            }
        """)

        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(32, 24, 32, 32)
        container_layout.setSpacing(0)

        # Close button at top right
        close_row = QHBoxLayout()
        close_row.addStretch()
        close_btn = QPushButton("×")
        close_btn.setFixedSize(32, 32)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                color: #666666;
                font-size: 20px;
                font-weight: bold;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #EF4444;
                color: #FFFFFF;
            }
            QPushButton:pressed {
                background-color: #DC2626;
            }
        """)
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.clicked.connect(self.close)
        close_row.addWidget(close_btn)
        container_layout.addLayout(close_row)

        # Login card
        login_card = QFrame()
        login_card.setStyleSheet("background: transparent; border: none;")

        card_layout = QVBoxLayout(login_card)
        card_layout.setSpacing(20)
        card_layout.setContentsMargins(32, 32, 32, 32)

        # Logo/Title
        title_label = QLabel("Chairman")
        title_label.setAlignment(Qt.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(28)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #5865F2; background: transparent;")
        card_layout.addWidget(title_label)

        # Subtitle
        subtitle_label = QLabel("Barber Shop Management")
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setStyleSheet("color: #B0B0B0; font-size: 13px; background: transparent;")
        card_layout.addWidget(subtitle_label)

        card_layout.addSpacing(20)

        # Form styling
        label_style = "font-size: 11px; font-weight: 600; color: #666666; background: transparent;"
        input_style = """
            QLineEdit {
                background-color: #252525;
                border: 1px solid #333333;
                border-radius: 8px;
                padding: 12px 16px;
                color: #FFFFFF;
                font-size: 14px;
            }
            QLineEdit:hover {
                border-color: #444444;
            }
            QLineEdit:focus {
                border-color: #5865F2;
            }
            QLineEdit::placeholder {
                color: #555555;
            }
        """

        # Username field
        username_label = QLabel("USERNAME")
        username_label.setStyleSheet(label_style)
        card_layout.addWidget(username_label)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter your username")
        self.username_input.setMinimumHeight(48)
        self.username_input.setStyleSheet(input_style)
        card_layout.addWidget(self.username_input)

        card_layout.addSpacing(16)

        # Password field
        password_label = QLabel("PASSWORD")
        password_label.setStyleSheet(label_style)
        card_layout.addWidget(password_label)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter your password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setMinimumHeight(48)
        self.password_input.setStyleSheet(input_style)
        self.password_input.returnPressed.connect(self._handle_login)
        card_layout.addWidget(self.password_input)

        card_layout.addSpacing(24)

        # Login button with press animation
        login_btn = QPushButton("Login")
        login_btn.setMinimumHeight(50)
        login_btn.setStyleSheet("""
            QPushButton {
                background-color: #5865F2;
                border: none;
                border-radius: 8px;
                color: #FFFFFF;
                font-size: 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #4752C4;
            }
            QPushButton:pressed {
                background-color: #3C45A5;
                padding-top: 2px;
            }
        """)
        login_btn.setCursor(Qt.PointingHandCursor)
        login_btn.clicked.connect(self._handle_login)
        card_layout.addWidget(login_btn)

        # Error message label (hidden by default)
        self.error_label = QLabel()
        self.error_label.setAlignment(Qt.AlignCenter)
        self.error_label.setStyleSheet("color: #ED4245; font-size: 12px; padding: 8px; background: transparent;")
        self.error_label.setWordWrap(True)
        self.error_label.hide()
        card_layout.addWidget(self.error_label)

        container_layout.addWidget(login_card)
        container_layout.addStretch()

        # Version label at bottom
        from config import VERSION
        version_label = QLabel(f"v{VERSION}")
        version_label.setAlignment(Qt.AlignCenter)
        version_label.setStyleSheet("color: #555555; font-size: 11px; background: transparent;")
        container_layout.addWidget(version_label)

        main_layout.addWidget(container)

    def _handle_login(self):
        """Handle login attempt."""
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        # Simple validation
        if not username or not password:
            self.show_error("Please enter both username and password")
            return

        # Accept any non-empty credentials
        if len(username) >= 3 and len(password) >= 4:
            self.login_successful.emit()
            self.close()
        else:
            self.show_error("Username must be at least 3 characters and password at least 4 characters")

    def show_error(self, message: str):
        """Show an error message."""
        self.error_label.setText(message)
        self.error_label.show()

    def keyPressEvent(self, event):
        """Handle key press events."""
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            self._handle_login()
        elif event.key() == Qt.Key_Escape:
            self.close()
        else:
            super().keyPressEvent(event)

    def mousePressEvent(self, event):
        """Handle mouse press for window dragging."""
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        """Handle mouse move for window dragging."""
        if event.buttons() == Qt.LeftButton and hasattr(self, 'drag_position'):
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()
