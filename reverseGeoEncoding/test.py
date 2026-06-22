import requests, json

url = "https://nominatim.openstreetmap.org/reverse"
headers = {"User-Agent": "CivicSightProject/1.0(ishurathore0000@gmail.com)"}
params = {"format": "jsonv2", "lat": 28.701220, "lon": 77.270935, "addressdetails": 1}

r = requests.get(url, params=params, headers=headers, timeout=10)
print(json.dumps(r.json().get("address", {}), indent=2))