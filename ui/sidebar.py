from PySide6.QtWidgets import QWidget, QPushButton, QVBoxLayout
from PySide6.QtCore import Qt, Signal, QPoint, QPropertyAnimation, QEasingCurve


class SideBar(QWidget):
    page_selected = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("sidebar")
        self.setFixedWidth(220)

        self._active_index = 0
        self.buttons: list[QPushButton] = []

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 18, 12, 18)
        layout.setSpacing(6)

        items = [
            ("📅  Schedule", 0),
            ("👤  Clients", 1),
            ("✂️  Services", 2),
            ("⚙️  Settings", 3),
        ]

        for text, idx in items:
            btn = QPushButton(text)
            btn.setObjectName("sidebar_button")
            btn.setCheckable(True)
            btn.setFixedHeight(44)
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda _, x=idx: self._on_click(x))

            self.buttons.append(btn)
            layout.addWidget(btn)

        layout.addStretch()

        # Blue selection bar (STAYS)
        self.selection_bar = QWidget(self)
        self.selection_bar.setObjectName("sidebar_selection")
        self.selection_bar.setFixedWidth(3)
        self.selection_bar.setFixedHeight(44)
        self.selection_bar.move(0, self.buttons[0].y())
        self.selection_bar.show()

        self.set_active(0)

    def _on_click(self, index: int):
        self.page_selected.emit(index)
        self.set_active(index)

    def set_active(self, index: int):
        self._active_index = index

        for i, b in enumerate(self.buttons):
            b.setChecked(i == index)

        self._animate_selection_bar(self.buttons[index])

    def _animate_selection_bar(self, btn: QPushButton):
        anim = QPropertyAnimation(self.selection_bar, b"pos", self)
        anim.setDuration(180)
        anim.setEasingCurve(QEasingCurve.OutCubic)
        anim.setStartValue(self.selection_bar.pos())
        anim.setEndValue(QPoint(0, btn.y()))
        anim.start()
