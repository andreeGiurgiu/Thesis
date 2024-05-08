import csv
from collections import defaultdict, Counter

def read_csv(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return list(csv.DictReader(file))

def analyze_columns(data):
    column_values = defaultdict(list)
    # Collect values for each column in the dataset
    for entry in data:
        for column, value in entry.items():
            column_values[column].append(value)

    results = {}
    for column, values in column_values.items():
        value_counts = Counter(values)
        most_common = value_counts.most_common()
        if most_common[0][1] == 1:  # The most frequently occurring value appears only once
            results[column] = 'X'
        else:
            results[column] = most_common[:10]  # Only record the top 10 if no value is unique
    return results

def write_analysis_results(results, file_path):
    with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['column', 'values']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for column, values in results.items():
            if isinstance(values, list):
                values_formatted = ', '.join(f'{v[0]}: {v[1]}' for v in values)
                writer.writerow({'column': column, 'values': values_formatted})
            else:
                writer.writerow({'column': column, 'values': values})  # Writes 'X' if all values are unique

# Path to the Wikivoyage CSV file
wv_path = '/Users/andreeagiurgiu/Desktop/Thesis/wikivoyage-amsterdam.csv'
output_analysis_path = '/Users/andreeagiurgiu/Desktop/Thesis/wikivoyage_analysis.csv'

# Load the Wikivoyage data
wv_data = read_csv(wv_path)

# Analyze the data columns
columns_analysis = analyze_columns(wv_data)

# Write the analysis results to a new CSV
write_analysis_results(columns_analysis, output_analysis_path)
