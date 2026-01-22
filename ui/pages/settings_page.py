"""
CHAIRMAN - Settings Page
Professional user profile and application settings
"""
from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFrame, QScrollArea, QMessageBox, QDialog,
    QDialogButtonBox, QFileDialog, QComboBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap

from core.auth import AuthService
from core.logging_config import get_logger

logger = get_logger(__name__)


class SettingsPage(QWidget):
    """Professional settings page."""

    logout_requested = Signal()
    account_deleted = Signal()
    logo_changed = Signal(str)  # Emits new logo path

    def __init__(self):
        super().__init__()
        self.auth_service = AuthService()
        self.current_user = None
        self._is_editing = False
        self._setup_ui()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(32, 32, 32, 32)
        content_layout.setSpacing(24)

        # Header
        header = QHBoxLayout()

        title_col = QVBoxLayout()
        title_col.setSpacing(4)

        title = QLabel("Settings")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #FFFFFF;")
        title_col.addWidget(title)

        subtitle = QLabel("Manage your profile and application preferences")
        subtitle.setStyleSheet("font-size: 14px; color: #666666;")
        title_col.addWidget(subtitle)

        header.addLayout(title_col)
        header.addStretch()

        # Logout button in header
        logout_btn = QPushButton("Log Out")
        logout_btn.setFixedSize(100, 36)
        logout_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: 1px solid #333333;
                border-radius: 8px;
                color: #FFFFFF;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #333333;
            }
        """)
        logout_btn.setCursor(Qt.PointingHandCursor)
        logout_btn.clicked.connect(self._logout)
        header.addWidget(logout_btn)

        content_layout.addLayout(header)

        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")

        scroll_content = QWidget()
        scroll_content.setStyleSheet("background: transparent;")
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(20)
        scroll_layout.setContentsMargins(0, 0, 0, 0)

        # Profile Section
        profile_card = self._create_profile_section()
        scroll_layout.addWidget(profile_card)

        # Business Logo Section
        logo_card = self._create_logo_section()
        scroll_layout.addWidget(logo_card)

        # Team Section
        team_card = self._create_team_section()
        scroll_layout.addWidget(team_card)

        # Security Section
        security_card = self._create_security_section()
        scroll_layout.addWidget(security_card)

        # Danger Zone Section
        danger_card = self._create_danger_section()
        scroll_layout.addWidget(danger_card)

        scroll_layout.addStretch()
        scroll.setWidget(scroll_content)
        content_layout.addWidget(scroll, 1)

        layout.addWidget(content)

    def _create_profile_section(self) -> QFrame:
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #1E1E1E;
                border: 1px solid #2A2A2A;
                border-radius: 10px;
            }
        """)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(12)

        # Header with edit button
        header = QHBoxLayout()
        section_title = QLabel("Profile Information")
        section_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #FFFFFF; border: none;")
        header.addWidget(section_title)
        header.addStretch()

        self.edit_btn = QPushButton("Edit")
        self.edit_btn.setFixedSize(70, 32)
        self.edit_btn.setStyleSheet("""
            QPushButton {
                background-color: #333333;
                border: none;
                border-radius: 6px;
                color: #FFFFFF;
                font-weight: 500;
            }
            QPushButton:hover { background-color: #444444; }
        """)
        self.edit_btn.setCursor(Qt.PointingHandCursor)
        self.edit_btn.clicked.connect(self._toggle_edit_mode)
        header.addWidget(self.edit_btn)

        layout.addLayout(header)

        # Form styling
        label_style = "font-size: 11px; font-weight: bold; color: #666666; border: none;"
        self.input_style_readonly = """
            QLineEdit {
                background-color: #252525;
                border: 1px solid #333333;
                border-radius: 8px;
                padding: 10px 12px;
                color: #FFFFFF;
                font-size: 13px;
            }
        """
        self.input_style_editable = """
            QLineEdit {
                background-color: #252525;
                border: 1px solid #5865F2;
                border-radius: 8px;
                padding: 10px 12px;
                color: #FFFFFF;
                font-size: 13px;
            }
            QLineEdit:focus { border-color: #7289DA; }
        """

        # Name
        name_label = QLabel("FULL NAME")
        name_label.setStyleSheet(label_style)
        layout.addWidget(name_label)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Your full name")
        self.name_input.setMinimumHeight(40)
        self.name_input.setReadOnly(True)
        self.name_input.setStyleSheet(self.input_style_readonly)
        layout.addWidget(self.name_input)

        # Business Name
        business_label = QLabel("BUSINESS NAME")
        business_label.setStyleSheet(label_style)
        layout.addWidget(business_label)

        self.business_input = QLineEdit()
        self.business_input.setPlaceholderText("Business name")
        self.business_input.setMinimumHeight(40)
        self.business_input.setReadOnly(True)
        self.business_input.setStyleSheet(self.input_style_readonly)
        layout.addWidget(self.business_input)

        # Email (read-only always)
        email_label = QLabel("EMAIL ADDRESS (cannot be changed)")
        email_label.setStyleSheet(label_style)
        layout.addWidget(email_label)

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("your.email@example.com")
        self.email_input.setMinimumHeight(40)
        self.email_input.setReadOnly(True)
        self.email_input.setStyleSheet(self.input_style_readonly)
        layout.addWidget(self.email_input)

        # Business Email
        business_email_label = QLabel("BUSINESS EMAIL")
        business_email_label.setStyleSheet(label_style)
        layout.addWidget(business_email_label)

        self.business_email_input = QLineEdit()
        self.business_email_input.setPlaceholderText("Business email (optional)")
        self.business_email_input.setMinimumHeight(40)
        self.business_email_input.setReadOnly(True)
        self.business_email_input.setStyleSheet(self.input_style_readonly)
        layout.addWidget(self.business_email_input)

        # Phone
        phone_label = QLabel("PHONE NUMBER")
        phone_label.setStyleSheet(label_style)
        layout.addWidget(phone_label)

        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("Your phone number")
        self.phone_input.setMinimumHeight(40)
        self.phone_input.setReadOnly(True)
        self.phone_input.setStyleSheet(self.input_style_readonly)
        layout.addWidget(self.phone_input)

        # Save/Cancel buttons (hidden by default)
        self.save_buttons = QWidget()
        save_layout = QHBoxLayout(self.save_buttons)
        save_layout.setContentsMargins(0, 8, 0, 0)
        save_layout.setSpacing(8)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setMinimumHeight(40)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: 1px solid #333333;
                border-radius: 8px;
                color: #FFFFFF;
                font-weight: 500;
                padding: 0 20px;
            }
            QPushButton:hover { background-color: #252525; }
        """)
        cancel_btn.setCursor(Qt.PointingHandCursor)
        cancel_btn.clicked.connect(self._cancel_edit)
        save_layout.addWidget(cancel_btn)

        save_btn = QPushButton("Save Changes")
        save_btn.setMinimumHeight(40)
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #22C55E;
                border: none;
                border-radius: 8px;
                color: #FFFFFF;
                font-weight: 600;
                padding: 0 20px;
            }
            QPushButton:hover { background-color: #16A34A; }
        """)
        save_btn.setCursor(Qt.PointingHandCursor)
        save_btn.clicked.connect(self._save_changes)
        save_layout.addWidget(save_btn)

        self.save_buttons.hide()
        layout.addWidget(self.save_buttons)

        return card

    def _create_logo_section(self) -> QFrame:
        """Create business logo section."""
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #1E1E1E;
                border: 1px solid #2A2A2A;
                border-radius: 10px;
            }
        """)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(12)

        section_title = QLabel("Business Logo")
        section_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #FFFFFF; border: none;")
        layout.addWidget(section_title)

        desc = QLabel("Upload your business logo to display in the sidebar")
        desc.setStyleSheet("font-size: 12px; color: #666666; border: none;")
        layout.addWidget(desc)

        # Logo preview and upload row
        logo_row = QHBoxLayout()
        logo_row.setSpacing(16)

        # Logo preview
        self.logo_preview = QLabel()
        self.logo_preview.setFixedSize(80, 80)
        self.logo_preview.setAlignment(Qt.AlignCenter)
        self.logo_preview.setStyleSheet("""
            background-color: #252525;
            border: 2px dashed #333333;
            border-radius: 10px;
            color: #555555;
            font-size: 12px;
        """)
        self.logo_preview.setText("No Logo")
        logo_row.addWidget(self.logo_preview)

        # Upload/Remove buttons
        btn_col = QVBoxLayout()
        btn_col.setSpacing(8)

        upload_btn = QPushButton("Upload New Logo")
        upload_btn.setMinimumHeight(36)
        upload_btn.setStyleSheet("""
            QPushButton {
                background-color: #5865F2;
                border: none;
                border-radius: 8px;
                color: #FFFFFF;
                font-weight: 500;
                padding: 0 16px;
            }
            QPushButton:hover { background-color: #4752C4; }
        """)
        upload_btn.setCursor(Qt.PointingHandCursor)
        upload_btn.clicked.connect(self._upload_logo)
        btn_col.addWidget(upload_btn)

        remove_btn = QPushButton("Remove Logo")
        remove_btn.setMinimumHeight(36)
        remove_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: 1px solid #333333;
                border-radius: 8px;
                color: #888888;
                font-weight: 500;
                padding: 0 16px;
            }
            QPushButton:hover {
                background-color: #252525;
                color: #FFFFFF;
            }
        """)
        remove_btn.setCursor(Qt.PointingHandCursor)
        remove_btn.clicked.connect(self._remove_logo)
        btn_col.addWidget(remove_btn)

        logo_row.addLayout(btn_col)
        logo_row.addStretch()

        layout.addLayout(logo_row)

        # Supported formats note
        note = QLabel("Supported formats: PNG, JPG, GIF (max 2MB)")
        note.setStyleSheet("color: #555555; font-size: 11px; border: none;")
        layout.addWidget(note)

        return card

    def _upload_logo(self):
        """Upload a new business logo."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Logo", "",
            "Images (*.png *.jpg *.jpeg *.gif *.webp)"
        )

        if file_path and self.current_user:
            # Save the logo
            saved_path = self.auth_service.save_logo(file_path, self.current_user['email'])

            if saved_path:
                # Update database
                try:
                    from data.db import get_connection
                    conn = get_connection()
                    cursor = conn.cursor()
                    cursor.execute(
                        "UPDATE users SET logo_path = ? WHERE id = ?",
                        (saved_path, self.current_user['id'])
                    )
                    conn.commit()

                    self.current_user['logo_path'] = saved_path
                    self._update_logo_preview(saved_path)
                    self.logo_changed.emit(saved_path)

                    QMessageBox.information(self, "Success", "Logo updated successfully!")

                except Exception as e:
                    logger.error(f"Error saving logo: {e}")
                    QMessageBox.critical(self, "Error", f"Failed to save logo: {e}")

    def _remove_logo(self):
        """Remove the current business logo."""
        if not self.current_user:
            return

        reply = QMessageBox.question(
            self, "Remove Logo",
            "Are you sure you want to remove your business logo?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                from data.db import get_connection
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE users SET logo_path = NULL WHERE id = ?",
                    (self.current_user['id'],)
                )
                conn.commit()

                self.current_user['logo_path'] = None
                self._update_logo_preview(None)
                self.logo_changed.emit("")

                QMessageBox.information(self, "Success", "Logo removed.")

            except Exception as e:
                logger.error(f"Error removing logo: {e}")
                QMessageBox.critical(self, "Error", f"Failed to remove logo: {e}")

    def _update_logo_preview(self, logo_path: str):
        """Update the logo preview widget."""
        if logo_path and Path(logo_path).exists():
            pixmap = QPixmap(logo_path)
            if not pixmap.isNull():
                scaled = pixmap.scaled(76, 76, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.logo_preview.setPixmap(scaled)
                self.logo_preview.setStyleSheet("""
                    background-color: #252525;
                    border: 2px solid #22C55E;
                    border-radius: 10px;
                """)
                return

        # No logo
        self.logo_preview.clear()
        self.logo_preview.setText("No Logo")
        self.logo_preview.setStyleSheet("""
            background-color: #252525;
            border: 2px dashed #333333;
            border-radius: 10px;
            color: #555555;
            font-size: 12px;
        """)

    def _create_team_section(self) -> QFrame:
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #1E1E1E;
                border: 1px solid #2A2A2A;
                border-radius: 10px;
            }
        """)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(12)

        section_title = QLabel("Team Members")
        section_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #FFFFFF; border: none;")
        layout.addWidget(section_title)

        desc = QLabel("Add team members by email to give them access to your business")
        desc.setStyleSheet("font-size: 12px; color: #666666; border: none;")
        layout.addWidget(desc)

        # Add member row
        add_row = QHBoxLayout()
        add_row.setSpacing(8)

        self.team_email_input = QLineEdit()
        self.team_email_input.setPlaceholderText("Enter team member's email")
        self.team_email_input.setMinimumHeight(40)
        self.team_email_input.setStyleSheet("""
            QLineEdit {
                background-color: #252525;
                border: 1px solid #333333;
                border-radius: 8px;
                padding: 10px 12px;
                color: #FFFFFF;
                font-size: 13px;
            }
            QLineEdit:focus { border-color: #5865F2; }
        """)
        add_row.addWidget(self.team_email_input, 1)

        # Role selector
        self.team_role_combo = QComboBox()
        self.team_role_combo.addItems(["Member", "Admin", "Owner"])
        self.team_role_combo.setFixedSize(100, 40)
        self.team_role_combo.setStyleSheet("""
            QComboBox {
                background-color: #252525;
                border: 1px solid #333333;
                border-radius: 8px;
                padding: 8px 12px;
                color: #FFFFFF;
                font-size: 13px;
            }
            QComboBox:hover { border-color: #444444; }
            QComboBox:focus { border-color: #5865F2; }
            QComboBox::drop-down {
                border: none;
                padding-right: 8px;
            }
            QComboBox::down-arrow {
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 5px solid #666666;
            }
            QComboBox QAbstractItemView {
                background-color: #252525;
                border: 1px solid #333333;
                border-radius: 8px;
                selection-background-color: #5865F2;
                color: #FFFFFF;
            }
        """)
        add_row.addWidget(self.team_role_combo)

        add_btn = QPushButton("Add")
        add_btn.setFixedSize(80, 40)
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #5865F2;
                border: none;
                border-radius: 8px;
                color: #FFFFFF;
                font-weight: 600;
            }
            QPushButton:hover { background-color: #4752C4; }
        """)
        add_btn.setCursor(Qt.PointingHandCursor)
        add_btn.clicked.connect(self._add_team_member)
        add_row.addWidget(add_btn)

        layout.addLayout(add_row)

        # Team members list
        self.team_list = QVBoxLayout()
        self.team_list.setSpacing(8)
        layout.addLayout(self.team_list)

        # Placeholder for empty state
        self.empty_team_label = QLabel("No team members yet")
        self.empty_team_label.setStyleSheet("color: #555555; font-size: 13px; padding: 12px; border: none;")
        self.empty_team_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.empty_team_label)

        return card

    def _create_security_section(self) -> QFrame:
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #1E1E1E;
                border: 1px solid #2A2A2A;
                border-radius: 10px;
            }
        """)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(12)

        section_title = QLabel("Account Security")
        section_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #FFFFFF; border: none;")
        layout.addWidget(section_title)

        label_style = "font-size: 11px; font-weight: bold; color: #666666; border: none;"
        info_style = """
            background-color: #252525;
            border-radius: 8px;
            padding: 10px 12px;
            color: #FFFFFF;
            font-size: 13px;
            border: none;
        """

        # Account created
        created_label = QLabel("ACCOUNT CREATED")
        created_label.setStyleSheet(label_style)
        layout.addWidget(created_label)

        self.created_date = QLabel("--")
        self.created_date.setStyleSheet(info_style)
        layout.addWidget(self.created_date)

        # Last login
        login_label = QLabel("LAST LOGIN")
        login_label.setStyleSheet(label_style)
        layout.addWidget(login_label)

        self.last_login = QLabel("--")
        self.last_login.setStyleSheet(info_style)
        layout.addWidget(self.last_login)

        # Change password button
        change_pwd_btn = QPushButton("Change Password")
        change_pwd_btn.setMinimumHeight(40)
        change_pwd_btn.setStyleSheet("""
            QPushButton {
                background-color: #333333;
                border: none;
                border-radius: 8px;
                color: #FFFFFF;
                font-weight: 500;
            }
            QPushButton:hover { background-color: #444444; }
        """)
        change_pwd_btn.setCursor(Qt.PointingHandCursor)
        change_pwd_btn.clicked.connect(self._change_password)
        layout.addWidget(change_pwd_btn)

        return card

    def _create_danger_section(self) -> QFrame:
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #1E1E1E;
                border: 1px solid #3A2020;
                border-radius: 10px;
            }
        """)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(12)

        section_title = QLabel("Danger Zone")
        section_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #EF4444; border: none;")
        layout.addWidget(section_title)

        desc = QLabel("Permanently delete your account and all associated data. This action cannot be undone.")
        desc.setStyleSheet("font-size: 12px; color: #888888; border: none;")
        desc.setWordWrap(True)
        layout.addWidget(desc)

        delete_btn = QPushButton("Delete Account")
        delete_btn.setMinimumHeight(40)
        delete_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: 1px solid #EF4444;
                border-radius: 8px;
                color: #EF4444;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #EF4444;
                color: #FFFFFF;
            }
        """)
        delete_btn.setCursor(Qt.PointingHandCursor)
        delete_btn.clicked.connect(self._delete_account)
        layout.addWidget(delete_btn)

        return card

    def load_user_data(self, user_data: dict):
        """Load and display user data."""
        self.current_user = user_data

        self.name_input.setText(user_data.get('name', ''))
        self.email_input.setText(user_data.get('email', ''))
        self.business_input.setText(user_data.get('business_name', ''))
        self.business_email_input.setText(user_data.get('business_email', '') or '')
        self.phone_input.setText(user_data.get('phone', '') or '')

        try:
            from data.db import get_connection
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT created_at, last_login FROM users WHERE id = ?
            """, (user_data['id'],))
            result = cursor.fetchone()

            if result:
                created_at, last_login = result
                self.created_date.setText(created_at or "Unknown")
                self.last_login.setText(last_login or "Never")
        except Exception as e:
            logger.error(f"Error loading user timestamps: {e}")

        # Load team members
        self._load_team_members()

        # Load logo preview
        self._update_logo_preview(user_data.get('logo_path'))

    def _toggle_edit_mode(self):
        """Toggle between view and edit mode."""
        self._is_editing = not self._is_editing

        if self._is_editing:
            self.edit_btn.setText("Cancel")
            self.edit_btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    border: 1px solid #333333;
                    border-radius: 6px;
                    color: #FFFFFF;
                    font-weight: 500;
                }
                QPushButton:hover { background-color: #333333; }
            """)

            # Make fields editable (except email)
            for field in [self.name_input, self.business_input, self.business_email_input, self.phone_input]:
                field.setReadOnly(False)
                field.setStyleSheet(self.input_style_editable)

            self.save_buttons.show()
        else:
            self._cancel_edit()

    def _cancel_edit(self):
        """Cancel editing and restore original values."""
        self._is_editing = False
        self.edit_btn.setText("Edit")
        self.edit_btn.setStyleSheet("""
            QPushButton {
                background-color: #333333;
                border: none;
                border-radius: 6px;
                color: #FFFFFF;
                font-weight: 500;
            }
            QPushButton:hover { background-color: #444444; }
        """)

        # Restore original values
        if self.current_user:
            self.name_input.setText(self.current_user.get('name', ''))
            self.business_input.setText(self.current_user.get('business_name', ''))
            self.business_email_input.setText(self.current_user.get('business_email', '') or '')
            self.phone_input.setText(self.current_user.get('phone', '') or '')

        # Make fields read-only
        for field in [self.name_input, self.business_input, self.business_email_input, self.phone_input]:
            field.setReadOnly(True)
            field.setStyleSheet(self.input_style_readonly)

        self.save_buttons.hide()

    def _save_changes(self):
        """Save profile changes to database."""
        if not self.current_user:
            return

        name = self.name_input.text().strip()
        business_name = self.business_input.text().strip()
        business_email = self.business_email_input.text().strip()
        phone = self.phone_input.text().strip()

        if not name or not business_name:
            QMessageBox.warning(self, "Error", "Name and business name are required.")
            return

        try:
            from data.db import get_connection
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE users SET name = ?, business_name = ?, business_email = ?, phone = ?
                WHERE id = ?
            """, (name, business_name, business_email or None, phone or None, self.current_user['id']))
            conn.commit()

            # Update current user data
            self.current_user['name'] = name
            self.current_user['business_name'] = business_name
            self.current_user['business_email'] = business_email
            self.current_user['phone'] = phone

            self._cancel_edit()
            QMessageBox.information(self, "Success", "Profile updated successfully.")

        except Exception as e:
            logger.error(f"Error saving profile: {e}")
            QMessageBox.critical(self, "Error", f"Failed to save changes: {e}")

    def _load_team_members(self):
        """Load team members from database."""
        # Clear existing items
        while self.team_list.count():
            item = self.team_list.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not self.current_user:
            return

        try:
            from data.db import get_connection
            conn = get_connection()
            cursor = conn.cursor()

            # Check if team_members table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='team_members'")
            if not cursor.fetchone():
                # Create table
                cursor.execute("""
                    CREATE TABLE team_members (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        business_id INTEGER NOT NULL,
                        email TEXT NOT NULL,
                        name TEXT,
                        role TEXT DEFAULT 'member',
                        invited_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(business_id, email)
                    )
                """)
                conn.commit()

            cursor.execute("""
                SELECT id, email, name, role FROM team_members WHERE business_id = ?
            """, (self.current_user['id'],))
            members = cursor.fetchall()

            if members:
                self.empty_team_label.hide()
                for member_id, email, name, role in members:
                    self._add_team_member_widget(member_id, email, name, role)
            else:
                self.empty_team_label.show()

        except Exception as e:
            logger.error(f"Error loading team members: {e}")

    def _add_team_member_widget(self, member_id: int, email: str, name: str, role: str):
        """Add a team member widget to the list."""
        row = QFrame()
        row.setStyleSheet("""
            QFrame {
                background-color: #252525;
                border: 1px solid #333333;
                border-radius: 8px;
            }
        """)

        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(12, 10, 12, 10)
        row_layout.setSpacing(12)

        # Avatar placeholder with role-based color
        avatar_colors = {
            'owner': '#F59E0B',   # Gold for owner
            'admin': '#5865F2',   # Blue for admin
            'member': '#22C55E',  # Green for member
        }
        avatar_color = avatar_colors.get(role.lower(), '#5865F2')

        avatar = QLabel(email[0].upper())
        avatar.setFixedSize(36, 36)
        avatar.setAlignment(Qt.AlignCenter)
        avatar.setStyleSheet(f"""
            background-color: {avatar_color};
            border-radius: 18px;
            color: #FFFFFF;
            font-weight: bold;
            font-size: 14px;
        """)
        row_layout.addWidget(avatar)

        # Info
        info = QVBoxLayout()
        info.setSpacing(2)

        name_label = QLabel(name or email)
        name_label.setStyleSheet("color: #FFFFFF; font-size: 13px; font-weight: 500; border: none;")
        info.addWidget(name_label)

        email_label = QLabel(email)
        email_label.setStyleSheet("color: #666666; font-size: 11px; border: none;")
        info.addWidget(email_label)

        row_layout.addLayout(info, 1)

        # Role dropdown
        role_colors = {
            'owner': ('background-color: #92400E; color: #FCD34D;', 'Owner'),
            'admin': ('background-color: #3730A3; color: #A5B4FC;', 'Admin'),
            'member': ('background-color: #14532D; color: #86EFAC;', 'Member'),
        }
        role_style, role_text = role_colors.get(role.lower(), ('background-color: #333333; color: #AAAAAA;', role.title()))

        role_combo = QComboBox()
        role_combo.addItems(["Member", "Admin", "Owner"])
        role_combo.setCurrentText(role.title())
        role_combo.setFixedSize(90, 28)
        role_combo.setStyleSheet(f"""
            QComboBox {{
                {role_style}
                border: none;
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 11px;
                font-weight: 600;
            }}
            QComboBox::drop-down {{
                border: none;
                width: 16px;
            }}
            QComboBox::down-arrow {{
                border-left: 3px solid transparent;
                border-right: 3px solid transparent;
                border-top: 4px solid currentColor;
            }}
            QComboBox QAbstractItemView {{
                background-color: #252525;
                border: 1px solid #333333;
                border-radius: 6px;
                selection-background-color: #5865F2;
                color: #FFFFFF;
            }}
        """)
        role_combo.currentTextChanged.connect(lambda new_role: self._change_member_role(member_id, new_role, role_combo, avatar))
        row_layout.addWidget(role_combo)

        # Remove button
        remove_btn = QPushButton("×")
        remove_btn.setFixedSize(28, 28)
        remove_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                color: #666666;
                font-size: 18px;
                font-weight: bold;
            }
            QPushButton:hover {
                color: #EF4444;
            }
        """)
        remove_btn.setCursor(Qt.PointingHandCursor)
        remove_btn.clicked.connect(lambda: self._remove_team_member(member_id, row))
        row_layout.addWidget(remove_btn)

        self.team_list.addWidget(row)

    def _add_team_member(self):
        """Add a new team member."""
        email = self.team_email_input.text().strip()
        role = self.team_role_combo.currentText().lower()

        if not email or '@' not in email:
            QMessageBox.warning(self, "Error", "Please enter a valid email address.")
            return

        if not self.current_user:
            return

        try:
            from data.db import get_connection
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO team_members (business_id, email, role) VALUES (?, ?, ?)
            """, (self.current_user['id'], email, role))
            conn.commit()

            member_id = cursor.lastrowid
            self.team_email_input.clear()
            self.team_role_combo.setCurrentIndex(0)  # Reset to Member
            self.empty_team_label.hide()
            self._add_team_member_widget(member_id, email, None, role)

            QMessageBox.information(self, "Success", f"Invited {email} as {role.title()} to your team.")

        except Exception as e:
            if "UNIQUE constraint" in str(e):
                QMessageBox.warning(self, "Error", "This email is already in your team.")
            else:
                logger.error(f"Error adding team member: {e}")
                QMessageBox.critical(self, "Error", f"Failed to add team member: {e}")

    def _change_member_role(self, member_id: int, new_role: str, combo: QComboBox, avatar: QLabel):
        """Change a team member's role."""
        role = new_role.lower()

        try:
            from data.db import get_connection
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE team_members SET role = ? WHERE id = ?
            """, (role, member_id))
            conn.commit()

            # Update styling
            role_colors = {
                'owner': ('background-color: #92400E; color: #FCD34D;', '#F59E0B'),
                'admin': ('background-color: #3730A3; color: #A5B4FC;', '#5865F2'),
                'member': ('background-color: #14532D; color: #86EFAC;', '#22C55E'),
            }
            combo_style, avatar_color = role_colors.get(role, ('background-color: #333333; color: #AAAAAA;', '#5865F2'))

            combo.setStyleSheet(f"""
                QComboBox {{
                    {combo_style}
                    border: none;
                    border-radius: 4px;
                    padding: 4px 8px;
                    font-size: 11px;
                    font-weight: 600;
                }}
                QComboBox::drop-down {{
                    border: none;
                    width: 16px;
                }}
                QComboBox::down-arrow {{
                    border-left: 3px solid transparent;
                    border-right: 3px solid transparent;
                    border-top: 4px solid currentColor;
                }}
                QComboBox QAbstractItemView {{
                    background-color: #252525;
                    border: 1px solid #333333;
                    border-radius: 6px;
                    selection-background-color: #5865F2;
                    color: #FFFFFF;
                }}
            """)

            avatar.setStyleSheet(f"""
                background-color: {avatar_color};
                border-radius: 18px;
                color: #FFFFFF;
                font-weight: bold;
                font-size: 14px;
            """)

        except Exception as e:
            logger.error(f"Error changing role: {e}")
            QMessageBox.critical(self, "Error", f"Failed to change role: {e}")

    def _remove_team_member(self, member_id: int, widget: QWidget):
        """Remove a team member."""
        reply = QMessageBox.question(
            self, "Remove Team Member",
            "Are you sure you want to remove this team member?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                from data.db import get_connection
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("DELETE FROM team_members WHERE id = ?", (member_id,))
                conn.commit()

                widget.deleteLater()

                # Check if list is empty
                if self.team_list.count() == 0:
                    self.empty_team_label.show()

            except Exception as e:
                logger.error(f"Error removing team member: {e}")
                QMessageBox.critical(self, "Error", f"Failed to remove team member: {e}")

    def _change_password(self):
        """Show change password dialog."""
        dialog = ChangePasswordDialog(self, self.current_user, self.auth_service)
        dialog.exec()

    def _logout(self):
        """Log out the current user."""
        reply = QMessageBox.question(
            self, "Log Out",
            "Are you sure you want to log out?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            if self.current_user:
                self.auth_service.logout(self.current_user.get('id'))
            self.logout_requested.emit()

    def _delete_account(self):
        """Delete the user's account."""
        # First confirmation
        reply = QMessageBox.warning(
            self, "Delete Account",
            "Are you sure you want to delete your account?\n\nThis will permanently delete all your data including:\n• Your profile\n• All clients\n• All appointments\n• All services\n\nThis action CANNOT be undone.",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply != QMessageBox.Yes:
            return

        # Second confirmation with email verification
        dialog = QDialog(self)
        dialog.setWindowTitle("Confirm Account Deletion")
        dialog.setFixedSize(350, 180)
        dialog.setStyleSheet("background-color: #1E1E1E;")

        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        label = QLabel(f"Type your email to confirm:\n{self.current_user.get('email', '')}")
        label.setStyleSheet("color: #FFFFFF; font-size: 13px;")
        layout.addWidget(label)

        email_input = QLineEdit()
        email_input.setPlaceholderText("Enter your email")
        email_input.setMinimumHeight(40)
        email_input.setStyleSheet("""
            QLineEdit {
                background-color: #252525;
                border: 1px solid #333333;
                border-radius: 8px;
                padding: 10px;
                color: #FFFFFF;
            }
        """)
        layout.addWidget(email_input)

        buttons = QDialogButtonBox()
        cancel_btn = buttons.addButton("Cancel", QDialogButtonBox.RejectRole)
        delete_btn = buttons.addButton("Delete Forever", QDialogButtonBox.AcceptRole)

        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #333333;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                color: #FFFFFF;
            }
        """)
        delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #EF4444;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                color: #FFFFFF;
                font-weight: bold;
            }
        """)

        layout.addWidget(buttons)

        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)

        if dialog.exec() == QDialog.Accepted:
            if email_input.text().strip() == self.current_user.get('email', ''):
                self._perform_account_deletion()
            else:
                QMessageBox.warning(self, "Error", "Email doesn't match. Account not deleted.")

    def _perform_account_deletion(self):
        """Actually delete the account from database."""
        try:
            from data.db import get_connection
            conn = get_connection()
            cursor = conn.cursor()

            user_id = self.current_user['id']

            # Delete team members
            cursor.execute("DELETE FROM team_members WHERE business_id = ?", (user_id,))

            # Delete user
            cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))

            conn.commit()

            # Clear device token
            self.auth_service.logout(user_id)

            QMessageBox.information(self, "Account Deleted", "Your account has been deleted.")
            self.account_deleted.emit()

        except Exception as e:
            logger.error(f"Error deleting account: {e}")
            QMessageBox.critical(self, "Error", f"Failed to delete account: {e}")


