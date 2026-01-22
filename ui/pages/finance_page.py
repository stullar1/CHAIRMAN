"""
CHAIRMAN - Finance Page
Financial overview with charts, stats, and transaction history
"""
from __future__ import annotations

from datetime import datetime, timedelta

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QScrollArea, QLineEdit, QComboBox, QTableWidget,
    QTableWidgetItem, QHeaderView, QGraphicsOpacityEffect
)
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QTimer, QSequentialAnimationGroup
from PySide6.QtGui import QPainter, QColor, QPen, QFont, QLinearGradient

from core.logging_config import get_logger

logger = get_logger(__name__)


class MiniBarChart(QWidget):
    """Modern bar chart widget."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.data = []
        self.labels = []
        self.color = QColor("#5865F2")
        self.setMinimumHeight(220)

    def set_data(self, data: list, labels: list, color: str = "#5865F2"):
        self.data = data
        self.labels = labels
        self.color = QColor(color)
        self.update()

    def paintEvent(self, event):
        if not self.data:
            return

        painter = QPainter(self)
        if not painter.isActive():
            return

        try:
            painter.setRenderHint(QPainter.Antialiasing)

            width = self.width()
            height = self.height()
            padding = 50
            chart_height = height - padding * 2
            chart_width = width - padding * 2

            max_val = max(self.data) if self.data else 1
            if max_val == 0:
                max_val = 1

            bar_count = len(self.data)
            if bar_count == 0:
                painter.end()
                return

            bar_width = min(50, (chart_width - (bar_count - 1) * 12) / bar_count)
            total_bars_width = bar_count * bar_width + (bar_count - 1) * 12
            start_x = padding + (chart_width - total_bars_width) / 2

            for i, value in enumerate(self.data):
                bar_height = (value / max_val) * chart_height if max_val > 0 else 0
                x = start_x + i * (bar_width + 12)
                y = padding + chart_height - bar_height

                # Gradient fill for bars
                gradient = QLinearGradient(x, y, x, y + bar_height)
                gradient.setColorAt(0, self.color)
                gradient.setColorAt(1, self.color.darker(130))

                painter.setBrush(gradient)
                painter.setPen(Qt.NoPen)
                painter.drawRoundedRect(int(x), int(y), int(bar_width), int(bar_height), 6, 6)

                # Label
                if i < len(self.labels):
                    painter.setPen(QColor("#555555"))
                    font = QFont()
                    font.setPointSize(10)
                    painter.setFont(font)
                    painter.drawText(int(x), height - padding + 10, int(bar_width), 20,
                                   Qt.AlignCenter, self.labels[i])

                # Value
                painter.setPen(QColor("#FFFFFF"))
                font = QFont()
                font.setPointSize(11)
                font.setBold(True)
                painter.setFont(font)
                value_text = f"${value:,.0f}" if value >= 1000 else f"${value:.0f}"
                painter.drawText(int(x), int(y) - 10, int(bar_width), 20, Qt.AlignCenter, value_text)
        finally:
            painter.end()


class MiniLineChart(QWidget):
    """Modern line chart widget with area fill."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.data = []
        self.color = QColor("#22C55E")
        self.setMinimumHeight(140)

    def set_data(self, data: list, color: str = "#22C55E"):
        self.data = data
        self.color = QColor(color)
        self.update()

    def paintEvent(self, event):
        if len(self.data) < 2:
            return

        painter = QPainter(self)
        if not painter.isActive():
            return

        try:
            painter.setRenderHint(QPainter.Antialiasing)

            width = self.width()
            height = self.height()
            padding = 25

            max_val = max(self.data) if self.data else 1
            min_val = min(self.data) if self.data else 0
            val_range = max_val - min_val if max_val != min_val else 1

            points = []
            for i, value in enumerate(self.data):
                x = padding + (i / (len(self.data) - 1)) * (width - padding * 2)
                y = padding + (1 - (value - min_val) / val_range) * (height - padding * 2)
                points.append((x, y))

            # Draw area fill
            from PySide6.QtGui import QPolygonF
            from PySide6.QtCore import QPointF

            polygon_points = [QPointF(points[0][0], height - padding)]
            for x, y in points:
                polygon_points.append(QPointF(x, y))
            polygon_points.append(QPointF(points[-1][0], height - padding))

            gradient = QLinearGradient(0, padding, 0, height - padding)
            gradient.setColorAt(0, QColor(self.color.red(), self.color.green(), self.color.blue(), 50))
            gradient.setColorAt(1, QColor(self.color.red(), self.color.green(), self.color.blue(), 10))

            painter.setBrush(gradient)
            painter.setPen(Qt.NoPen)
            painter.drawPolygon(QPolygonF(polygon_points))

            # Draw line
            pen = QPen(self.color, 3)
            pen.setCapStyle(Qt.RoundCap)
            pen.setJoinStyle(Qt.RoundJoin)
            painter.setPen(pen)
            for i in range(len(points) - 1):
                painter.drawLine(int(points[i][0]), int(points[i][1]),
                               int(points[i+1][0]), int(points[i+1][1]))

            # Draw points
            painter.setBrush(self.color)
            painter.setPen(QPen(QColor("#121212"), 2))
            for x, y in points:
                painter.drawEllipse(int(x) - 5, int(y) - 5, 10, 10)
        finally:
            painter.end()


