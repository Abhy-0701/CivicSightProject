import sqlite3
import uuid
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "tickets.db"


class Ticket:
    @staticmethod
    def init_db() -> None:
        """Initialize SQLite database with tickets table if it doesn't exist."""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute("""

            CREATE TABLE IF NOT EXISTS tickets (
                id TEXT PRIMARY KEY,
                ticket_id VARCHAR(50) UNIQUE,
                issue_type VARCHAR(100),
                authority VARCHAR(100),
                latitude DECIMAL(10,8),
                longitude DECIMAL(11,8),
                address TEXT,
                image_url TEXT,
                confidence_score FLOAT,
                description TEXT,
                status VARCHAR(50),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()

    @staticmethod
    def _get_next_ticket_number() -> int:
        """Get the next sequential ticket number."""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM tickets")
        count = cursor.fetchone()[0]
        conn.close()

        return count + 1

    @staticmethod
    def create_ticket(
        report: dict,
        latitude: float,
        longitude: float,
        image_path: str,
    ) -> str:
        """
        Create a new ticket from a report and store it in the database.

        Args:
            report: Full dict from main.py process_report()
            latitude: GPS latitude
            longitude: GPS longitude
            image_path: Path to the image file

        Returns:
            ticket_id (e.g., "CIV-2026-00001")

        Raises:
            ValueError: If report is missing required fields
            sqlite3.IntegrityError: If ticket creation fails
        """
        if not report.get("vision_analysis", {}).get("is_valid_civic_issue"):
            raise ValueError("Cannot create ticket for invalid civic issue")

        vision = report["vision_analysis"]
        location = report["location"]
        authority = report.get("authority", {})

        # Extract authority name
        authority_name = authority.get("responsible_authority", "Unknown")

        # Generate IDs
        unique_id = str(uuid.uuid4())
        ticket_number = Ticket._get_next_ticket_number()
        current_year = datetime.now().year
        ticket_id = f"CIV-{current_year}-{ticket_number:05d}"

        # Extract confidence score (handle both int and float)
        confidence = vision.get("confidence_score", 0.0)
        if isinstance(confidence, str):
            try:
                confidence = float(confidence)
            except ValueError:
                confidence = 0.0

        # Insert into database
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO tickets (
                id,
                ticket_id,
                issue_type,
                authority,
                latitude,
                longitude,
                address,
                image_url,
                confidence_score,
                description,
                status,
                created_at,
                updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            unique_id,
            ticket_id,
            vision.get("issue_type", "Unknown"),
            authority_name,
            latitude,
            longitude,
            location.get("full_address", ""),
            image_path,
            confidence,
            report.get("description", ""), # Added description here
            "pending",
            datetime.now().isoformat(),
            datetime.now().isoformat(),
        ))

        conn.commit()
        conn.close()

        return ticket_id

    @staticmethod
    def get_ticket(ticket_id: str) -> dict:
        """
        Retrieve ticket details by ticket_id.

        Args:
            ticket_id: The ticket ID (e.g., "CIV-2026-00001")

        Returns:
            Dict with ticket details or empty dict if not found
        """
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM tickets WHERE ticket_id = ?", (ticket_id,))
        row = cursor.fetchone()
        conn.close()

        if row:
            return dict(row)
        return {}

    @staticmethod
    def update_status(ticket_id: str, new_status: str) -> bool:
        """
        Update ticket status and updated_at timestamp.

        Args:
            ticket_id: The ticket ID
            new_status: New status (pending, rejected, resolved, in_progress)

        Returns:
            True if update succeeded, False otherwise
        """
        valid_statuses = ["pending", "rejected", "resolved", "in_progress"]
        if new_status not in valid_statuses:
            raise ValueError(f"Invalid status. Must be one of: {', '.join(valid_statuses)}")

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE tickets
            SET status = ?, updated_at = ?
            WHERE ticket_id = ?
        """, (new_status, datetime.now().isoformat(), ticket_id))

        conn.commit()
        success = cursor.rowcount > 0
        conn.close()

        return success

    @staticmethod
    def list_all_tickets() -> list:
        """Get all tickets from database."""
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM tickets ORDER BY created_at DESC")
        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]