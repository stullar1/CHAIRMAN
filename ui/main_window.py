"""
CHAIRMAN - Main Window
Frameless with rounded corners
"""
from __future__ import annotations

from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QStackedWidget, QLabel, QPushButton,
    QGraphicsOpacityEffect
)
from PySide6.QtCore import Qt, QPoint, QPropertyAnimation, QEasingCurve, QParallelAnimationGroup
from PySide6.QtGui import QPainter, QColor, QBrush

from config import APP_NAME, VERSION, UIConfig
from ui.sidebar import SideBar
from ui.pages.dashboard_page import DashboardPage
from ui.pages.schedule_page import SchedulePage
from ui.pages.client_page import ClientPage
from ui.pages.services_page import ServicesPage
from ui.pages.products_page import ProductsPage
from ui.pages.finance_page import FinancePage
from ui.pages.settings_page import SettingsPage


class MainWindow(QWidget):
    """Frameless main window with rounded corners."""

    def __init__(self):
        super().__init__()

        # Frameless window
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.resize(UIConfig.WINDOW_MIN_WIDTH, UIConfig.WINDOW_MIN_HEIGHT)
        self.setMinimumSize(900, 600)

        self.current_user = None
        self._drag_pos = None
        self._current_page_index = 0
        self._animating = False
        self._setup_ui()

    def _setup_ui(self):
        # Outer layout for rounded corners
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        # Container with rounded corners
        self.container = QWidget()
        self.container.setObjectName("main_container")
        self.container.setStyleSheet("""
            QWidget#main_container {
                background-color: #121212;
                border-radius: 12px;
            }
        """)

        container_layout = QVBoxLayout(self.container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)

        # Custom title bar
        title_bar = self._create_title_bar()
        container_layout.addWidget(title_bar)

        # Main content
        content_widget = QWidget()
        main_layout = QHBoxLayout(content_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Sidebar
        self.sidebar = SideBar(self)
        main_layout.addWidget(self.sidebar)

        # Pages area
        pages_area = QWidget()
        pages_layout = QVBoxLayout(pages_area)
        pages_layout.setContentsMargins(0, 0, 0, 0)
        pages_layout.setSpacing(0)

        # Pages
        self.pages = QStackedWidget()

        self.dashboard_page = DashboardPage()
        self.schedule_page = SchedulePage()
        self.client_page = ClientPage()
        self.services_page = ServicesPage()
        self.products_page = ProductsPage()
        self.finance_page = FinancePage()
        self.settings_page = SettingsPage()

        self.pages.addWidget(self.dashboard_page)   # 0 - Home
        self.pages.addWidget(self.schedule_page)    # 1
        self.pages.addWidget(self.client_page)      # 2
        self.pages.addWidget(self.services_page)    # 3
        self.pages.addWidget(self.products_page)    # 4
        self.pages.addWidget(self.finance_page)     # 5
        self.pages.addWidget(self.settings_page)    # 6

        # Connect dashboard quick actions
        self.dashboard_page.view_schedule_clicked.connect(lambda: self._switch_page(1))
        self.dashboard_page.view_finances_clicked.connect(lambda: self._switch_page(5))

        pages_layout.addWidget(self.pages)

        main_layout.addWidget(pages_area, 1)
        container_layout.addWidget(content_widget, 1)

        outer.addWidget(self.container)

        # Connect sidebar
        self.sidebar.page_selected.connect(self._switch_page)
        self._switch_page(0)

    def _create_title_bar(self) -> QWidget:
        """Create minimal title bar."""
        bar = QWidget()
        bar.setFixedHeight(40)
        bar.setStyleSheet("""
            QWidget {
                background-color: #1A1A1A;
                border-top-left-radius: 12px;
                border-top-right-radius: 12px;
            }
        """)

        layout = QHBoxLayout(bar)
        layout.setContentsMargins(16, 0, 8, 0)
        layout.setSpacing(8)

        # App name
        title = QLabel(f"{APP_NAME}")
        title.setStyleSheet("color: #5865F2; font-weight: bold; font-size: 13px;")
        layout.addWidget(title)

        layout.addStretch()

        # Window controls
        btn_style = """
            QPushButton {
                background-color: transparent;
                border: none;
                color: #666666;
                font-size: 16px;
                padding: 8px 12px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #252525;
                color: #FFFFFF;
            }
        """

        min_btn = QPushButton("─")
        min_btn.setStyleSheet(btn_style)
        min_btn.setCursor(Qt.PointingHandCursor)
        min_btn.clicked.connect(self.showMinimized)
        layout.addWidget(min_btn)

        max_btn = QPushButton("□")
        max_btn.setStyleSheet(btn_style)
        max_btn.setCursor(Qt.PointingHandCursor)
        max_btn.clicked.connect(self._toggle_maximize)
        layout.addWidget(max_btn)

        close_btn = QPushButton("✕")
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                color: #666666;
                font-size: 14px;
                padding: 8px 12px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #EF4444;
                color: #FFFFFF;
            }
        """)
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)

        return bar

    def _toggle_maximize(self):
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()

    def _switch_page(self, index: int):
        """Switch to a new page with fade animation."""
        if self._animating or index == self._current_page_index:
            return

        self._animating = True
        current_widget = self.pages.currentWidget()
        new_widget = self.pages.widget(index)

        # Setup opacity effects
        current_effect = QGraphicsOpacityEffect(current_widget)
        current_widget.setGraphicsEffect(current_effect)

        new_effect = QGraphicsOpacityEffect(new_widget)
        new_effect.setOpacity(0)
        new_widget.setGraphicsEffect(new_effect)

        # Fade out current page
        fade_out = QPropertyAnimation(current_effect, b"opacity")
        fade_out.setDuration(150)
        fade_out.setStartValue(1.0)
        fade_out.setEndValue(0.0)
        fade_out.setEasingCurve(QEasingCurve.OutQuad)

        # Fade in new page
        fade_in = QPropertyAnimation(new_effect, b"opacity")
        fade_in.setDuration(150)
        fade_in.setStartValue(0.0)
        fade_in.setEndValue(1.0)
        fade_in.setEasingCurve(QEasingCurve.InQuad)

        def on_fade_out_finished():
            self.pages.setCurrentIndex(index)
            fade_in.start()

        def on_fade_in_finished():
            # Clean up effects
            current_widget.setGraphicsEffect(None)
            new_widget.setGraphicsEffect(None)
            self._current_page_index = index
            self._animating = False

        fade_out.finished.connect(on_fade_out_finished)
        fade_in.finished.connect(on_fade_in_finished)

        # Keep references to prevent garbage collection
        self._fade_out = fade_out
        self._fade_in = fade_in

        fade_out.start()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and event.position().y() < 40:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if self._drag_pos and event.buttons() == Qt.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        self._drag_pos = None

    def mouseDoubleClickEvent(self, event):
        if event.position().y() < 40:
            self._toggle_maximize()
