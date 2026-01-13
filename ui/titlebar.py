from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt, QPoint


class TitleBar(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self._drag_pos: QPoint | None = None

        self.setFixedHeight(40)
        self.setObjectName("titlebar")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 0, 14, 0)

        self.title = QLabel("Barber App")
        self.title.setObjectName("titlebar_title")

        layout.addWidget(self.title)
        layout.addStretch()

        self.min_btn = QPushButton("–")
        self.close_btn = QPushButton("✕")

        self.min_btn.clicked.connect(parent.showMinimized)
        self.close_btn.clicked.connect(parent.close)

        layout.addWidget(self.min_btn)
        layout.addWidget(self.close_btn)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if self._drag_pos is not None:
            delta = event.globalPosition().toPoint() - self._drag_pos
            self.parent.move(self.parent.pos() + delta)
            self._drag_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event):
        self._drag_pos = None
