import csv
from openai import OpenAI

# Initialize the OpenAI client
client = OpenAI(api_key=None)

# Function to load data from a CSV file
def load_csv_data(file_path):
    columns = [
    'addr:housenumber', 'addr:street', 'name:en', 'reservation',
    'memorial', 'title', 'lgbtq', 'brand', 'description', 'latitude',
    'brand:wikipedia', 'common_tags', 'wikipedia', 'image', 'wheelchair', 'checkIn', 'name',
    'wheelchair:description', 'addr:postcode', 'diet:vegan', 'address', 'checkOut',
    'note', 'takeaway', 'indoor_seating', 'cuisine', 'beauty', 'shop',
    'wikimedia_commons', 'contact:website', 'longitude', 'toilets:wheelchair', 'diet:vegetarian',
    'fee', 'hours', 'stars', 'changing_table', 'toilets', 'url', 'internet_access', 'alt', 'building',
    'outdoor_seating', 'smoking', 'diet:gluten_free', 'opening_hours', 'type', 'phone', 'amenity',
    'old_name', 'price', 'tourism', 'website','amenity', 'check_date', 'cuisine', 'name', 'opening_hours', 'shop'
]
    data = []
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            # Filter out only the columns we need
            filtered_row = {field: row[field] for field in columns if field in row}
            data.append(filtered_row)
    return data

# Function to write data to a new CSV file
def write_csv(data, file_path):
    with open(file_path, 'w', newline='', encoding='utf-8') as file:
        # List all the existing field names from the Wikivoyage data
        # followed by the new columns you're adding at the end.
        fieldnames = [
           'addr:housenumber', 'addr:street', 'name:en', 'reservation',
    'memorial', 'title', 'lgbtq', 'brand', 'description', 'latitude',
    'brand:wikipedia', 'common_tags', 'wikipedia', 'image', 'wheelchair', 'checkIn', 'name',
    'wheelchair:description', 'addr:postcode', 'diet:vegan', 'address', 'checkOut',
    'note', 'takeaway', 'indoor_seating', 'cuisine', 'beauty', 'shop',
    'wikimedia_commons', 'contact:website', 'longitude', 'toilets:wheelchair', 'diet:vegetarian',
    'fee', 'hours', 'stars', 'changing_table', 'toilets', 'url', 'internet_access', 'alt', 'building',
    'outdoor_seating', 'smoking', 'diet:gluten_free', 'opening_hours', 'type', 'phone', 'amenity',
    'old_name', 'price', 'tourism', 'website','amenity', 'brand', 'check_date', 'cuisine', 'name', 'opening_hours', 'shop',
            # New fields to add at the end
            'meal', 'Micheline', 'category', 'Service', 'room_facilities', 'accommodation_type', 'drink type', 'music type', 'Ambiental','price range', 'private_bath' , 'air_conditioning' , 'bath' , 'balcony' , 'view' , 'kitchen' , 'tv',  'bed_number' , 'size'
        ]

        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for row in data:
            # Ensure all new fields exist in the dictionary to avoid KeyError
            for field in ['meal', 'Micheline', 'category', 'Service', 'room_facilities', 'accommodation_type', 'drink type', 'music type', 'Ambiental','price range', 'private_bath' , 'air_conditioning' , 'bath' , 'balcony' , 'view' , 'kitchen' , 'tv',  'bed_number' , 'size']:
                row.setdefault(field, '')
            writer.writerow(row)


