import pandas as pd

# Load your CSV file
data = pd.read_csv('/Users/andreeagiurgiu/Desktop/Thesis/OpenAI_add_new_Buget_Sleep_Do_Eat_attributes.csv')

# Define the function to combine the seating information
def combine_seating(indoor, outdoor):
    if outdoor in ['yes', 'pedestrian_zone'] and indoor == 'yes':
        return 'indoor and outdoor'
    elif outdoor in ['yes', 'pedestrian_zone']:
        return 'outdoor'
    elif indoor == 'yes':
        return 'indoor'
    return None

# Define the function to combine dietary information
def combine_diet(vegan, vegetarian, gluten_free):
    diet_types = []
    if vegan in ['yes', 'only']:
        diet_types.append('vegan')
    if vegetarian in ['yes', 'only']:
        diet_types.append('vegetarian')
    if gluten_free in ['yes', 'only']:
        diet_types.append('gluten free')
    return ' and '.join(diet_types)

# Define the function to update the price based on the fee
def update_price(fee, price):
    if fee == 'no':
        return 'Free'
    return price

# Define the function to update the amenity column
def update_amenity(amenity, building, tourism):
    if pd.isna(amenity) or amenity == '':
        return building if not pd.isna(building) and building != '' else tourism if not pd.isna(tourism) and tourism != '' else None
    return amenity

# Apply the functions to create the new columns and update the existing ones
data['indoor/outdoor seating'] = data.apply(lambda x: combine_seating(x['indoor_seating'], x['outdoor_seating']), axis=1)
data['dietary'] = data.apply(lambda x: combine_diet(x['diet:vegan'], x['diet:vegetarian'], x['diet:gluten_free']), axis=1)
data['price'] = data.apply(lambda x: update_price(x['fee'], x['price']), axis=1)
data['amenity'] = data.apply(lambda x: update_amenity(x['amenity'], x['building'], x['tourism']), axis=1)

# Drop the specified columns
columns_to_drop = ['indoor_seating', 'outdoor_seating', 'diet:vegan', 'diet:vegetarian', 'diet:gluten_free', 'fee', 'building', 'tourism']
data.drop(columns=columns_to_drop, inplace=True)

# Save the updated DataFrame to a new CSV file
data.to_csv('/Users/andreeagiurgiu/Desktop/Thesis/New_filter_sections.csv', index=False)

print("File has been updated and saved.")

# Getting only the colloms on which we want to do the filtering 

def filter_columns(input_file_path, output_file_path):
    # List of columns to keep
    columns_to_keep = [
        'lgbtq', 'brand', 'wheelchair', 'dietary', 'takeaway', 
        'indoor/outdoor seating', 'cuisine', 'beauty', 'shop', 
        'stars', 'internet_access', 'smoking', 'type', 'amenity', 
        'price', 'meal', 'Micheline', 'category', 'Service', 
        'room_facilities', 'accommodation_type', 'drink type', 
        'music type', 'Ambiental', 'price range'
    ]

    # Load the dataset
    data = pd.read_csv(input_file_path)

    # Filter the data to keep only the specified columns
    # Using intersection to avoid errors if some columns are not present
    filtered_data = data[data.columns.intersection(columns_to_keep)]

    # Save the filtered data to a new CSV file
    filtered_data.to_csv(output_file_path, index=False)

    print(f"Filtered data saved to {output_file_path}")

# Example usage
input_path = '/Users/andreeagiurgiu/Desktop/Thesis/New_filter_sections.csv'  # Update this path
output_path = '/Users/andreeagiurgiu/Desktop/Thesis/Ready_for_filtering.csv'  # Update this path

filter_columns(input_path, output_path)