class FinancePage(QWidget):
    """Finance dashboard with stats, charts, and transaction history."""

    def __init__(self):
        super().__init__()
        self.current_user = None
        self._setup_ui()

        # Animate in
        QTimer.singleShot(100, self._animate_in)

    def _animate_in(self):
        """Animate the page content."""
        self._load_data()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        content = QWidget()
        content.setStyleSheet("background-color: #121212;")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(32, 32, 32, 32)
        content_layout.setSpacing(28)

        # Header
        header = QHBoxLayout()

        title_col = QVBoxLayout()
        title_col.setSpacing(6)

        title = QLabel("Finance")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #FFFFFF;")
        title_col.addWidget(title)

        subtitle = QLabel("Track revenue and financial performance")
        subtitle.setStyleSheet("font-size: 14px; color: #555555;")
        title_col.addWidget(subtitle)

        header.addLayout(title_col)
        header.addStretch()

        # Period selector
        self.period_combo = QComboBox()
        self.period_combo.addItems(["This Week", "This Month", "This Year", "All Time"])
        self.period_combo.setFixedWidth(150)
        self.period_combo.setFixedHeight(44)
        self.period_combo.setStyleSheet("""
            QComboBox {
                background-color: #1A1A1A;
                border: 1px solid #252525;
                border-radius: 10px;
                padding: 10px 16px;
                color: #FFFFFF;
                font-size: 13px;
                font-weight: 500;
            }
            QComboBox:hover { border-color: #333333; }
            QComboBox:focus { border-color: #5865F2; }
            QComboBox::drop-down {
                border: none;
                padding-right: 12px;
            }
            QComboBox QAbstractItemView {
                background-color: #1A1A1A;
                border: 1px solid #252525;
                border-radius: 8px;
                selection-background-color: #5865F2;
                color: #FFFFFF;
            }
        """)
        self.period_combo.currentIndexChanged.connect(self._on_period_changed)
        header.addWidget(self.period_combo)

        content_layout.addLayout(header)

        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("""
            QScrollArea { background: transparent; border: none; }
            QScrollBar:vertical {
                background-color: #121212;
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background-color: #333333;
                border-radius: 4px;
                min-height: 40px;
            }
            QScrollBar::handle:vertical:hover { background-color: #444444; }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
        """)

        scroll_content = QWidget()
        scroll_content.setStyleSheet("background: transparent;")
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(24)
        scroll_layout.setContentsMargins(0, 0, 0, 0)

        # Stats cards
        stats_row = QHBoxLayout()
        stats_row.setSpacing(16)

        self.revenue_card = self._create_stat_card("Total Revenue", "$0", "#22C55E", "↑")
        stats_row.addWidget(self.revenue_card)

        self.appointments_card = self._create_stat_card("Appointments", "0", "#5865F2", "📅")
        stats_row.addWidget(self.appointments_card)

        self.avg_card = self._create_stat_card("Avg. Per Service", "$0", "#F59E0B", "💰")
        stats_row.addWidget(self.avg_card)

        self.clients_card = self._create_stat_card("Clients Served", "0", "#EC4899", "👤")
        stats_row.addWidget(self.clients_card)

        scroll_layout.addLayout(stats_row)

        # Charts row
        charts_row = QHBoxLayout()
        charts_row.setSpacing(20)

        # Revenue chart
        revenue_chart_card = self._create_chart_card("Revenue by Day", "bar")
        charts_row.addWidget(revenue_chart_card, 2)

        # Trend chart
        trend_chart_card = self._create_chart_card("Revenue Trend", "line")
        charts_row.addWidget(trend_chart_card, 1)

        scroll_layout.addLayout(charts_row)

        # Transaction history
        history_card = self._create_history_section()
        scroll_layout.addWidget(history_card)

        scroll_layout.addStretch()
        scroll.setWidget(scroll_content)
        content_layout.addWidget(scroll, 1)

        layout.addWidget(content)

    def _create_stat_card(self, title: str, value: str, color: str, icon: str) -> QFrame:
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #1A1A1A;
                border: 1px solid #222222;
                border-radius: 16px;
            }
        """)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(12)

        # Title row with icon
        title_row = QHBoxLayout()

        title_label = QLabel(title)
        title_label.setStyleSheet("color: #666666; font-size: 13px; font-weight: 500; border: none;")
        title_row.addWidget(title_label)

        title_row.addStretch()

        icon_label = QLabel(icon)
        icon_label.setStyleSheet(f"font-size: 16px; border: none;")
        title_row.addWidget(icon_label)

        layout.addLayout(title_row)

        # Value
        value_label = QLabel(value)
        value_label.setObjectName(f"stat_value")
        value_label.setStyleSheet(f"color: {color}; font-size: 36px; font-weight: bold; border: none;")
        layout.addWidget(value_label)

        # Accent bar
        accent = QFrame()
        accent.setFixedHeight(4)
        accent.setStyleSheet(f"background-color: {color}; border-radius: 2px; border: none;")
        layout.addWidget(accent)

        card.value_label = value_label
        card.color = color

        return card

    def _create_chart_card(self, title: str, chart_type: str) -> QFrame:
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #1A1A1A;
                border: 2px solid #2A2A2A;
                border-radius: 16px;
            }
            QFrame:hover {
                border-color: #333333;
            }
        """)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)

        title_label = QLabel(title)
        title_label.setStyleSheet("color: #FFFFFF; font-size: 16px; font-weight: 600; border: none;")
        layout.addWidget(title_label)

        if chart_type == "bar":
            self.bar_chart = MiniBarChart()
            layout.addWidget(self.bar_chart)
        else:
            self.line_chart = MiniLineChart()
            layout.addWidget(self.line_chart)

        return card

    def _create_history_section(self) -> QFrame:
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #1A1A1A;
                border: 1px solid #222222;
                border-radius: 16px;
            }
        """)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)

        # Header
        header = QHBoxLayout()

        title_label = QLabel("Transaction History")
        title_label.setStyleSheet("color: #FFFFFF; font-size: 16px; font-weight: 600; border: none;")
        header.addWidget(title_label)

        header.addStretch()

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search transactions...")
        self.search_input.setFixedWidth(220)
        self.search_input.setFixedHeight(40)
        self.search_input.setStyleSheet("""
            QLineEdit {
                background-color: #252525;
                border: 1px solid #2A2A2A;
                border-radius: 8px;
                padding: 10px 14px;
                color: #FFFFFF;
                font-size: 13px;
            }
            QLineEdit:focus { border-color: #5865F2; }
            QLineEdit::placeholder { color: #555555; }
        """)
        self.search_input.textChanged.connect(self._filter_transactions)
        header.addWidget(self.search_input)

        layout.addLayout(header)

        # Table
        self.transactions_table = QTableWidget()
        self.transactions_table.setColumnCount(5)
        self.transactions_table.setHorizontalHeaderLabels(["Date", "Client", "Service", "Amount", "Status"])
        self.transactions_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.transactions_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        self.transactions_table.setColumnWidth(0, 110)
        self.transactions_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Fixed)
        self.transactions_table.setColumnWidth(3, 100)
        self.transactions_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Fixed)
        self.transactions_table.setColumnWidth(4, 100)
        self.transactions_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.transactions_table.setAlternatingRowColors(True)
        self.transactions_table.verticalHeader().setVisible(False)
        self.transactions_table.setStyleSheet("""
            QTableWidget {
                background-color: transparent;
                border: none;
                gridline-color: transparent;
            }
            QTableWidget::item {
                padding: 12px 8px;
                border-bottom: 1px solid #252525;
                color: #FFFFFF;
            }
            QTableWidget::item:selected {
                background-color: rgba(88, 101, 242, 0.15);
            }
            QTableWidget::item:alternate {
                background-color: #1E1E1E;
            }
            QHeaderView::section {
                background-color: #252525;
                color: #888888;
                font-weight: 600;
                font-size: 11px;
                padding: 12px 8px;
                border: none;
                border-bottom: 1px solid #2A2A2A;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
        """)
        self.transactions_table.setMinimumHeight(280)

        layout.addWidget(self.transactions_table)

        return card

    def _load_data(self):
        """Load financial data."""
        try:
            from data.db import get_connection
            conn = get_connection()
            cursor = conn.cursor()

            # Check for appointments table
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='appointments'")
            if not cursor.fetchone():
                self._load_sample_data()
                return

            period = self.period_combo.currentText()
            date_filter = self._get_date_filter(period)

            # Get stats from appointments - paid ones for revenue
            cursor.execute(f"""
                SELECT
                    COALESCE(SUM(s.price), 0) as revenue,
                    COUNT(*) as count
                FROM appointments a
                LEFT JOIN services s ON a.service_id = s.id
                WHERE a.paid = 1 {date_filter}
            """)
            result = cursor.fetchone()
            paid_revenue = result[0] or 0
            paid_appointments = result[1] or 0

            # Get total appointments count
            cursor.execute(f"""
                SELECT COUNT(*) FROM appointments a WHERE 1=1 {date_filter}
            """)
            total_appointments = cursor.fetchone()[0] or 0

            self._update_stat(self.revenue_card, f"${paid_revenue:,.0f}")
            self._update_stat(self.appointments_card, str(total_appointments))

            avg = paid_revenue / paid_appointments if paid_appointments > 0 else 0
            self._update_stat(self.avg_card, f"${avg:.0f}")

            # Clients served
            cursor.execute(f"""
                SELECT COUNT(DISTINCT a.client_id)
                FROM appointments a
                WHERE 1=1 {date_filter}
            """)
            clients = cursor.fetchone()[0] or 0
            self._update_stat(self.clients_card, str(clients))

            # Chart data
            self._load_chart_data(cursor, date_filter)
            self._load_transactions(cursor, date_filter)

        except Exception as e:
            logger.error(f"Error loading finance data: {e}")
            self._load_sample_data()

    def _get_date_filter(self, period: str) -> str:
        today = datetime.now()

        if period == "This Week":
            start = today - timedelta(days=today.weekday())
            return f"AND DATE(a.start_time) >= '{start.strftime('%Y-%m-%d')}'"
        elif period == "This Month":
            start = today.replace(day=1)
            return f"AND DATE(a.start_time) >= '{start.strftime('%Y-%m-%d')}'"
        elif period == "This Year":
            start = today.replace(month=1, day=1)
            return f"AND DATE(a.start_time) >= '{start.strftime('%Y-%m-%d')}'"
        return ""

    def _load_chart_data(self, cursor, date_filter: str):
        try:
            # Revenue by day of week
            cursor.execute(f"""
                SELECT strftime('%w', a.start_time) as dow, COALESCE(SUM(s.price), 0)
                FROM appointments a
                LEFT JOIN services s ON a.service_id = s.id
                WHERE 1=1 {date_filter}
                GROUP BY dow
                ORDER BY dow
            """)
            results = cursor.fetchall()

            days = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
            day_data = {str(i): 0 for i in range(7)}
            for dow, amount in results:
                if dow is not None:
                    day_data[str(dow)] = amount or 0

            self.bar_chart.set_data(
                [day_data[str(i)] for i in range(7)],
                days
            )

            # Trend data - last 7 days with activity
            cursor.execute(f"""
                SELECT DATE(a.start_time) as dt, COALESCE(SUM(s.price), 0)
                FROM appointments a
                LEFT JOIN services s ON a.service_id = s.id
                WHERE 1=1 {date_filter}
                GROUP BY dt
                ORDER BY dt DESC
                LIMIT 7
            """)
            trend_data = [row[1] or 0 for row in cursor.fetchall()][::-1]
            if len(trend_data) >= 2:
                self.line_chart.set_data(trend_data)
            else:
                self.line_chart.set_data([0, 0, 0, 0, 0, 0, 0])

        except Exception as e:
            logger.error(f"Error loading chart data: {e}")
            # Set sample data on error
            self.bar_chart.set_data([0, 0, 0, 0, 0, 0, 0], ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"])
            self.line_chart.set_data([0, 0, 0, 0, 0, 0, 0])

    def _load_transactions(self, cursor, date_filter: str):
        self.transactions_table.setRowCount(0)

        try:
            cursor.execute(f"""
                SELECT DATE(a.start_time) as dt, c.name, s.name, s.price,
                       CASE WHEN a.paid = 1 THEN 'Completed' ELSE 'Pending' END as status
                FROM appointments a
                LEFT JOIN clients c ON a.client_id = c.id
                LEFT JOIN services s ON a.service_id = s.id
                WHERE 1=1 {date_filter}
                ORDER BY a.start_time DESC
                LIMIT 50
            """)

            for row_data in cursor.fetchall():
                row = self.transactions_table.rowCount()
                self.transactions_table.insertRow(row)

                date_str = row_data[0] or "N/A"
                client = row_data[1] or "Walk-in"
                service = row_data[2] or "Service"
                amount = f"${row_data[3]:.0f}" if row_data[3] else "$0"
                status = row_data[4] or "Pending"

                self.transactions_table.setItem(row, 0, QTableWidgetItem(date_str))
                self.transactions_table.setItem(row, 1, QTableWidgetItem(client))
                self.transactions_table.setItem(row, 2, QTableWidgetItem(service))
                self.transactions_table.setItem(row, 3, QTableWidgetItem(amount))

                status_item = QTableWidgetItem(status)
                if status == "Completed":
                    status_item.setForeground(QColor("#22C55E"))
                else:
                    status_item.setForeground(QColor("#F59E0B"))
                self.transactions_table.setItem(row, 4, status_item)

        except Exception as e:
            logger.error(f"Error loading transactions: {e}")

    def _load_sample_data(self):
        """Load sample data for demonstration."""
        self._update_stat(self.revenue_card, "$2,450")
        self._update_stat(self.appointments_card, "47")
        self._update_stat(self.avg_card, "$52")
        self._update_stat(self.clients_card, "28")

        self.bar_chart.set_data(
            [320, 450, 380, 520, 480, 650, 420],
            ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
        )

        self.line_chart.set_data([180, 220, 195, 280, 310, 290, 350])

        sample_transactions = [
            ("2024-01-15", "John Smith", "Haircut", "$35", "Completed"),
            ("2024-01-15", "Mike Johnson", "Beard Trim", "$20", "Completed"),
            ("2024-01-14", "David Brown", "Full Service", "$55", "Completed"),
            ("2024-01-14", "Chris Wilson", "Haircut", "$35", "Pending"),
            ("2024-01-13", "Tom Davis", "Hair Color", "$75", "Completed"),
        ]

        self.transactions_table.setRowCount(0)
        for row_data in sample_transactions:
            row = self.transactions_table.rowCount()
            self.transactions_table.insertRow(row)
            for col, value in enumerate(row_data):
                item = QTableWidgetItem(value)
                if col == 4:
                    if value == "Completed":
                        item.setForeground(QColor("#22C55E"))
                    else:
                        item.setForeground(QColor("#F59E0B"))
                self.transactions_table.setItem(row, col, item)

    def _update_stat(self, card: QFrame, value: str):
        card.value_label.setText(value)

    def _filter_transactions(self, text: str):
        for row in range(self.transactions_table.rowCount()):
            match = False
            for col in range(self.transactions_table.columnCount()):
                item = self.transactions_table.item(row, col)
                if item and text.lower() in item.text().lower():
                    match = True
                    break
            self.transactions_table.setRowHidden(row, not match)

    def _on_period_changed(self, index: int):
        self._load_data()

    def load_user_data(self, user_data: dict):
        self.current_user = user_data
        self._load_data()
