import json
from collections import defaultdict

def fix_and_analyze_json(file_path, output_file):
    with open(file_path, 'r') as file:
        content = file.read().strip()

    # Ensure the entire content is an array of objects
    if not content.startswith('['):
        content = '[' + content + ']'

    # Fix missing commas between objects and incorrect trailing commas
    content = content.replace('}{', '},{').replace(',}', '}').replace(',]', ']')

    # Attempt to load the JSON and perform operations if successful
    try:
        data = json.loads(content)
        print("JSON is valid after fixing!")
        with open(file_path, 'w') as file:
            json.dump(data, file, indent=4)

        # Dictionaries to hold counts
        key_counts = defaultdict(int)
        type_counts = defaultdict(int)

        # Count frequency of each key in the 'properties' object and types
        for feature in data:
            if 'properties' in feature:
                properties = feature['properties']
                for key in properties:
                    key_counts[key] += 1

            if 'type' in feature:
                type_counts[feature['type']] += 1

        # Write results to the output file
        with open(output_file, 'w') as file:
            file.write("Key Frequencies:\n")
            sorted_key_counts = sorted(key_counts.items(), key=lambda item: item[1], reverse=True)
            for key, count in sorted_key_counts:
                file.write(f"{key}: {count}\n")

            file.write("\nType Frequencies:\n")
            sorted_type_counts = sorted(type_counts.items(), key=lambda item: item[1], reverse=True)
            for type, count in sorted_type_counts:
                file.write(f"{type}: {count}\n")

        return True

    except json.JSONDecodeError as e:
        print(f"Failed to fix JSON: {e}")
        # Log the problematic part for debugging
        error_char_index = e.pos  # get the position of the error
        print("Error near: ", content[max(0, error_char_index - 50):error_char_index + 50])  # print characters around the error
        return False

# Path to the problematic GeoJSON file
geojson_file_path = '/Users/andreeagiurgiu/Desktop/Thesis/Amsterdam_interesting.osm.geojson'
# Output file path for key and type frequencies
output_file_path = '/Users/andreeagiurgiu/Desktop/Thesis/frequencies_analysis.txt'

# Fix the JSON file and analyze key and type frequencies
fix_and_analyze_json(geojson_file_path, output_file_path)
