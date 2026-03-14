import math

LOCATIONS = {
    "Paris, France":         {"lat":  48.86, "lon":   2.35},
    "New York, USA":         {"lat":  40.71, "lon": -74.01},
    "Tokyo, Japan":          {"lat":  35.68, "lon": 139.69},
    "Sydney, Australia":     {"lat": -33.87, "lon": 151.21},
    "Mumbai, India":         {"lat":  19.07, "lon":  72.88},
    "London, UK":            {"lat":  51.51, "lon":  -0.13},
    "Beijing, China":        {"lat":  39.91, "lon": 116.39},
    "Cairo, Egypt":          {"lat":  30.04, "lon":  31.24},
    "São Paulo, Brazil":     {"lat": -23.55, "lon": -46.63},
    "Moscow, Russia":        {"lat":  55.75, "lon":  37.62},
    "Reykjavik, Iceland":    {"lat":  64.13, "lon": -21.93},
    "Cape Town, South Africa": {"lat": -33.93, "lon":  18.42},
}

def nearest_city(lat, lon):
    """
    Finds the nearest city from the LOCATIONS dictionary using standard Euclidean 
    distance on lat/lon, which is fine as an approximation for clicking.
    Returns (city_string, city_lat, city_lon).
    """
    best_city = list(LOCATIONS.keys())[0]
    best_dist = float('inf')
    
    for city, coords in LOCATIONS.items():
        clat, clon = coords["lat"], coords["lon"]
        dist = math.sqrt((lat - clat)**2 + (lon - clon)**2)
        if dist < best_dist:
            best_dist = dist
            best_city = city
            
    return best_city, LOCATIONS[best_city]["lat"], LOCATIONS[best_city]["lon"]
