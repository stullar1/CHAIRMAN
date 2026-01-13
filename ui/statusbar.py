from PySide6.QtWidgets import QLabel


class StatusBar(QLabel):
    def __init__(self):
        super().__init__("Ready")
        self.setObjectName("StatusBar")

    def set_message(self, text: str):
        self.setText(text)
