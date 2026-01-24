"""
CHAIRMAN - Auto-Updater Module
Checks for updates from GitHub releases and handles automatic updates
"""
from __future__ import annotations

import json
import os
import platform
import subprocess
import sys
import tempfile
import threading
from pathlib import Path
from typing import Optional, Callable
from urllib.request import urlopen, Request
from urllib.error import URLError

from PySide6.QtCore import QObject, Signal, QThread

from config import VERSION
from core.logging_config import get_logger

logger = get_logger(__name__)

# GitHub repository info - UPDATE THESE FOR YOUR REPO
GITHUB_OWNER = "stullar1"
GITHUB_REPO = "CHAIRMAN"
GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/releases/latest"


class UpdateChecker(QThread):
    """Background thread to check for updates."""

    update_available = Signal(str, str, str)  # version, download_url, release_notes
    no_update = Signal()
    error = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_version = VERSION

    def run(self):
        """Check GitHub for the latest release."""
        try:
            # Create request with headers
            request = Request(
                GITHUB_API_URL,
                headers={
                    'Accept': 'application/vnd.github.v3+json',
                    'User-Agent': f'CHAIRMAN/{self.current_version}'
                }
            )

            with urlopen(request, timeout=10) as response:
                data = json.loads(response.read().decode('utf-8'))

            latest_version = data.get('tag_name', '').lstrip('v')
            release_notes = data.get('body', 'No release notes available.')

            # Find the right asset for this platform
            download_url = self._get_download_url(data.get('assets', []))

            if not download_url:
                self.error.emit("No download available for your platform.")
                return

            # Compare versions
            if self._is_newer_version(latest_version, self.current_version):
                self.update_available.emit(latest_version, download_url, release_notes)
            else:
                self.no_update.emit()

        except URLError as e:
            logger.debug(f"Update check failed: {e}")
            self.error.emit(f"Could not check for updates: {e.reason}")
        except Exception as e:
            logger.debug(f"Update check error: {e}")
            self.error.emit(str(e))

    def _get_download_url(self, assets: list) -> Optional[str]:
        """Get the appropriate download URL for the current platform."""
        system = platform.system().lower()

        # Map platform to expected asset name patterns
        if system == 'windows':
            patterns = ['windows', 'win', '.exe', 'setup']
        elif system == 'darwin':
            patterns = ['macos', 'mac', 'darwin', '.dmg']
        else:
            patterns = ['linux', '.appimage', '.deb']

        for asset in assets:
            name = asset.get('name', '').lower()
            for pattern in patterns:
                if pattern in name:
                    return asset.get('browser_download_url')

        return None

    def _is_newer_version(self, latest: str, current: str) -> bool:
        """Compare version strings (e.g., '1.2.3' > '1.2.0')."""
        try:
            latest_parts = [int(x) for x in latest.split('.')]
            current_parts = [int(x) for x in current.split('.')]

            # Pad shorter version with zeros
            while len(latest_parts) < len(current_parts):
                latest_parts.append(0)
            while len(current_parts) < len(latest_parts):
                current_parts.append(0)

            return latest_parts > current_parts
        except (ValueError, AttributeError):
            return False


class UpdateDownloader(QThread):
    """Background thread to download updates."""

    progress = Signal(int)  # percentage
    finished = Signal(str)  # filepath
    error = Signal(str)

    def __init__(self, download_url: str, parent=None):
        super().__init__(parent)
        self.download_url = download_url

    def run(self):
        """Download the update file."""
        try:
            request = Request(
                self.download_url,
                headers={'User-Agent': f'CHAIRMAN/{VERSION}'}
            )

            with urlopen(request, timeout=60) as response:
                # Get file info
                total_size = int(response.headers.get('content-length', 0))
                filename = self.download_url.split('/')[-1]

                # Create temp file
                temp_dir = tempfile.gettempdir()
                filepath = os.path.join(temp_dir, filename)

                # Download with progress
                downloaded = 0
                block_size = 8192

                with open(filepath, 'wb') as f:
                    while True:
                        chunk = response.read(block_size)
                        if not chunk:
                            break
                        f.write(chunk)
                        downloaded += len(chunk)

                        if total_size > 0:
                            progress = int((downloaded / total_size) * 100)
                            self.progress.emit(progress)

                self.finished.emit(filepath)

        except Exception as e:
            logger.error(f"Download failed: {e}")
            self.error.emit(str(e))


class AutoUpdater(QObject):
    """Main auto-updater class that coordinates checking and downloading updates."""

    update_available = Signal(str, str)  # version, release_notes
    download_progress = Signal(int)
    update_ready = Signal(str)  # filepath
    no_update = Signal()
    error = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._checker: Optional[UpdateChecker] = None
        self._downloader: Optional[UpdateDownloader] = None
        self._download_url: Optional[str] = None

    def check_for_updates(self, silent: bool = True):
        """
        Check for available updates.

        Args:
            silent: If True, don't emit error signals for network failures
        """
        self._checker = UpdateChecker()
        self._checker.update_available.connect(self._on_update_available)
        self._checker.no_update.connect(self.no_update.emit)
        if not silent:
            self._checker.error.connect(self.error.emit)
        self._checker.start()

    def _on_update_available(self, version: str, download_url: str, release_notes: str):
        """Handle when an update is found."""
        self._download_url = download_url
        self.update_available.emit(version, release_notes)

    def download_update(self):
        """Download the available update."""
        if not self._download_url:
            self.error.emit("No update URL available.")
            return

        self._downloader = UpdateDownloader(self._download_url)
        self._downloader.progress.connect(self.download_progress.emit)
        self._downloader.finished.connect(self.update_ready.emit)
        self._downloader.error.connect(self.error.emit)
        self._downloader.start()

    @staticmethod
    def install_update(filepath: str):
        """
        Install the downloaded update.
        This will launch the installer and close the current application.
        """
        system = platform.system().lower()

        try:
            if system == 'windows':
                # Run the installer
                subprocess.Popen([filepath], shell=True)
            elif system == 'darwin':
                # Open the DMG
                subprocess.Popen(['open', filepath])
            else:
                # Linux - try to make executable and run
                os.chmod(filepath, 0o755)
                subprocess.Popen([filepath])

            # Exit current application
            sys.exit(0)

        except Exception as e:
            logger.error(f"Failed to install update: {e}")
            raise
