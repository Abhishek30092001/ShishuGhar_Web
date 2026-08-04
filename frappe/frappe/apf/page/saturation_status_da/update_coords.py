import json
import urllib.request
import os

# URLs for LGD GeoJSONs from Bharatlas
STATE_URL = "https://bharatlas.com/api/dl/admin/states/LGD_States.geojson"
DISTRICT_URL = "https://bharatlas.com/api/dl/admin/districts/LGD_Districts.geojson"

def get_centroid(coordinates, geom_type):
    """Calculate an approximate centroid for the polygon/multipolygon."""
    all_points = []
    
    if geom_type == "Polygon":
        for ring in coordinates:
            all_points.extend(ring)
    elif geom_type == "MultiPolygon":
        for polygon in coordinates:
            for ring in polygon:
                all_points.extend(ring)
                
    if not all_points:
        return [0, 0]
        
    x_coords = [p[0] for p in all_points]
    y_coords = [p[1] for p in all_points]
    
    center_x = sum(x_coords) / len(x_coords)
    center_y = sum(y_coords) / len(y_coords)
    
    # Leaflet expects [lat, lng] (i.e. [y, x])
    return [round(center_y, 4), round(center_x, 4)]

def update_geolocation():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(base_dir, "geolocation.json")
    
    with open(json_path, "r", encoding="utf-8") as f:
        geo_config = json.load(f)

    print("Fetching States GeoJSON...")
    with urllib.request.urlopen(STATE_URL) as response:
        states_data = json.loads(response.read().decode())
        
    print("Updating state coordinates...")
    new_states = {}
    for feature in states_data.get("features", []):
        props = feature.get("properties", {})
        # LGD fields in bharatlas dataset
        name = props.get("state_name") or props.get("ST_NM") or props.get("stname") or props.get("NAME_1")
        if not name:
            continue
            
        geom = feature.get("geometry")
        if geom:
            centroid = get_centroid(geom["coordinates"], geom["type"])
            # Keep existing zoom or default to 7
            existing_zoom = geo_config.get("states", {}).get(name, {}).get("zoom", 7)
            new_states[name] = {"center": centroid, "zoom": existing_zoom}

    print("Fetching Districts GeoJSON...")
    with urllib.request.urlopen(DISTRICT_URL) as response:
        districts_data = json.loads(response.read().decode())
        
    print("Updating district coordinates...")
    new_districts = {}
    for feature in districts_data.get("features", []):
        props = feature.get("properties", {})
        state_name = props.get("state_name") or props.get("stname") or props.get("NAME_1") or props.get("ST_NM")
        dist_name = props.get("district_name") or props.get("dtname") or props.get("DT_NM") or props.get("NAME_2")
        
        if not dist_name:
            continue
            
        geom = feature.get("geometry")
        if geom:
            centroid = get_centroid(geom["coordinates"], geom["type"])
            # Keep existing zoom or default to 9
            existing_zoom = geo_config.get("districts", {}).get(dist_name, {}).get("zoom", 9)
            new_districts[dist_name] = {
                "state": state_name or "",
                "center": centroid,
                "zoom": existing_zoom
            }

    geo_config["states"] = new_states
    geo_config["districts"] = new_districts

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(geo_config, f, indent=4)
        
    print("Successfully updated geolocation.json with accurate LGD coordinates.")

if __name__ == "__main__":
    update_geolocation()
