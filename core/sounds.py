"""
CHAIRMAN - Sound Manager
Handles UI sound effects for interactions
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional

from PySide6.QtCore import QUrl, QObject
from PySide6.QtMultimedia import QSoundEffect

from core.logging_config import get_logger

logger = get_logger(__name__)


class SoundManager(QObject):
    """Manages UI sound effects."""

    _instance: Optional['SoundManager'] = None
    _sounds: dict[str, QSoundEffect] = {}
    _enabled: bool = True
    _volume: float = 0.3  # 30% volume by default

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        super().__init__()
        self._initialized = True
        self._sounds = {}
        self._load_sounds()

    def _load_sounds(self):
        """Load all sound effects."""
        from config import Assets
        sounds_dir = Assets.SOUNDS_DIR

        # Define sound mappings
        sound_files = {
            "click": "click.wav",
            "hover": "hover.wav",
            "success": "success.wav",
            "error": "error.wav",
            "warning": "warning.wav",
            "popup": "popup.wav",
            "notification": "notification.wav",
            "toggle": "toggle.wav",
        }

        for name, filename in sound_files.items():
            path = sounds_dir / filename
            if path.exists():
                try:
                    effect = QSoundEffect()
                    effect.setSource(QUrl.fromLocalFile(str(path)))
                    effect.setVolume(self._volume)
                    self._sounds[name] = effect
                except Exception as e:
                    logger.debug(f"Could not load sound {name}: {e}")

    def play(self, sound_name: str):
        """Play a sound effect by name."""
        if not self._enabled:
            return

        if sound_name in self._sounds:
            try:
                self._sounds[sound_name].play()
            except Exception as e:
                logger.debug(f"Could not play sound {sound_name}: {e}")

    def set_enabled(self, enabled: bool):
        """Enable or disable all sounds."""
        self._enabled = enabled

    def is_enabled(self) -> bool:
        """Check if sounds are enabled."""
        return self._enabled

    def set_volume(self, volume: float):
        """Set volume for all sounds (0.0 to 1.0)."""
        self._volume = max(0.0, min(1.0, volume))
        for effect in self._sounds.values():
            effect.setVolume(self._volume)

    def get_volume(self) -> float:
        """Get current volume level."""
        return self._volume
