def extract_keys_from_file(file_path):
    keys = set()
    with open(file_path, 'r') as file:
        for line in file:
            if ':' in line:
                key = line.split(':')[0].strip()
                keys.add(key)
    return keys

def write_keys_to_file(keys, output_file_path):
    with open(output_file_path, 'w') as file:
        for key in sorted(keys):
            file.write(f"{key}\n")

# load data
frequencies_analysis_keys = extract_keys_from_file('/Users/andreeagiurgiu/Desktop/Thesis/frequencies_analysis.txt')
key_frequencies_keys = extract_keys_from_file('/Users/andreeagiurgiu/Desktop/Thesis/key_frequencies.txt')

# Find the overlapping keys
overlapping_keys = frequencies_analysis_keys.intersection(key_frequencies_keys)
write_keys_to_file(overlapping_keys, 'overlapping_keys.txt')
