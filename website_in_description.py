import pandas as pd
import re

# Read the CSV file
df = pd.read_csv('/Users/andreeagiurgiu/Desktop/Thesis/Website_ALL.csv')

# Define a function to clean the website_description column
def clean_text(text):
    if pd.isna(text):
        return ''
    # Remove newlines and any non-printable characters
    return re.sub(r'[\r\n]+', ' ', text).strip()

# Apply the cleaning function to the website_description column
df['website_description'] = df['website_description'].apply(clean_text)

# Append the cleaned website_description to the description column
df['description'] = df.apply(lambda row: f"{row['description']} {row['website_description']}".strip() if pd.notna(row['description']) else row['website_description'], axis=1)

# Drop the now redundant website_description column
df.drop(columns=['website_description'], inplace=True)

# Save the modified DataFrame back to a CSV file
output_path = '/Users/andreeagiurgiu/Desktop/Thesis/Database_ALL_WV_OSM_Website.csv'
df.to_csv(output_path, index=False)

# Output the path to the modified file
output_path