class ChangePasswordDialog(QDialog):
    """Dialog for changing password."""

    def __init__(self, parent, user_data, auth_service):
        super().__init__(parent)
        self.user_data = user_data
        self.auth_service = auth_service

        self.setWindowTitle("Change Password")
        self.setFixedSize(380, 300)
        self.setStyleSheet("background-color: #1E1E1E;")

        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        title = QLabel("Change Password")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #FFFFFF;")
        layout.addWidget(title)

        input_style = """
            QLineEdit {
                background-color: #252525;
                border: 1px solid #333333;
                border-radius: 8px;
                padding: 10px 12px;
                color: #FFFFFF;
                font-size: 13px;
            }
            QLineEdit:focus { border-color: #5865F2; }
        """

        # Current password
        self.current_pwd = QLineEdit()
        self.current_pwd.setPlaceholderText("Current password")
        self.current_pwd.setEchoMode(QLineEdit.Password)
        self.current_pwd.setMinimumHeight(40)
        self.current_pwd.setStyleSheet(input_style)
        layout.addWidget(self.current_pwd)

        # New password
        self.new_pwd = QLineEdit()
        self.new_pwd.setPlaceholderText("New password (min 8 characters)")
        self.new_pwd.setEchoMode(QLineEdit.Password)
        self.new_pwd.setMinimumHeight(40)
        self.new_pwd.setStyleSheet(input_style)
        layout.addWidget(self.new_pwd)

        # Confirm new password
        self.confirm_pwd = QLineEdit()
        self.confirm_pwd.setPlaceholderText("Confirm new password")
        self.confirm_pwd.setEchoMode(QLineEdit.Password)
        self.confirm_pwd.setMinimumHeight(40)
        self.confirm_pwd.setStyleSheet(input_style)
        layout.addWidget(self.confirm_pwd)

        # Error label
        self.error_label = QLabel()
        self.error_label.setStyleSheet("color: #EF4444; font-size: 12px;")
        self.error_label.hide()
        layout.addWidget(self.error_label)

        layout.addStretch()

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(8)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setMinimumHeight(40)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #333333;
                border: none;
                border-radius: 8px;
                color: #FFFFFF;
                padding: 0 20px;
            }
            QPushButton:hover { background-color: #444444; }
        """)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        save_btn = QPushButton("Update Password")
        save_btn.setMinimumHeight(40)
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #5865F2;
                border: none;
                border-radius: 8px;
                color: #FFFFFF;
                font-weight: 600;
                padding: 0 20px;
            }
            QPushButton:hover { background-color: #4752C4; }
        """)
        save_btn.clicked.connect(self._change_password)
        btn_layout.addWidget(save_btn)

        layout.addLayout(btn_layout)

    def _change_password(self):
        current = self.current_pwd.text()
        new = self.new_pwd.text()
        confirm = self.confirm_pwd.text()

        if not current or not new or not confirm:
            self._show_error("Please fill in all fields")
            return

        if len(new) < 8:
            self._show_error("New password must be at least 8 characters")
            return

        if new != confirm:
            self._show_error("New passwords don't match")
            return

        # Verify current password
        success, _, _ = self.auth_service.authenticate(
            self.user_data.get('email', ''), current, False
        )

        if not success:
            self._show_error("Current password is incorrect")
            return

        # Update password
        try:
            from core.auth import PasswordHasher
            from data.db import get_connection

            password_hash, salt = PasswordHasher.hash_password(new)

            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE users SET password_hash = ?, password_salt = ? WHERE id = ?
            """, (password_hash, salt, self.user_data['id']))
            conn.commit()

            QMessageBox.information(self, "Success", "Password updated successfully.")
            self.accept()

        except Exception as e:
            logger.error(f"Error changing password: {e}")
            self._show_error(f"Failed to change password: {e}")

    def _show_error(self, message: str):
        self.error_label.setText(message)
        self.error_label.show()
