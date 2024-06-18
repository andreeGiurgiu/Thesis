import csv
from trafilatura import fetch_url, extract

# Function to load data from a CSV file
def load_csv_data(file_path):
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        return list(csv.DictReader(csvfile))

# Function to write data to a new CSV file
def write_csv(data, file_path):
    if not data:
        return  # If data is empty, exit the function

    with open(file_path, 'w', newline='', encoding='utf-8') as file:
        # Dynamically determine the full set of fieldnames from all records
        fieldnames = set(data[0].keys())
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for row in data:
            writer.writerow(row)

# Function to fetch and extract website description
def fetch_description(url):
    downloaded = fetch_url(url)
    if downloaded:
        result = extract(downloaded)
        return result if result else ''
    return ''

# Load data from the original CSV file
file_path = '/Users/andreeagiurgiu/Desktop/Thesis/Data_NEW_adds_OSM_data.csv'
data = load_csv_data(file_path)

# Process each entry in the original data
for entry in data:
    url = entry.get('url')
    if url:
        description = fetch_description(url)
        entry['website_description'] = description

# Write the enhanced data to a new CSV file
output_path = '/Users/andreeagiurgiu/Desktop/Thesis/Website_ALL.csv'
write_csv(data, output_path)
