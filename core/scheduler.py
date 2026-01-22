"""
CHAIRMAN - Appointment Scheduler Module

This module handles all appointment booking, scheduling, and management logic.
"""
from __future__ import annotations

from datetime import datetime, timedelta, date
from typing import Any

from core.logging_config import get_logger
from core.validators import Validator
from data.db import get_connection

logger = get_logger(__name__)


class SchedulerError(Exception):
    """Base exception for scheduler-related errors."""
    pass


class TimeSlotUnavailableError(SchedulerError):
    """Raised when attempting to book an unavailable time slot."""
    pass


class InvalidAppointmentError(SchedulerError):
    """Raised when appointment data is invalid."""
    pass


class Scheduler:
    """
    Manages appointment scheduling, booking, and availability.

    This class provides methods for:
    - Checking time slot availability
    - Booking new appointments
    - Listing appointments for a given date
    - Managing appointment payment status
    - Canceling appointments
    """

    def __init__(self):
        """Initialize the scheduler with a database connection."""
        self.conn = get_connection()
        logger.debug("Scheduler initialized")

    def is_time_available(
        self,
        start: datetime,
        end: datetime,
        exclude_appointment_id: int | None = None
    ) -> bool:
        """
        Check if a time slot is available for booking.

        Args:
            start: Start time of the slot
            end: End time of the slot
            exclude_appointment_id: Optional appointment ID to exclude from check
                                   (useful when rescheduling)

        Returns:
            True if the time slot is available, False otherwise
        """
        try:
            cursor = self.conn.cursor()

            if exclude_appointment_id:
                cursor.execute("""
                    SELECT COUNT(*) FROM appointments
                    WHERE id != ? AND NOT (end_time <= ? OR start_time >= ?)
                """, (exclude_appointment_id, start.isoformat(), end.isoformat()))
            else:
                cursor.execute("""
                    SELECT COUNT(*) FROM appointments
                    WHERE NOT (end_time <= ? OR start_time >= ?)
                """, (start.isoformat(), end.isoformat()))

            count = cursor.fetchone()[0]
            is_available = count == 0

            logger.debug(
                f"Time slot {start.isoformat()} to {end.isoformat()} "
                f"{'is' if is_available else 'is not'} available"
            )

            return is_available

        except Exception as e:
            logger.error(f"Error checking time availability: {e}")
            raise SchedulerError(f"Failed to check time availability: {e}") from e

    def book(
        self,
        client_id: int,
        service_id: int,
        start: datetime,
        paid: bool = False,
        payment_method: str = "",
        notes: str = "",
    ) -> int:
        """
        Book a new appointment.

        Args:
            client_id: ID of the client
            service_id: ID of the service
            start: Start time of the appointment
            paid: Whether the appointment has been paid
            payment_method: Payment method used (if paid)
            notes: Optional notes for the appointment

        Returns:
            ID of the newly created appointment

        Raises:
            InvalidAppointmentError: If appointment data is invalid
            TimeSlotUnavailableError: If the requested time slot is not available
            SchedulerError: If booking fails for any other reason
        """
        try:
            # Validate notes
            notes_validation = Validator.validate_notes(notes)
            if not notes_validation:
                raise InvalidAppointmentError(notes_validation.error_message)

            # Get service details
            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT duration_minutes, buffer_minutes FROM services WHERE id=?",
                (service_id,),
            )
            service_row = cursor.fetchone()

            if not service_row:
                logger.warning(f"Attempted to book with non-existent service ID: {service_id}")
                raise InvalidAppointmentError(f"Service with ID {service_id} does not exist")

            duration_minutes, buffer_minutes = service_row
            end = start + timedelta(minutes=int(duration_minutes) + int(buffer_minutes))

            # Check availability
            if not self.is_time_available(start, end):
                logger.warning(
                    f"Time slot {start.isoformat()} to {end.isoformat()} is not available"
                )
                raise TimeSlotUnavailableError(
                    f"Time slot from {start.strftime('%I:%M %p')} to {end.strftime('%I:%M %p')} "
                    f"is not available"
                )

            # Book the appointment
            cursor.execute("""
                INSERT INTO appointments
                (client_id, service_id, start_time, end_time, paid, payment_method, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                client_id,
                service_id,
                start.isoformat(),
                end.isoformat(),
                1 if paid else 0,
                payment_method or "",
                notes or "",
            ))

            self.conn.commit()
            appointment_id = cursor.lastrowid

            logger.info(
                f"Booked appointment {appointment_id} for client {client_id}, "
                f"service {service_id} at {start.isoformat()}"
            )

            return appointment_id

        except (InvalidAppointmentError, TimeSlotUnavailableError):
            # Re-raise these specific exceptions
            raise
        except Exception as e:
            logger.error(f"Error booking appointment: {e}")
            self.conn.rollback()
            raise SchedulerError(f"Failed to book appointment: {e}") from e

    def list_for_date(self, day: date) -> list[dict[str, Any]]:
        """
        Get all appointments for a specific date with full details.

        Args:
            day: The date to get appointments for

        Returns:
            List of appointment dictionaries with client and service details.
            Each dict contains consistent keys that match UI expectations:
            - appointment_id
            - start_time
            - end_time
            - paid
            - payment_method
            - notes
            - client (name)
            - client_id
            - client_phone
            - service (name)
            - service_id
            - service_price
            - service_duration
            - service_buffer
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT
                    a.id,
                    a.start_time,
                    a.end_time,
                    a.paid,
                    a.payment_method,
                    a.notes,
                    c.id,
                    c.name,
                    c.phone,
                    s.id,
                    s.name,
                    s.price,
                    s.duration_minutes,
                    s.buffer_minutes
                FROM appointments a
                JOIN clients c ON c.id = a.client_id
                JOIN services s ON s.id = a.service_id
                WHERE date(a.start_time) = ?
                ORDER BY a.start_time ASC
            """, (day.isoformat(),))

            appointments = []
            for row in cursor.fetchall():
                appointments.append({
                    # Appointment details
                    "appointment_id": row[0],
                    "start_time": row[1],
                    "end_time": row[2],
                    "paid": bool(row[3]),
                    "payment_method": row[4] or "",
                    "notes": row[5] or "",

                    # Client details
                    "client_id": row[6],
                    "client": row[7],  # Name for UI display
                    "client_name": row[7],  # Explicit name field
                    "client_phone": row[8] or "",

                    # Service details
                    "service_id": row[9],
                    "service": row[10],  # Name for UI display
                    "service_name": row[10],  # Explicit name field
                    "service_price": float(row[11]),
                    "service_duration": int(row[12]),
                    "service_buffer": int(row[13]),
                })

            logger.debug(f"Retrieved {len(appointments)} appointments for {day.isoformat()}")
            return appointments

        except Exception as e:
            logger.error(f"Error listing appointments for {day.isoformat()}: {e}")
            raise SchedulerError(f"Failed to retrieve appointments: {e}") from e

    def toggle_paid(self, appointment_id: int) -> bool:
        """
        Toggle the paid status of an appointment.

        Args:
            appointment_id: ID of the appointment to toggle

        Returns:
            New paid status (True if now paid, False if now unpaid)

        Raises:
            InvalidAppointmentError: If appointment doesn't exist
            SchedulerError: If toggle fails
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT paid FROM appointments WHERE id=?", (appointment_id,))
            row = cursor.fetchone()

            if not row:
                logger.warning(f"Attempted to toggle non-existent appointment ID: {appointment_id}")
                raise InvalidAppointmentError(f"Appointment with ID {appointment_id} does not exist")

            new_paid_status = 0 if int(row[0]) == 1 else 1
            cursor.execute(
                "UPDATE appointments SET paid=? WHERE id=?",
                (new_paid_status, appointment_id)
            )
            self.conn.commit()

            logger.info(
                f"Toggled payment status for appointment {appointment_id} "
                f"to {'paid' if new_paid_status else 'unpaid'}"
            )

            return bool(new_paid_status)

        except InvalidAppointmentError:
            raise
        except Exception as e:
            logger.error(f"Error toggling payment status for appointment {appointment_id}: {e}")
            self.conn.rollback()
            raise SchedulerError(f"Failed to toggle payment status: {e}") from e

    def delete(self, appointment_id: int) -> None:
        """
        Delete (cancel) an appointment.

        Args:
            appointment_id: ID of the appointment to delete

        Raises:
            InvalidAppointmentError: If appointment doesn't exist
            SchedulerError: If deletion fails
        """
        try:
            cursor = self.conn.cursor()

            # Check if appointment exists
            cursor.execute("SELECT id FROM appointments WHERE id=?", (appointment_id,))
            if not cursor.fetchone():
                logger.warning(f"Attempted to delete non-existent appointment ID: {appointment_id}")
                raise InvalidAppointmentError(f"Appointment with ID {appointment_id} does not exist")

            cursor.execute("DELETE FROM appointments WHERE id=?", (appointment_id,))
            self.conn.commit()

            logger.info(f"Deleted appointment {appointment_id}")

        except InvalidAppointmentError:
            raise
        except Exception as e:
            logger.error(f"Error deleting appointment {appointment_id}: {e}")
            self.conn.rollback()
            raise SchedulerError(f"Failed to delete appointment: {e}") from e

    def get_appointment(self, appointment_id: int) -> dict[str, Any] | None:
        """
        Get details for a specific appointment.

        Args:
            appointment_id: ID of the appointment

        Returns:
            Appointment dictionary with full details, or None if not found
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT
                    a.id,
                    a.start_time,
                    a.end_time,
                    a.paid,
                    a.payment_method,
                    a.notes,
                    c.id,
                    c.name,
                    c.phone,
                    s.id,
                    s.name,
                    s.price,
                    s.duration_minutes,
                    s.buffer_minutes
                FROM appointments a
                JOIN clients c ON c.id = a.client_id
                JOIN services s ON s.id = a.service_id
                WHERE a.id = ?
            """, (appointment_id,))

            row = cursor.fetchone()
            if not row:
                return None

            return {
                "appointment_id": row[0],
                "start_time": row[1],
                "end_time": row[2],
                "paid": bool(row[3]),
                "payment_method": row[4] or "",
                "notes": row[5] or "",
                "client_id": row[6],
                "client": row[7],
                "client_name": row[7],
                "client_phone": row[8] or "",
                "service_id": row[9],
                "service": row[10],
                "service_name": row[10],
                "service_price": float(row[11]),
                "service_duration": int(row[12]),
                "service_buffer": int(row[13]),
            }

        except Exception as e:
            logger.error(f"Error retrieving appointment {appointment_id}: {e}")
            raise SchedulerError(f"Failed to retrieve appointment: {e}") from e
