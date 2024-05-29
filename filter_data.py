import pandas as pd
import string
import nltk
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet

# Download necessary NLTK data files
#nltk.download('punkt')
#nltk.download('wordnet')
#nltk.download('averaged_perceptron_tagger')

# Load your CSV file
data = pd.read_csv('/Users/andreeagiurgiu/Desktop/Thesis/OpenAI_add_to_test_new_Buget_Sleep_Do_Eat_attributes.csv')

# Initialize the WordNetLemmatizer
lemmatizer = WordNetLemmatizer()
def clean_and_lemmatize(value):
    if isinstance(value, str):
        # Remove punctuation
        value = value.translate(str.maketrans('', '', string.punctuation)).strip()
        # Convert to lowercase
        value = value.lower()
        # Tokenize and lemmatize
        tokens = nltk.word_tokenize(value)
        lemmatized_tokens = [lemmatizer.lemmatize(token, get_wordnet_pos(token)) for token in tokens]
        return ' '.join(lemmatized_tokens)
    return value

# Helper function to map POS tags to WordNet POS tags
def get_wordnet_pos(word):
    """Map POS tag to first character lemmatize() accepts"""
    tag = nltk.pos_tag([word])[0][1][0].upper()
    tag_dict = {"J": wordnet.ADJ,
                "N": wordnet.NOUN,
                "V": wordnet.VERB,
                "R": wordnet.ADV}
    return tag_dict.get(tag, wordnet.NOUN)

# Apply the cleaning and lemmatization function to all columns in the dataframe
for column in data.columns:
    data[column] = data[column].apply(clean_and_lemmatize)


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

def clean_column(value):
    if isinstance(value, str) and value.strip().lower() == 'yes':
        return 'yes'
    elif isinstance(value, str) and pd.isna(value):
        return 'no'
    else:
        return ''

columns_to_clean = ['wheelchair','takeaway', 'internet_access','private_bath' , 'air_conditioning', 'balcony', 'kitchen', 'tv',]

# Define the function to update the price based on the fee
def update_price(fee, price):
    if fee == 'no':
        return 'Free'
    return price

#clean Micheline start
def update_micheline(value):
    if value in ['1 star', '2 star', '3 star']:
        return value
    return 'no'

# Apply the function to the "Micheline" column
data['Micheline'] = data['Micheline'].apply(update_micheline)


# cleaning the data to make sure we have just yes and no
for column in columns_to_clean:
    data[column] = data[column].apply(clean_column)

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

# delete the nothing colloms from Chat
data.replace(["Nothing", "nothing", 'nan', 'Unknown', 'None.','Nothing.', pd.NA, pd.NaT, None], "", inplace=True)
data.replace(["wlan"], "yes", inplace=True)
data.replace(["cleanliness"], "clean", inplace=True)
# Save the updated DataFrame to a new CSV file
data.to_csv('/Users/andreeagiurgiu/Desktop/Thesis/New_filter_sections2.csv', index=False)

print("File has been updated and saved.")




