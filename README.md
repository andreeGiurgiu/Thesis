# Thesis

## Methodology 
The OSM database which is in form of a json file is composed from type,geometry and properties. We first look for the most frequent types and properties, then we create a csv file with the overlaping of the 2 frequency lists. After we manually filter the 362 overlaping keys, we remain with 162 keys. The next step was in understanding which of this key are fix or variable. Fix meaning they have a specific set of tag and variable meaning they can take any variable ( like phone numbers and adress number ) At the end we combine the OSM dataset with the WV one based on geometry points and assigned theright tags. 

### 1. Key_type.py / Key_properties.py
We load and refromated the geojson file which was formatted as json in json file and was missing some brachets.Then we composed the frequency of each key type, repsectivly property and sort it.

### 2. Overlaping.py
Composed the overlaping of the 2 csv files with the frequent key type and properties

### 3. Values_for_keys.py
Analyzes the distribution and frequency of values for each key, identifying common patterns or anomalies. We also analyse which key has fix or variant variables. We choose to marc with an X the variant variables

### 4. Combine_OSM_WV_Keys.py
Merge the OSM and WIkivoyage dataset based on geographic proximity and enhange the WV dataset with key variables from OSM. We  use geodesic distance in order to understand if the node from the WV is in the same space proximity with the node or way from the OSM dataset.
