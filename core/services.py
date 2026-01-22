"""
CHAIRMAN - Service Management Module

This module handles all service-related operations including CRUD operations.
"""
from __future__ import annotations

from core.logging_config import get_logger
from core.validators import Validator
from data.db import get_connection
from data.models import Service

logger = get_logger(__name__)


class ServiceError(Exception):
    """Base exception for service-related errors."""
    pass


class InvalidServiceDataError(ServiceError):
    """Raised when service data is invalid."""
    pass


class DuplicateServiceError(ServiceError):
    """Raised when attempting to create a duplicate service."""
    pass


class ServiceManager:
    """
    Manages service data and operations.

    This class provides methods for:
    - Creating new services
    - Retrieving all services
    - Updating service information
    - Managing service records
    """

    def __init__(self):
        """Initialize the service manager with a database connection."""
        self.conn = get_connection()
        logger.debug("ServiceManager initialized")

    def create(
        self,
        name: str,
        price: float,
        duration_minutes: int,
        buffer_minutes: int = 0
    ) -> int:
        """
        Create a new service.

        Args:
            name: Service name
            price: Service price
            duration_minutes: Service duration in minutes
            buffer_minutes: Buffer time after service (optional, defaults to 0)

        Returns:
            ID of the newly created service

        Raises:
            InvalidServiceDataError: If service data is invalid
            DuplicateServiceError: If service already exists
            ServiceError: If creation fails for any other reason
        """
        try:
            # Validate name
            name_validation = Validator.validate_service_name(name)
            if not name_validation:
                raise InvalidServiceDataError(name_validation.error_message)

            # Validate price
            price_validation = Validator.validate_price(price)
            if not price_validation:
                raise InvalidServiceDataError(price_validation.error_message)

            # Validate duration
            duration_validation = Validator.validate_duration(duration_minutes)
            if not duration_validation:
                raise InvalidServiceDataError(duration_validation.error_message)

            # Validate buffer (use same validation as duration)
            buffer_validation = Validator.validate_duration(buffer_minutes)
            if not buffer_validation:
                raise InvalidServiceDataError(f"Buffer time: {buffer_validation.error_message}")

            # Sanitize name
            name = Validator.sanitize_input(name)

            # Check for duplicate
            if self._service_exists(name):
                logger.warning(f"Attempted to create duplicate service: {name}")
                raise DuplicateServiceError(
                    f"A service with the name '{name}' already exists"
                )

            # Create service
            cursor = self.conn.cursor()
            cursor.execute(
                "INSERT INTO services VALUES (NULL, ?, ?, ?, ?)",
                (name, float(price), int(duration_minutes), int(buffer_minutes)),
            )
            self.conn.commit()
            service_id = cursor.lastrowid

            logger.info(f"Created new service: {name} (ID: {service_id}) - ${price}, {duration_minutes}min")
            return service_id

        except (InvalidServiceDataError, DuplicateServiceError):
            raise
        except Exception as e:
            logger.error(f"Error creating service: {e}")
            self.conn.rollback()
            raise ServiceError(f"Failed to create service: {e}") from e

    def all(self) -> list[Service]:
        """
        Retrieve all services.

        Returns:
            List of all Service objects

        Raises:
            ServiceError: If retrieval fails
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT id, name, price, duration_minutes, buffer_minutes FROM services ORDER BY name"
            )
            services = [Service(*row) for row in cursor.fetchall()]

            logger.debug(f"Retrieved {len(services)} services")
            return services

        except Exception as e:
            logger.error(f"Error retrieving services: {e}")
            raise ServiceError(f"Failed to retrieve services: {e}") from e

    def get(self, service_id: int) -> Service | None:
        """
        Get a specific service by ID.

        Args:
            service_id: ID of the service to retrieve

        Returns:
            Service object if found, None otherwise

        Raises:
            ServiceError: If retrieval fails
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT id, name, price, duration_minutes, buffer_minutes FROM services WHERE id = ?",
                (service_id,)
            )
            row = cursor.fetchone()

            if row:
                return Service(*row)
            return None

        except Exception as e:
            logger.error(f"Error retrieving service {service_id}: {e}")
            raise ServiceError(f"Failed to retrieve service: {e}") from e

    def update(
        self,
        service_id: int,
        name: str | None = None,
        price: float | None = None,
        duration_minutes: int | None = None,
        buffer_minutes: int | None = None
    ) -> bool:
        """
        Update service information.

        Args:
            service_id: ID of the service to update
            name: New name (optional)
            price: New price (optional)
            duration_minutes: New duration (optional)
            buffer_minutes: New buffer time (optional)

        Returns:
            True if update was successful

        Raises:
            InvalidServiceDataError: If new data is invalid
            ServiceError: If update fails
        """
        try:
            # Get existing service
            existing = self.get(service_id)
            if not existing:
                raise InvalidServiceDataError(f"Service with ID {service_id} does not exist")

            # Validate and prepare updates
            updates = []
            values = []

            if name is not None:
                name_validation = Validator.validate_service_name(name)
                if not name_validation:
                    raise InvalidServiceDataError(name_validation.error_message)
                updates.append("name = ?")
                values.append(Validator.sanitize_input(name))

            if price is not None:
                price_validation = Validator.validate_price(price)
                if not price_validation:
                    raise InvalidServiceDataError(price_validation.error_message)
                updates.append("price = ?")
                values.append(float(price))

            if duration_minutes is not None:
                duration_validation = Validator.validate_duration(duration_minutes)
                if not duration_validation:
                    raise InvalidServiceDataError(duration_validation.error_message)
                updates.append("duration_minutes = ?")
                values.append(int(duration_minutes))

            if buffer_minutes is not None:
                buffer_validation = Validator.validate_duration(buffer_minutes)
                if not buffer_validation:
                    raise InvalidServiceDataError(f"Buffer time: {buffer_validation.error_message}")
                updates.append("buffer_minutes = ?")
                values.append(int(buffer_minutes))

            if not updates:
                return True  # Nothing to update

            # Perform update
            values.append(service_id)
            query = f"UPDATE services SET {', '.join(updates)} WHERE id = ?"

            cursor = self.conn.cursor()
            cursor.execute(query, values)
            self.conn.commit()

            logger.info(f"Updated service {service_id}")
            return True

        except InvalidServiceDataError:
            raise
        except Exception as e:
            logger.error(f"Error updating service {service_id}: {e}")
            self.conn.rollback()
            raise ServiceError(f"Failed to update service: {e}") from e

    def delete(self, service_id: int) -> bool:
        """
        Delete a service.

        Args:
            service_id: ID of the service to delete

        Returns:
            True if deletion was successful

        Raises:
            ServiceError: If deletion fails
        """
        try:
            cursor = self.conn.cursor()

            # Check if service has appointments
            cursor.execute(
                "SELECT COUNT(*) FROM appointments WHERE service_id = ?",
                (service_id,)
            )
            appointment_count = cursor.fetchone()[0]

            if appointment_count > 0:
                raise ServiceError(
                    f"Cannot delete service with existing appointments. "
                    f"This service has {appointment_count} appointment(s)."
                )

            # Delete service
            cursor.execute("DELETE FROM services WHERE id = ?", (service_id,))
            self.conn.commit()

            logger.info(f"Deleted service {service_id}")
            return True

        except ServiceError:
            raise
        except Exception as e:
            logger.error(f"Error deleting service {service_id}: {e}")
            self.conn.rollback()
            raise ServiceError(f"Failed to delete service: {e}") from e

    def _service_exists(self, name: str) -> bool:
        """
        Check if a service with the same name already exists.

        Args:
            name: Service name to check

        Returns:
            True if service exists, False otherwise
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT COUNT(*) FROM services WHERE LOWER(name) = LOWER(?)",
                (name.strip(),)
            )
            return cursor.fetchone()[0] > 0

        except Exception:
            # If we can't check, assume it doesn't exist to allow creation
            return False
