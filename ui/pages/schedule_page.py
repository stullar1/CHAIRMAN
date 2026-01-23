"""
CHAIRMAN - Schedule Page
Clean calendar with time slots and sliding QuickBook panel
"""
from __future__ import annotations

from datetime import datetime, date, time as dtime, timedelta

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea,
    QComboBox, QTimeEdit, QTextEdit, QCheckBox,
    QFrame, QPushButton, QGraphicsOpacityEffect
)

from ui.dialogs import StyledMessageBox
from PySide6.QtCore import Qt, QTime, QPropertyAnimation, QEasingCurve, QTimer, Property, QRect
from PySide6.QtGui import QFont

from config import PAYMENT_METHODS
from core.app_state import AppState
from core.logging_config import get_logger

logger = get_logger(__name__)

START_HOUR = 8
END_HOUR = 20


class TimeSlot(QFrame):
    """Individual time slot in the calendar."""

    def __init__(self, hour: int, minute: int = 0, parent=None):
        super().__init__(parent)
        self.hour = hour
        self.minute = minute
        self.appointment = None

        self.setMinimumHeight(72)
        self.setStyleSheet("""
            QFrame {
                background-color: transparent;
                border: none;
            }
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Time label
        time_str = datetime(2000, 1, 1, hour, minute).strftime("%I:%M %p")
        self.time_label = QLabel(time_str)
        self.time_label.setFixedWidth(80)
        self.time_label.setAlignment(Qt.AlignRight | Qt.AlignTop)
        self.time_label.setStyleSheet("""
            color: #555555;
            font-size: 11px;
            font-weight: 500;
            padding: 12px 16px 0 0;
            background: transparent;
        """)
        layout.addWidget(self.time_label)

        # Content area with left border
        self.content_area = QFrame()
        self.content_area.setStyleSheet("""
            QFrame {
                background-color: transparent;
                border-left: 1px solid #252525;
                border-bottom: 1px solid #1A1A1A;
            }
        """)
        self.content_layout = QVBoxLayout(self.content_area)
        self.content_layout.setContentsMargins(16, 8, 16, 8)
        self.content_layout.setSpacing(0)
        layout.addWidget(self.content_area, 1)

    def set_appointment(self, appt: dict, color: str = "#5865F2"):
        """Set appointment data for this slot."""
        self.appointment = appt

        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        card = QFrame()
        card.setObjectName("appt_card")
        card.setStyleSheet(f"""
            QFrame#appt_card {{
                background-color: {color}18;
                border: 1px solid {color}40;
                border-left: 3px solid {color};
                border-radius: 10px;
            }}
            QFrame#appt_card QLabel {{
                border: none;
            }}
        """)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(14, 10, 14, 10)
        card_layout.setSpacing(6)

        # Top row: client name and actions
        top_row = QHBoxLayout()
        top_row.setSpacing(8)

        client = QLabel(appt["client"])
        client.setStyleSheet("font-size: 13px; font-weight: 600; color: #FFFFFF; background: transparent;")
        top_row.addWidget(client)

        top_row.addStretch()

        # Quick actions
        toggle_btn = QPushButton("Mark Paid" if not appt["paid"] else "Paid ✓")
        toggle_btn.setFixedHeight(24)
        btn_color = "#22C55E" if appt["paid"] else color
        toggle_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {btn_color};
                border: none;
                border-radius: 5px;
                color: #FFFFFF;
                font-size: 10px;
                font-weight: 600;
                padding: 0 10px;
            }}
            QPushButton:hover {{
                background-color: {btn_color}DD;
            }}
        """)
        toggle_btn.setCursor(Qt.PointingHandCursor)
        appt_id = appt["appointment_id"]
        toggle_btn.clicked.connect(lambda: self._toggle_paid(appt_id))
        top_row.addWidget(toggle_btn)

        del_btn = QPushButton("×")
        del_btn.setFixedSize(24, 24)
        del_btn.setStyleSheet("""
            QPushButton {
                background-color: #1E1E1E;
                border: none;
                border-radius: 5px;
                color: #555555;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #EF4444;
                color: #FFFFFF;
            }
        """)
        del_btn.setCursor(Qt.PointingHandCursor)
        del_btn.clicked.connect(lambda: self._delete_appointment(appt_id))
        top_row.addWidget(del_btn)

        card_layout.addLayout(top_row)

        # Service and price
        service = QLabel(f"{appt['service']}  •  ${appt['service_price']:.2f}")
        service.setStyleSheet("font-size: 11px; color: #777777; background: transparent;")
        card_layout.addWidget(service)

        self.content_layout.addWidget(card)

    def _toggle_paid(self, appt_id: int):
        try:
            AppState.scheduler.toggle_paid(appt_id)
            parent = self.parent()
            while parent and not isinstance(parent, SchedulePage):
                parent = parent.parent()
            if parent:
                parent._load_appointments()
        except Exception as e:
            logger.error(f"Error toggling paid: {e}")

    def _delete_appointment(self, appt_id: int):
        confirmed = StyledMessageBox.question(
            self, "Delete Appointment",
            "Are you sure you want to delete this appointment?"
        )
        if confirmed:
            try:
                AppState.scheduler.delete(appt_id)
                parent = self.parent()
                while parent and not isinstance(parent, SchedulePage):
                    parent = parent.parent()
                if parent:
                    parent._load_appointments()
            except Exception as e:
                logger.error(f"Error deleting: {e}")

    def clear_appointment(self):
        """Clear appointment from slot."""
        self.appointment = None
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()


