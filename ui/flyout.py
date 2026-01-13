from __future__ import annotations
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QDateTimeEdit, QTextEdit, QCheckBox
)
from PySide6.QtCore import Qt, Signal, QDateTime
from datetime import datetime

from core.app_state import AppState


class Flyout(QWidget):
    booked = Signal()  # emitted after successful booking

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("flyout")

        root = QVBoxLayout(self)
        root.setContentsMargins(14, 14, 14, 14)
        root.setSpacing(10)

        title = QLabel("Quick Book")
        title.setObjectName("flyout_title")

        subtitle = QLabel("Book an appointment fast. No extra screens.")
        subtitle.setObjectName("muted")

        root.addWidget(title)
        root.addWidget(subtitle)

        # Client
        root.addWidget(QLabel("Client"))
        self.client_cb = QComboBox()
        root.addWidget(self.client_cb)

        # Service
        root.addWidget(QLabel("Service"))
        self.service_cb = QComboBox()
        root.addWidget(self.service_cb)

        # Time
        root.addWidget(QLabel("Start time"))
        self.dt = QDateTimeEdit()
        self.dt.setDisplayFormat("yyyy-MM-dd  hh:mm AP")
        self.dt.setCalendarPopup(True)
        self.dt.setDateTime(QDateTime.currentDateTime())
        root.addWidget(self.dt)

        # Notes
        root.addWidget(QLabel("Notes (optional)"))
        self.notes = QTextEdit()
        self.notes.setFixedHeight(90)
        root.addWidget(self.notes)

        # Paid row
        paid_row = QHBoxLayout()
        self.paid_chk = QCheckBox("Mark as paid")
        self.method_cb = QComboBox()
        self.method_cb.addItems(["", "Cash", "Zelle", "Cash App", "Venmo", "Other"])
        self.method_cb.setEnabled(False)

        self.paid_chk.toggled.connect(self.method_cb.setEnabled)

        paid_row.addWidget(self.paid_chk)
        paid_row.addStretch()
        paid_row.addWidget(QLabel("Method"))
        paid_row.addWidget(self.method_cb)
        root.addLayout(paid_row)

        # Buttons
        btn_row = QHBoxLayout()
        btn_row.addStretch()

        self.book_btn = QPushButton("Book Appointment")
        self.book_btn.setObjectName("primary")
        self.book_btn.clicked.connect(self._book)

        btn_row.addWidget(self.book_btn)
        root.addLayout(btn_row)

        root.addStretch()

        self.reload()

    def reload(self):
        self.client_cb.clear()
        self.service_cb.clear()

        clients = AppState.clients.all()
        services = AppState.services.all()

        for c in clients:
            self.client_cb.addItem(f"{c.name}  •  {c.phone}", c.id)

        for s in services:
            self.service_cb.addItem(f"{s.name}  •  ${s.price:.2f}  •  {s.duration_minutes}m", s.id)

        self.book_btn.setEnabled(self.client_cb.count() > 0 and self.service_cb.count() > 0)

    def _book(self):
        if self.client_cb.currentIndex() < 0 or self.service_cb.currentIndex() < 0:
            return

        client_id = int(self.client_cb.currentData())
        service_id = int(self.service_cb.currentData())

        qdt = self.dt.dateTime()
        start = qdt.toPython()  # datetime

        paid = self.paid_chk.isChecked()
        method = self.method_cb.currentText().strip() if paid else ""
        notes = self.notes.toPlainText().strip()

        appt_id = AppState.scheduler.book(
            client_id=client_id,
            service_id=service_id,
            start=start,
            paid=paid,
            payment_method=method,
            notes=notes,
        )

        if appt_id is None:
            # simple failure handling (no popup spam yet)
            self.book_btn.setText("Time Not Available")
            self.book_btn.setEnabled(False)
            self.book_btn.repaint()
            # reset after short user-visible “feedback”
            self.book_btn.setText("Book Appointment")
            self.book_btn.setEnabled(True)
            return

        self.notes.clear()
        self.paid_chk.setChecked(False)
        self.method_cb.setCurrentIndex(0)
        self.booked.emit()
