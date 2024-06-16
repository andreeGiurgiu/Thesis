from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import pandas as pd
import openai
import markdown
import time
import math

app = Flask(__name__, template_folder='.')
CORS(app)


import pathlib
root = pathlib.Path(__file__).parent
print(root)

# Configure your OpenAI API key here
key = open(root / 'OPENAI_API_KEY.txt').read().strip()
print(key)
openai.api_key = key

import pathlib
root = pathlib.Path(__file__).parent
print(root)

# Configure your OpenAI API key here
key = open(root / 'OPENAI_API_KEY.txt').read().strip()
print(key)
openai.api_key = key

# Load your dataset
data = pd.read_csv(root /'Final_Database2.csv')

def filter_columns(dataframe):
    # List of columns to keep
    columns_to_keep = [
        'wheelchair', 'dietary', 'takeaway', 
        'indoor/outdoor seating', 'cuisine', 'beauty', 'shop', 
        'stars', 'internet_access', 'smoking', 'type', 'amenity', 
        'meal', 'category', 'Service', 
        'accommodation_type', 'drink type', 
        'music type', 'Ambiental', 'price range', 'private_bath' , 'air_conditioning' , 'bath' , 'balcony' , 'view' ,
        'kitchen' , 'tv',  'bed_number' , 'size','shop','brand'

        'meal', 'category', 'Service', 
        'accommodation_type', 'drink type', 
        'music type', 'Ambiental', 'price range', 'private_bath' , 'air_conditioning' , 'bath' , 'balcony' , 'view' ,
        'kitchen' , 'tv',  'bed_number' , 'size','shop','brand'

    ]

    filtered_data = dataframe[dataframe.columns.intersection(columns_to_keep)]


    return filtered_data

def get_most_frequent_column(input_file_path):
    """
    Identify the column with the highest number of filled (non-null) cells in a CSV file 
    Identify the column with the highest number of filled (non-null) cells in a CSV file 
    and return its unique values.

    Parameters:
    input_file_path (str): The path to the input CSV file.

    Returns:
    tuple: A tuple containing the name of the column and its unique values as a pandas Series.
    """
   

    # Calculate the number of non-null values in each column
    non_null_counts = input_file_path.count()

    # Identify the column with the highest number of non-null values
    most_filled_column = non_null_counts.idxmax()

    # Retrieve the unique values from this column
    unique_values = input_file_path[most_filled_column].dropna().unique()

    return (most_filled_column, unique_values)

def filter_data_by_column_value(input_file_path, column_name, filter_value):
    """
    Filter a CSV file based on a specified column and a value, returning the filtered DataFrame.

    Parameters:
    input_file_path (str): The input dataframe.
    column_name (str): The name of the column to filter by.
    filter_value (str): The value in the column to filter for.

    Returns:
    pandas.DataFrame: A DataFrame containing only the rows where the column value matches the filter value.
    """

    # Filter the data based on the column name and value
    if filter_value not in input_file_path[column_name].values:
        print(f"Error: Value '{filter_value}' not found in column '{column_name}'.")
        print(f"Unique values in '{column_name}':", input_file_path[column_name].unique())
    filtered_data = input_file_path[input_file_path[column_name] == filter_value]
    if filter_value not in input_file_path[column_name].values:
        print(f"Error: Value '{filter_value}' not found in column '{column_name}'.")
        print(f"Unique values in '{column_name}':", input_file_path[column_name].unique())
    filtered_data = input_file_path[input_file_path[column_name] == filter_value]
    return filtered_data


def three_questions(merged_dataframe,value):
    questions = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
               {"role": "system", "content": f"You are a travel agents that recives a dataframe from the user and needs to explain the places by first saying the title of the place from this '{value}' list and then a short explanation about the values that you find in the cells that are fill. Please just mention the explanation not give a list of the colloms are full or not"},
               {"role": "user", "content": f"'{merged_dataframe}'" }
        ]
    )
    return markdown.markdown(questions.choices[0].message.content)


     

def choise(database,user_input, collom):
    if user_input == 'yes':
        new = filter_data_by_column_value(database,collom,user_input)
    elif user_input == 'no':
        new = database
    else:
        new = filter_data_by_column_value(database,collom,user_input)
    return new



def final_location(dataframe):
    final_answer = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": f"You are a travel agents that want to find the perfect place for the user. You need to asimilate the database given by the user and explain the possible option. Make sure that you first say the name that you find in the title or name collom of the places and then a short explanation. Give a cursive explanation. Say just thing that make sense for the place. Just explain the name, where can I find it and if it has a wibsite please also share it"},
                 {"role": "user", "content": f"'{dataframe}'" }
        ]
    )
    top_value = final_answer.choices[0].message.content
    return markdown.markdown(top_value)
     