# Load data from the original Wikivoyage CSV file
original_data = load_csv_data('/Users/andreeagiurgiu/Desktop/Thesis/test.csv')

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
    

    if entry['type'].lower() == 'sleep' and entry['description']:
        if entry['price']:
            price_range = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a system that categorize each place as cheap, medium, or expensive based on the price ranges. if the price of a place to sleep per nighth is around 50 euro mark it as cheap, if it is around 120 mark is at medium and if it more then 200 mark it as expensive. Please just say 1 word and if you are confused or do not know just say Nothing"},
                    {"role": "user", "content": entry['price']}
            ]
        )
            price_range_type = price_range.choices[0].message.content
            entry['price range'] = price_range_type
        count_s += 1
        # Predict accommodation type
        accom_response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Identify the type of accommodation from the description. Possible types include: Hotel, Hostel, Apartment, House, Close to center, Near Airport.If you do not find anything or you are unsure or the description doesn't mention anything about this just say Nothing"},
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

        if entry['description']:
            #Privare bath
            private_bath = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": " Determine from the description if the hotel room has a Private bath. If it has say yes, if it dosn't say no. If you are not sure or is not mention in the description, just say Nothing"},
                {"role": "user", "content": entry['description']}
            ]
        )
            private_bath_type = private_bath.choices[0].message.content
            entry['private_bath'] = private_bath_type

            #Air conditioning
            air_conditioning = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": " Determine from the description if the hotel room has a air conditioning. If it has say yes, if it dosn't say no. If you are not sure or is not mention in the description, just say Nothing"},
                {"role": "user", "content": entry['description']}
            ]
        )
            air_conditioning_type = air_conditioning.choices[0].message.content
            entry['air_conditioning'] = air_conditioning_type

            #Bath
            bath= client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": " Determine from the description if the hotel room has a bath. If it has say yes, if it dosn't say no. If you are not sure or is not mention in the description, just say Nothing"},
                {"role": "user", "content": entry['description']}
            ]
        )
            bath_type = bath.choices[0].message.content
            entry['bath'] = bath_type

            #Balcony
            balcony= client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": " Determine from the description if the hotel room has a balcony. If it has say yes, if it dosn't say no. If you are not sure or is not mention in the description, just say Nothing"},
                {"role": "user", "content": entry['description']}
            ]
        )
            balcony_type = balcony.choices[0].message.content
            entry['balcony'] = balcony_type

            #View
            view = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": " Determine from the description if the hotel room has a view. Please just choose if and say: city view, mountain view, park view, if it dosn't say no. If you are not sure or is not mention in the description, just say Nothing"},
                {"role": "user", "content": entry['description']}
            ]
        )
            view_type = view.choices[0].message.content
            entry['view'] = view_type

            #Kitchen
            kitchen = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": " Determine from the description if the hotel room has a kitchen. If it has say yes, if it dosn't say no. If you are not sure or is not mention in the description, just say Nothing"},
                {"role": "user", "content": entry['description']}
            ]
        )
            kitchen_type = kitchen.choices[0].message.content
            entry['kitchen'] =kitchen_type

            #TV
            tv = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": " Determine from the description if the hotel room has a TV. If it has say yes, if it dosn't say no. If you are not sure or is not mention in the description, just say Nothing"},
                {"role": "user", "content": entry['description']}
            ]
        )
            tv_type = tv.choices[0].message.content
            entry['tv'] =tv_type

            #Bed numbers
            bed_number = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": " Determine from the description if it specify how many number of beds does the accomodation has. If it has say the max number of beds you can have, if it dosn't say 0. If you are not sure or is not mention in the description, just say Nothing"},
                {"role": "user", "content": entry['description']}
            ]
        )
            bed_number_type = bed_number.choices[0].message.content
            entry['bed_number'] = bed_number_type

            #Size
            size = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": " Determine from the description if it specify the room size. If it has specify just small, medium or large. If you are not sure or is not mention in the description, just say Nothing"},
                {"role": "user", "content": entry['description']}
            ]
        )
            size_type = size.choices[0].message.content
            entry['size'] = size_type

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
        if entry['price']:
            price_range = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a system that categorize each place as cheap, medium, or expensive based on the price ranges. if the price of an activity is around 10 euro mark it as cheap, if it is around 25 mark is at medium and if it more then 50 mark it as expensive"},
                    {"role": "user", "content": entry['price']}
            ]
        )
            price_range_type = price_range.choices[0].message.content
            entry['price range'] = price_range_type
        count_d += 1
        # Predict category of the activity
        category_response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Identify the type of acctivity from the description. Possible types include:Cultural, Historic, Local, Tehnologic, Walking, Testing, Art, Night, Museum, Theater, Golf, Park, Entartiment, ZOO, Cinema, Interactive.Please just chose 1 that it would fit the most. Alo if you are confused or there is nothing indicated what type of activity is just say Nothing"},
                {"role": "user", "content": entry['description']}
            ]
        )
        category_type = category_response.choices[0].message.content
        entry['category'] = category_type
    if entry['type'].lower() == 'eat':
        if entry['price']:
            price_range = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a system that categorize each place as cheap, medium, or expensive based on the price ranges. if the price of a meal is around 10 euro mark it as cheap, if it is around 25 mark is at medium and if it more then 50 mark it as expensive"},
                    {"role": "user", "content": entry['price']}
            ]
        )
            price_range_type = price_range.choices[0].message.content
            entry['price range'] = price_range_type
        count_e +=1
        # Predict meal type
        meal_response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Identify the type of meal from the description. Possible types include:Breakfast, Brunch, Lunch, Dinner.Please just chose one. If there is nothing mention, or you are confused just say Nothing"},
                {"role": "user", "content": entry['description']}
            ]
        )
        meal_type = meal_response.choices[0].message.content
        entry['meal'] = meal_type
        #Predict micheline
        Micheline_response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Identify the type of Micheline from the description. Please just specify if it is 1 start, 2 start, 3 start or if there is notging mention about this juust say No"},
                {"role": "user", "content": entry['description']}
            ]
        )
        Micheline_type = Micheline_response.choices[0].message.content
        entry['Micheline'] = Micheline_type

        #Predict Ambiental
        Ambiental_response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Identify the type of ambiental from the description. Possible types are:Casual, Intimate, Romantic, Family-friendly, Chic. If you do not find anything about the ambiental please right just No or Nothing. Do not write full sentances, this data will just be one tag, so please just give one word"},
                {"role": "user", "content": entry['description']}
            ]
        )
        Ambiental_type = Ambiental_response.choices[0].message.content
        entry['Ambiental'] = Ambiental_type

    if entry['type'].lower() == 'drink':
        if entry['price']:
            price_range = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a system that categorize each place as cheap, medium, or expensive based on the price ranges. if the price of a drink is around 5 euro mark it as cheap, if it is around 10 mark is at medium and if it more then 18 mark it as expensive"},
                    {"role": "user", "content": entry['price']}
            ]
        )
            price_range_type = price_range.choices[0].message.content
            entry['price range'] = price_range_type
        count_s += 1
        # Predict drinks type
        type_drink_response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Identify the type of drink from the description. Possible types include: beer, coktail, wine, Coffee, Tea, soft drinks.If you do not find anything or you are unsure just say nothing. Do not write full sentances, this data will just be one tag, so please just give one word"},
                {"role": "user", "content": entry['description']}
            ]
        )
        type_drink_type = type_drink_response.choices[0].message.content
        entry['drink type'] = type_drink_type

        # Predict music type

        music_response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Identify the type of music from the description.If you do not find anything or you are unsure just say nothing. Do not write full sentances, this data will just be one tag, so please just give one word"},
                {"role": "user", "content": entry['description']}
            ]
        )
        music_type = music_response.choices[0].message.content
        entry['music type'] = music_type

        #Predict Ambiental
        Ambiental_response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Identify the type of ambiental from the description. Possible types are:Casual, Intimate, Romantic, Family-friendly, Chic. If you do not find anything about the ambiental please right just No. Do not write full sentances, this data will just be one tag, so please just give one word"},
                {"role": "user", "content": entry['description']}
            ]
        )
        Ambiental_type = Ambiental_response.choices[0].message.content
        entry['Ambiental'] = Ambiental_type

        if entry['type'] == 'other' and entry['price']:
            price_range = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a system that categorize each place as cheap, medium, or expensive based on the price ranges. if the price of an type of activity from there is around 8 euro mark it as cheap, if it is around 15 mark is at medium and if it more then 20 mark it as expensive"},
                    {"role": "user", "content": entry['price']}
            ]
        )
            price_range_type = price_range.choices[0].message.content
            entry['price range'] = price_range_type




    
    enhanced_data.append(entry)

# Write the enhanced data to a new CSV file
write_csv(enhanced_data, '/Users/andreeagiurgiu/Desktop/Thesis/OpenAI_add_to_test_new_Buget_Sleep_Do_Eat_attributes.csv')

# Print the counts of filled and unfilled price cells
print(f"Filled: {filled_count}, Unfilled: {unfilled_count}")
print('eat')
print(count_e)
print('sleep')
print(count_s)
print('do')
print(count_d)
