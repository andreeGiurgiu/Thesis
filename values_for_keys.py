import json
import csv
from collections import defaultdict, Counter

def load_data(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

def load_keys(file_path):
    with open("/Users/andreeagiurgiu/Desktop/Thesis/manual_filter_keys.txt", "r") as keys:
       lines = keys.readlines()
    listt = []
    for l in lines:
            as_list = l.split(", ")
            listt.append(as_list[0].replace("\n", ""))
    return listt

def analyze_keys(data, fixed_key_set):
    key_values = defaultdict(list)
    # Collect values only for keys in the fixed_key_set
    for item in data:
        for key, value in item['properties'].items():
            if key in fixed_key_set:
                key_values[key].append(value)
    
    results = {}
    for key, values in key_values.items():
        if len(set(values)) > 30:  # If more than 30 unique values, just put 'X'
            results[key] = 'X'
        else:  # Otherwise, compute the top 10 common values
            results[key] = Counter(values).most_common(10)
    return results


# Load the list of fixed keys from the file
fixed_keys_list = load_keys('/Users/andreeagiurgiu/Desktop/Thesis/manual_filter_keys.txt')


# Load your GeoJSON data
data = load_data('/Users/andreeagiurgiu/Desktop/Thesis/Amsterdam_interesting.osm.geojson')

# Analyze the keys based on the fixed keys list
keys_analysis = analyze_keys(data, fixed_keys_list)

# Writing results to a CSV file
with open('keys_analysis.csv', 'w', newline='') as csvfile:
    fieldnames = ['key', 'values']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    for key, values in keys_analysis.items():
        if isinstance(values, list):
            values_formatted = ', '.join(f'{v[0]}: {v[1]}' for v in values)
            writer.writerow({'key': key, 'values': values_formatted})
        else:
            writer.writerow({'key': key, 'values': values})  # Writes 'X' if more than 30 unique values
