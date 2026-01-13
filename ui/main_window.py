from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QStackedWidget
from PySide6.QtCore import Qt

from ui.sidebar import SideBar
from ui.statusbar import StatusBar

from ui.pages.schedule_page import SchedulePage
from ui.pages.client_page import ClientPage
from ui.pages.services_page import ServicesPage
from ui.pages.settings_page import SettingsPage


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Barber App")
        self.resize(1100, 680)

        # ===== ROOT =====
        root = QVBoxLayout(self)
        root.setContentsMargins(10, 10, 10, 10)
        root.setSpacing(8)

        # ===== ROW (SIDEBAR + PAGES) =====
        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(10)

        self.sidebar = SideBar(self)
        self.pages = QStackedWidget()

        # Pages
        self.schedule_page = SchedulePage()
        self.client_page = ClientPage()
        self.services_page = ServicesPage()
        self.settings_page = SettingsPage()

        self.pages.addWidget(self.schedule_page)
        self.pages.addWidget(self.client_page)
        self.pages.addWidget(self.services_page)
        self.pages.addWidget(self.settings_page)

        # Sidebar navigation
        self.sidebar.page_selected.connect(self.switch_page)

        row.addWidget(self.sidebar)
        row.addWidget(self.pages, 1)

        root.addLayout(row)

        # ===== STATUS BAR =====
        self.status = StatusBar()
        root.addWidget(self.status)

        # Default page
        self.switch_page(0)

    def switch_page(self, index: int):
        self.pages.setCurrentIndex(index)

        names = ["Schedule", "Clients", "Services", "Settings"]
        name = names[index] if index < len(names) else "Page"

        self.status.set_message(f"Viewing · {name}")