def is_nan_str(value):
    try:
        return math.isnan(float(value))
    except (TypeError, ValueError):
        return value.lower() == 'nan'


@app.route('/answer', methods=['POST'])
def answer(): 
    
    state = request.get_json(force=True)
    fname = state.get('dataset') or 'Final_Database1.csv'
    print('Using ', fname)
    # Load your dataset
    data = pd.read_csv(root / fname)

    counter = state.get('count', 0)
    if not counter: 
        # first question
        dataframe = filter_columns(data)
        colloms_filter = []
        collom, values = get_most_frequent_column(dataframe)
        colloms_filter.append(collom)

        return {
            'start_time': state.get('start_time', time.time()),
            'count': counter, 
            'index': list(dataframe.index),
            'next_question': f'Please filter {collom}:', 
            'values':[str(v) for v in values],
            'collom': collom,
            'colloms_filter': colloms_filter,
        }
    else:
        # next questions
        dataframe = filter_columns(data).loc[state['index']]

        user_input = state.get('answer')
        collom = state.get('collom')
        
        if collom == 'title':
             dataframe = data.loc[dataframe.index]

        new_dataframe = choise(dataframe, user_input, collom)
        print('New dataframe length:', len(new_dataframe))

      
             # Filter dataframe on columns
        colloms_filter = state.get('colloms_filter')
        colloms_filter = list(new_dataframe.columns.intersection(colloms_filter))

        new_dataframe = new_dataframe.drop(columns=colloms_filter)
        new_dataframe = new_dataframe.dropna(axis=1, how='all')
        

        print('New dataframe columns:', new_dataframe.columns)
        print(new_dataframe)

        
    
    if len(new_dataframe )>= 10:
            collom, values = get_most_frequent_column(new_dataframe)
            colloms_filter.append(collom)
            print('next column to filter is ', collom)

            if collom in ['wheelchair','takeaway', 'internet_access','private_bath' , 'air_conditioning', 'balcony', 'kitchen', 'tv']:
                response = f'Do you need {collom}?'
                return {
                    'start_time': state.get('start_time', time.time()),
                    'count': counter, 
                    'index': list(new_dataframe.index),
                    'next_question': response, 
                    'values':['yes', 'no'],
                    'collom': collom,
                    'colloms_filter': colloms_filter,
                }
            else:
                return {
                    'start_time': state.get('start_time', time.time()),
                    'count': counter, 
                    'index': list(new_dataframe.index),
                    'next_question': f'Please filter {collom}:', 
                    'values':[str(v) for v in values],
                    'collom': collom,
                    'colloms_filter': colloms_filter,
                }
    elif len(new_dataframe)>1: 
        filtered_dataframe = data.loc[new_dataframe.index].drop(columns=colloms_filter).dropna(axis=1, how='all')
        print('filtered', filtered_dataframe)

        
        if 'title' in filtered_dataframe:
           value = list(filtered_dataframe['title'])
        elif 'name' in filtered_dataframe:
           value = list(filtered_dataframe['name'])
        else:
            value = list(filtered_dataframe['website'])
        value = [x for x in value if not is_nan_str(x)]
        response = three_questions(filtered_dataframe,value)
        print(value)
        return {
            'start_time': state.get('start_time', time.time()),
            'count': counter, 
            'index': list(new_dataframe.index),
            'next_question': response, 
            'values': value,
            'collom': 'title',
            'colloms_filter': colloms_filter,
        }
    else:
        filtered_dataframe = data.loc[new_dataframe.index].drop(columns=colloms_filter).dropna(axis=1, how='all').iloc[0]
        print('filtered', filtered_dataframe)
        if 'title' in filtered_dataframe:
           response = 'Recommendation: ' + str(filtered_dataframe['title'])
        elif 'name' in filtered_dataframe:
           response = 'Recommendation: ' + str(filtered_dataframe['name'])
        else:
            response = final_location(filtered_dataframe)

        seconds = int(time.time() - state.get('start_time'))
        response += f'<br><br>It took {counter} questions and {seconds} seconds.'
        return {
            'start_time': state.get('start_time', time.time()),
            'count': counter, 
            'index': list(new_dataframe.index),
            'next_question': response, 
            'values':[]
        }





@app.route('/finalize', methods=['GET'])
def finalize():
    depression_status = ' Thank you!'
    return jsonify({'depression_status': depression_status})

@app.route('/')
def hello_world():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
    app.run(debug=True)
