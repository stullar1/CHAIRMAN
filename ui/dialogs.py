"""
CHAIRMAN - Custom Styled Dialogs
Modern dark theme dialogs with blur effect
"""
from __future__ import annotations

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QGraphicsBlurEffect, QWidget, QApplication, QProgressBar,
    QTextEdit
)
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QRectF
from PySide6.QtGui import QColor, QPainter, QPainterPath, QFont

from config import VERSION

from core.sounds import SoundManager


class StyledMessageBox(QDialog):
    """Custom styled message box matching app theme."""

    # Message types
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    QUESTION = "question"
    SUCCESS = "success"

    def __init__(
        self,
        parent=None,
        title: str = "Message",
        message: str = "",
        msg_type: str = INFO,
        buttons: list[str] = None
    ):
        super().__init__(parent)

        self.msg_type = msg_type
        self.result_button = None
        self.sound_manager = SoundManager()

        # Play sound based on type
        if msg_type == self.ERROR:
            self.sound_manager.play("error")
        elif msg_type == self.WARNING:
            self.sound_manager.play("warning")
        elif msg_type == self.SUCCESS:
            self.sound_manager.play("success")
        else:
            self.sound_manager.play("popup")

        # Window setup
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setModal(True)
        self.setFixedWidth(380)

        if buttons is None:
            buttons = ["OK"] if msg_type != self.QUESTION else ["Yes", "No"]

        self._setup_ui(title, message, buttons)
        self._center_on_parent()

    def _setup_ui(self, title: str, message: str, buttons: list[str]):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Container
        container = QWidget()
        container.setObjectName("dialog_container")
        container.setStyleSheet("""
            QWidget#dialog_container {
                background-color: #1A1A1A;
                border: 1px solid #2A2A2A;
                border-radius: 12px;
            }
        """)

        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(24, 20, 24, 20)
        container_layout.setSpacing(16)

        # Header with icon and title
        header = QHBoxLayout()
        header.setSpacing(12)

        # Icon based on type
        icon_colors = {
            self.INFO: ("#5865F2", "ℹ"),
            self.WARNING: ("#F59E0B", "⚠"),
            self.ERROR: ("#EF4444", "✕"),
            self.QUESTION: ("#5865F2", "?"),
            self.SUCCESS: ("#22C55E", "✓"),
        }
        color, icon_text = icon_colors.get(self.msg_type, ("#5865F2", "ℹ"))

        icon = QLabel(icon_text)
        icon.setFixedSize(36, 36)
        icon.setAlignment(Qt.AlignCenter)
        icon.setStyleSheet(f"""
            background-color: {color}20;
            border-radius: 18px;
            color: {color};
            font-size: 18px;
            font-weight: bold;
        """)
        header.addWidget(icon)

        # Title
        title_label = QLabel(title)
        title_label.setStyleSheet("""
            color: #FFFFFF;
            font-size: 16px;
            font-weight: 600;
        """)
        header.addWidget(title_label)
        header.addStretch()

        container_layout.addLayout(header)

        # Message
        msg_label = QLabel(message)
        msg_label.setWordWrap(True)
        msg_label.setStyleSheet("""
            color: #AAAAAA;
            font-size: 14px;
            line-height: 1.5;
            padding: 8px 0;
        """)
        container_layout.addWidget(msg_label)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        btn_layout.addStretch()

        for i, btn_text in enumerate(buttons):
            btn = QPushButton(btn_text)
            btn.setMinimumHeight(40)
            btn.setMinimumWidth(90)
            btn.setCursor(Qt.PointingHandCursor)

            # Primary button (last one) or Yes button
            is_primary = (i == len(buttons) - 1) or btn_text.lower() == "yes"
            is_danger = btn_text.lower() in ["delete", "remove", "yes"] and self.msg_type in [self.WARNING, self.ERROR]

            if is_danger:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #EF4444;
                        color: #FFFFFF;
                        border: none;
                        border-radius: 8px;
                        font-weight: 600;
                        padding: 0 20px;
                    }
                    QPushButton:hover { background-color: #DC2626; }
                    QPushButton:pressed { background-color: #B91C1C; }
                """)
            elif is_primary:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #5865F2;
                        color: #FFFFFF;
                        border: none;
                        border-radius: 8px;
                        font-weight: 600;
                        padding: 0 20px;
                    }
                    QPushButton:hover { background-color: #4752C4; }
                    QPushButton:pressed { background-color: #3C45A5; }
                """)
            else:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #252525;
                        color: #FFFFFF;
                        border: 1px solid #333333;
                        border-radius: 8px;
                        font-weight: 500;
                        padding: 0 20px;
                    }
                    QPushButton:hover { background-color: #333333; }
                    QPushButton:pressed { background-color: #1A1A1A; }
                """)

            btn.clicked.connect(lambda checked, t=btn_text: self._on_button_click(t))
            btn_layout.addWidget(btn)

        container_layout.addLayout(btn_layout)
        layout.addWidget(container)

    def _on_button_click(self, button_text: str):
        self.sound_manager.play("click")
        self.result_button = button_text
        if button_text.lower() in ["yes", "ok", "confirm", "delete", "remove"]:
            self.accept()
        else:
            self.reject()

    def _center_on_parent(self):
        if self.parent():
            parent_geo = self.parent().geometry()
            x = parent_geo.x() + (parent_geo.width() - self.width()) // 2
            y = parent_geo.y() + (parent_geo.height() - self.height()) // 2
            self.move(x, y)
        else:
            screen = QApplication.primaryScreen().geometry()
            x = (screen.width() - self.width()) // 2
            y = (screen.height() - self.height()) // 2
            self.move(x, y)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Draw shadow/background
        path = QPainterPath()
        path.addRoundedRect(QRectF(self.rect()), 12, 12)
        painter.fillPath(path, QColor(0, 0, 0, 100))

    @staticmethod
    def information(parent, title: str, message: str) -> bool:
        dialog = StyledMessageBox(parent, title, message, StyledMessageBox.INFO)
        return dialog.exec() == QDialog.Accepted

    @staticmethod
    def warning(parent, title: str, message: str) -> bool:
        dialog = StyledMessageBox(parent, title, message, StyledMessageBox.WARNING)
        return dialog.exec() == QDialog.Accepted

    @staticmethod
    def error(parent, title: str, message: str) -> bool:
        dialog = StyledMessageBox(parent, title, message, StyledMessageBox.ERROR)
        return dialog.exec() == QDialog.Accepted

    @staticmethod
    def question(parent, title: str, message: str) -> bool:
        dialog = StyledMessageBox(parent, title, message, StyledMessageBox.QUESTION)
        return dialog.exec() == QDialog.Accepted

    @staticmethod
    def success(parent, title: str, message: str) -> bool:
        dialog = StyledMessageBox(parent, title, message, StyledMessageBox.SUCCESS)
        return dialog.exec() == QDialog.Accepted


class UpdateDialog(QDialog):
    """Dialog for showing available updates and download progress."""

    def __init__(
        self,
        parent=None,
        new_version: str = "",
        release_notes: str = ""
    ):
        super().__init__(parent)

        self.new_version = new_version
        self.release_notes = release_notes
        self.sound_manager = SoundManager()
        self.sound_manager.play("notification")

        # Window setup
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setModal(True)
        self.setFixedWidth(450)

        self._setup_ui()
        self._center_on_parent()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Container
        container = QWidget()
        container.setObjectName("update_container")
        container.setStyleSheet("""
            QWidget#update_container {
                background-color: #1A1A1A;
                border: 1px solid #2A2A2A;
                border-radius: 12px;
            }
        """)

        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(24, 20, 24, 20)
        container_layout.setSpacing(16)

        # Header
        header = QHBoxLayout()
        header.setSpacing(12)

        # Update icon
        icon = QLabel("⬆")
        icon.setFixedSize(40, 40)
        icon.setAlignment(Qt.AlignCenter)
        icon.setStyleSheet("""
            background-color: #22C55E20;
            border-radius: 20px;
            color: #22C55E;
            font-size: 20px;
            font-weight: bold;
        """)
        header.addWidget(icon)

        # Title and version info
        title_container = QVBoxLayout()
        title_container.setSpacing(2)

        title_label = QLabel("Update Available!")
        title_label.setStyleSheet("""
            color: #FFFFFF;
            font-size: 18px;
            font-weight: 600;
        """)
        title_container.addWidget(title_label)

        version_label = QLabel(f"v{VERSION} → v{self.new_version}")
        version_label.setStyleSheet("""
            color: #22C55E;
            font-size: 12px;
            font-weight: 500;
        """)
        title_container.addWidget(version_label)

        header.addLayout(title_container)
        header.addStretch()

        container_layout.addLayout(header)

        # Release notes
        notes_label = QLabel("What's New:")
        notes_label.setStyleSheet("""
            color: #888888;
            font-size: 12px;
            font-weight: 500;
            margin-top: 8px;
        """)
        container_layout.addWidget(notes_label)

        notes_text = QTextEdit()
        notes_text.setReadOnly(True)
        notes_text.setPlainText(self.release_notes or "Bug fixes and improvements.")
        notes_text.setMaximumHeight(120)
        notes_text.setStyleSheet("""
            QTextEdit {
                background-color: #121212;
                border: 1px solid #2A2A2A;
                border-radius: 8px;
                color: #AAAAAA;
                font-size: 13px;
                padding: 10px;
            }
        """)
        container_layout.addWidget(notes_text)

        # Progress bar (hidden initially)
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("Downloading... %p%")
        self.progress_bar.hide()
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                background-color: #252525;
                border: none;
                border-radius: 6px;
                height: 24px;
                text-align: center;
                color: #FFFFFF;
                font-weight: 500;
            }
            QProgressBar::chunk {
                background-color: #5865F2;
                border-radius: 6px;
            }
        """)
        container_layout.addWidget(self.progress_bar)

        # Status label (for download progress)
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("""
            color: #888888;
            font-size: 12px;
        """)
        self.status_label.hide()
        container_layout.addWidget(self.status_label)

        # Buttons
        self.btn_layout = QHBoxLayout()
        self.btn_layout.setSpacing(10)
        self.btn_layout.addStretch()

        self.later_btn = QPushButton("Later")
        self.later_btn.setMinimumHeight(40)
        self.later_btn.setMinimumWidth(90)
        self.later_btn.setCursor(Qt.PointingHandCursor)
        self.later_btn.setStyleSheet("""
            QPushButton {
                background-color: #252525;
                color: #FFFFFF;
                border: 1px solid #333333;
                border-radius: 8px;
                font-weight: 500;
                padding: 0 20px;
            }
            QPushButton:hover { background-color: #333333; }
            QPushButton:pressed { background-color: #1A1A1A; }
        """)
        self.later_btn.clicked.connect(self.reject)
        self.btn_layout.addWidget(self.later_btn)

        self.update_btn = QPushButton("Update Now")
        self.update_btn.setMinimumHeight(40)
        self.update_btn.setMinimumWidth(120)
        self.update_btn.setCursor(Qt.PointingHandCursor)
        self.update_btn.setStyleSheet("""
            QPushButton {
                background-color: #22C55E;
                color: #FFFFFF;
                border: none;
                border-radius: 8px;
                font-weight: 600;
                padding: 0 20px;
            }
            QPushButton:hover { background-color: #16A34A; }
            QPushButton:pressed { background-color: #15803D; }
        """)
        self.update_btn.clicked.connect(self._on_update_click)
        self.btn_layout.addWidget(self.update_btn)

        container_layout.addLayout(self.btn_layout)
        layout.addWidget(container)

    def _on_update_click(self):
        self.sound_manager.play("click")
        self.accept()

    def show_progress(self):
        """Show the progress bar for downloading."""
        self.progress_bar.show()
        self.status_label.show()
        self.later_btn.hide()
        self.update_btn.setEnabled(False)
        self.update_btn.setText("Downloading...")

    def set_progress(self, value: int):
        """Update the progress bar value."""
        self.progress_bar.setValue(value)

    def set_status(self, status: str):
        """Update the status label."""
        self.status_label.setText(status)

    def download_complete(self):
        """Called when download is complete."""
        self.progress_bar.setValue(100)
        self.progress_bar.setFormat("Download Complete!")
        self.status_label.setText("Installing update...")
        self.sound_manager.play("success")

    def _center_on_parent(self):
        if self.parent():
            parent_geo = self.parent().geometry()
            x = parent_geo.x() + (parent_geo.width() - self.width()) // 2
            y = parent_geo.y() + (parent_geo.height() - self.height()) // 2
            self.move(x, y)
        else:
            screen = QApplication.primaryScreen().geometry()
            x = (screen.width() - self.width()) // 2
            y = (screen.height() - self.height()) // 2
            self.move(x, y)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        path = QPainterPath()
        path.addRoundedRect(QRectF(self.rect()), 12, 12)
        painter.fillPath(path, QColor(0, 0, 0, 100))
