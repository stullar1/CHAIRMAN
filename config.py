"""
CHAIRMAN - Professional Barber Shop Management System
Configuration Module

This module contains all application configuration, constants, and settings.
"""
from __future__ import annotations

from pathlib import Path
from typing import Final

# ============================================================================
# APPLICATION METADATA
# ============================================================================

APP_NAME: Final[str] = "CHAIRMAN"
APP_TAGLINE: Final[str] = "Run the shop. Own the chair."
VERSION: Final[str] = "1.0.0"
AUTHOR: Final[str] = "CHAIRMAN Development Team"

# ============================================================================
# BUSINESS MODES
# ============================================================================

class BusinessMode:
    """Business operating modes for the application."""
    SOLO: Final[str] = "solo"  # Single barber/hairdresser
    ENTERPRISE: Final[str] = "enterprise"  # Multiple employees

DEFAULT_BUSINESS_MODE: Final[str] = BusinessMode.SOLO

# ============================================================================
# DATABASE CONFIGURATION
# ============================================================================

# Get the project root directory
# When running as a PyInstaller bundle, use the executable's directory
# When running from source, use the directory containing config.py
import sys
if getattr(sys, 'frozen', False):
    # Running as compiled executable
    # Database and user data should be next to the .exe
    PROJECT_ROOT: Path = Path(sys.executable).resolve().parent
    # Assets are bundled inside _internal folder by PyInstaller
    BUNDLE_DIR: Path = PROJECT_ROOT / "_internal"
else:
    # Running from source
    PROJECT_ROOT: Path = Path(__file__).resolve().parent
    BUNDLE_DIR: Path = PROJECT_ROOT

# Database file location
DB_FILE: Final[Path] = PROJECT_ROOT / "barber.db"

# Database connection settings
DB_TIMEOUT: Final[int] = 10  # seconds
DB_CHECK_SAME_THREAD: Final[bool] = False

# ============================================================================
# UI CONFIGURATION
# ============================================================================

class UIConfig:
    """UI-related configuration constants."""

    # Window settings
    WINDOW_MIN_WIDTH: Final[int] = 950
    WINDOW_MIN_HEIGHT: Final[int] = 600

    # Sidebar
    SIDEBAR_WIDTH: Final[int] = 180
    SIDEBAR_ANIMATION_DURATION: Final[int] = 250  # milliseconds

    # Component sizing
    APPOINTMENT_LIST_HEIGHT: Final[int] = 420
    NOTES_INPUT_HEIGHT: Final[int] = 90

    # Colors (can be moved to QSS later)
    LABEL_COLOR: Final[str] = "rgba(230, 230, 230, 160)"
    LABEL_FONT_SIZE: Final[int] = 12

    # Version for sidebar display
    VERSION: Final[str] = "1.0.0"

# ============================================================================
# PAYMENT METHODS
# ============================================================================

PAYMENT_METHODS: Final[list[str]] = [
    "",  # Empty option for "not selected"
    "Cash",
    "Card (Manual)",
    "Cash App",
    "Zelle",
    "Venmo",
    "PayPal",
    "Other"
]

# ============================================================================
# SCHEDULING CONFIGURATION
# ============================================================================

class ScheduleConfig:
    """Scheduling and appointment configuration."""

    # Default buffer time between appointments (minutes)
    DEFAULT_BUFFER_MINUTES: Final[int] = 15

    # Business hours (24-hour format)
    BUSINESS_HOURS_START: Final[int] = 9  # 9 AM
    BUSINESS_HOURS_END: Final[int] = 18  # 6 PM

    # Appointment slot interval (minutes)
    APPOINTMENT_SLOT_INTERVAL: Final[int] = 30

    # Maximum appointments per day
    MAX_APPOINTMENTS_PER_DAY: Final[int] = 20

# ============================================================================
# VALIDATION RULES
# ============================================================================

