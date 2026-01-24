"""
CHAIRMAN - Modern Sidebar Navigation
Dark theme with animated indicator and draggable tabs
"""
from __future__ import annotations

from datetime import datetime
from pathlib import Path

from PySide6.QtWidgets import QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QGraphicsOpacityEffect
from PySide6.QtCore import Qt, Signal, QPropertyAnimation, QEasingCurve, QRect, QMimeData, QTimer, QSequentialAnimationGroup, QParallelAnimationGroup
from PySide6.QtGui import QFont, QPainter, QColor, QPixmap, QDrag, QPalette

from config import UIConfig, VERSION


class AnimatedIndicator(QWidget):
    """Animated sliding indicator for active tab."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._color = QColor("#5865F2")
        self.setFixedWidth(4)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)

    def paintEvent(self, event):
        painter = QPainter(self)
        if not painter.isActive():
            return
        try:
            painter.setRenderHint(QPainter.Antialiasing)
            painter.setBrush(self._color)
            painter.setPen(Qt.NoPen)
            painter.drawRoundedRect(self.rect(), 2, 2)
        finally:
            painter.end()


class DraggableNavButton(QPushButton):
    """Navigation button that supports drag and drop reordering."""

    drag_started = Signal(int)
    dropped = Signal(int, int)

    def __init__(self, text: str, index: int, parent=None):
        super().__init__(text, parent)
        self.index = index
        self.original_index = index
        self._drag_start_pos = None
        self.setAcceptDrops(True)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_start_pos = event.position().toPoint()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._drag_start_pos is None:
            return

        if (event.position().toPoint() - self._drag_start_pos).manhattanLength() < 20:
            return

        drag = QDrag(self)
        mime_data = QMimeData()
        mime_data.setText(str(self.index))
        drag.setMimeData(mime_data)
        drag.exec(Qt.MoveAction)
        self._drag_start_pos = None

    def mouseReleaseEvent(self, event):
        self._drag_start_pos = None
        super().mouseReleaseEvent(event)

    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()

    def dragLeaveEvent(self, event):
        self.update()

    def dropEvent(self, event):
        from_index = int(event.mimeData().text())
        to_index = self.index
        if from_index != to_index:
            self.dropped.emit(from_index, to_index)
        event.acceptProposedAction()


class SideBar(QWidget):
    """Modern sidebar navigation with animated indicator."""

    page_selected = Signal(int)
    tab_order_changed = Signal(list)

    # Noticeably lighter than main content (#121212) for clear visual distinction
    SIDEBAR_BG = "#1A1A1A"
    SIDEBAR_ACCENT = "#252525"

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setObjectName("sidebar")
        self.setFixedWidth(UIConfig.SIDEBAR_WIDTH)

        # Force sidebar background color - must be applied directly
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(self.backgroundRole(), QColor(self.SIDEBAR_BG))
        self.setPalette(palette)

        self.setStyleSheet(f"""
            QWidget#sidebar {{
                background-color: {self.SIDEBAR_BG};
                border-right: 1px solid #2A2A2A;
                border-bottom-left-radius: 12px;
            }}
        """)

        self._active_index = 0
        self.buttons: list[DraggableNavButton] = []
        self._logo_path = None
        self._owner_name = "there"

        self._nav_items = [
            ("Home", 0),
            ("Schedule", 1),
            ("Clients", 2),
            ("Services", 3),
            ("Products", 4),
            ("Finance", 5),
            ("Settings", 6),
        ]

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 24, 12, 20)
        layout.setSpacing(4)

        # Animated greeting header
        self.greeting_label = QLabel()
        self.greeting_label.setAlignment(Qt.AlignLeft)
        greeting_font = QFont()
        greeting_font.setPointSize(14)
        greeting_font.setBold(True)
        self.greeting_label.setFont(greeting_font)
        self.greeting_label.setStyleSheet("""
            color: #FFFFFF;
            padding: 8px 8px 0px 8px;
            background: transparent;
        """)
        self.greeting_label.setWordWrap(True)

        # Setup opacity effect for fade animation
        self.greeting_opacity = QGraphicsOpacityEffect(self.greeting_label)
        self.greeting_opacity.setOpacity(0)
        self.greeting_label.setGraphicsEffect(self.greeting_opacity)

        layout.addWidget(self.greeting_label)

        # Subtext under greeting
        self.greeting_subtext = QLabel()
        self.greeting_subtext.setAlignment(Qt.AlignLeft)
        self.greeting_subtext.setStyleSheet("""
            color: #555555;
            padding: 2px 8px 16px 8px;
            background: transparent;
            font-size: 11px;
        """)
        self.greeting_subtext_opacity = QGraphicsOpacityEffect(self.greeting_subtext)
        self.greeting_subtext_opacity.setOpacity(0)
        self.greeting_subtext.setGraphicsEffect(self.greeting_subtext_opacity)
        layout.addWidget(self.greeting_subtext)

        # Nav container
        self.nav_container = QWidget()
        self.nav_container.setStyleSheet("background: transparent;")
        self.nav_layout = QVBoxLayout(self.nav_container)
        self.nav_layout.setContentsMargins(0, 0, 0, 0)
        self.nav_layout.setSpacing(4)

        # Animated indicator
        self.indicator = AnimatedIndicator(self.nav_container)
        self.indicator.setFixedSize(4, 44)
        self.indicator.move(0, 0)

        self.indicator_animation = QPropertyAnimation(self.indicator, b"geometry")
        self.indicator_animation.setDuration(200)
        self.indicator_animation.setEasingCurve(QEasingCurve.OutCubic)

        self._create_nav_buttons()

        layout.addWidget(self.nav_container)
        layout.addStretch()

        # Business section at bottom
        business_frame = QFrame()
        business_frame.setObjectName("business_section")
        business_frame.setStyleSheet(f"""
            QFrame#business_section {{
                background-color: {self.SIDEBAR_ACCENT};
                border-radius: 10px;
                border: 1px solid #1A1A1A;
            }}
        """)
        business_layout = QHBoxLayout(business_frame)
        business_layout.setContentsMargins(10, 10, 10, 10)
        business_layout.setSpacing(10)

        # Business logo
        self.business_logo = QLabel()
        self.business_logo.setFixedSize(40, 40)
        self.business_logo.setAlignment(Qt.AlignCenter)
        self.business_logo.setStyleSheet("""
            background-color: #252525;
            border-radius: 8px;
            color: #666666;
            font-size: 14px;
            font-weight: bold;
        """)
        self.business_logo.setText("B")
        business_layout.addWidget(self.business_logo)

        # Business info
        info_layout = QVBoxLayout()
        info_layout.setSpacing(2)

        self.business_name_label = QLabel("Business")
        self.business_name_label.setStyleSheet("""
            color: #FFFFFF;
            font-weight: 600;
            font-size: 12px;
            background: transparent;
        """)
        info_layout.addWidget(self.business_name_label)

        self.owner_name_label = QLabel("Owner")
        self.owner_name_label.setStyleSheet("""
            color: #555555;
            font-size: 10px;
            background: transparent;
        """)
        info_layout.addWidget(self.owner_name_label)

        business_layout.addLayout(info_layout, 1)
        layout.addWidget(business_frame)

        # Version
        version_label = QLabel(f"v{VERSION}")
        version_label.setAlignment(Qt.AlignCenter)
        version_label.setStyleSheet("""
            color: #333333;
            font-size: 10px;
            padding: 12px 0 0 0;
            background: transparent;
        """)
        layout.addWidget(version_label)

        self.set_active(0)

        # Start greeting animation after a short delay
        QTimer.singleShot(100, self._animate_greeting_in)

    def _animate_greeting_in(self):
        """Fade in the greeting with animation."""
        self._update_greeting()

        # Main greeting fade in
        self.greeting_fade = QPropertyAnimation(self.greeting_opacity, b"opacity")
        self.greeting_fade.setDuration(600)
        self.greeting_fade.setStartValue(0)
        self.greeting_fade.setEndValue(1)
        self.greeting_fade.setEasingCurve(QEasingCurve.OutCubic)

        # Subtext fade in (delayed)
        self.subtext_fade = QPropertyAnimation(self.greeting_subtext_opacity, b"opacity")
        self.subtext_fade.setDuration(500)
        self.subtext_fade.setStartValue(0)
        self.subtext_fade.setEndValue(1)
        self.subtext_fade.setEasingCurve(QEasingCurve.OutCubic)

        # Sequential animation group
        self.greeting_group = QSequentialAnimationGroup()
        self.greeting_group.addAnimation(self.greeting_fade)
        self.greeting_group.addAnimation(self.subtext_fade)
        self.greeting_group.start()

    def _update_greeting(self):
        """Update greeting based on time of day."""
        hour = datetime.now().hour
        if 5 <= hour < 12:
            greeting = "Good morning"
            subtext = "Ready to start the day?"
        elif 12 <= hour < 17:
            greeting = "Good afternoon"
            subtext = "Keep up the great work!"
        elif 17 <= hour < 21:
            greeting = "Good evening"
            subtext = "Finishing up strong?"
        else:
            greeting = "Good night"
            subtext = "Working late tonight?"

        first_name = self._owner_name.split()[0] if self._owner_name else "there"
        self.greeting_label.setText(f"{greeting}, {first_name}")
        self.greeting_subtext.setText(subtext)

    def _create_nav_buttons(self):
        """Create navigation buttons based on current order."""
        for btn in self.buttons:
            self.nav_layout.removeWidget(btn)
            btn.deleteLater()
        self.buttons.clear()

        for display_idx, (text, page_idx) in enumerate(self._nav_items):
            btn = DraggableNavButton(text, display_idx)
            btn.original_index = page_idx
            btn.setObjectName("sidebar_button")
            btn.setCheckable(True)
            btn.setFixedHeight(44)
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda _, x=display_idx: self._on_click(x))
            btn.dropped.connect(self._handle_drop)
            btn.setStyleSheet(f"""
                QPushButton#sidebar_button {{
                    background-color: transparent;
                    color: #666666;
                    border: none;
                    border-radius: 8px;
                    padding: 10px 14px;
                    text-align: left;
                    font-size: 13px;
                    margin: 2px 6px 2px 12px;
                }}
                QPushButton#sidebar_button:checked {{
                    background-color: rgba(88, 101, 242, 0.15);
                    color: #FFFFFF;
                }}
                QPushButton#sidebar_button:hover:!checked {{
                    background-color: #252525;
                    color: #AAAAAA;
                }}
                QPushButton#sidebar_button:pressed {{
                    background-color: rgba(88, 101, 242, 0.25);
                }}
            """)

            btn_font = QFont()
            btn_font.setPointSize(13)
            btn.setFont(btn_font)

            self.buttons.append(btn)
            self.nav_layout.addWidget(btn)

    def _handle_drop(self, from_idx: int, to_idx: int):
        """Handle drag and drop reordering of tabs."""
        if from_idx == to_idx:
            return

        item = self._nav_items.pop(from_idx)
        self._nav_items.insert(to_idx, item)

        active_page = self.buttons[self._active_index].original_index if self.buttons else 0

        self._create_nav_buttons()

        for i, btn in enumerate(self.buttons):
            if btn.original_index == active_page:
                self.set_active(i)
                break

        new_order = [item[1] for item in self._nav_items]
        self.tab_order_changed.emit(new_order)

    def _on_click(self, index: int) -> None:
        """Handle navigation button click."""
        page_idx = self.buttons[index].original_index
        self.page_selected.emit(page_idx)
        self.set_active(index)

    def set_active(self, index: int) -> None:
        """Set the active navigation item with animation."""
        self._active_index = index

        for i, button in enumerate(self.buttons):
            button.setChecked(i == index)

        if index < len(self.buttons):
            btn = self.buttons[index]
            btn_pos = btn.pos()
            target_y = btn_pos.y()

            current_geo = self.indicator.geometry()
            target_geo = QRect(0, target_y, 4, 44)

            self.indicator_animation.stop()
            self.indicator_animation.setStartValue(current_geo)
            self.indicator_animation.setEndValue(target_geo)
            self.indicator_animation.start()

    def set_active_by_page(self, page_index: int) -> None:
        """Set active button by the original page index."""
        for i, btn in enumerate(self.buttons):
            if btn.original_index == page_index:
                self.set_active(i)
                break

    def set_user_info(self, name: str, role: str = "Barber"):
        """Update user information in sidebar (legacy)."""
        self.owner_name_label.setText(name)
        self._owner_name = name
        self._update_greeting()

    def set_business_info(self, business_name: str, owner_name: str, logo_path: str = None):
        """Update business information in sidebar."""
        self.business_name_label.setText(business_name)
        self.owner_name_label.setText(owner_name)
        self._logo_path = logo_path
        self._owner_name = owner_name
        self._update_greeting()

        # Re-animate greeting with new name
        self._animate_greeting_in()

        if logo_path and Path(logo_path).exists():
            pixmap = QPixmap(logo_path)
            if not pixmap.isNull():
                scaled = pixmap.scaled(36, 36, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.business_logo.setPixmap(scaled)
                self.business_logo.setStyleSheet("""
                    background-color: #252525;
                    border-radius: 8px;
                """)
        else:
            initial = business_name[0].upper() if business_name else "B"
            self.business_logo.clear()
            self.business_logo.setText(initial)
            self.business_logo.setStyleSheet("""
                background-color: #5865F2;
                border-radius: 8px;
                color: #FFFFFF;
                font-size: 16px;
                font-weight: bold;
            """)

    def update_logo(self, logo_path: str):
        """Update just the business logo."""
        self._logo_path = logo_path
        if logo_path and Path(logo_path).exists():
            pixmap = QPixmap(logo_path)
            if not pixmap.isNull():
                scaled = pixmap.scaled(36, 36, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.business_logo.setPixmap(scaled)
                self.business_logo.setStyleSheet("""
                    background-color: #252525;
                    border-radius: 8px;
                """)

    def set_tab_order(self, order: list):
        """Set the tab order from saved preferences."""
        if not order:
            return

        default_items = {
            0: ("Schedule", 0),
            1: ("Clients", 1),
            2: ("Services", 2),
            3: ("Products", 3),
            4: ("Finance", 4),
            5: ("Settings", 5),
        }

        new_items = []
        for page_idx in order:
            if page_idx in default_items:
                new_items.append(default_items[page_idx])

        for page_idx, item in default_items.items():
            if page_idx not in order:
                new_items.append(item)

        self._nav_items = new_items
        self._create_nav_buttons()
        self.set_active(0)

    def get_tab_order(self) -> list:
        """Get the current tab order as a list of page indices."""
        return [item[1] for item in self._nav_items]
