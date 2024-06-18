# Thesis

## Datasets
Manual filter list of keys: https://docs.google.com/document/d/1sB-nQCXBu0jGPG9COnK6wgwA35o8ewaHtSu6YpbOSUg/edit?usp=share_link

Combine OSM with WV final csv file: https://docs.google.com/spreadsheets/d/1ffB7ZDX7pY9FB4BdlbphqGFMUCDQiKokl1V134UKXxY/edit?usp=share_link

Final datasets: https://drive.google.com/drive/folders/12WYz74yCR9Ua24UKDbomkAJhppvY9QFQ?usp=drive_link


## Methodology 
The OSM database which is in form of a json file is composed from type,geometry and properties. We first look for the most frequent types and properties, then we create a csv file with the overlaping of the 2 frequency lists. After we manually filter the 362 overlaping keys, we remain with 162 keys. The next step was in understanding which of this key are fix or variable. Fix meaning they have a specific set of tag and variable meaning they can take any variable ( like phone numbers and adress number ) At the end we combine the OSM dataset with the WV one based on geometry points and assigned theright tags. 

### 1. Key_type.py / Key_properties.py
We load and refromated the geojson file which was formatted as json in json file and was missing some brachets.Then we composed the frequency of each key type, repsectivly property and sort it.

### 2. Overlaping.py
Composed the overlaping of the 2 csv files with the frequent key type and properties

### 3. Values_for_keys.py
Analyzes the distribution and frequency of values for each key, identifying common patterns or anomalies. We also analyse which key has fix or variant variables. We choose to marc with an X the variant variables

### 4. Creating the manual main key and variable list
We had a look at the possible keys that we could extract from OSM and WV, alongside doing some research on the most used key for filtering travelling destinations based on preferences and created a manual key list with possiblee different variables. We used this list alongside the whole research in order to eliminate the variant variables and additional,not helpful key for the chat agent filtering possibilities.
You can final the list here: https://docs.google.com/spreadsheets/d/1Wc9zRy75CuumkUvDbh5n2jAs7ssYEJB8GGE4cD3nMTo/edit?usp=sharing


### 5. Combine_OSM_WV_Keys.py
Merge the OSM and WIkivoyage dataset based on geographic proximity and enhange the WV dataset with key variables from OSM.Due to the fact the the WV database is composed alwyes from 1 geographical point while the OSM database has 3 different geographic representation: point, line and polygon we needed to use geodesic distance in order to understand if the node from the WV is in the same space proximity with the node or way from the OSM dataset. This method could still combine the datasets inaccurate so we decided to only merge the datasets in case alongside the space proximity the points have similarities in the name or url.
At the end we have added the variables from the OSM keys to WV based on the list created in point 4

### 6.Creating the 4 different dataset 
In our research we needed to create 4 different datasets in order to understand what different combination could create the best key/variable set
Database 1 = Is the base case coming from step 5 which only contains the geographical points from WV with key and values added from OSM
Database 2 = To the base case we have added the text from the website of the location in order to create longer descriptions that are going to be used in the next steps
Database 3 = To the base case we have added new datapoints from OSM on store, restaurants, fast_food, cinema, bar,pub as we observed the lack of data on this variabels
Daatabase 4 = To the datbase 3 we have added the text from the website of the location in order to create longer descriptions that are going to be used in the next steps

#### 6.1 Adding website text website.py + website_in_description.py
We use the Fetch API in order to extract the text from the websites find on the OM/WV data and add it to the description cell

#### 6.2 Adding OSM locations
We extract location from OSM bases on searching if in the priperties data we find any shops or in amenity section they have as a variable restaurant,fast_food,pub,bar,cinema. As we did not want to look into data quantity but rather data quality we also ensure that all the extracted locations have a website and amaenity property and it has at least 15 different tags

### 7 Creating variabele tags with OpenAI API Buget.py
We use the OpenAI 3.5 turbo API in order to create the variables tag ( the ones mention in the manual list form point 4) and add it to the database. For each key we made a request to the API and mention in details that the agent shold choose from a specific list of possibilities and that if its confused or doesn't find any information about the key it should just say Nothing.

### 8 Filter the data  filter_data.py -> Creates the final dataset
The OpenAI API agent has a halucination rate of 39.6%, which creates a lot of different ranges of tags or excesive text explaining its choise. But this text cannot be used in filtering the data. We use natural language processing in order to determine the steam word which can be used as a tag. We also combine differnet keys like indoor, outdoor seating, dietrary optiontion for vegan, vegetarian and halal, and in the amenity key when we saw missing variables we were adding from the building/tourism key. On this code we also eliminate all the variables that are not necessary like the nothing words given by the agent. We did a lot of testing on what are the best filtering options in order to create a clear perspective.

### 9 Chat Bot app.py + index.html
We create the chat bot which has as main component a recursive algorithm which is getting the most fill collom, presenting to the user all the unique variable and ask him which one would it prefer, then we are filtering based on the specific variable and droping the collom. The recurve compenent ends in the moment that we arrive to the last 10 rows in the dataset wher the agent is giving the option to the user with a short explenation based on the data colloms it has.
In the cases where we are filtering based on wheelchair, takeaway,internet_access, private_bath, air_conditioning, balcony, kitchen and tv where the answer can be only yes or no, we choose to not filter at all the data in the cases where we see no.




