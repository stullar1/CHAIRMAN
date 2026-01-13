import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication
from data.db import init_db
from ui.main_window import MainWindow


def _load_stylesheet(app: QApplication) -> None:
    """
    Loads style.qss from project root (same folder as this file).
    Safe: if missing, app still runs.
    """
    qss_path = Path(__file__).resolve().parent / "style.qss"
    if qss_path.exists():
        app.setStyleSheet(qss_path.read_text(encoding="utf-8"))


def run_app() -> None:
    # Create/upgrade local DB (offline-first)
    init_db()

    app = QApplication(sys.argv)
    _load_stylesheet(app)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    run_app()