class ValidationRules:
    """Data validation rules and constraints."""

    # Client validation
    CLIENT_NAME_MIN_LENGTH: Final[int] = 2
    CLIENT_NAME_MAX_LENGTH: Final[int] = 100
    PHONE_MIN_LENGTH: Final[int] = 10
    PHONE_MAX_LENGTH: Final[int] = 15

    # Service validation
    SERVICE_NAME_MIN_LENGTH: Final[int] = 3
    SERVICE_NAME_MAX_LENGTH: Final[int] = 100
    SERVICE_MIN_PRICE: Final[float] = 0.0
    SERVICE_MAX_PRICE: Final[float] = 10000.0
    SERVICE_MIN_DURATION: Final[int] = 5  # minutes
    SERVICE_MAX_DURATION: Final[int] = 480  # 8 hours

    # Appointment validation
    APPOINTMENT_NOTES_MAX_LENGTH: Final[int] = 500

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

class LogConfig:
    """Logging configuration settings."""

    LOG_DIR: Final[Path] = PROJECT_ROOT / "logs"
    LOG_FILE: Final[Path] = LOG_DIR / "chairman.log"
    LOG_LEVEL: Final[str] = "INFO"
    LOG_FORMAT: Final[str] = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_MAX_BYTES: Final[int] = 10 * 1024 * 1024  # 10 MB
    LOG_BACKUP_COUNT: Final[int] = 5

# ============================================================================
# FEATURE FLAGS
# ============================================================================

class Features:
    """Feature flags for enabling/disabling functionality."""

    ENABLE_NOTIFICATIONS: Final[bool] = False  # Future feature
    ENABLE_ONLINE_SYNC: Final[bool] = False  # Future feature
    ENABLE_SMS_REMINDERS: Final[bool] = False  # Future feature
    ENABLE_ANALYTICS: Final[bool] = False  # Future feature
    ENABLE_MULTI_LOCATION: Final[bool] = False  # Future feature

# ============================================================================
# TAX CONFIGURATION
# ============================================================================

class TaxConfig:
    """Tax calculation configuration."""

    # Default sales tax rate (can be customized per state/location)
    DEFAULT_TAX_RATE: Final[float] = 0.0875  # 8.75% (adjust for your location)

    # Tax on services (typically yes)
    TAX_SERVICES: Final[bool] = True

    # Tax on products (typically yes)
    TAX_PRODUCTS: Final[bool] = True

    # Include tax in displayed prices
    TAX_INCLUSIVE: Final[bool] = False

# ============================================================================
# ENTERPRISE MODE CONFIGURATION
# ============================================================================

class EnterpriseConfig:
    """Configuration specific to enterprise mode."""

    # Privacy settings for enterprise mode
    SHOW_EARNINGS_TO_OTHERS: Final[bool] = False
    SHOW_CLIENT_DETAILS_TO_OTHERS: Final[bool] = True
    SHOW_SCHEDULE_TO_OTHERS: Final[bool] = True

    # Maximum number of barbers/employees
    MAX_EMPLOYEES: Final[int] = 50

# ============================================================================
# ASSET PATHS
# ============================================================================

class Assets:
    """Paths to application assets."""

    # Assets are in BUNDLE_DIR (which is _internal when frozen, or PROJECT_ROOT when running from source)
    ASSETS_DIR: Final[Path] = BUNDLE_DIR / "assets"
    ICONS_DIR: Final[Path] = ASSETS_DIR / "icons"
    IMAGES_DIR: Final[Path] = ASSETS_DIR / "images"
    SOUNDS_DIR: Final[Path] = ASSETS_DIR / "sounds"
    # User-uploaded logos go in PROJECT_ROOT (next to exe/db) so they persist
    LOGOS_DIR: Final[Path] = PROJECT_ROOT / "logos"
    STYLESHEET: Final[Path] = BUNDLE_DIR / "style.qss"

# ============================================================================
# EMAIL CONFIGURATION
# ============================================================================

class EmailConfig:
    """Email/SMTP configuration for verification codes."""

    # SMTP Settings - Configure these for your email provider
    # For Gmail: smtp.gmail.com, port 587, use App Password
    # For Outlook: smtp-mail.outlook.com, port 587
    SMTP_HOST: Final[str] = ""  # e.g., "smtp.gmail.com"
    SMTP_PORT: Final[int] = 587
    SMTP_USER: Final[str] = ""  # Your email address
    SMTP_PASSWORD: Final[str] = ""  # App password (not regular password)
    FROM_EMAIL: Final[str] = ""  # Sender email (usually same as SMTP_USER)
    FROM_NAME: Final[str] = "CHAIRMAN"

    # Verification settings
    CODE_EXPIRY_MINUTES: Final[int] = 10
