#This is a test to check and understand how reverse geoencoding will work.
import requests

def reverse_geocode_osm(latitude, longitude):
    # 1. Define the endpoint URL
    # Nominatim requires a descriptive User-Agent header so they know who is calling it
    url = "https://nominatim.openstreetmap.org/reverse"
    headers = {
        "User-Agent": "CivicSightProject/1.0(ishurathore0000@gmail.com)"
    }
    
    # 2. Add your parameters (Format, Latitude, Longitude)
    params = {
        "format": "json",
        "lat": latitude,
        "lon": longitude
    }
    
    print(f"Sending request to OpenStreetMap for ({latitude}, {longitude})...")
    
    # 3. Make the network request
    response = requests.get(url, params=params, headers=headers)
    
    # 4. Parse the map-like response
    if response.status_code == 200:
        data = response.json()
        
        # OpenStreetMap returns a key named 'display_name' containing the full address
        full_address = data.get("display_name", "Address not found")
        return full_address
    else:
        return f"Error: Status code {response.status_code}"

# Example Coordinates (Near Wazirabad Road / Yamuna Vihar area)
sample_lat = 28.701220
sample_lng = 77.270935

address = reverse_geocode_osm(sample_lat, sample_lng)
print("\n--- Resulting Standardized Address ---")
print(address)