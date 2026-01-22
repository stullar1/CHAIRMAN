"""
CHAIRMAN - Data Validation Module

This module provides centralized validation for all user inputs and data.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, time
from typing import Any

from config import ValidationRules


@dataclass
class ValidationResult:
    """Result of a validation check."""
    is_valid: bool
    error_message: str = ""

    def __bool__(self) -> bool:
        """Allow using ValidationResult in boolean context."""
        return self.is_valid


class Validator:
    """Centralized validation for all application data."""

    @staticmethod
    def validate_client_name(name: str | None) -> ValidationResult:
        """
        Validate client name.

        Args:
            name: Client name to validate

        Returns:
            ValidationResult with validation status and error message if invalid
        """
        if not name or not name.strip():
            return ValidationResult(False, "Client name cannot be empty")

        name = name.strip()

        if len(name) < ValidationRules.CLIENT_NAME_MIN_LENGTH:
            return ValidationResult(
                False,
                f"Client name must be at least {ValidationRules.CLIENT_NAME_MIN_LENGTH} characters"
            )

        if len(name) > ValidationRules.CLIENT_NAME_MAX_LENGTH:
            return ValidationResult(
                False,
                f"Client name cannot exceed {ValidationRules.CLIENT_NAME_MAX_LENGTH} characters"
            )

        # Check for valid characters (letters, spaces, hyphens, apostrophes)
        if not re.match(r"^[a-zA-Z\s\-'\.]+$", name):
            return ValidationResult(
                False,
                "Client name can only contain letters, spaces, hyphens, and apostrophes"
            )

        return ValidationResult(True)

    @staticmethod
    def validate_phone(phone: str | None) -> ValidationResult:
        """
        Validate phone number.

        Args:
            phone: Phone number to validate (can be empty)

        Returns:
            ValidationResult with validation status and error message if invalid
        """
        if not phone or not phone.strip():
            # Phone is optional, so empty is valid
            return ValidationResult(True)

        # Remove common formatting characters
        cleaned = re.sub(r'[\s\-\(\)\.]', '', phone)

        if not cleaned.isdigit():
            return ValidationResult(False, "Phone number can only contain digits and formatting characters")

        if len(cleaned) < ValidationRules.PHONE_MIN_LENGTH:
            return ValidationResult(
                False,
                f"Phone number must be at least {ValidationRules.PHONE_MIN_LENGTH} digits"
            )

        if len(cleaned) > ValidationRules.PHONE_MAX_LENGTH:
            return ValidationResult(
                False,
                f"Phone number cannot exceed {ValidationRules.PHONE_MAX_LENGTH} digits"
            )

        return ValidationResult(True)

    @staticmethod
    def validate_service_name(name: str | None) -> ValidationResult:
        """
        Validate service name.

        Args:
            name: Service name to validate

        Returns:
            ValidationResult with validation status and error message if invalid
        """
        if not name or not name.strip():
            return ValidationResult(False, "Service name cannot be empty")

        name = name.strip()

        if len(name) < ValidationRules.SERVICE_NAME_MIN_LENGTH:
            return ValidationResult(
                False,
                f"Service name must be at least {ValidationRules.SERVICE_NAME_MIN_LENGTH} characters"
            )

        if len(name) > ValidationRules.SERVICE_NAME_MAX_LENGTH:
            return ValidationResult(
                False,
                f"Service name cannot exceed {ValidationRules.SERVICE_NAME_MAX_LENGTH} characters"
            )

        return ValidationResult(True)

    @staticmethod
    def validate_price(price: Any) -> ValidationResult:
        """
        Validate service price.

        Args:
            price: Price to validate (can be string or number)

        Returns:
            ValidationResult with validation status and error message if invalid
        """
        try:
            price_float = float(price)
        except (ValueError, TypeError):
            return ValidationResult(False, "Price must be a valid number")

        if price_float < ValidationRules.SERVICE_MIN_PRICE:
            return ValidationResult(False, f"Price cannot be negative")

        if price_float > ValidationRules.SERVICE_MAX_PRICE:
            return ValidationResult(
                False,
                f"Price cannot exceed ${ValidationRules.SERVICE_MAX_PRICE:,.2f}"
            )

        return ValidationResult(True)

    @staticmethod
    def validate_duration(duration: Any) -> ValidationResult:
        """
        Validate service duration in minutes.

        Args:
            duration: Duration to validate (can be string or number)

        Returns:
            ValidationResult with validation status and error message if invalid
        """
        try:
            duration_int = int(duration)
        except (ValueError, TypeError):
            return ValidationResult(False, "Duration must be a valid number")

        if duration_int < ValidationRules.SERVICE_MIN_DURATION:
            return ValidationResult(
                False,
                f"Duration must be at least {ValidationRules.SERVICE_MIN_DURATION} minutes"
            )

        if duration_int > ValidationRules.SERVICE_MAX_DURATION:
            return ValidationResult(
                False,
                f"Duration cannot exceed {ValidationRules.SERVICE_MAX_DURATION} minutes"
            )

        return ValidationResult(True)

    @staticmethod
    def validate_notes(notes: str | None) -> ValidationResult:
        """
        Validate appointment notes.

        Args:
            notes: Notes to validate (can be empty)

        Returns:
            ValidationResult with validation status and error message if invalid
        """
        if not notes:
            # Notes are optional
            return ValidationResult(True)

        if len(notes) > ValidationRules.APPOINTMENT_NOTES_MAX_LENGTH:
            return ValidationResult(
                False,
                f"Notes cannot exceed {ValidationRules.APPOINTMENT_NOTES_MAX_LENGTH} characters"
            )

        return ValidationResult(True)

    @staticmethod
    def validate_time_slot(slot_time: time, business_start: time, business_end: time) -> ValidationResult:
        """
        Validate that a time slot falls within business hours.

        Args:
            slot_time: Time to validate
            business_start: Business opening time
            business_end: Business closing time

        Returns:
            ValidationResult with validation status and error message if invalid
        """
        if slot_time < business_start:
            return ValidationResult(
                False,
                f"Time is before business hours (opens at {business_start.strftime('%I:%M %p')})"
            )

        if slot_time >= business_end:
            return ValidationResult(
                False,
                f"Time is after business hours (closes at {business_end.strftime('%I:%M %p')})"
            )

        return ValidationResult(True)

    @staticmethod
    def validate_datetime_in_future(dt: datetime) -> ValidationResult:
        """
        Validate that a datetime is in the future.

        Args:
            dt: Datetime to validate

        Returns:
            ValidationResult with validation status and error message if invalid
        """
        if dt < datetime.now():
            return ValidationResult(False, "Appointment time must be in the future")

        return ValidationResult(True)

    @staticmethod
    def format_phone(phone: str | None) -> str:
        """
        Format a phone number for display.

        Args:
            phone: Raw phone number

        Returns:
            Formatted phone number (e.g., "(123) 456-7890")
        """
        if not phone:
            return ""

        # Remove all non-digit characters
        digits = re.sub(r'\D', '', phone)

        # Format based on length
        if len(digits) == 10:
            return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
        elif len(digits) == 11 and digits[0] == '1':
            return f"+1 ({digits[1:4]}) {digits[4:7]}-{digits[7:]}"
        else:
            # Return as-is if we can't format it
            return phone

    @staticmethod
    def sanitize_input(text: str | None) -> str:
        """
        Sanitize user input by removing potentially dangerous characters.

        Args:
            text: Text to sanitize

        Returns:
            Sanitized text
        """
        if not text:
            return ""

        # Remove leading/trailing whitespace
        sanitized = text.strip()

        # Remove control characters except newlines and tabs
        sanitized = ''.join(char for char in sanitized if char.isprintable() or char in '\n\t')

        return sanitized
