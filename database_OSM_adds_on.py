import json
import pandas as pd

# Load the GeoJSON file
with open('/Users/andreeagiurgiu/Desktop/Thesis/Amsterdam_interesting.osm.geojson', 'r') as file:
    geojson_data = json.load(file)

# Load the existing CSV file
csv_path = '/Users/andreeagiurgiu/Desktop/Thesis/OpenAI_add_Buget_Sleep_Do_Eat_attributes.csv'  
df = pd.read_csv(csv_path)

# Filter the GeoJSON data for relevant amenities
relevant_features = [
    feature for feature in geojson_data 
     if (feature.get('properties', {}).get('amenity') in ['restaurant', 'fast_food', 'pub', 'bar', 'cinema'] 
        or 'shop' in feature.get('properties', {}))
        and feature.get('properties', {}).get('website') and feature.get('properties',{}).get('amenity')
    ]

# List of required columns
required_columns = [
    'addr:housenumber', 'payment:cash', 'contact:twitter', 'entrance', 'addr:street', 'drink', 'name:he', 'level',
    'layer', 'guest_house', 'coffee', 'name:en', 'reservation', 'payment:notes', 'museum', 'service:bicycle:pump',
    'article', 'roof:shape', 'memorial', 'internet_access:fee', 'name:de', 'payment:lightning', 'survey:date', 'title',
    'addr:city', 'comment', 'lgbtq', 'tollFree', 'brand', 'contact:facebook', 'accessibility', 'description', 'latitude',
    'disused:shop', 'name:ru', 'brand:wikipedia', 'source', 'addr:housename', 'common_tags', 'wikipedia', 'image',
    'designation', 'brand:wikidata', 'wheelchair', 'checkIn', 'source:date', 'directions', 'name', 'description:ru',
    'lastEdit', 'wheelchair:description', 'addr:postcode', 'diet:vegan', 'contact:tripadvisor', 'official_name',
    'last_checked', 'second_hand', 'rooms', 'denomination', 'changing_table:wheelchair', 'address', 'checkOut', 'note',
    'wheelchair:description:de', 'disused:tourism', 'wikidata', 'email', 'ref:rce', 'heritage', 'surveillance',
    'check_date:opening_hours', 'takeaway', 'start_date', 'historic', 'indoor_seating', 'check_date', 'stroller',
    'cuisine', 'beauty', 'craft_beer', 'payment:credit_cards', 'payment:onchain', 'addr:country', 'name:zh', 'shop',
    'building:architecture', 'wikimedia_commons', 'religion', 'wifi', 'alt_name', 'unisex', 'contact:website', 'longitude',
    'toilets:wheelchair', 'diet:vegetarian', 'name:ko', 'fee', 'name:lb', 'sport', 'contact:instagram', 'name:es',
    'brewery', 'landuse', 'highchair', 'ref:bag', 'hours', 'drink:club-mate', 'stars', 'contact:phone', 'changing_table',
    'toilets', 'url', 'name:da', 'changing_table:location', 'internet_access', 'alt', 'building', 'name:uk',
    'outdoor_seating', 'atm', 'fax', 'name:nl', 'smoking', 'diet:gluten_free', 'heritage:operator', 'drive_through',
    'toilets:access', 'opening_hours', 'name:ml', 'currency:XBT', 'operator', 'type', 'payment:coins', 'air_conditioning',
    'delivery', 'bicycle_rental', 'landmark', 'building:levels', 'phone', 'contact:email', 'amenity', 'access', 'int_name',
    'old_name', 'price', 'tourism', 'website', 'meal', 'Micheline', 'category', 'Service', 'room_facilities',
    'accommodation_type', 'drink type', 'music type'
]

# Function to extract properties from a feature
def extract_properties(feature, columns):
    properties = feature.get('properties', {})
    extracted = {col: properties.get(col, None) for col in columns}
    
    # Set type based on amenity or shop
    if 'shop' in properties:
        extracted['type'] = 'buy'
    else:
        amenity = properties.get('amenity')
        if amenity in ['restaurant', 'fast_food']:
            extracted['type'] = 'eat'
        elif amenity in ['pub', 'bar']:
            extracted['type'] = 'drink'
        elif amenity == 'cinema':
            extracted['type'] = 'do'
    
    return extracted

# Extract properties and create a DataFrame
filtered_relevant_data = [extract_properties(feature, required_columns) for feature in relevant_features 
                          if len([v for v in feature.get('properties', {}).values() if v is not None]) >= 15]

relevant_df = pd.DataFrame(filtered_relevant_data)

# Add any new columns that are in the relevant data but not in the CSV
for col in relevant_df.columns:
    if col not in df.columns:
        df[col] = None

# Append the relevant data to the existing DataFrame
df = pd.concat([df, relevant_df], ignore_index=True)


# Save the updated DataFrame to a new CSV file
output_path = '/Users/andreeagiurgiu/Desktop/Thesis/Data_NEW_adds_OSM_data.csv'
df.to_csv(output_path, index=False)

# Output the path to the updated file
output_path
