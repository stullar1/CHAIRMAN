"""
CHAIRMAN - Professional Status Bar
Real-time information and system status
"""
from __future__ import annotations

from datetime import datetime

from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont


class StatusBar(QWidget):
    """
    Professional status bar with real-time information.

    Features:
    - Current page indicator
    - Live clock
    - System status
    """

    def __init__(self):
        """Initialize the status bar."""
        super().__init__()
        self.setObjectName("StatusBar")
        self.setFixedHeight(36)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(22, 0, 22, 0)
        layout.setSpacing(16)

        # Current page indicator
        self.page_label = QLabel("Viewing Schedule")
        self.page_label.setStyleSheet("""
            color: #B0B0B0;
            font-size: 12px;
            font-weight: 500;
            background: transparent;
        """)
        layout.addWidget(self.page_label)

        # Separator
        sep1 = QLabel("•")
        sep1.setStyleSheet("color: #404040; background: transparent;")
        layout.addWidget(sep1)

        # Status indicator
        self.status_label = QLabel("🟢 Online")
        self.status_label.setStyleSheet("""
            color: #57F287;
            font-size: 12px;
            font-weight: 500;
            background: transparent;
        """)
        layout.addWidget(self.status_label)

        layout.addStretch()

        # Live clock
        self.clock_label = QLabel()
        self.clock_label.setStyleSheet("""
            color: #808080;
            font-size: 12px;
            font-family: 'Courier New', monospace;
            background: transparent;
        """)
        layout.addWidget(self.clock_label)

        # Update clock every second
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update_clock)
        self.timer.start(1000)
        self._update_clock()

    def _update_clock(self):
        """Update the clock display."""
        now = datetime.now()
        time_str = now.strftime("%I:%M:%S %p")
        date_str = now.strftime("%b %d, %Y")
        self.clock_label.setText(f"{time_str}  •  {date_str}")

    def set_message(self, text: str) -> None:
        """
        Set the page indicator message.

        Args:
            text: The message to display
        """
        self.page_label.setText(text)

    def set_status(self, status: str, color: str = "#57F287"):
        """Set the status indicator."""
        self.status_label.setText(status)
        self.status_label.setStyleSheet(f"""
            color: {color};
            font-size: 12px;
            font-weight: 500;
            background: transparent;
        """)
