"""
CHAIRMAN - Dashboard Home Page
Overview with stats, quick actions, and today's summary
"""
from __future__ import annotations

from datetime import datetime, date
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QGridLayout, QScrollArea, QSizePolicy
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QFont


class StatCard(QFrame):
    """Card widget for displaying a statistic."""

    def __init__(self, title: str, value: str, subtitle: str = "", icon: str = "", color: str = "#5865F2"):
        super().__init__()

        self.setObjectName("stat_card")
        self.setStyleSheet(f"""
            QFrame#stat_card {{
                background-color: #1A1A1A;
                border: 1px solid #2A2A2A;
                border-radius: 12px;
                padding: 16px;
            }}
            QFrame#stat_card:hover {{
                border-color: {color}40;
                background-color: #1E1E1E;
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(8)

        # Header with icon
        header = QHBoxLayout()
        header.setSpacing(8)

        if icon:
            icon_label = QLabel(icon)
            icon_label.setStyleSheet(f"""
                font-size: 20px;
                color: {color};
            """)
            header.addWidget(icon_label)

        title_label = QLabel(title)
        title_label.setStyleSheet("""
            color: #888888;
            font-size: 12px;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 1px;
        """)
        header.addWidget(title_label)
        header.addStretch()

        layout.addLayout(header)

        # Value
        self.value_label = QLabel(value)
        self.value_label.setStyleSheet(f"""
            color: #FFFFFF;
            font-size: 32px;
            font-weight: 700;
        """)
        layout.addWidget(self.value_label)

        # Subtitle
        if subtitle:
            subtitle_label = QLabel(subtitle)
            subtitle_label.setStyleSheet("""
                color: #666666;
                font-size: 12px;
            """)
            layout.addWidget(subtitle_label)

    def set_value(self, value: str):
        self.value_label.setText(value)


class QuickActionButton(QPushButton):
    """Styled quick action button."""

    def __init__(self, text: str, icon: str = "", color: str = "#5865F2"):
        super().__init__(f"{icon}  {text}" if icon else text)

        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumHeight(50)
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: #1A1A1A;
                color: #FFFFFF;
                border: 1px solid #2A2A2A;
                border-radius: 10px;
                font-size: 14px;
                font-weight: 500;
                padding: 12px 20px;
                text-align: left;
            }}
            QPushButton:hover {{
                background-color: {color}20;
                border-color: {color}60;
            }}
            QPushButton:pressed {{
                background-color: {color}30;
            }}
        """)


