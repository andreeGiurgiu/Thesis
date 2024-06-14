
from flask import Flask, request, jsonify, session
from flask_cors import CORS
from flask_session import Session  # For session management
import pandas as pd
import openai

app = Flask(__name__)
CORS(app)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config["SECRET_KEY"] = "supersecretkey"
Session(app)

openai.api_key = 'x'

# Load your dataset
data = pd.read_csv('/Users/andreeagiurgiu/Desktop/Thesis/New_filter_sections.csv')

# Getting only the colloms on which we want to do the filtering

def filter_columns(dataframe):
    # List of columns to keep
    columns_to_keep = [
        'wheelchair', 'dietary', 'takeaway', 
        'indoor/outdoor seating', 'cuisine', 'beauty', 'shop', 
        'stars', 'internet_access', 'smoking', 'type', 'amenity', 
        'meal', 'Micheline', 'category', 'Service', 
        'accommodation_type', 'drink type', 
        'music type', 'Ambiental', 'price range', 'private_bath' , 'air_conditioning' , 'bath' , 'balcony' , 'view' ,
        'kitchen' , 'tv',  'bed_number' , 'size','shop','brand'

    ]

    filtered_data = dataframe[dataframe.columns.intersection(columns_to_keep)]

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
    # Load the CSV file
    data = input_file_path

    # Calculate the number of non-null values in each column
    non_null_counts = data.count()

    # Identify the column with the highest number of non-null values
    most_filled_column = non_null_counts.idxmax()

    # Retrieve the unique values from this column
    unique_values = data[most_filled_column].dropna().unique()

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
    # Load the data
    data = input_file_path

    # Filter the data based on the column name and value
    filtered_data = data[data[column_name] == filter_value]

    return filtered_data

def yes_no_question(collom):
    questions = openai.chat.completions.create(
               model="gpt-3.5-turbo",
               messages=[
                   {"role": "system", "content": f"Create a simple question that just asked a person if they need the amenity given by the user "},
                   {"role": "user", "content": f"'{collom}'"}
               ]
           )

    return questions.choices[0].message.content

def three_questions(merged_dataframe,colloms_filter):
    questions = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
               {"role": "system", "content": f"You are a travel agents that want to find the perfect place for the user. You need to asimilate the dataframe given by the user and look only at the possible fill colloms that you have the data and that are different from each other so that the user can choose, and create 3 question that will help you find the perfect location. Try to not ask about this colloms '{colloms_filter}' as the user alredy filter on this "},
               {"role": "user", "content": f"'{merged_dataframe}'" }
        ]
    )
    return questions.choices[0].message.content

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
        
    return final_answer.choices[0].message.content
     
    

@app.route('/start', methods=['GET'])
def start():
    # Initial question
    #first_question = "Hello! I am Kuromi. I am here to help you in choosing the best place or activity for you in your travelling plans in Amsterdam?"
    #most variant collom

    session['dataframe'] = data
    session.modified = True
    session['counter'] = 0
    session['columns_filter'] = []
    colloms_filter = []
    collom, values = get_most_frequent_column(filter_columns(data))
    colloms_filter.append(collom)
    session['columns_filter'] = colloms_filter
    first_question = general_question(values)


    return jsonify({'next_question': first_question})



@app.route('/answer', methods=['POST'])
def answer(): 
    counter = session.get('counter')
    columns_filter = session.get('columns_filter')
    if counter > 0:
        new_dataframe = session.get('dataframe')
    else:
        new_dataframe = data
  
    collom, values = get_most_frequent_column(filter_columns(new_dataframe))
    if len(new_dataframe) > 10: 
        input = request.json
        user_input = input.get('answer')
        columns_filter.append(collom)
        print(collom)
        print(values)
        print(user_input)
        if user_input in ['0','1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18','19','20']:
            print(values[int(user_input)])
            new_dataframe = filter_data_by_column_value(new_dataframe,collom,values[int(user_input)])
      
        
        elif user_input == 'yes':
             new_dataframe = filter_data_by_column_value(new_dataframe,collom,user_input)
             
        
        new_dataframe = new_dataframe.drop(columns=[collom])
        collom, values = get_most_frequent_column(filter_columns(new_dataframe))
        while len(values) < 2 and len(new_dataframe) > 10:
            new_dataframe = filter_data_by_column_value(new_dataframe,collom,values[0])
            new_dataframe = new_dataframe.drop(columns=[collom])
            columns_filter.append(collom)
            collom, values = get_most_frequent_column(filter_columns(new_dataframe))
        if collom in ['wheelchair','takeaway', 'internet_access','private_bath' , 'air_conditioning', 'balcony', 'kitchen', 'tv']:
            response = yes_no_question(collom)
            finished = False
        elif len(new_dataframe) < 10 and len(new_dataframe)> 1:
            merged_dataframe = pd.merge(new_dataframe, data, on='title', how='inner')
            response = three_questions(merged_dataframe,columns_filter)
            finished = False
        else:
            response = general_question(values)
            finished = False
        
    else:
        merged_dataframe = pd.merge(new_dataframe, data, on='title', how='inner')
        user_input = data.get(merged_dataframe,'answer')
        response = final(user_input)
        finished = True
    session['dataframe'] = new_dataframe.to_dict(orient='records')
    session['counter'] = counter + 1
    session['columns_filter'] = columns_filter
    session.modified = True

    return jsonify({'next_question': response, 'finished': finished})

@app.route('/finalize', methods=['GET'])
def finalize():
    depression_status = ' Thank you!'
    return jsonify({'depression_status': depression_status})

if __name__ == '__main__':
    app.run(debug=True)
