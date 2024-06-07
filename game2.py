import pandas as pd
import openai
import numpy as np
import csv

# Configure your OpenAI API key here
openai.api_key = 'x'


# Load your dataset
data = pd.read_csv('New_filter_sections.csv')

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
     

def responses(database,collom,value,columns_filter):
    while len(value) < 2 and len(database) >10:
        print('B')
        new = filter_data_by_column_value(database,collom,value[0])
        new = new.drop(columns=[collom])
        collom, value = get_most_frequent_column(filter_columns(new))
        columns_filter.append(collom)
    if len(database) < 10 and len(database) > 1:
        merged_dataframe = pd.merge(database, data, on='title', how='inner')
        response = three_questions(merged_dataframe,columns_filter)
    elif len(database) < 2:
        response = final(database)
    if collom in ['wheelchair','takeaway', 'internet_access','private_bath' , 'air_conditioning', 'balcony', 'kitchen', 'tv']:
        response = yes_no_question(collom)
    else:
        response = general_question(value)
    
    return response,database, collom, value, columns_filter

def choise(database,user_input, collom, value):
    if user_input == 'yes':
        new = filter_data_by_column_value(database,collom,user_input)
        new = new.drop(columns=[collom])
    elif user_input == 'no':
        new = database
    else:
        print('A')
        new = filter_data_by_column_value(database,collom,value[int(user_input)-1])
        new = new.drop(columns=[collom])
    return new




if __name__ == '__main__':
    database = data
    c = 0
    columns_filter = []
    while len(database) > 10:
        collom, values = get_most_frequent_column(filter_columns(database))
        print(collom)
        response, database, collom, values, columns_filter = responses(database,collom,values,columns_filter)
        print(response)
        if len(database) < 10:
            c = 1
            break
        user_input = input("Type your response here: ")
        database = choise(database,user_input, collom, values)
        
    print('final')
    if c == 1: 
        user_input = input("Type your response here: ")
    merged_dataframe = pd.merge(database, data, on='title', how='inner')
    response =  final(merged_dataframe, user_input)
    print(response)
    print("Thank you for using our services! Hope I helped you find the perfect location! See you soon")
    



