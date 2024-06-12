from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import pandas as pd
import openai
import markdown

app = Flask(__name__, template_folder='.')
CORS(app)


import pathlib
root = pathlib.Path(__file__).parent

# Configure your OpenAI API key here
openai.api_key = open(root / 'OPENAI_API_KEY.txt').read().strip()

# Load your dataset
data = pd.read_csv(root / 'New_filter_sections.csv')

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

    ]

    filtered_data = dataframe[dataframe.columns.intersection(columns_to_keep)]

    # filtered_data = filtered_data.rename(columns={'type': 'activity'})

    return filtered_data

def get_most_frequent_column(input_file_path):
    """
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
    return filtered_data


def three_questions(merged_dataframe):
    questions = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
               {"role": "system", "content": f"You are a travel agents that want to find the perfect place for the user. You need to asimilate the dataframe given by the user and look only at the possible fill colloms that you have the data and that are different from each other so that the user can choose, and create 3 question that will help you find the perfect location."},
               {"role": "user", "content": f"'{merged_dataframe}'" }
        ]
    )
    return markdown.markdown(questions.choices[0].message.content)

def general_question(values):
        value_options = "\n".join([f"{i+1}. {v}" for i, v in enumerate(values)])
        question = f"Choose a number corresponding to the value you want to filter by:\n{value_options}"
        return question
def final(merged_dataframe, user_input):
    final_answer = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": f"You are a travel agents that want to find the perfect place for the user. You need to asimilate theis database '{merged_dataframe}'and based on the user answer to choose exactly one place that you think will be best to recomand. Make sure that you specify the name of the place that is found on the title collom. Also make everything in a sentance specifying only the colloms with value"},
                {"role": "user", "content": f"'{user_input}'" }
        ]
    )
        
    return markdown.markdown(final_answer.choices[0].message.content)


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
     

def choise(database,user_input, collom):
    if user_input == 'yes':
        new = filter_data_by_column_value(database,collom,user_input)
    elif user_input == 'no':
        new = database
    else:
        new = filter_data_by_column_value(database,collom,user_input)
    return new




@app.route('/answer', methods=['POST'])
def answer(): 
    state = request.get_json(force=True)
    counter = state.get('count', 0)
    if not counter: 
        # first question
        dataframe = filter_columns(data)
        colloms_filter = []
        collom, values = get_most_frequent_column(dataframe)
        colloms_filter.append(collom)
        # first_question = general_question(values)
        return {
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
        if collom not in dataframe.columns:
             print(f"Error: Column '{collom}' not found in the DataFrame.")
        print('Filtering column:', collom)
        new_dataframe = choise(dataframe,user_input, collom)
        print('New dataframe length:', len(new_dataframe))
        
        
        # Filter dataframe on columns
        colloms_filter = state.get('colloms_filter')
        colloms_filter = list(new_dataframe.columns.intersection(colloms_filter))
        new_dataframe = new_dataframe.drop(columns=colloms_filter)
        new_dataframe = new_dataframe.dropna(axis=1, how='all')

        print('New dataframe columns:', new_dataframe.columns)
        print(new_dataframe)

        
    
    if len(new_dataframe )> 10:
            collom, values = get_most_frequent_column(new_dataframe)
            colloms_filter.append(collom)
            print('next column to filter is ', collom)

            if collom in ['wheelchair','takeaway', 'internet_access','private_bath' , 'air_conditioning', 'balcony', 'kitchen', 'tv']:
                response = f'Do you need {collom}?'
                return {
                    'count': counter, 
                    'index': list(new_dataframe.index),
                    'next_question': response, 
                    'values':['yes', 'no'],
                    'collom': collom,
                    'colloms_filter': colloms_filter,
                }
            else:
                return {
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

        response = three_questions(filtered_dataframe)
        return {
            'count': counter, 
            'index': list(new_dataframe.index),
            'next_question': response, 
            'values': list(filtered_dataframe['title']),
            'collom': 'title',
            'colloms_filter': colloms_filter,
        }
    else:
        filtered_dataframe = data.loc[new_dataframe.index].drop(columns=colloms_filter).dropna(axis=1, how='all').iloc[0]
        print('filtered', filtered_dataframe)

        response = final_location(filtered_dataframe)
        return {
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




