"""
CHAIRMAN - Animated Splash Screen
Modern loading screen with logo animation
"""
from __future__ import annotations

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGraphicsOpacityEffect
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, Signal, QSequentialAnimationGroup, QParallelAnimationGroup
from PySide6.QtGui import QColor, QPainter, QLinearGradient, QFont, QPen

from config import APP_NAME, APP_TAGLINE, VERSION


class SplashScreen(QWidget):
    """Animated splash screen shown during app startup."""

    finished = Signal()

    def __init__(self):
        super().__init__()

        # Window setup - frameless, stay on top
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.SplashScreen)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(500, 350)

        # Center on screen
        from PySide6.QtWidgets import QApplication
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)

        self._setup_ui()
        self._setup_animations()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 50, 40, 40)
        layout.setSpacing(0)

        # Logo/Icon area
        self.icon_label = QLabel("✂")
        self.icon_label.setAlignment(Qt.AlignCenter)
        self.icon_label.setStyleSheet("""
            font-size: 64px;
            color: #5865F2;
        """)
        self.icon_opacity = QGraphicsOpacityEffect()
        self.icon_opacity.setOpacity(0)
        self.icon_label.setGraphicsEffect(self.icon_opacity)
        layout.addWidget(self.icon_label)

        layout.addSpacing(20)

        # App name
        self.title_label = QLabel(APP_NAME)
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("""
            font-size: 48px;
            font-weight: 700;
            color: #FFFFFF;
            letter-spacing: 8px;
        """)
        self.title_opacity = QGraphicsOpacityEffect()
        self.title_opacity.setOpacity(0)
        self.title_label.setGraphicsEffect(self.title_opacity)
        layout.addWidget(self.title_label)

        layout.addSpacing(8)

        # Tagline
        self.tagline_label = QLabel(APP_TAGLINE)
        self.tagline_label.setAlignment(Qt.AlignCenter)
        self.tagline_label.setStyleSheet("""
            font-size: 14px;
            font-weight: 400;
            color: #888888;
            letter-spacing: 2px;
        """)
        self.tagline_opacity = QGraphicsOpacityEffect()
        self.tagline_opacity.setOpacity(0)
        self.tagline_label.setGraphicsEffect(self.tagline_opacity)
        layout.addWidget(self.tagline_label)

        layout.addStretch()

        # Loading indicator
        self.loading_label = QLabel("Loading...")
        self.loading_label.setAlignment(Qt.AlignCenter)
        self.loading_label.setStyleSheet("""
            font-size: 12px;
            color: #5865F2;
            letter-spacing: 1px;
        """)
        self.loading_opacity = QGraphicsOpacityEffect()
        self.loading_opacity.setOpacity(0)
        self.loading_label.setGraphicsEffect(self.loading_opacity)
        layout.addWidget(self.loading_label)

        # Version
        self.version_label = QLabel(f"v{VERSION}")
        self.version_label.setAlignment(Qt.AlignCenter)
        self.version_label.setStyleSheet("""
            font-size: 11px;
            color: #444444;
        """)
        self.version_opacity = QGraphicsOpacityEffect()
        self.version_opacity.setOpacity(0)
        self.version_label.setGraphicsEffect(self.version_opacity)
        layout.addWidget(self.version_label)

        # Loading dots animation
        self.dot_count = 0
        self.loading_timer = QTimer()
        self.loading_timer.timeout.connect(self._update_loading_dots)

    def _setup_animations(self):
        """Setup fade-in animations for each element."""
        duration = 400

        # Icon animation
        self.icon_anim = QPropertyAnimation(self.icon_opacity, b"opacity")
        self.icon_anim.setDuration(duration)
        self.icon_anim.setStartValue(0)
        self.icon_anim.setEndValue(1)
        self.icon_anim.setEasingCurve(QEasingCurve.OutCubic)

        # Title animation
        self.title_anim = QPropertyAnimation(self.title_opacity, b"opacity")
        self.title_anim.setDuration(duration)
        self.title_anim.setStartValue(0)
        self.title_anim.setEndValue(1)
        self.title_anim.setEasingCurve(QEasingCurve.OutCubic)

        # Tagline animation
        self.tagline_anim = QPropertyAnimation(self.tagline_opacity, b"opacity")
        self.tagline_anim.setDuration(duration)
        self.tagline_anim.setStartValue(0)
        self.tagline_anim.setEndValue(1)
        self.tagline_anim.setEasingCurve(QEasingCurve.OutCubic)

        # Loading animation
        self.loading_anim = QPropertyAnimation(self.loading_opacity, b"opacity")
        self.loading_anim.setDuration(duration)
        self.loading_anim.setStartValue(0)
        self.loading_anim.setEndValue(1)
        self.loading_anim.setEasingCurve(QEasingCurve.OutCubic)

        # Version animation
        self.version_anim = QPropertyAnimation(self.version_opacity, b"opacity")
        self.version_anim.setDuration(duration)
        self.version_anim.setStartValue(0)
        self.version_anim.setEndValue(1)
        self.version_anim.setEasingCurve(QEasingCurve.OutCubic)

        # Sequence the animations
        self.anim_group = QSequentialAnimationGroup()
        self.anim_group.addAnimation(self.icon_anim)

        # Title and tagline together
        parallel1 = QParallelAnimationGroup()
        parallel1.addAnimation(self.title_anim)
        self.anim_group.addAnimation(parallel1)

        self.anim_group.addAnimation(self.tagline_anim)

        # Loading and version together
        parallel2 = QParallelAnimationGroup()
        parallel2.addAnimation(self.loading_anim)
        parallel2.addAnimation(self.version_anim)
        self.anim_group.addAnimation(parallel2)

    def _update_loading_dots(self):
        """Animate the loading dots."""
        self.dot_count = (self.dot_count + 1) % 4
        dots = "." * self.dot_count
        self.loading_label.setText(f"Loading{dots}")

    def paintEvent(self, event):
        """Draw the background."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Draw rounded rectangle background
        rect = self.rect()
        painter.setPen(Qt.NoPen)

        # Gradient background
        gradient = QLinearGradient(0, 0, 0, rect.height())
        gradient.setColorAt(0, QColor("#1A1A1A"))
        gradient.setColorAt(1, QColor("#121212"))

        painter.setBrush(gradient)
        painter.drawRoundedRect(rect, 16, 16)

        # Subtle border
        painter.setPen(QPen(QColor("#2A2A2A"), 1))
        painter.setBrush(Qt.NoBrush)
        painter.drawRoundedRect(rect.adjusted(0, 0, -1, -1), 16, 16)

        # Accent line at top
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor("#5865F2"))
        painter.drawRoundedRect(0, 0, rect.width(), 3, 2, 2)

    def start(self):
        """Start the splash screen animation."""
        self.show()
        self.anim_group.start()
        self.loading_timer.start(400)

    def finish(self):
        """Fade out and close the splash screen."""
        self.loading_timer.stop()

        # Fade out animation
        self.fade_out = QPropertyAnimation(self, b"windowOpacity")
        self.fade_out.setDuration(300)
        self.fade_out.setStartValue(1)
        self.fade_out.setEndValue(0)
        self.fade_out.setEasingCurve(QEasingCurve.OutCubic)
        self.fade_out.finished.connect(self._on_fade_finished)
        self.fade_out.start()

    def _on_fade_finished(self):
        """Called when fade out is complete."""
        self.close()
        self.finished.emit()
