# This module converts GPS coordinates into a human-readable address and
# extracts the most specific location identifier available (road name if
# tagged in OpenStreetMap, otherwise the nearest locality/neighbourhood),
# using OpenStreetMap's Nominatim reverse geocoding service.
import requests


def reverse_geocode_osm(latitude: float, longitude: float) -> dict:
    """
    Reverse geocodes a lat/lng pair into a full address, distinguishing
    between street-level ("road") and locality-level ("locality") matches,
    since many real-world coordinates (especially residential lanes) have
    no road tagged in OSM at all.

    Args:
        latitude: Latitude coordinate.
        longitude: Longitude coordinate.

    Returns:
        dict with keys:
            "full_address": str — full display address, or an error message.
            "road": str — road/street/highway name if OSM has one tagged,
                     else "".
            "locality": str — neighbourhood/suburb/district name, used as a
                     fallback when no road-level tag exists. "" if unavailable.
            "is_road_level": bool — True if "road" is non-empty, i.e. the
                     result is genuinely street-level rather than a fallback.
            "raw": dict — full Nominatim response (or {} on error), useful
                     for debugging or pulling additional fields later.
    """
    url = "https://nominatim.openstreetmap.org/reverse"
    headers = {
        "User-Agent": "CivicSightProject/1.0(ishurathore0000@gmail.com)"
    }
    params = {
        "format": "jsonv2",
        "lat": latitude,
        "lon": longitude,
        "addressdetails": 1,
        "zoom": 18,  # request street-level detail where available
    }

    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
    except requests.RequestException as e:
        return {
            "full_address": f"Error: request failed ({e})",
            "road": "",
            "locality": "",
            "is_road_level": False,
            "raw": {},
        }

    if response.status_code != 200:
        return {
            "full_address": f"Error: Status code {response.status_code}",
            "road": "",
            "locality": "",
            "is_road_level": False,
            "raw": {},
        }

    data = response.json()
    full_address = data.get("display_name", "Address not found")
    address_block = data.get("address", {})

    # Street-level identifiers, in order of preference.
    road = (
        address_block.get("road")
        or address_block.get("pedestrian")
        or address_block.get("highway")
        or address_block.get("residential")
        or ""
    )

    # Locality-level fallback, used only when no road-level tag exists.
    locality = (
        address_block.get("neighbourhood")
        or address_block.get("suburb")
        or address_block.get("city_district")
        or address_block.get("village")
        or ""
    )

    return {
        "full_address": full_address,
        "road": road,
        "locality": locality,
        "is_road_level": bool(road),
        "raw": data,
    }


# --- Simple manual test ---
if __name__ == "__main__":
    sample_lat = 28.702693
    sample_lng = 77.271329

    print(f"Sending request to OpenStreetMap for ({sample_lat}, {sample_lng})...")
    result = reverse_geocode_osm(sample_lat, sample_lng)

    print("\n--- Resulting Standardized Address ---")
    print(result["full_address"])
    print("\n--- Road (street-level) ---")
    print(result["road"] or "(none tagged in OSM)")
    print("\n--- Locality (fallback) ---")
    print(result["locality"] or "(none found)")
    print("\n--- Is road-level? ---")
    print(result["is_road_level"])