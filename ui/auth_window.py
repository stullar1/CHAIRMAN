"""
CHAIRMAN - Authentication Window
Frameless with rounded corners, email-based login
"""
from __future__ import annotations

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QStackedWidget, QCheckBox, QFileDialog
)
from PySide6.QtCore import Qt, Signal, QTimer, QRectF
from PySide6.QtGui import (
    QPainter, QBrush, QColor, QPainterPath, QPixmap,
    QRegion, QPen
)

from core.auth import AuthService
from core.email_service import EmailService
from core.logging_config import get_logger

logger = get_logger(__name__)

RADIUS = 12


class AuthWindow(QWidget):
    """Frameless authentication window with rounded corners."""

    login_successful = Signal(dict)

    def __init__(self):
        super().__init__()

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(400, 480)

        self.auth_service = AuthService()
        self.email_service = EmailService.from_config()
        self._drag_pos = None
        self._pending_email = None
        self._selected_logo_path = None

        self._setup_ui()
        self._center_on_screen()
        self._update_mask()
        self._check_remembered_device()

    def _update_mask(self):
        """Update the window mask for proper rounded corners on Windows."""
        path = QPainterPath()
        path.addRoundedRect(QRectF(self.rect()), RADIUS, RADIUS)
        region = QRegion(path.toFillPolygon().toPolygon())
        self.setMask(region)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._update_mask()

    def _center_on_screen(self):
        from PySide6.QtGui import QGuiApplication
        screen = QGuiApplication.primaryScreen().geometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)

    def _check_remembered_device(self):
        """Check if device is remembered and auto-login."""
        user_data = self.auth_service.check_device_token()
        if user_data:
            logger.info(f"Auto-login from remembered device: {user_data['business_name']}")
            self.login_successful.emit(user_data)
            self.close()

    def _setup_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        self.container = QWidget()
        self.container.setObjectName("auth_container")

        container_layout = QVBoxLayout(self.container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)

        title_bar = self._create_title_bar()
        container_layout.addWidget(title_bar)

        content = QWidget()
        content.setObjectName("auth_content")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(32, 16, 32, 24)
        content_layout.setSpacing(0)

        logo = QLabel("CHAIRMAN")
        logo.setAlignment(Qt.AlignCenter)
        logo.setStyleSheet("""
            color: #5865F2;
            font-size: 22px;
            font-weight: bold;
            letter-spacing: 3px;
            margin-bottom: 16px;
        """)
        content_layout.addWidget(logo)

        self.pages = QStackedWidget()
        self.pages.addWidget(self._create_login_page())
        self.pages.addWidget(self._create_setup_page())
        self.pages.addWidget(self._create_verify_page())
        content_layout.addWidget(self.pages)

        container_layout.addWidget(content, 1)
        outer.addWidget(self.container)

    def _create_title_bar(self) -> QWidget:
        bar = QWidget()
        bar.setFixedHeight(32)
        bar.setStyleSheet("background-color: #1A1A1A;")

        layout = QHBoxLayout(bar)
        layout.setContentsMargins(12, 0, 8, 0)
        layout.setSpacing(0)
        layout.addStretch()

        close_btn = QPushButton("×")
        close_btn.setFixedSize(24, 24)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                color: #666666;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #EF4444;
                color: #FFFFFF;
                border-radius: 4px;
            }
        """)
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)

        return bar

    def _create_login_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(12)
        layout.setContentsMargins(0, 0, 0, 0)

        title = QLabel("Welcome Back")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #FFFFFF;")
        layout.addWidget(title)

        layout.addSpacing(16)

        # Email
        self.login_email = QLineEdit()
        self.login_email.setPlaceholderText("Email")
        self.login_email.setMinimumHeight(42)
        layout.addWidget(self.login_email)

        # Password
        self.login_password = QLineEdit()
        self.login_password.setPlaceholderText("Password")
        self.login_password.setEchoMode(QLineEdit.Password)
        self.login_password.setMinimumHeight(42)
        self.login_password.returnPressed.connect(self._do_login)
        layout.addWidget(self.login_password)

        # Remember device - custom animated checkbox
        self.remember_device = QCheckBox("Remember this device")
        self.remember_device.setCursor(Qt.PointingHandCursor)
        self.remember_device.setStyleSheet("""
            QCheckBox {
                color: #888888;
                font-size: 12px;
                spacing: 10px;
            }
            QCheckBox:hover {
                color: #AAAAAA;
            }
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
                border: 2px solid #404040;
                border-radius: 6px;
                background-color: #1A1A1A;
            }
            QCheckBox::indicator:hover {
                border-color: #5865F2;
                background-color: #252525;
            }
            QCheckBox::indicator:checked {
                background-color: #5865F2;
                border-color: #5865F2;
                image: url(assets/icons/checkmark.svg);
            }
            QCheckBox::indicator:checked:hover {
                background-color: #4752C4;
                border-color: #4752C4;
            }
        """)
        layout.addWidget(self.remember_device)

        # Error
        self.login_error = QLabel()
        self.login_error.setAlignment(Qt.AlignCenter)
        self.login_error.setWordWrap(True)
        self.login_error.setStyleSheet("color: #EF4444; font-size: 12px;")
        self.login_error.hide()
        layout.addWidget(self.login_error)

        # Sign In Button
        sign_in_btn = QPushButton("Sign In")
        sign_in_btn.setMinimumHeight(44)
        sign_in_btn.setCursor(Qt.PointingHandCursor)
        sign_in_btn.setStyleSheet("""
            QPushButton {
                background-color: #5865F2;
                color: #FFFFFF;
                border: none;
                border-radius: 8px;
                font-weight: 600;
                font-size: 14px;
            }
            QPushButton:hover { background-color: #4752C4; }
        """)
        sign_in_btn.clicked.connect(self._do_login)
        layout.addWidget(sign_in_btn)

        layout.addStretch()

        # Setup business link
        switch_row = QHBoxLayout()
        switch_row.setAlignment(Qt.AlignCenter)

        switch_text = QLabel("New here?")
        switch_text.setStyleSheet("color: #666666; font-size: 12px;")
        switch_row.addWidget(switch_text)

        switch_btn = QPushButton("Set Up Your Business")
        switch_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #5865F2;
                border: none;
                font-weight: 600;
                font-size: 12px;
            }
            QPushButton:hover { color: #4752C4; }
        """)
        switch_btn.setCursor(Qt.PointingHandCursor)
        switch_btn.clicked.connect(lambda: self._go_to_page(1))
        switch_row.addWidget(switch_btn)

        layout.addLayout(switch_row)

        return page

    def _create_setup_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(10)
        layout.setContentsMargins(0, 0, 0, 0)

        title = QLabel("Set Up Your Business")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #FFFFFF;")
        layout.addWidget(title)

        layout.addSpacing(16)

        # Logo upload - cleaner inline design
        logo_container = QWidget()
        logo_container.setStyleSheet("""
            QWidget {
                background-color: #1E1E1E;
                border: 1px solid #2A2A2A;
                border-radius: 8px;
            }
        """)
        logo_layout = QHBoxLayout(logo_container)
        logo_layout.setContentsMargins(12, 10, 12, 10)
        logo_layout.setSpacing(12)

        self.logo_preview = QLabel()
        self.logo_preview.setFixedSize(48, 48)
        self.logo_preview.setAlignment(Qt.AlignCenter)
        self.logo_preview.setStyleSheet("""
            QLabel {
                background-color: #252525;
                border: 1px dashed #444444;
                border-radius: 6px;
                color: #555555;
                font-size: 9px;
            }
        """)
        self.logo_preview.setText("LOGO")
        logo_layout.addWidget(self.logo_preview)

        logo_info = QVBoxLayout()
        logo_info.setSpacing(2)

        logo_title = QLabel("Business Logo")
        logo_title.setStyleSheet("color: #FFFFFF; font-size: 13px; font-weight: 500; border: none;")
        logo_info.addWidget(logo_title)

        logo_sub = QLabel("Optional - PNG, JPG up to 2MB")
        logo_sub.setStyleSheet("color: #666666; font-size: 11px; border: none;")
        logo_info.addWidget(logo_sub)

        logo_layout.addLayout(logo_info, 1)

        logo_btn = QPushButton("Upload")
        logo_btn.setFixedSize(70, 32)
        logo_btn.setStyleSheet("""
            QPushButton {
                background-color: #333333;
                color: #FFFFFF;
                border: none;
                border-radius: 6px;
                font-size: 12px;
                font-weight: 500;
            }
            QPushButton:hover { background-color: #444444; }
        """)
        logo_btn.setCursor(Qt.PointingHandCursor)
        logo_btn.clicked.connect(self._select_logo)
        logo_layout.addWidget(logo_btn)

        layout.addWidget(logo_container)

        layout.addSpacing(12)

        # Business Name
        self.setup_business_name = QLineEdit()
        self.setup_business_name.setPlaceholderText("Business Name")
        self.setup_business_name.setMinimumHeight(42)
        layout.addWidget(self.setup_business_name)

        layout.addSpacing(4)

        # Personal Email (required)
        self.setup_email = QLineEdit()
        self.setup_email.setPlaceholderText("Your Email")
        self.setup_email.setMinimumHeight(42)
        layout.addWidget(self.setup_email)

        layout.addSpacing(4)

        # Business Email (optional)
        self.setup_business_email = QLineEdit()
        self.setup_business_email.setPlaceholderText("Business Email (optional)")
        self.setup_business_email.setMinimumHeight(42)
        layout.addWidget(self.setup_business_email)

        layout.addSpacing(4)

        # Password
        self.setup_password = QLineEdit()
        self.setup_password.setPlaceholderText("Password (min 8 characters)")
        self.setup_password.setEchoMode(QLineEdit.Password)
        self.setup_password.setMinimumHeight(42)
        layout.addWidget(self.setup_password)

        layout.addSpacing(4)

        # Confirm Password
        self.setup_confirm = QLineEdit()
        self.setup_confirm.setPlaceholderText("Confirm Password")
        self.setup_confirm.setEchoMode(QLineEdit.Password)
        self.setup_confirm.setMinimumHeight(42)
        self.setup_confirm.returnPressed.connect(self._do_setup)
        layout.addWidget(self.setup_confirm)

        # Error/Message
        self.setup_msg = QLabel()
        self.setup_msg.setAlignment(Qt.AlignCenter)
        self.setup_msg.setWordWrap(True)
        self.setup_msg.setStyleSheet("font-size: 12px;")
        self.setup_msg.hide()
        layout.addWidget(self.setup_msg)

        layout.addSpacing(20)

        # Continue Button
        continue_btn = QPushButton("Continue")
        continue_btn.setMinimumHeight(44)
        continue_btn.setCursor(Qt.PointingHandCursor)
        continue_btn.setStyleSheet("""
            QPushButton {
                background-color: #22C55E;
                color: #FFFFFF;
                border: none;
                border-radius: 8px;
                font-weight: 600;
                font-size: 14px;
            }
            QPushButton:hover { background-color: #16A34A; }
        """)
        continue_btn.clicked.connect(self._do_setup)
        layout.addWidget(continue_btn)

        layout.addStretch()

        # Back to login
        switch_row = QHBoxLayout()
        switch_row.setAlignment(Qt.AlignCenter)

        switch_text = QLabel("Already have an account?")
        switch_text.setStyleSheet("color: #666666; font-size: 12px;")
        switch_row.addWidget(switch_text)

        switch_btn = QPushButton("Sign In")
        switch_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #5865F2;
                border: none;
                font-weight: 600;
                font-size: 12px;
            }
            QPushButton:hover { color: #4752C4; }
        """)
        switch_btn.setCursor(Qt.PointingHandCursor)
        switch_btn.clicked.connect(lambda: self._go_to_page(0))
        switch_row.addWidget(switch_btn)

        layout.addLayout(switch_row)

        return page

    def _create_verify_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(12)
        layout.setContentsMargins(0, 0, 0, 0)

        title = QLabel("Verify Your Email")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #FFFFFF;")
        layout.addWidget(title)

        layout.addSpacing(8)

        self.verify_subtitle = QLabel("Enter the 6-digit code sent to your email")
        self.verify_subtitle.setAlignment(Qt.AlignCenter)
        self.verify_subtitle.setWordWrap(True)
        self.verify_subtitle.setStyleSheet("color: #888888; font-size: 13px;")
        layout.addWidget(self.verify_subtitle)

        layout.addSpacing(16)

        # Code input
        self.verify_code = QLineEdit()
        self.verify_code.setPlaceholderText("000000")
        self.verify_code.setAlignment(Qt.AlignCenter)
        self.verify_code.setMinimumHeight(52)
        self.verify_code.setMaxLength(6)
        self.verify_code.setStyleSheet("""
            QLineEdit {
                background-color: #1E1E1E;
                border: 2px solid #333333;
                border-radius: 8px;
                color: #5865F2;
                font-size: 24px;
                font-weight: bold;
                letter-spacing: 10px;
            }
            QLineEdit:focus { border-color: #5865F2; }
        """)
        self.verify_code.returnPressed.connect(self._do_verify)
        layout.addWidget(self.verify_code)

        # Error/Message
        self.verify_msg = QLabel()
        self.verify_msg.setAlignment(Qt.AlignCenter)
        self.verify_msg.setWordWrap(True)
        self.verify_msg.setStyleSheet("font-size: 12px;")
        self.verify_msg.hide()
        layout.addWidget(self.verify_msg)

        # Verify Button
        verify_btn = QPushButton("Verify & Create Account")
        verify_btn.setMinimumHeight(44)
        verify_btn.setCursor(Qt.PointingHandCursor)
        verify_btn.setStyleSheet("""
            QPushButton {
                background-color: #22C55E;
                color: #FFFFFF;
                border: none;
                border-radius: 8px;
                font-weight: 600;
                font-size: 14px;
            }
            QPushButton:hover { background-color: #16A34A; }
        """)
        verify_btn.clicked.connect(self._do_verify)
        layout.addWidget(verify_btn)

        layout.addSpacing(8)

        # Resend code
        resend_row = QHBoxLayout()
        resend_row.setAlignment(Qt.AlignCenter)

        resend_text = QLabel("Didn't receive a code?")
        resend_text.setStyleSheet("color: #666666; font-size: 12px;")
        resend_row.addWidget(resend_text)

        self.resend_btn = QPushButton("Resend")
        self.resend_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #5865F2;
                border: none;
                font-weight: 600;
                font-size: 12px;
            }
            QPushButton:hover { color: #4752C4; }
        """)
        self.resend_btn.setCursor(Qt.PointingHandCursor)
        self.resend_btn.clicked.connect(self._resend_code)
        resend_row.addWidget(self.resend_btn)

        layout.addLayout(resend_row)

        layout.addStretch()

        # Back button
        back_btn = QPushButton("← Back")
        back_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #888888;
                border: 1px solid #333333;
                border-radius: 8px;
                padding: 10px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #1E1E1E;
                color: #FFFFFF;
            }
        """)
        back_btn.setCursor(Qt.PointingHandCursor)
        back_btn.clicked.connect(lambda: self._go_to_page(1))
        layout.addWidget(back_btn)

        return page

    def _go_to_page(self, index: int):
        """Switch to a page with size adjustment."""
        heights = {0: 480, 1: 580, 2: 440}
        self.setFixedSize(400, heights.get(index, 480))
        self.pages.setCurrentIndex(index)
        self._update_mask()
        self._center_on_screen()

    def _select_logo(self):
        """Open file dialog to select logo."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Logo", "",
            "Images (*.png *.jpg *.jpeg *.gif *.webp)"
        )

        if file_path:
            self._selected_logo_path = file_path
            pixmap = QPixmap(file_path)
            if not pixmap.isNull():
                scaled = pixmap.scaled(44, 44, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.logo_preview.setPixmap(scaled)
                self.logo_preview.setStyleSheet("""
                    QLabel {
                        background-color: #252525;
                        border: 2px solid #22C55E;
                        border-radius: 6px;
                    }
                """)

    def _do_login(self):
        self.login_error.hide()

        email = self.login_email.text().strip()
        password = self.login_password.text()
        remember = self.remember_device.isChecked()

        if not email or not password:
            self.login_error.setText("Please enter email and password")
            self.login_error.show()
            return

        success, user_data, message = self.auth_service.authenticate(email, password, remember)

        if success:
            logger.info(f"Login successful: {user_data['business_name']}")
            self.login_successful.emit(user_data)
            self.close()
        else:
            self.login_error.setText(message)
            self.login_error.show()

    def _do_setup(self):
        self.setup_msg.hide()

        business_name = self.setup_business_name.text().strip()
        email = self.setup_email.text().strip()
        business_email = self.setup_business_email.text().strip()
        password = self.setup_password.text()
        confirm = self.setup_confirm.text()

        if not business_name:
            self._show_setup_error("Please enter your business name")
            return

        if not email:
            self._show_setup_error("Please enter your email")
            return

        if not password:
            self._show_setup_error("Please enter a password")
            return

        if password != confirm:
            self._show_setup_error("Passwords don't match")
            return

        if len(password) < 8:
            self._show_setup_error("Password must be at least 8 characters")
            return

        logo_path = None
        if self._selected_logo_path:
            logo_path = self.auth_service.save_logo(self._selected_logo_path, email)

        success, message, code = self.auth_service.start_registration(
            email=email,
            business_name=business_name,
            business_email=business_email,
            password=password,
            logo_path=logo_path
        )

        if success:
            self._pending_email = email

            email_sent, _ = self.email_service.send_verification_email(email, code)

            if email_sent:
                self.verify_subtitle.setText(f"Enter the 6-digit code sent to\n{email}")
            else:
                self.verify_subtitle.setText(f"Your verification code is:\n{code}")
                logger.warning(f"Email not sent. Code for {email}: {code}")

            self._go_to_page(2)
        else:
            self._show_setup_error(message)

    def _show_setup_error(self, message: str):
        self.setup_msg.setText(message)
        self.setup_msg.setStyleSheet("color: #EF4444; font-size: 12px;")
        self.setup_msg.show()

    def _do_verify(self):
        self.verify_msg.hide()

        code = self.verify_code.text().strip()

        if not code or len(code) != 6:
            self.verify_msg.setText("Please enter the 6-digit code")
            self.verify_msg.setStyleSheet("color: #EF4444;")
            self.verify_msg.show()
            return

        success, message = self.auth_service.verify_and_complete_registration(
            self._pending_email, code
        )

        if success:
            self.verify_msg.setText("Account created! Redirecting...")
            self.verify_msg.setStyleSheet("color: #22C55E;")
            self.verify_msg.show()
            QTimer.singleShot(1500, self._go_to_login_after_signup)
        else:
            self.verify_msg.setText(message)
            self.verify_msg.setStyleSheet("color: #EF4444;")
            self.verify_msg.show()

    def _go_to_login_after_signup(self):
        """Reset form and go to login page."""
        self.setup_business_name.clear()
        self.setup_email.clear()
        self.setup_business_email.clear()
        self.setup_password.clear()
        self.setup_confirm.clear()
        self.verify_code.clear()
        self._selected_logo_path = None
        self.logo_preview.clear()
        self.logo_preview.setText("LOGO")
        self.logo_preview.setStyleSheet("""
            QLabel {
                background-color: #252525;
                border: 1px dashed #444444;
                border-radius: 6px;
                color: #555555;
                font-size: 9px;
            }
        """)
        self._go_to_page(0)

    def _resend_code(self):
        if not self._pending_email:
            return

        success, message, code = self.auth_service.resend_verification_code(self._pending_email)

        if success:
            email_sent, _ = self.email_service.send_verification_email(self._pending_email, code)

            if email_sent:
                self.verify_msg.setText("New code sent!")
            else:
                self.verify_msg.setText(f"New code: {code}")

            self.verify_msg.setStyleSheet("color: #22C55E;")
        else:
            self.verify_msg.setText(message)
            self.verify_msg.setStyleSheet("color: #EF4444;")

        self.verify_msg.show()

    def paintEvent(self, event):
        """Paint rounded rectangle background."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Draw background
        path = QPainterPath()
        path.addRoundedRect(QRectF(self.rect()), RADIUS, RADIUS)
        painter.fillPath(path, QBrush(QColor("#121212")))

        # Draw border
        painter.setPen(QPen(QColor("#2A2A2A"), 1))
        painter.drawRoundedRect(QRectF(self.rect()).adjusted(0.5, 0.5, -0.5, -0.5), RADIUS, RADIUS)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and event.position().y() < 32:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if self._drag_pos and event.buttons() == Qt.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        self._drag_pos = None
