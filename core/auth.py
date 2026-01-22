"""
CHAIRMAN - Authentication Module
Secure user authentication and password management
"""
from __future__ import annotations

import hashlib
import secrets
import json
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional

from core.logging_config import get_logger

logger = get_logger(__name__)

# Path for device token storage
DATA_DIR = Path(__file__).parent.parent / "data"
DEVICE_TOKEN_FILE = DATA_DIR / ".device_token"
PENDING_VERIFICATIONS_FILE = DATA_DIR / ".pending_verifications"


class PasswordHasher:
    """Secure password hashing using PBKDF2-SHA256."""

    @staticmethod
    def hash_password(password: str, salt: Optional[bytes] = None) -> tuple[str, str]:
        """Hash a password using PBKDF2-SHA256."""
        if salt is None:
            salt = secrets.token_bytes(32)
        elif isinstance(salt, str):
            salt = bytes.fromhex(salt)

        key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
        return key.hex(), salt.hex()

    @staticmethod
    def verify_password(password: str, hashed_password: str, salt: str) -> bool:
        """Verify a password against its hash."""
        computed_hash, _ = PasswordHasher.hash_password(password, salt)
        return secrets.compare_digest(computed_hash, hashed_password)


class AuthService:
    """User authentication service."""

    def __init__(self, db_connection=None):
        """Initialize auth service with database connection."""
        self.db = db_connection
        self._pending_registrations = {}
        self._ensure_users_table()
        self._load_pending_verifications()

    def _ensure_users_table(self):
        """Create users table if it doesn't exist."""
        if self.db is None:
            from data.db import get_connection
            self.db = get_connection()

        cursor = self.db.cursor()

        # Drop old table and create new one with updated schema
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        if cursor.fetchone():
            # Check current schema
            cursor.execute("PRAGMA table_info(users)")
            columns = [col[1] for col in cursor.fetchall()]

            # Add missing columns
            if 'business_email' not in columns:
                cursor.execute("ALTER TABLE users ADD COLUMN business_email TEXT")
            if 'logo_path' not in columns:
                cursor.execute("ALTER TABLE users ADD COLUMN logo_path TEXT")
            if 'email_verified' not in columns:
                cursor.execute("ALTER TABLE users ADD COLUMN email_verified INTEGER DEFAULT 0")
            if 'device_token' not in columns:
                cursor.execute("ALTER TABLE users ADD COLUMN device_token TEXT")

            # Rename username to business_name if needed
            if 'username' in columns and 'business_name' not in columns:
                cursor.execute("ALTER TABLE users RENAME COLUMN username TO business_name")

            self.db.commit()
        else:
            cursor.execute("""
                CREATE TABLE users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    business_name TEXT NOT NULL,
                    business_email TEXT,
                    phone TEXT,
                    logo_path TEXT,
                    password_hash TEXT NOT NULL,
                    password_salt TEXT NOT NULL,
                    email_verified INTEGER DEFAULT 0,
                    device_token TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP
                )
            """)
            self.db.commit()

        logger.info("Users table initialized")

    def _load_pending_verifications(self):
        """Load pending verifications from file."""
        try:
            if PENDING_VERIFICATIONS_FILE.exists():
                data = json.loads(PENDING_VERIFICATIONS_FILE.read_text())
                # Clean expired entries
                now = datetime.now().isoformat()
                self._pending_registrations = {
                    k: v for k, v in data.items()
                    if v.get('expires_at', '') > now
                }
        except Exception as e:
            logger.error(f"Failed to load pending verifications: {e}")
            self._pending_registrations = {}

    def _save_pending_verifications(self):
        """Save pending verifications to file."""
        try:
            DATA_DIR.mkdir(parents=True, exist_ok=True)
            PENDING_VERIFICATIONS_FILE.write_text(json.dumps(self._pending_registrations))
        except Exception as e:
            logger.error(f"Failed to save pending verifications: {e}")

    def start_registration(
        self,
        email: str,
        business_name: str,
        business_email: str,
        password: str,
        logo_path: Optional[str] = None
    ) -> tuple[bool, str, str]:
        """
        Start registration process - generates verification code.

        Returns:
            Tuple of (success, message, verification_code)
        """
        try:
            # Validate inputs
            if not email or not business_name or not password:
                return False, "Email, business name, and password are required", ""

            if len(password) < 8:
                return False, "Password must be at least 8 characters", ""

            if len(business_name) < 2:
                return False, "Business name must be at least 2 characters", ""

            # Check if email already exists
            cursor = self.db.cursor()
            cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
            if cursor.fetchone():
                return False, "An account with this email already exists", ""

            # Generate verification code
            code = f"{secrets.randbelow(1000000):06d}"
            expires_at = (datetime.now() + timedelta(minutes=10)).isoformat()

            # Hash password for storage
            password_hash, salt = PasswordHasher.hash_password(password)

            # Store pending registration
            self._pending_registrations[email] = {
                'code': code,
                'business_name': business_name,
                'business_email': business_email,
                'password_hash': password_hash,
                'password_salt': salt,
                'logo_path': logo_path,
                'expires_at': expires_at
            }
            self._save_pending_verifications()

            logger.info(f"Verification code generated for {email}")
            return True, "Verification code sent", code

        except Exception as e:
            logger.error(f"Registration start error: {e}")
            return False, f"Registration failed: {str(e)}", ""

    def verify_and_complete_registration(self, email: str, code: str) -> tuple[bool, str]:
        """
        Verify code and complete registration.

        Returns:
            Tuple of (success, message)
        """
        try:
            pending = self._pending_registrations.get(email)
            if not pending:
                return False, "No pending registration found. Please start over."

            # Check expiry
            if datetime.now().isoformat() > pending['expires_at']:
                del self._pending_registrations[email]
                self._save_pending_verifications()
                return False, "Verification code expired. Please start over."

            # Verify code
            if not secrets.compare_digest(code, pending['code']):
                return False, "Invalid verification code"

            # Create user
            cursor = self.db.cursor()
            cursor.execute("""
                INSERT INTO users (
                    name, email, business_name, business_email,
                    password_hash, password_salt, logo_path, email_verified
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, 1)
            """, (
                pending['business_name'],  # Use business name as display name
                email,
                pending['business_name'],
                pending['business_email'],
                pending['password_hash'],
                pending['password_salt'],
                pending['logo_path']
            ))
            self.db.commit()

            # Clean up pending registration
            del self._pending_registrations[email]
            self._save_pending_verifications()

            logger.info(f"User registered: {email}")
            return True, "Account created successfully"

        except Exception as e:
            logger.error(f"Registration completion error: {e}")
            return False, f"Registration failed: {str(e)}"

    def resend_verification_code(self, email: str) -> tuple[bool, str, str]:
        """
        Resend verification code for pending registration.

        Returns:
            Tuple of (success, message, new_code)
        """
        pending = self._pending_registrations.get(email)
        if not pending:
            return False, "No pending registration found", ""

        # Generate new code
        code = f"{secrets.randbelow(1000000):06d}"
        expires_at = (datetime.now() + timedelta(minutes=10)).isoformat()

        pending['code'] = code
        pending['expires_at'] = expires_at
        self._save_pending_verifications()

        logger.info(f"New verification code generated for {email}")
        return True, "New verification code sent", code

    def authenticate(
        self,
        email: str,
        password: str,
        remember_device: bool = False
    ) -> tuple[bool, Optional[dict], str]:
        """
        Authenticate a user by email.

        Returns:
            Tuple of (success, user_data, message)
        """
        try:
            cursor = self.db.cursor()
            cursor.execute("""
                SELECT id, name, email, business_name, business_email, phone,
                       logo_path, password_hash, password_salt, email_verified
                FROM users
                WHERE email = ?
            """, (email,))

            user = cursor.fetchone()
            if not user:
                return False, None, "Invalid email or password"

            (user_id, name, email, business_name, business_email, phone,
             logo_path, password_hash, salt, email_verified) = user

            # Verify password
            if not PasswordHasher.verify_password(password, password_hash, salt):
                return False, None, "Invalid email or password"

            # Update last login
            cursor.execute("UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?", (user_id,))

            # Handle remember device
            if remember_device:
                device_token = secrets.token_hex(32)
                cursor.execute("UPDATE users SET device_token = ? WHERE id = ?", (device_token, user_id))
                self._save_device_token(device_token, user_id)

            self.db.commit()

            user_data = {
                'id': user_id,
                'name': name,
                'email': email,
                'business_name': business_name,
                'business_email': business_email,
                'phone': phone,
                'logo_path': logo_path
            }

            logger.info(f"User authenticated: {email}")
            return True, user_data, "Login successful"

        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return False, None, f"Authentication failed: {str(e)}"

    def save_logo(self, source_path: str, email: str) -> Optional[str]:
        """
        Save uploaded logo to assets folder.

        Returns:
            Path to saved logo or None on failure
        """
        try:
            from config import Assets

            # Create logos directory
            Assets.LOGOS_DIR.mkdir(parents=True, exist_ok=True)

            # Generate unique filename
            source = Path(source_path)
            ext = source.suffix.lower()
            if ext not in ['.png', '.jpg', '.jpeg', '.gif', '.webp']:
                logger.warning(f"Invalid logo format: {ext}")
                return None

            # Use email hash for filename
            filename = f"{hashlib.md5(email.encode()).hexdigest()}{ext}"
            dest_path = Assets.LOGOS_DIR / filename

            # Copy file
            shutil.copy2(source_path, dest_path)
            logger.info(f"Logo saved: {dest_path}")

            return str(dest_path)

        except Exception as e:
            logger.error(f"Failed to save logo: {e}")
            return None

    def _save_device_token(self, token: str, user_id: int):
        """Save device token to local file."""
        try:
            DATA_DIR.mkdir(parents=True, exist_ok=True)
            data = {'token': token, 'user_id': user_id}
            DEVICE_TOKEN_FILE.write_text(json.dumps(data))
            logger.info("Device token saved")
        except Exception as e:
            logger.error(f"Failed to save device token: {e}")

    def check_device_token(self) -> Optional[dict]:
        """Check if a valid device token exists for auto-login."""
        try:
            if not DEVICE_TOKEN_FILE.exists():
                return None

            data = json.loads(DEVICE_TOKEN_FILE.read_text())
            token = data.get('token')
            user_id = data.get('user_id')

            if not token or not user_id:
                return None

            cursor = self.db.cursor()
            cursor.execute("""
                SELECT id, name, email, business_name, business_email, phone, logo_path, device_token
                FROM users
                WHERE id = ?
            """, (user_id,))

            user = cursor.fetchone()
            if not user:
                self._clear_device_token()
                return None

            db_user_id, name, email, business_name, business_email, phone, logo_path, db_token = user

            if not db_token or not secrets.compare_digest(token, db_token):
                self._clear_device_token()
                return None

            cursor.execute("UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?", (user_id,))
            self.db.commit()

            return {
                'id': db_user_id,
                'name': name,
                'email': email,
                'business_name': business_name,
                'business_email': business_email,
                'phone': phone,
                'logo_path': logo_path
            }

        except Exception as e:
            logger.error(f"Device token check error: {e}")
            return None

    def _clear_device_token(self):
        """Clear saved device token."""
        try:
            if DEVICE_TOKEN_FILE.exists():
                DEVICE_TOKEN_FILE.unlink()
                logger.info("Device token cleared")
        except Exception as e:
            logger.error(f"Failed to clear device token: {e}")

    def logout(self, user_id: int = None):
        """Logout and clear device token."""
        if user_id:
            try:
                cursor = self.db.cursor()
                cursor.execute("UPDATE users SET device_token = NULL WHERE id = ?", (user_id,))
                self.db.commit()
            except Exception as e:
                logger.error(f"Failed to clear DB token: {e}")

        self._clear_device_token()
        logger.info("User logged out")

    def user_exists(self) -> bool:
        """Check if any users exist in the database."""
        try:
            cursor = self.db.cursor()
            cursor.execute("SELECT COUNT(*) FROM users")
            count = cursor.fetchone()[0]
            return count > 0
        except Exception:
            return False
