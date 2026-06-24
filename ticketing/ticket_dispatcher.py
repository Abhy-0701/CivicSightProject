from ticketing.ticket_model import Ticket


def create_and_dispatch_ticket(
    report: dict,
    latitude: float,
    longitude: float,
    image_path: str,
) -> dict:
    """
    Creates a ticket from the report and stores it in SQLite.

    Args:
        report: Full dict from main.py process_report()
        latitude: GPS latitude coordinate
        longitude: GPS longitude coordinate
        image_path: Path to the photo file

    Returns:
        {
            "success": bool,
            "ticket_id": str or None,
            "error": str or None
        }
    """
    try:
        # Validate that it's a valid civic issue
        if not report.get("vision_analysis", {}).get("is_valid_civic_issue"):
            return {
                "success": False,
                "ticket_id": None,
                "error": "Photo was not classified as a valid civic issue. Ticket not created."
            }

        # Validate that an authority was resolved
        authority = report.get("authority", {})
        if not authority.get("responsible_authority"):
            return {
                "success": False,
                "ticket_id": None,
                "error": "No authority could be determined. Ticket not created."
            }

        # Create the ticket
        ticket_id = Ticket.create_ticket(report, latitude, longitude, image_path)

        return {
            "success": True,
            "ticket_id": ticket_id,
            "error": None
        }

    except ValueError as e:
        return {
            "success": False,
            "ticket_id": None,
            "error": f"Validation error: {str(e)}"
        }
    except Exception as e:
        return {
            "success": False,
            "ticket_id": None,
            "error": f"Ticket creation failed: {str(e)}"
        }
