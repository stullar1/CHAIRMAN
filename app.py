"""
CHAIRMAN - Main Application Module

This is the entry point for the CHAIRMAN barber shop management system.
"""
from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer

from config import APP_NAME, VERSION, Assets
from core.logging_config import setup_logging, get_logger
from core.updater import AutoUpdater
from data.db import init_db, get_tab_order, save_tab_order
from ui.auth_window import AuthWindow
from ui.main_window import MainWindow
from ui.dialogs import UpdateDialog

# Initialize logging first
logger = setup_logging()


def load_stylesheet(app: QApplication) -> None:
    """
    Load the application stylesheet from style.qss.

    This function safely loads the QSS file. If the file doesn't exist,
    the application will continue to run with default styling.

    Args:
        app: The QApplication instance to apply the stylesheet to
    """
    if Assets.STYLESHEET.exists():
        try:
            stylesheet_content = Assets.STYLESHEET.read_text(encoding="utf-8")
            app.setStyleSheet(stylesheet_content)
            logger.info("Stylesheet loaded successfully")
        except Exception as e:
            logger.warning(f"Failed to load stylesheet: {e}")
    else:
        logger.warning(f"Stylesheet not found at {Assets.STYLESHEET}")


def run_app() -> None:
    """
    Main application entry point.

    This function:
    1. Initializes the database
    2. Creates the Qt application
    3. Loads the stylesheet
    4. Shows login window
    5. Shows main window after successful login
    6. Starts the event loop
    """
    logger.info(f"Starting {APP_NAME} v{VERSION}")

    try:
        # Initialize database
        logger.info("Initializing database...")
        init_db()
        logger.info("Database initialized successfully")

        # Create Qt application
        app = QApplication(sys.argv)
        app.setApplicationName(APP_NAME)
        app.setApplicationVersion(VERSION)

        # Load stylesheet
        load_stylesheet(app)

        # Create authentication window
        logger.info("Creating authentication window...")
        auth_window = AuthWindow()

        # Create main window (but don't show it yet)
        main_window = MainWindow()

        # Connect login success to show main window
        def on_login_success(user_data: dict):
            logger.info(f"Login successful for {user_data['name']}, showing main window...")
            # Store user data in main window and update UI
            main_window.current_user = user_data
            main_window.sidebar.set_business_info(
                user_data.get('business_name', 'Business'),
                user_data.get('name', 'Owner'),
                user_data.get('logo_path')
            )

            # Load saved tab order preference
            user_id = user_data.get('id')
            if user_id:
                saved_order = get_tab_order(user_id)
                if saved_order:
                    logger.info(f"Loading saved tab order: {saved_order}")
                    main_window.sidebar.set_tab_order(saved_order)

            main_window.settings_page.load_user_data(user_data)
            main_window.finance_page.load_user_data(user_data)
            main_window.show()

        auth_window.login_successful.connect(on_login_success)

        # Handle logout - show new auth window
        def on_logout():
            logger.info("User logged out, showing auth window...")
            main_window.hide()
            main_window.current_user = None
            # Create new auth window
            new_auth = AuthWindow()
            new_auth.login_successful.connect(on_login_success)
            new_auth.show()

        main_window.settings_page.logout_requested.connect(on_logout)

        # Handle account deletion - same as logout
        def on_account_deleted():
            logger.info("Account deleted, showing auth window...")
            main_window.hide()
            main_window.current_user = None
            # Create new auth window
            new_auth = AuthWindow()
            new_auth.login_successful.connect(on_login_success)
            new_auth.show()

        main_window.settings_page.account_deleted.connect(on_account_deleted)

        # Handle logo change - update sidebar
        def on_logo_changed(logo_path: str):
            logger.info(f"Logo changed: {logo_path}")
            main_window.sidebar.update_logo(logo_path)

        main_window.settings_page.logo_changed.connect(on_logo_changed)

        # Handle tab order changes - save to database
        def on_tab_order_changed(new_order: list):
            if main_window.current_user:
                user_id = main_window.current_user.get('id')
                if user_id:
                    logger.info(f"Saving tab order: {new_order}")
                    save_tab_order(user_id, new_order)

        main_window.sidebar.tab_order_changed.connect(on_tab_order_changed)

        # Show authentication window
        auth_window.show()
        logger.info("Application started successfully")

        # Check for updates in the background (after a short delay)
        updater = AutoUpdater()
        update_dialog = None

        def on_update_available(version: str, release_notes: str):
            nonlocal update_dialog
            logger.info(f"Update available: v{version}")
            # Show update dialog
            update_dialog = UpdateDialog(
                parent=auth_window if auth_window.isVisible() else main_window,
                new_version=version,
                release_notes=release_notes
            )
            if update_dialog.exec():
                # User clicked "Update Now"
                update_dialog.show_progress()
                updater.download_update()

        def on_download_progress(progress: int):
            if update_dialog:
                update_dialog.set_progress(progress)

        def on_update_ready(filepath: str):
            if update_dialog:
                update_dialog.download_complete()
            logger.info(f"Update downloaded to: {filepath}")
            # Install the update (this will close the app)
            QTimer.singleShot(1000, lambda: AutoUpdater.install_update(filepath))

        updater.update_available.connect(on_update_available)
        updater.download_progress.connect(on_download_progress)
        updater.update_ready.connect(on_update_ready)

        # Check for updates after 2 seconds (let the UI load first)
        QTimer.singleShot(2000, lambda: updater.check_for_updates(silent=True))

        # Start event loop
        exit_code = app.exec()
        logger.info(f"Application exited with code {exit_code}")
        sys.exit(exit_code)

    except Exception as e:
        logger.critical(f"Fatal error during application startup: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    run_app()
