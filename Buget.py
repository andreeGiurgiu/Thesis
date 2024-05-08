import csv
from openai import OpenAI

# Initialize the OpenAI client
client = OpenAI(api_key='my key')

# Function to load data from a CSV file
def load_csv_data(file_path):
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        return list(csv.DictReader(csvfile))

# Function to write data to a new CSV file
def write_csv(data, file_path):
    with open(file_path, 'w', newline='', encoding='utf-8') as file:
        # List all the existing field names from the Wikivoyage data
        # followed by the new columns you're adding at the end.
        fieldnames = [
            'addr:housenumber', 'payment:cash', 'contact:twitter', 'entrance', 'addr:street', 'drink', 'name:he', 'level',
            'layer', 'guest_house', 'coffee', 'name:en', 'reservation', 'payment:notes', 'museum', 'service:bicycle:pump',
            'article', 'roof:shape', 'memorial', 'internet_access:fee', 'name:de', 'payment:lightning', 'survey:date',
            'title', 'addr:city', 'comment', 'lgbtq', 'tollFree', 'brand', 'contact:facebook', 'accessibility', 'description',
            'latitude', 'disused:shop', 'name:ru', 'brand:wikipedia', 'source', 'addr:housename', 'common_tags', 'wikipedia',
            'image', 'designation', 'brand:wikidata', 'wheelchair', 'checkIn', 'source:date', 'directions', 'name', 'description:ru',
            'lastEdit', 'wheelchair:description', 'addr:postcode', 'diet:vegan', 'contact:tripadvisor', 'official_name',
            'last_checked', 'second_hand', 'rooms', 'denomination', 'changing_table:wheelchair', 'address', 'checkOut', 'note',
            'wheelchair:description:de', 'disused:tourism', 'wikidata', 'email', 'ref:rce', 'heritage', 'surveillance',
            'check_date:opening_hours', 'takeaway', 'start_date', 'historic', 'indoor_seating', 'check_date', 'stroller', 'cuisine',
            'beauty', 'craft_beer', 'payment:credit_cards', 'payment:onchain', 'addr:country', 'name:zh', 'shop', 'building:architecture',
            'wikimedia_commons', 'religion', 'wifi', 'alt_name', 'unisex', 'contact:website', 'longitude', 'toilets:wheelchair', 'diet:vegetarian',
            'name:ko', 'fee', 'name:lb', 'sport', 'contact:instagram', 'name:es', 'brewery', 'landuse', 'highchair', 'ref:bag', 'hours',
            'drink:club-mate', 'stars', 'contact:phone', 'changing_table', 'toilets', 'url', 'name:da', 'changing_table:location', 'internet_access',
            'alt', 'building', 'name:uk', 'outdoor_seating', 'atm', 'fax', 'name:nl', 'smoking', 'diet:gluten_free', 'heritage:operator',
            'drive_through', 'toilets:access', 'opening_hours', 'name:ml', 'currency:XBT', 'operator', 'type', 'payment:coins', 'air_conditioning',
            'delivery', 'bicycle_rental', 'landmark', 'building:levels', 'phone', 'contact:email', 'amenity', 'access', 'int_name', 'old_name',
            'price', 'tourism', 'website',
            # New fields to add at the end
            'meal', 'Micheline', 'category', 'Service', 'room_facilities', 'accommodation_type', 'drink type', 'music type'
        ]

        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for row in data:
            # Ensure all new fields exist in the dictionary to avoid KeyError
            for field in ['meal', 'Micheline', 'category', 'Service', 'room_facilities', 'accommodation_type']:
                row.setdefault(field, '')
            writer.writerow(row)


# Load data from the original Wikivoyage CSV file
original_data = load_csv_data('/Users/andreeagiurgiu/Desktop/Thesis/new_better_wikivoyage2.csv')

# Prepare the enhanced data list
enhanced_data = []
filled_count = 0
unfilled_count = 0
count_s = 0
count_d = 0
count_e = 0