class AppointmentItem(QFrame):
    """Widget for displaying an appointment in the list."""

    def __init__(self, time: str, client: str, service: str, status: str = "scheduled"):
        super().__init__()

        self.setStyleSheet("""
            QFrame {
                background-color: #1A1A1A;
                border: 1px solid #252525;
                border-radius: 8px;
                padding: 8px;
            }
            QFrame:hover {
                background-color: #1E1E1E;
            }
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(12)

        # Time
        time_label = QLabel(time)
        time_label.setFixedWidth(60)
        time_label.setStyleSheet("""
            color: #5865F2;
            font-size: 14px;
            font-weight: 600;
        """)
        layout.addWidget(time_label)

        # Client and service
        info_layout = QVBoxLayout()
        info_layout.setSpacing(2)

        client_label = QLabel(client)
        client_label.setStyleSheet("""
            color: #FFFFFF;
            font-size: 14px;
            font-weight: 500;
        """)
        info_layout.addWidget(client_label)

        service_label = QLabel(service)
        service_label.setStyleSheet("""
            color: #666666;
            font-size: 12px;
        """)
        info_layout.addWidget(service_label)

        layout.addLayout(info_layout, 1)

        # Status indicator
        status_colors = {
            "scheduled": "#5865F2",
            "completed": "#22C55E",
            "cancelled": "#EF4444",
            "in_progress": "#F59E0B"
        }
        color = status_colors.get(status, "#5865F2")

        status_dot = QLabel("●")
        status_dot.setStyleSheet(f"color: {color}; font-size: 10px;")
        layout.addWidget(status_dot)


class DashboardPage(QWidget):
    """Dashboard home page with stats and quick actions."""

    # Signals for quick actions
    new_appointment_clicked = Signal()
    add_client_clicked = Signal()
    view_schedule_clicked = Signal()
    view_finances_clicked = Signal()

    def __init__(self):
        super().__init__()
        self._setup_ui()

        # Refresh timer
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_data)
        self.refresh_timer.start(60000)  # Refresh every minute

    def _setup_ui(self):
        # Main layout with scroll
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                background-color: #1A1A1A;
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background-color: #333333;
                border-radius: 4px;
                min-height: 30px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #444444;
            }
        """)

        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(32, 24, 32, 24)
        layout.setSpacing(24)

        # Greeting
        self.greeting_label = QLabel()
        self.greeting_label.setStyleSheet("""
            color: #FFFFFF;
            font-size: 28px;
            font-weight: 700;
        """)
        layout.addWidget(self.greeting_label)

        self.date_label = QLabel()
        self.date_label.setStyleSheet("""
            color: #666666;
            font-size: 14px;
            margin-top: -8px;
        """)
        layout.addWidget(self.date_label)

        layout.addSpacing(8)

        # Stats cards
        stats_layout = QGridLayout()
        stats_layout.setSpacing(16)

        self.appointments_card = StatCard(
            "Today's Appointments", "0",
            icon="📅", color="#5865F2"
        )
        stats_layout.addWidget(self.appointments_card, 0, 0)

        self.revenue_today_card = StatCard(
            "Today's Revenue", "$0",
            icon="💰", color="#22C55E"
        )
        stats_layout.addWidget(self.revenue_today_card, 0, 1)

        self.total_clients_card = StatCard(
            "Total Clients", "0",
            icon="👥", color="#F59E0B"
        )
        stats_layout.addWidget(self.total_clients_card, 0, 2)

        self.weekly_revenue_card = StatCard(
            "This Week", "$0",
            icon="📊", color="#8B5CF6"
        )
        stats_layout.addWidget(self.weekly_revenue_card, 0, 3)

        layout.addLayout(stats_layout)

        # Quick actions section
        actions_label = QLabel("Quick Actions")
        actions_label.setStyleSheet("""
            color: #FFFFFF;
            font-size: 18px;
            font-weight: 600;
            margin-top: 8px;
        """)
        layout.addWidget(actions_label)

        actions_layout = QGridLayout()
        actions_layout.setSpacing(12)

        new_apt_btn = QuickActionButton("New Appointment", "📅", "#5865F2")
        new_apt_btn.clicked.connect(self.new_appointment_clicked.emit)
        actions_layout.addWidget(new_apt_btn, 0, 0)

        add_client_btn = QuickActionButton("Add Client", "👤", "#22C55E")
        add_client_btn.clicked.connect(self.add_client_clicked.emit)
        actions_layout.addWidget(add_client_btn, 0, 1)

        view_schedule_btn = QuickActionButton("View Schedule", "📋", "#F59E0B")
        view_schedule_btn.clicked.connect(self.view_schedule_clicked.emit)
        actions_layout.addWidget(view_schedule_btn, 0, 2)

        view_finances_btn = QuickActionButton("View Finances", "💵", "#8B5CF6")
        view_finances_btn.clicked.connect(self.view_finances_clicked.emit)
        actions_layout.addWidget(view_finances_btn, 0, 3)

        layout.addLayout(actions_layout)

        # Today's appointments section
        appointments_header = QHBoxLayout()

        appointments_label = QLabel("Today's Schedule")
        appointments_label.setStyleSheet("""
            color: #FFFFFF;
            font-size: 18px;
            font-weight: 600;
            margin-top: 8px;
        """)
        appointments_header.addWidget(appointments_label)
        appointments_header.addStretch()

        view_all_btn = QPushButton("View All →")
        view_all_btn.setCursor(Qt.PointingHandCursor)
        view_all_btn.setStyleSheet("""
            QPushButton {
                color: #5865F2;
                background: transparent;
                border: none;
                font-size: 13px;
                font-weight: 500;
            }
            QPushButton:hover {
                color: #7289DA;
            }
        """)
        view_all_btn.clicked.connect(self.view_schedule_clicked.emit)
        appointments_header.addWidget(view_all_btn)

        layout.addLayout(appointments_header)

        # Appointments list container
        self.appointments_container = QVBoxLayout()
        self.appointments_container.setSpacing(8)
        layout.addLayout(self.appointments_container)

        layout.addStretch()

        scroll.setWidget(content)
        main_layout.addWidget(scroll)

        # Initial data load
        self._update_greeting()
        self.refresh_data()

    def _update_greeting(self):
        """Update greeting based on time of day."""
        hour = datetime.now().hour
        if hour < 12:
            greeting = "Good Morning"
        elif hour < 17:
            greeting = "Good Afternoon"
        else:
            greeting = "Good Evening"

        self.greeting_label.setText(f"{greeting}!")
        self.date_label.setText(datetime.now().strftime("%A, %B %d, %Y"))

    def refresh_data(self):
        """Refresh all dashboard data."""
        self._update_greeting()
        self._load_stats()
        self._load_todays_appointments()

    def _load_stats(self):
        """Load statistics - placeholder values for now."""
        # These will show placeholder values
        # Can be connected to actual database functions later
        self.appointments_card.set_value("0")
        self.revenue_today_card.set_value("$0")
        self.total_clients_card.set_value("0")
        self.weekly_revenue_card.set_value("$0")

    def _load_todays_appointments(self):
        """Load today's appointments list."""
        # Clear existing
        while self.appointments_container.count():
            item = self.appointments_container.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Show empty state for now
        empty_label = QLabel("No appointments scheduled for today")
        empty_label.setStyleSheet("""
            color: #666666;
            font-size: 14px;
            padding: 20px;
        """)
        empty_label.setAlignment(Qt.AlignCenter)
        self.appointments_container.addWidget(empty_label)

    def showEvent(self, event):
        """Refresh data when page becomes visible."""
        super().showEvent(event)
        self.refresh_data()