class QuickBookPanel(QFrame):
    """Sliding panel for quick booking."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("quickbook_panel")
        self._panel_width = 320
        self.setFixedWidth(self._panel_width)
        self._is_open = False

        self.setStyleSheet("""
            QFrame#quickbook_panel {
                background-color: #1A1A1A;
                border-left: 1px solid #252525;
            }
        """)

        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(0)

        # Header with close button
        header_row = QHBoxLayout()
        header_row.setSpacing(0)

        form_title = QLabel("Quick Book")
        form_title.setStyleSheet("""
            font-size: 18px;
            font-weight: 700;
            color: #FFFFFF;
            background: transparent;
        """)
        header_row.addWidget(form_title)

        header_row.addStretch()

        close_btn = QPushButton("×")
        close_btn.setFixedSize(32, 32)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #252525;
                border: none;
                border-radius: 6px;
                color: #888888;
                font-size: 18px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #333333;
                color: #FFFFFF;
            }
        """)
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.clicked.connect(self._request_close)
        header_row.addWidget(close_btn)

        layout.addLayout(header_row)

        form_subtitle = QLabel("Schedule a new appointment")
        form_subtitle.setStyleSheet("""
            font-size: 12px;
            color: #666666;
            background: transparent;
            padding-top: 4px;
            padding-bottom: 20px;
        """)
        layout.addWidget(form_subtitle)

        # Shared styles
        label_style = """
            font-size: 11px;
            font-weight: 600;
            color: #888888;
            background: transparent;
            padding-top: 16px;
            padding-bottom: 8px;
        """

        combo_style = """
            QComboBox {
                background-color: #252525;
                border: none;
                border-radius: 8px;
                padding: 12px 14px;
                color: #FFFFFF;
                font-size: 13px;
            }
            QComboBox:hover {
                background-color: #2A2A2A;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: center right;
                width: 30px;
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 6px solid #666666;
                margin-right: 10px;
            }
            QComboBox QAbstractItemView {
                background-color: #252525;
                border: 1px solid #333333;
                border-radius: 8px;
                selection-background-color: #5865F2;
                padding: 4px;
                outline: none;
            }
        """

        time_style = """
            QTimeEdit {
                background-color: #252525;
                border: none;
                border-radius: 8px;
                padding: 12px 14px;
                color: #FFFFFF;
                font-size: 13px;
            }
            QTimeEdit:hover {
                background-color: #2A2A2A;
            }
            QTimeEdit::up-button, QTimeEdit::down-button {
                subcontrol-origin: border;
                width: 20px;
                border: none;
                background: #333333;
                border-radius: 4px;
                margin: 2px;
            }
            QTimeEdit::up-button:hover, QTimeEdit::down-button:hover {
                background: #444444;
            }
            QTimeEdit::up-arrow {
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-bottom: 5px solid #888888;
            }
            QTimeEdit::down-arrow {
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 5px solid #888888;
            }
        """

        # Client
        client_label = QLabel("Client")
        client_label.setStyleSheet(label_style)
        layout.addWidget(client_label)

        self.client_combo = QComboBox()
        self.client_combo.setFixedHeight(44)
        self.client_combo.setStyleSheet(combo_style)
        layout.addWidget(self.client_combo)

        # Service
        service_label = QLabel("Service")
        service_label.setStyleSheet(label_style)
        layout.addWidget(service_label)

        self.service_combo = QComboBox()
        self.service_combo.setFixedHeight(44)
        self.service_combo.setStyleSheet(combo_style)
        layout.addWidget(self.service_combo)

        # Time
        time_label = QLabel("Time")
        time_label.setStyleSheet(label_style)
        layout.addWidget(time_label)

        self.time_edit = QTimeEdit(QTime(9, 0))
        self.time_edit.setDisplayFormat("h:mm AP")
        self.time_edit.setFixedHeight(44)
        self.time_edit.setStyleSheet(time_style)
        layout.addWidget(self.time_edit)

        # Notes
        notes_label = QLabel("Notes")
        notes_label.setStyleSheet(label_style)
        layout.addWidget(notes_label)

        self.notes_edit = QTextEdit()
        self.notes_edit.setFixedHeight(70)
        self.notes_edit.setPlaceholderText("Optional notes...")
        self.notes_edit.setStyleSheet("""
            QTextEdit {
                background-color: #252525;
                border: none;
                border-radius: 8px;
                padding: 12px 14px;
                color: #FFFFFF;
                font-size: 13px;
            }
            QTextEdit:hover {
                background-color: #2A2A2A;
            }
        """)
        layout.addWidget(self.notes_edit)

        # Payment section
        payment_label = QLabel("Payment")
        payment_label.setStyleSheet(label_style)
        layout.addWidget(payment_label)

        self.paid_checkbox = QCheckBox("Mark as Paid")
        self.paid_checkbox.setStyleSheet("""
            QCheckBox {
                color: #AAAAAA;
                font-size: 13px;
                background: transparent;
                spacing: 10px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 2px solid #444444;
                border-radius: 4px;
                background-color: transparent;
            }
            QCheckBox::indicator:hover {
                border-color: #5865F2;
            }
            QCheckBox::indicator:checked {
                background-color: #5865F2;
                border-color: #5865F2;
            }
        """)
        self.paid_checkbox.toggled.connect(self._on_paid_toggled)
        layout.addWidget(self.paid_checkbox)

        self.payment_combo = QComboBox()
        self.payment_combo.addItems(PAYMENT_METHODS)
        self.payment_combo.setFixedHeight(40)
        self.payment_combo.setEnabled(False)
        self.payment_combo.setStyleSheet(combo_style + """
            QComboBox {
                margin-top: 10px;
            }
            QComboBox:disabled {
                background-color: #1E1E1E;
                color: #555555;
            }
        """)
        layout.addWidget(self.payment_combo)

        layout.addStretch()

        # Book button
        self.book_btn = QPushButton("Book Appointment")
        self.book_btn.setFixedHeight(48)
        self.book_btn.setStyleSheet("""
            QPushButton {
                background-color: #5865F2;
                border: none;
                border-radius: 10px;
                color: #FFFFFF;
                font-weight: 600;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #4752C4;
            }
            QPushButton:pressed {
                background-color: #3C45A5;
            }
        """)
        self.book_btn.setCursor(Qt.PointingHandCursor)
        layout.addWidget(self.book_btn)

        # Clear button
        clear_btn = QPushButton("Clear Form")
        clear_btn.setFixedHeight(40)
        clear_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                border-radius: 8px;
                color: #666666;
                font-weight: 500;
                font-size: 13px;
                margin-top: 8px;
            }
            QPushButton:hover {
                background-color: #252525;
                color: #FFFFFF;
            }
        """)
        clear_btn.setCursor(Qt.PointingHandCursor)
        clear_btn.clicked.connect(self.clear_form)
        layout.addWidget(clear_btn)

    def _on_paid_toggled(self, checked: bool):
        self.payment_combo.setEnabled(checked)

    def _request_close(self):
        # Find parent schedule page and close panel
        parent = self.parent()
        while parent and not isinstance(parent, SchedulePage):
            parent = parent.parent()
        if parent:
            parent.toggle_quickbook()

    def clear_form(self):
        self.client_combo.setCurrentIndex(0)
        self.service_combo.setCurrentIndex(0)
        self.time_edit.setTime(QTime(9, 0))
        self.notes_edit.clear()
        self.paid_checkbox.setChecked(False)

    def load_clients(self, clients):
        self.client_combo.clear()
        if clients:
            for c in clients:
                self.client_combo.addItem(c.name, c.id)
        else:
            self.client_combo.addItem("No clients yet", None)

    def load_services(self, services):
        self.service_combo.clear()
        if services:
            for s in services:
                self.service_combo.addItem(f"{s.name}  •  ${s.price:.2f}", s.id)
        else:
            self.service_combo.addItem("No services yet", None)


class SchedulePage(QWidget):
    """Clean schedule page with time grid and sliding QuickBook panel."""

    COLORS = ["#5865F2", "#22C55E", "#F59E0B", "#EF4444", "#8B5CF6", "#EC4899", "#06B6D4"]

    def __init__(self):
        super().__init__()
        self._current_date = date.today()
        self._color_index = 0
        self._quickbook_open = False
        self._setup_ui()

        QTimer.singleShot(100, self._load_appointments)

    def _get_next_color(self) -> str:
        color = self.COLORS[self._color_index % len(self.COLORS)]
        self._color_index += 1
        return color

    def _setup_ui(self):
        # Main layout - no margins, we'll use a stacked approach
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Main content area (calendar)
        self.main_content = QWidget()
        self.main_content.setStyleSheet("background-color: #121212;")
        main_layout = QVBoxLayout(self.main_content)
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(0)

        # Header section
        header = QWidget()
        header.setStyleSheet("background: transparent;")
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 24)
        header_layout.setSpacing(16)

        # Title row with Quick Book button
        title_row = QHBoxLayout()
        title_row.setSpacing(16)

        page_title = QLabel("Schedule")
        page_title.setStyleSheet("""
            font-size: 26px;
            font-weight: 700;
            color: #FFFFFF;
            background: transparent;
        """)
        title_row.addWidget(page_title)

        title_row.addStretch()

        # Quick Book toggle button
        self.quickbook_btn = QPushButton("+ New Booking")
        self.quickbook_btn.setFixedHeight(40)
        self.quickbook_btn.setStyleSheet("""
            QPushButton {
                background-color: #5865F2;
                border: none;
                border-radius: 10px;
                color: #FFFFFF;
                font-weight: 600;
                padding: 0 20px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #4752C4;
            }
            QPushButton:pressed {
                background-color: #3C45A5;
            }
        """)
        self.quickbook_btn.setCursor(Qt.PointingHandCursor)
        self.quickbook_btn.clicked.connect(self.toggle_quickbook)
        title_row.addWidget(self.quickbook_btn)

        header_layout.addLayout(title_row)

        # Date navigation row
        nav_row = QHBoxLayout()
        nav_row.setSpacing(12)

        prev_btn = QPushButton("‹")
        prev_btn.setFixedSize(36, 36)
        prev_btn.setStyleSheet("""
            QPushButton {
                background-color: #1A1A1A;
                border: 1px solid #252525;
                border-radius: 8px;
                color: #888888;
                font-size: 18px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #252525;
                color: #FFFFFF;
                border-color: #333333;
            }
            QPushButton:pressed {
                background-color: #333333;
            }
        """)
        prev_btn.setCursor(Qt.PointingHandCursor)
        prev_btn.clicked.connect(self._prev_day)
        nav_row.addWidget(prev_btn)

        self.date_label = QLabel()
        self.date_label.setStyleSheet("""
            font-size: 16px;
            font-weight: 600;
            color: #FFFFFF;
            background: transparent;
            padding: 0 4px;
        """)
        self._update_date_label()
        nav_row.addWidget(self.date_label)

        next_btn = QPushButton("›")
        next_btn.setFixedSize(36, 36)
        next_btn.setStyleSheet("""
            QPushButton {
                background-color: #1A1A1A;
                border: 1px solid #252525;
                border-radius: 8px;
                color: #888888;
                font-size: 18px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #252525;
                color: #FFFFFF;
                border-color: #333333;
            }
            QPushButton:pressed {
                background-color: #333333;
            }
        """)
        next_btn.setCursor(Qt.PointingHandCursor)
        next_btn.clicked.connect(self._next_day)
        nav_row.addWidget(next_btn)

        nav_row.addSpacing(16)

        today_btn = QPushButton("Today")
        today_btn.setFixedHeight(36)
        today_btn.setStyleSheet("""
            QPushButton {
                background-color: #252525;
                border: none;
                border-radius: 8px;
                color: #AAAAAA;
                font-weight: 500;
                padding: 0 16px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #333333;
                color: #FFFFFF;
            }
        """)
        today_btn.setCursor(Qt.PointingHandCursor)
        today_btn.clicked.connect(self._go_to_today)
        nav_row.addWidget(today_btn)

        nav_row.addStretch()

        header_layout.addLayout(nav_row)
        main_layout.addWidget(header)

        # Stats cards row
        stats_row = QHBoxLayout()
        stats_row.setSpacing(16)

        # Appointments count card
        appt_card = QFrame()
        appt_card.setFixedHeight(90)
        appt_card.setStyleSheet("""
            QFrame {
                background-color: #1A1A1A;
                border: 1px solid #252525;
                border-radius: 12px;
            }
        """)
        appt_card_layout = QVBoxLayout(appt_card)
        appt_card_layout.setContentsMargins(20, 14, 20, 14)
        appt_card_layout.setSpacing(2)

        appt_title = QLabel("APPOINTMENTS")
        appt_title.setStyleSheet("color: #555555; font-size: 10px; font-weight: 600; letter-spacing: 1px; border: none;")
        appt_card_layout.addWidget(appt_title)

        self.appt_count = QLabel("0")
        self.appt_count.setStyleSheet("color: #FFFFFF; font-size: 28px; font-weight: 700; border: none;")
        appt_card_layout.addWidget(self.appt_count)

        stats_row.addWidget(appt_card)

        # Revenue card
        rev_card = QFrame()
        rev_card.setFixedHeight(90)
        rev_card.setStyleSheet("""
            QFrame {
                background-color: #1A1A1A;
                border: 1px solid #252525;
                border-radius: 12px;
            }
        """)
        rev_card_layout = QVBoxLayout(rev_card)
        rev_card_layout.setContentsMargins(20, 14, 20, 14)
        rev_card_layout.setSpacing(2)

        rev_title = QLabel("TODAY'S REVENUE")
        rev_title.setStyleSheet("color: #555555; font-size: 10px; font-weight: 600; letter-spacing: 1px; border: none;")
        rev_card_layout.addWidget(rev_title)

        self.revenue_label = QLabel("$0")
        self.revenue_label.setStyleSheet("color: #22C55E; font-size: 28px; font-weight: 700; border: none;")
        rev_card_layout.addWidget(self.revenue_label)

        stats_row.addWidget(rev_card)
        stats_row.addStretch()

        main_layout.addLayout(stats_row)
        main_layout.addSpacing(20)

        # Time grid
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet("""
            QScrollArea {
                background-color: #161616;
                border: 1px solid #1E1E1E;
                border-radius: 14px;
            }
            QScrollBar:vertical {
                background-color: transparent;
                width: 6px;
                margin: 8px 2px;
            }
            QScrollBar::handle:vertical {
                background-color: #333333;
                border-radius: 3px;
                min-height: 40px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #444444;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: transparent;
            }
        """)

        self.time_grid = QWidget()
        self.time_grid.setStyleSheet("background-color: #161616;")
        self.time_layout = QVBoxLayout(self.time_grid)
        self.time_layout.setContentsMargins(8, 16, 8, 16)
        self.time_layout.setSpacing(0)

        self.time_slots = {}
        for hour in range(START_HOUR, END_HOUR + 1):
            slot = TimeSlot(hour, 0)
            self.time_slots[hour] = slot
            self.time_layout.addWidget(slot)

        self.time_layout.addStretch()
        scroll.setWidget(self.time_grid)
        main_layout.addWidget(scroll, 1)

        layout.addWidget(self.main_content, 1)

        # QuickBook sliding panel - starts hidden off-screen
        self.quickbook_panel = QuickBookPanel(self)
        self.quickbook_panel.book_btn.clicked.connect(self._book_appointment)
        self.quickbook_panel.move(self.width(), 0)  # Start off-screen
        self.quickbook_panel.hide()

        # Animation for sliding
        self.slide_animation = QPropertyAnimation(self.quickbook_panel, b"pos")
        self.slide_animation.setDuration(250)
        self.slide_animation.setEasingCurve(QEasingCurve.OutCubic)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Keep quickbook panel positioned correctly
        panel_width = self.quickbook_panel._panel_width
        if self._quickbook_open:
            self.quickbook_panel.move(self.width() - panel_width, 0)
        else:
            self.quickbook_panel.move(self.width(), 0)
        self.quickbook_panel.setFixedHeight(self.height())

    def toggle_quickbook(self):
        """Toggle the QuickBook panel visibility with animation."""
        panel_width = self.quickbook_panel._panel_width

        if self._quickbook_open:
            # Close panel - slide out to the right
            self.slide_animation.setStartValue(self.quickbook_panel.pos())
            self.slide_animation.setEndValue(self.quickbook_panel.pos() +
                                             type(self.quickbook_panel.pos())(panel_width, 0))
            self.slide_animation.finished.connect(self._on_panel_closed)
            self._quickbook_open = False
            self.quickbook_btn.setText("+ New Booking")
        else:
            # Open panel - slide in from the right
            self.quickbook_panel.setFixedHeight(self.height())
            self.quickbook_panel.move(self.width(), 0)
            self.quickbook_panel.show()
            self.quickbook_panel.raise_()

            # Load data
            self._load_panel_data()

            self.slide_animation.setStartValue(self.quickbook_panel.pos())
            self.slide_animation.setEndValue(self.quickbook_panel.pos() -
                                             type(self.quickbook_panel.pos())(panel_width, 0))
            try:
                self.slide_animation.finished.disconnect()
            except:
                pass
            self._quickbook_open = True
            self.quickbook_btn.setText("Close")

        self.slide_animation.start()

    def _on_panel_closed(self):
        self.quickbook_panel.hide()
        try:
            self.slide_animation.finished.disconnect(self._on_panel_closed)
        except:
            pass

    def _load_panel_data(self):
        """Load clients and services into the panel."""
        try:
            clients = AppState.client_service.all()
            self.quickbook_panel.load_clients(clients)
        except Exception as e:
            logger.error(f"Error loading clients: {e}")

        try:
            services = AppState.service_manager.all()
            self.quickbook_panel.load_services(services)
        except Exception as e:
            logger.error(f"Error loading services: {e}")

    def _update_date_label(self):
        if self._current_date == date.today():
            day_text = "Today"
        elif self._current_date == date.today() + timedelta(days=1):
            day_text = "Tomorrow"
        elif self._current_date == date.today() - timedelta(days=1):
            day_text = "Yesterday"
        else:
            day_text = self._current_date.strftime("%A")

        self.date_label.setText(f"{day_text}, {self._current_date.strftime('%B %d')}")

    def _prev_day(self):
        self._current_date -= timedelta(days=1)
        self._update_date_label()
        self._load_appointments()

    def _next_day(self):
        self._current_date += timedelta(days=1)
        self._update_date_label()
        self._load_appointments()

    def _go_to_today(self):
        self._current_date = date.today()
        self._update_date_label()
        self._load_appointments()

    def _load_appointments(self):
        for slot in self.time_slots.values():
            slot.clear_appointment()

        self._color_index = 0

        try:
            appointments = AppState.scheduler.list_for_date(self._current_date)

            total_revenue = 0
            for appt in appointments:
                start = datetime.fromisoformat(appt["start_time"])
                hour = start.hour

                if hour in self.time_slots:
                    color = self._get_next_color()
                    self.time_slots[hour].set_appointment(appt, color)

                total_revenue += appt["service_price"]

            count = len(appointments)
            self.appt_count.setText(str(count))
            self.revenue_label.setText(f"${total_revenue:.0f}")

        except Exception as e:
            logger.error(f"Error loading appointments: {e}")

    def _book_appointment(self):
        panel = self.quickbook_panel
        client_id = panel.client_combo.currentData()
        service_id = panel.service_combo.currentData()

        if not client_id or not service_id:
            StyledMessageBox.warning(self, "Missing Information", "Please select a client and service.")
            return

        try:
            qtime = panel.time_edit.time()
            start_dt = datetime.combine(
                self._current_date,
                dtime(qtime.hour(), qtime.minute())
            )

            AppState.scheduler.book(
                client_id=client_id,
                service_id=service_id,
                start=start_dt,
                paid=panel.paid_checkbox.isChecked(),
                payment_method=panel.payment_combo.currentText() if panel.paid_checkbox.isChecked() else "",
                notes=panel.notes_edit.toPlainText().strip()
            )

            StyledMessageBox.success(self, "Success", "Appointment booked successfully!")
            self._load_appointments()
            panel.clear_form()
            self.toggle_quickbook()  # Close panel after booking

        except Exception as e:
            logger.error(f"Error booking: {e}")
            StyledMessageBox.error(self, "Error", f"Failed to book appointment: {str(e)}")

    def refresh(self):
        """Refresh data when navigating to this page."""
        self._load_appointments()
