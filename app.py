from flask import Flask, request, jsonify, session
from flask_cors import CORS
from flask_session import Session  # For session management
import pandas as pd
import openai

app = Flask(__name__)
CORS(app)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

openai.api_key = 'sk-proj-fAgcyKyxgDuNFb5Ehbh2T3BlbkFJcAF0Xk1mXyhfPY0Q8HZp'

data = pd.read_csv('/Users/andreeagiurgiu/Desktop/Thesis/New_filter_sections.csv')

def filter_columns(dataframe):
    # List of columns to keep
    columns_to_keep = [
        'wheelchair', 'dietary', 'takeaway', 
        'indoor/outdoor seating', 'cuisine', 'beauty', 'shop', 
        'stars', 'internet_access', 'smoking', 'type', 'amenity', 
        'meal', 'Micheline', 'category', 'Service', 
        'room_facilities', 'accommodation_type', 'drink type', 
        'music type', 'Ambiental', 'price range'
    ]

    filtered_data = dataframe[dataframe.columns.intersection(columns_to_keep)]

    return filtered_data

def get_most_frequent_column(input_file_path):
    """
    Identify the column with the highest number of unique values in a CSV file 
    and return its unique values.

    Parameters:
    input_file_path (str): The path to the input CSV file.

    Returns:
    tuple: A tuple containing the name of the column and its unique values as a pandas Series.
    """
    # Load the CSV file
    data = input_file_path

    # Calculate the number of unique values in each column
    unique_values_count = data.nunique()

    # Identify the column with the highest number of unique values
    most_variant_column = unique_values_count.idxmax()

    # Retrieve the unique values from this column
    unique_values = data[most_variant_column].unique()

    return (most_variant_column, unique_values)


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
    # Load the data
    data = input_file_path

    # Filter the data based on the column name and value
    filtered_data = data[data[column_name] == filter_value]

    return filtered_data


@app.route('/start', methods=['GET'])
def start_conversation():
    session['conversation'] = []  # Initialize conversation history
    return jsonify({'next_question': "Hey, with what can I help you? Would you like to search for a place to sleep, eat, drink, do an activity, or buy ? Please just say sleep, eat, drink, do or buy:"})

@app.route('/answer', methods=['POST'])
def process_answer():
    user_input = request.json['answer']
    session['conversation'].append(user_input)  # Store user input in session
    
    filtered_data = filter_data_by_column_value(data[data['type'] == user_input.strip().lower()])
    
    
    if len(filtered_data) > 10:
        most_variant_column, values = get_most_frequent_column(filtered_data)
        next_question = f"Please specify your preference for {most_variant_column}: {', '.join(values)}"
        session['current_column'] = most_variant_column  # Store current column being queried
        return jsonify({'next_question': next_question})
    else:
        # If the conversation needs to be finalized or enough filtering has been done
        finalize_conversation(filtered_data)
        return jsonify({'final_data': filtered_data.to_dict(orient='records'), 'finished': True})

def finalize_conversation(filtered_data):
    # This function can summarize the conversation, provide final recommendations, etc.
    print("Finalizing conversation with the final set of data.")

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)  # use_reloader=False if running with Flask-Session
