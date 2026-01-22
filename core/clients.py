"""
CHAIRMAN - Client Management Module

This module handles all client-related operations including CRUD operations.
"""
from __future__ import annotations

from core.logging_config import get_logger
from core.validators import Validator
from data.db import get_connection
from data.models import Client

logger = get_logger(__name__)


class ClientError(Exception):
    """Base exception for client-related errors."""
    pass


class InvalidClientDataError(ClientError):
    """Raised when client data is invalid."""
    pass


class DuplicateClientError(ClientError):
    """Raised when attempting to create a duplicate client."""
    pass


class ClientService:
    """
    Manages client data and operations.

    This class provides methods for:
    - Creating new clients
    - Retrieving all clients
    - Updating client information
    - Managing client records
    """

    def __init__(self):
        """Initialize the client service with a database connection."""
        self.conn = get_connection()
        logger.debug("ClientService initialized")

    def create(self, name: str, phone: str = "", notes: str = "") -> int:
        """
        Create a new client.

        Args:
            name: Client's full name
            phone: Client's phone number (optional)
            notes: Additional notes about the client (optional)

        Returns:
            ID of the newly created client

        Raises:
            InvalidClientDataError: If client data is invalid
            DuplicateClientError: If client already exists
            ClientError: If creation fails for any other reason
        """
        try:
            # Validate name
            name_validation = Validator.validate_client_name(name)
            if not name_validation:
                raise InvalidClientDataError(name_validation.error_message)

            # Validate phone
            phone_validation = Validator.validate_phone(phone)
            if not phone_validation:
                raise InvalidClientDataError(phone_validation.error_message)

            # Sanitize inputs
            name = Validator.sanitize_input(name)
            phone = Validator.sanitize_input(phone) if phone else ""
            notes = Validator.sanitize_input(notes) if notes else ""

            # Check for duplicate
            if self._client_exists(name, phone):
                logger.warning(f"Attempted to create duplicate client: {name}")
                raise DuplicateClientError(
                    f"A client with the name '{name}' already exists"
                )

            # Format phone number
            if phone:
                phone = Validator.format_phone(phone)

            # Create client
            cursor = self.conn.cursor()
            cursor.execute(
                "INSERT INTO clients (name, phone, notes) VALUES (?, ?, ?)",
                (name, phone, notes)
            )
            self.conn.commit()
            client_id = cursor.lastrowid

            logger.info(f"Created new client: {name} (ID: {client_id})")
            return client_id

        except (InvalidClientDataError, DuplicateClientError):
            raise
        except Exception as e:
            logger.error(f"Error creating client: {e}")
            self.conn.rollback()
            raise ClientError(f"Failed to create client: {e}") from e

    def all(self) -> list[Client]:
        """
        Retrieve all clients.

        Returns:
            List of all Client objects

        Raises:
            ClientError: If retrieval fails
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT id, name, phone, notes, no_show_count FROM clients ORDER BY name")
            clients = [Client(*row) for row in cursor.fetchall()]

            logger.debug(f"Retrieved {len(clients)} clients")
            return clients

        except Exception as e:
            logger.error(f"Error retrieving clients: {e}")
            raise ClientError(f"Failed to retrieve clients: {e}") from e

    def get(self, client_id: int) -> Client | None:
        """
        Get a specific client by ID.

        Args:
            client_id: ID of the client to retrieve

        Returns:
            Client object if found, None otherwise

        Raises:
            ClientError: If retrieval fails
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT id, name, phone, notes, no_show_count FROM clients WHERE id = ?",
                (client_id,)
            )
            row = cursor.fetchone()

            if row:
                return Client(*row)
            return None

        except Exception as e:
            logger.error(f"Error retrieving client {client_id}: {e}")
            raise ClientError(f"Failed to retrieve client: {e}") from e

    def update(
        self,
        client_id: int,
        name: str | None = None,
        phone: str | None = None,
        notes: str | None = None
    ) -> bool:
        """
        Update client information.

        Args:
            client_id: ID of the client to update
            name: New name (optional)
            phone: New phone number (optional)
            notes: New notes (optional)

        Returns:
            True if update was successful

        Raises:
            InvalidClientDataError: If new data is invalid
            ClientError: If update fails
        """
        try:
            # Get existing client
            existing = self.get(client_id)
            if not existing:
                raise InvalidClientDataError(f"Client with ID {client_id} does not exist")

            # Validate and prepare updates
            updates = []
            values = []

            if name is not None:
                name_validation = Validator.validate_client_name(name)
                if not name_validation:
                    raise InvalidClientDataError(name_validation.error_message)
                updates.append("name = ?")
                values.append(Validator.sanitize_input(name))

            if phone is not None:
                phone_validation = Validator.validate_phone(phone)
                if not phone_validation:
                    raise InvalidClientDataError(phone_validation.error_message)
                updates.append("phone = ?")
                values.append(Validator.format_phone(phone) if phone else "")

            if notes is not None:
                updates.append("notes = ?")
                values.append(Validator.sanitize_input(notes))

            if not updates:
                return True  # Nothing to update

            # Perform update
            values.append(client_id)
            query = f"UPDATE clients SET {', '.join(updates)} WHERE id = ?"

            cursor = self.conn.cursor()
            cursor.execute(query, values)
            self.conn.commit()

            logger.info(f"Updated client {client_id}")
            return True

        except InvalidClientDataError:
            raise
        except Exception as e:
            logger.error(f"Error updating client {client_id}: {e}")
            self.conn.rollback()
            raise ClientError(f"Failed to update client: {e}") from e

    def delete(self, client_id: int) -> bool:
        """
        Delete a client.

        Args:
            client_id: ID of the client to delete

        Returns:
            True if deletion was successful

        Raises:
            ClientError: If deletion fails
        """
        try:
            cursor = self.conn.cursor()

            # Check if client has appointments
            cursor.execute(
                "SELECT COUNT(*) FROM appointments WHERE client_id = ?",
                (client_id,)
            )
            appointment_count = cursor.fetchone()[0]

            if appointment_count > 0:
                raise ClientError(
                    f"Cannot delete client with existing appointments. "
                    f"This client has {appointment_count} appointment(s)."
                )

            # Delete client
            cursor.execute("DELETE FROM clients WHERE id = ?", (client_id,))
            self.conn.commit()

            logger.info(f"Deleted client {client_id}")
            return True

        except ClientError:
            raise
        except Exception as e:
            logger.error(f"Error deleting client {client_id}: {e}")
            self.conn.rollback()
            raise ClientError(f"Failed to delete client: {e}") from e

    def increment_no_show(self, client_id: int) -> None:
        """
        Increment the no-show count for a client.

        Args:
            client_id: ID of the client

        Raises:
            ClientError: If update fails
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "UPDATE clients SET no_show_count = no_show_count + 1 WHERE id = ?",
                (client_id,)
            )
            self.conn.commit()

            logger.info(f"Incremented no-show count for client {client_id}")

        except Exception as e:
            logger.error(f"Error incrementing no-show count for client {client_id}: {e}")
            self.conn.rollback()
            raise ClientError(f"Failed to update no-show count: {e}") from e

    def search(self, query: str) -> list[Client]:
        """
        Search for clients by name or phone number.

        Args:
            query: Search query

        Returns:
            List of matching Client objects

        Raises:
            ClientError: If search fails
        """
        try:
            cursor = self.conn.cursor()
            search_pattern = f"%{query}%"
            cursor.execute("""
                SELECT id, name, phone, notes, no_show_count
                FROM clients
                WHERE name LIKE ? OR phone LIKE ?
                ORDER BY name
            """, (search_pattern, search_pattern))

            clients = [Client(*row) for row in cursor.fetchall()]
            logger.debug(f"Search for '{query}' returned {len(clients)} results")
            return clients

        except Exception as e:
            logger.error(f"Error searching clients: {e}")
            raise ClientError(f"Failed to search clients: {e}") from e

    def _client_exists(self, name: str, phone: str = "") -> bool:
        """
        Check if a client with the same name already exists.

        Args:
            name: Client name to check
            phone: Client phone to check (optional)

        Returns:
            True if client exists, False otherwise
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT COUNT(*) FROM clients WHERE LOWER(name) = LOWER(?)",
                (name.strip(),)
            )
            return cursor.fetchone()[0] > 0

        except Exception:
            # If we can't check, assume it doesn't exist to allow creation
            return False