# Process each entry in the original data
for entry in original_data:
    if not entry['price']:  # If the price field is empty
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a system that extracts pricing information from descriptions.If you unable to find the buget in the description please just leave it empty and go to the next one"},
                {"role": "user", "content": entry['description']}
            ]
        )
        price_estimate = response.choices[0].message.content
        if price_estimate and 'budget' not in price_estimate.lower() and 'hello' not in price_estimate.lower() and 'description' not in price_estimate.lower() and 'information' not in price_estimate.lower() and 'assist' not in price_estimate.lower() and 'N/A' not in price_estimate.lower():
            entry['price'] = price_estimate
            filled_count += 1
        else:
            entry['price'] = ''
            unfilled_count += 1
    if entry['type'].lower() == 'sleep':
        count_s += 1
        # Predict accommodation type
        accom_response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Identify the type of accommodation from the description. Possible types include: Hotel, Hostel, Apartment, House, Close to center, Near Airport.If you do not find anything or you are unsure just say nothing"},
                {"role": "user", "content": entry['description']}
            ]
        )
        accom_type = accom_response.choices[0].message.content
        entry['accommodation_type'] = accom_type

        # Predict room facilities
        facilities_response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "List the room facilities based on the description. Possible facilities include: Private bath, Air conditioning, Bath, Balcony, View, Kitchen, TV, Number beds, Size."},
                {"role": "user", "content": entry['description']}
            ]
        )
        facilities = facilities_response.choices[0].message.content
        entry['room_facilities'] = facilities

        # Predict service quality
        service_response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Determine if the description mentions 'Cleanliness' or 'Friendly staff'. If in mention cleanliness just say Clean, if it mention just friendly staff just say friendly staff, if it mention both say clean and friendly staff and if nothing appear just say nothing"},
                {"role": "user", "content": entry['description']}
            ]
        )
        service_info = service_response.choices[0].message.content
        if 'nothing' in service_info.lower():
            entry['Service'] = ''
        else:
            entry['Service'] = service_info
    if entry['type'].lower() == 'do':
        count_d += 1
        # Predict category of the activity
        category_response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Identify the type of acctivity from the description. Possible types include:Cultural, Historic, Local, Tehnologic, Walking, Testing, Art, Night, Museum, Theater, Golf, Park, Entartiment, ZOO, Cinema, Interactive"},
                {"role": "user", "content": entry['description']}
            ]
        )
        category_type = category_response.choices[0].message.content
        entry['category'] = category_type
    if entry['type'].lower() == 'eat':
        count_e +=1
        # Predict meal type
        meal_response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Identify the type of meal from the description. Possible types include:Breakfast, Brunch, Lunch, Dinner"},
                {"role": "user", "content": entry['description']}
            ]
        )
        meal_type = meal_response.choices[0].message.content
        entry['meal'] = meal_type
        #Predict micheline
        Micheline_response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Identify the type of Micheline from the description. Possible types include:1 start, 2 start, 3 start, No"},
                {"role": "user", "content": entry['description']}
            ]
        )
        Micheline_type = Micheline_response.choices[0].message.content
        entry['Micheline'] = Micheline_type

    if entry['type'].lower() == 'drink':
        count_s += 1
        # Predict drinks type
        type_drink_response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Identify the type of drink from the description. Possible types include: beer, coktail, wine, Coffee, Tea, soft drinks.If you do not find anything or you are unsure just say nothing"},
                {"role": "user", "content": entry['description']}
            ]
        )
        type_drink_type = type_drink_response.choices[0].message.content
        entry['drink type'] = type_drink_type

        # Predict music type

        music_response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Identify the type of music from the description.If you do not find anything or you are unsure just say nothing"},
                {"role": "user", "content": entry['description']}
            ]
        )
        music_type = music_response.choices[0].message.content
        entry['music type'] = music_type



    



    
    enhanced_data.append(entry)

# Write the enhanced data to a new CSV file
write_csv(enhanced_data, '/Users/andreeagiurgiu/Desktop/Thesis/OpenAI_add_Buget_Sleep_Do_Eat_attributes.csv')

# Print the counts of filled and unfilled price cells
print(f"Filled: {filled_count}, Unfilled: {unfilled_count}")
print('eat')
print(count_e)
print('sleep')
print(count_s)
print('do')
print(count_d)
