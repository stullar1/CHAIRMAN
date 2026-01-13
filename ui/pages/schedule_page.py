from datetime import datetime, date, time as dtime

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QDateEdit, QComboBox, QTimeEdit, QTextEdit, QCheckBox,
    QFrame, QListWidget, QListWidgetItem, QMessageBox
)
from PySide6.QtCore import Qt, QDate

from core.app_state import AppState


class SchedulePage(QWidget):
    def __init__(self):
        super().__init__()

        self._day: date = date.today()

        root = QHBoxLayout(self)
        root.setContentsMargins(18, 18, 18, 12)
        root.setSpacing(16)

        # ================= LEFT: DAY VIEW =================
        left = QVBoxLayout()
        left.setSpacing(12)

        header = QWidget()
        header.setObjectName("page_header")
        header.setProperty("class", "page_header")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(16, 14, 16, 14)

        self.title = QLabel("Schedule")
        self.title.setProperty("class", "page_title")
        self.title.setObjectName("page_title")

        header_layout.addWidget(self.title)
        header_layout.addStretch()

        self.date_picker = QDateEdit(QDate.currentDate())
        self.date_picker.setCalendarPopup(True)
        self.date_picker.dateChanged.connect(self._on_date_changed)

        self.new_btn = QPushButton("New Appointment")
        self.new_btn.setObjectName("primary")
        self.new_btn.clicked.connect(self._focus_quick_book)

        header_layout.addWidget(self.date_picker)
        header_layout.addSpacing(10)
        header_layout.addWidget(self.new_btn)

        left.addWidget(header)

        self.list_box = QFrame()
        self.list_box.setProperty("class", "card")
        self.list_box.setObjectName("card")
        list_layout = QVBoxLayout(self.list_box)
        list_layout.setContentsMargins(16, 16, 16, 16)
        list_layout.setSpacing(10)

        self.day_label = QLabel("")
        self.day_label.setObjectName("muted")
        self.day_label.setProperty("class", "subtle")
        list_layout.addWidget(self.day_label)

        self.appt_list = QListWidget()
        self.appt_list.setFixedHeight(420)
        list_layout.addWidget(self.appt_list)

        self.empty = QLabel("")
        self.empty.setProperty("class", "subtle")
        self.empty.setStyleSheet("color: rgba(230,230,230,130);")
        list_layout.addWidget(self.empty)

        left.addWidget(self.list_box, 1)

        self.stats = QLabel("")
        self.stats.setProperty("class", "subtle")
        self.stats.setStyleSheet("color: rgba(230,230,230,140); font-size: 12px;")
        left.addWidget(self.stats)

        root.addLayout(left, 1)

        # ================= RIGHT: QUICK BOOK =================
        right = QVBoxLayout()
        right.setSpacing(12)

        self.quick = QFrame()
        self.quick.setProperty("class", "card")
        self.quick.setObjectName("card")
        ql = QVBoxLayout(self.quick)
        ql.setContentsMargins(16, 16, 16, 16)
        ql.setSpacing(10)

        q_title = QLabel("Quick Book")
        q_title.setStyleSheet("font-size: 16px; font-weight: 650; color: #FFFFFF;")
        q_sub = QLabel("Book fast. No extra screens.")
        q_sub.setProperty("class", "subtle")
        q_sub.setStyleSheet("color: rgba(230,230,230,130);")
        ql.addWidget(q_title)
        ql.addWidget(q_sub)

        ql.addSpacing(8)

        # Client
        ql.addWidget(self._label("Client"))
        self.client_combo = QComboBox()
        ql.addWidget(self.client_combo)

        # Service
        ql.addWidget(self._label("Service"))
        self.service_combo = QComboBox()
        ql.addWidget(self.service_combo)

        # Time
        ql.addWidget(self._label("Start time"))
        self.time_edit = QTimeEdit()
        self.time_edit.setDisplayFormat("h:mm AP")
        self.time_edit.setTime(self._default_time())
        ql.addWidget(self.time_edit)

        # Notes
        ql.addWidget(self._label("Notes (optional)"))
        self.notes = QTextEdit()
        self.notes.setFixedHeight(90)
        ql.addWidget(self.notes)

        # Paid + Method
        row = QHBoxLayout()
        self.paid = QCheckBox("Mark as paid")
        self.method = QComboBox()
        self.method.addItems(["Cash", "Card (manual)", "Cash App", "Zelle", "Venmo", "Other"])
        row.addWidget(self.paid)
        row.addStretch()
        row.addWidget(self._label("Method"))
        row.addWidget(self.method)
        ql.addLayout(row)

        ql.addSpacing(8)

        self.book_btn = QPushButton("Book Appointment")
        self.book_btn.setObjectName("primary")
        self.book_btn.clicked.connect(self._book)
        ql.addWidget(self.book_btn, alignment=Qt.AlignRight)

        right.addWidget(self.quick)
        right.addStretch()

        root.addLayout(right)

        self.reload()
        self.load_day()

    def _label(self, text: str) -> QLabel:
        lab = QLabel(text)
        lab.setStyleSheet("color: rgba(230,230,230,160); font-size: 12px;")
        return lab

    def _default_time(self):
        # next half-hour
        now = datetime.now()
        minute = 30 if now.minute < 30 else 0
        hour = now.hour if now.minute < 30 else (now.hour + 1) % 24
        from PySide6.QtCore import QTime
        return QTime(hour, minute)

    def _on_date_changed(self, qdate: QDate):
        self._day = qdate.toPython()
        self.load_day()

    def _focus_quick_book(self):
        # This is what "New Appointment" should do: bring you to booking
        self.client_combo.setFocus()
        self.quick.setStyleSheet("")  # keep it theme-driven, but allows future pulse animation if you want

    def reload(self):
        # populate combos
        self.client_combo.clear()
        self.service_combo.clear()

        clients = AppState.clients.all()
        services = AppState.services.all()

        # Store IDs in itemData so we don’t rely on index
        for c in clients:
            self.client_combo.addItem(c.name, getattr(c, "id", None))

        for s in services:
            label = f"{s.name} • ${getattr(s, 'price', getattr(s, 'cost', 0))}"
            self.service_combo.addItem(label, getattr(s, "id", None))

    def load_day(self):
        self.day_label.setText(self._day.strftime("%A, %B %d, %Y"))
        self.appt_list.clear()

        appts = AppState.scheduler.list_for_date(self._day)

        collected = 0.0
        scheduled = 0.0

        if not appts:
            self.empty.setText("No appointments yet. Use Quick Book →")
        else:
            self.empty.setText("")

            # Expect scheduler returns list of dicts like:
            # { "client": "John", "service": "Haircut", "start": datetime, "paid": bool, "service_price": float }
            for a in appts:
                start = a.get("start")
                if isinstance(start, datetime):
                    t = start.strftime("%I:%M %p").lstrip("0")
                else:
                    t = "—"

                paid = a.get("paid", False)
                price = float(a.get("service_price", 0) or 0)

                scheduled += price
                if paid:
                    collected += price

                client = a.get("client", "Client")
                service = a.get("service", "Service")

                item = QListWidgetItem(f"{t}  •  {client}  •  {service}  •  ${price:.2f}")
                if paid:
                    item.setForeground(Qt.green)
                self.appt_list.addItem(item)

        self.stats.setText(f"Collected: ${collected:.2f}   •   Scheduled value: ${scheduled:.2f}")

    def _book(self):
        # basic validation
        if self.client_combo.count() == 0:
            QMessageBox.warning(self, "No clients", "Add a client first (Clients page).")
            return
        if self.service_combo.count() == 0:
            QMessageBox.warning(self, "No services", "Add a service first (Services page).")
            return

        client_id = self.client_combo.currentData()
        service_id = self.service_combo.currentData()

        # Build datetime
        qtime = self.time_edit.time()
        start_dt = datetime.combine(self._day, dtime(qtime.hour(), qtime.minute()))

        notes = self.notes.toPlainText().strip()
        paid = self.paid.isChecked()
        method = self.method.currentText()

        try:
            # Your scheduler should implement this signature (or close to it)
            AppState.scheduler.book(client_id, service_id, start_dt, notes=notes, paid=paid, method=method)
        except TypeError:
            # fallback if your scheduler has older signature
            AppState.scheduler.book(client_id, service_id, start_dt)

        # reset form a bit
        self.notes.clear()
        self.paid.setChecked(False)
        self.time_edit.setTime(self._default_time())

        self.load_day()
