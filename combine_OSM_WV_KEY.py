import csv
import json
from geopy.distance import geodesic
from shapely.geometry import Point, LineString, Polygon

def read_csv(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return list(csv.DictReader(file))

def read_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

def load_analysis_results(file_path):
    results = {}
    with open(file_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            results[row['key']] = row['values']
    return results

def write_csv(data, file_path):
    with open(file_path, 'w', newline='', encoding='utf-8') as file:
        fieldnames = set().union(*(d.keys() for d in data))
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for row in data:
            writer.writerow(row)

def find_closest_osm(wv_entry, osm_data, tags_analysis):
    if 'latitude' not in wv_entry or 'longitude' not in wv_entry or not wv_entry['latitude'] or not wv_entry['longitude']:
        return None
    wv_point = Point(float(wv_entry['longitude']), float(wv_entry['latitude']))

    min_distance = float('inf')
    closest_osm = None
    for osm_entry in osm_data:
        geometry = osm_entry['geometry']
        try:
            if geometry['type'] == 'Point':
                osm_point = Point(geometry['coordinates'])
            elif geometry['type'] == 'LineString':
                osm_point = LineString(geometry['coordinates']).centroid
            elif geometry['type'] == 'Polygon':
                osm_point = Polygon(geometry['coordinates']).centroid
            else:
                continue

            distance = geodesic((wv_point.y, wv_point.x), (osm_point.y, osm_point.x)).meters
            if distance < min_distance:
                osm_name = osm_entry['properties'].get('name', '').lower()
                osm_website = osm_entry['properties'].get('website', '').lower()
                wv_name = wv_entry.get('title', '').lower()
                wv_website = wv_entry.get('url', '').lower()
                if (osm_name == wv_name or osm_website == wv_website):
                    min_distance = distance
                    closest_osm = osm_entry
        except Exception as e:
            print(f"Error processing OSM entry: {osm_entry} -- {e}")

    return closest_osm if closest_osm and min_distance <= 100 else None

def attribute_osm_to_wv(wv_data, osm_data, tags_analysis):
    enhanced_wv_data = []
    combined_count = 0  # Initialize a counter to track successful combinations
    for wv_entry in wv_data:
        closest_osm = find_closest_osm(wv_entry, osm_data, tags_analysis)
        if closest_osm:
            for key, value in closest_osm['properties'].items():
                if key in tags_analysis and tags_analysis[key] != 'X':
                    wv_entry[key] = value
            combined_count += 1  # Increment the counter
        enhanced_wv_data.append(wv_entry)
    print(f"Total combined entries: {combined_count}")  # Output the count of combined entries
    return enhanced_wv_data

# Paths to your files
osm_tags_path = '/Users/andreeagiurgiu/Desktop/Thesis/Amsterdam_interesting.osm.geojson'
wv_path = '/Users/andreeagiurgiu/Desktop/Thesis/wikivoyage-amsterdam.csv'
analysis_path = '/Users/andreeagiurgiu/Desktop/Thesis/keys_analysis.csv'
output_path = '/Users/andreeagiurgiu/Desktop/Thesis/inproved_wikivoyage_with_OSM_values.csv'

# Load data
osm_data = read_json(osm_tags_path)
wv_data = read_csv(wv_path)
tags_analysis = load_analysis_results(analysis_path)

# Attribute OSM data to WV entries
enhanced_wv_data = attribute_osm_to_wv(wv_data, osm_data, tags_analysis)

# Write enhanced WV data to a new CSV
write_csv(enhanced_wv_data, output_path)
