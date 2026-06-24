# Main orchestrator for the CivicSight pipeline.
#
# Flow:
#   Photo + GPS coordinates
#     -> geocode.reverse_geocode_osm()       (lat/lng -> address + road name)
#     -> imageDesc.analyze_image()           (photo -> issue type, severity, description)
#     -> authRes.resolve_authority()         (road name -> responsible authority)
#     -> ticketing.create_and_dispatch_ticket()  (create ticket + store in database)
#   -> merged JSON result + ticket ID
import json
import sys

from authorityResolution.authRes import resolve_authority
from reverseGeoEncoding.geocode import reverse_geocode_osm
from imageDescription.imageDesc import analyze_image
from ticketing.ticket_dispatcher import create_and_dispatch_ticket
from ticketing.ticket_model import Ticket


def process_report(image_path: str, latitude: float, longitude: float) -> dict:
    """
    Runs the full CivicSight pipeline on a single photo + coordinate pair.

    Args:
        image_path: Local path to the photo (jpg/png/webp).
        latitude: GPS latitude of the report.
        longitude: GPS longitude of the report.

    Returns:
        A merged dict containing location info, vision analysis, and
        authority resolution. If the photo isn't a valid civic issue,
        authority resolution is skipped.
    """
    # 1. Reverse geocode the coordinates to get an address + road name
    location = reverse_geocode_osm(latitude, longitude)

    # 2. Run vision analysis on the photo
    with open(image_path, "rb") as f:
        image_bytes = f.read()

    mime_type = _guess_mime_type(image_path)
    vision_raw = analyze_image(image_bytes, mime_type=mime_type)
    vision_result = json.loads(vision_raw)

    result = {
        "location": location,
        "vision_analysis": vision_result,
        "authority": None,
    }

    # 3. Only resolve authority if the photo is a genuine civic issue
    if vision_result.get("is_valid_civic_issue"):
        road_name = location.get("road") or ""
        if road_name:
            authority_raw = resolve_authority(road_name)
            result["authority"] = json.loads(authority_raw)
        else:
            result["authority"] = {
                "error": "No road name could be extracted from coordinates; "
                         "authority resolution skipped."
            }
    else:
        result["authority"] = {
            "skipped_reason": "Photo was not classified as a valid civic issue."
        }

    return result


def _guess_mime_type(path: str) -> str:
    lower = path.lower()
    if lower.endswith(".png"):
        return "image/png"
    if lower.endswith(".webp"):
        return "image/webp"
    return "image/jpeg"


def _pretty_print(result: dict) -> None:
    print("\n========== CivicSight Report ==========")
    print(f"Address      : {result['location']['full_address']}")
    print(f"Road         : {result['location']['road'] or '(not found)'}")
    print("-" * 40)
    va = result["vision_analysis"]
    print(f"Valid issue? : {va.get('is_valid_civic_issue')}")
    if va.get("is_valid_civic_issue"):
        print(f"Issue type   : {va.get('issue_type')}")
        print(f"Severity     : {va.get('severity')}")
        print(f"Description  : {va.get('description')}")
        print(f"Confidence   : {va.get('confidence_score')}")
    print("-" * 40)
    auth = result["authority"]
    if auth and auth.get("responsible_authority"):
        print(f"Authority    : {auth.get('responsible_authority')}")
        print(f"Confidence   : {auth.get('confidence_score')}")
        print(f"Reasoning    : {auth.get('reasoning')}")
    else:
        print(f"Authority    : skipped — {auth}")
    print("========================================\n")


if __name__ == "__main__":
    # Usage: python main.py <image_path> <latitude> <longitude>
    if len(sys.argv) != 4:
        print("Usage: python main.py <image_path> <latitude> <longitude>")
        print("Example: python main.py photo.jpg 28.701220 77.270935")
        sys.exit(1)

    img_path = sys.argv[1]
    lat = float(sys.argv[2])
    lng = float(sys.argv[3])

    try:
        # Initialize database on startup
        Ticket.init_db()

        # Process the report through the pipeline
        report = process_report(img_path, lat, lng)
        _pretty_print(report)

        # Create ticket if it's a valid civic issue with authority
        ticket_result = create_and_dispatch_ticket(report, lat, lng, img_path)

        if ticket_result["success"]:
            print(f"✓ Ticket Created: {ticket_result['ticket_id']}")
        else:
            print(f"✗ Ticket Creation Failed: {ticket_result['error']}")

        print("\n--- Full JSON ---")
        print(json.dumps(report, indent=2))

    except FileNotFoundError:
        print(f"Image not found at '{img_path}'.")
    except Exception as e:
        print(f"An error occurred: {e}")