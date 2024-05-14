import pandas as pd
import openai
import numpy as np
import csv

# Configure your OpenAI API key here
openai.api_key = 'X'



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

def manin_conversation(dataframe):

    #first question
    print('Hey, with what can I help you? Would you like to search for a place to sleep, eat, drink, do an activity, or buy ?')
    user_input = input("Type your response here. Please just say sleep, eat, drink, do or buy: ")

    #filter data based on sleep, eat, drink, do or buy
    print(user_input.strip().lower())
    new_dataframe = filter_data_by_column_value(dataframe,'type',user_input.strip().lower())
    print(user_input)
    

    #loop until last 10 rows in order for the chat to be able to see all the data
    while len(dataframe) > 10:

       #most variant collom
       collom, values = get_most_frequent_column(filter_columns(new_dataframe))
       print(values)
       
       #chat asking + user choosing the variable
       response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a travel agent that is helping the user to find the best thing to do in Amsterdam. Create one question in order for the user to choose one of the filtering possible values. This question will bring you closer to finding the best location. Keep in mind the user can only choose this specific variables"},
            {"role": "user", "content": f"'{values}'" }
        ]
    )
       question = response.choices[0].message.content
       print(question)

       #chat giving the value
       user_input = input("Type your response here: ")
       value = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a system that is working on filtering data in order to find the best data points. In order to do so you need to choose one of the possible frequent values: '{values}' and give exactly just that one word so that the rest of the systme is able to filter. If the user is only giving you one words answers and it matching the frequent variable let that be your answer"},
            {"role": "user", "content": f"'{user_input}'"}
        ]
    )
       choise = value.choices[0].message.content
       print(choise)

       #filter basen on value
       new_dataframe = filter_data_by_column_value(new_dataframe,collom,choise)
    
    #return new_dataframe

    # let chat see all the data and choose tope 3 questions
    questions = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": f"You are a travel agents that want to find the perfect place for the user. You need to asimilate the dataframe given by the user and create 3 question that will help you find the perfect location "},
            {"role": "user", "content": f"'{new_dataframe}'" }
        ]
    )
    questions_ = questions.choices[0].message.content
    print(questions_)
    
    #based on user answers chat chose the perfect place to go
    user_input = input("Type your response here: ")
    final_answer = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": f"You are a travel agents that want to find the perfect place for the user. You need to asimilate theis database '{new_dataframe}'and based on the user answer to choose exactly one place that you think will be best to recomand"},
            {"role": "user", "content": f"'{user_input}'" }
        ]
    )
    top_value = final_answer.choices[0].message.content
    print(top_value)




input_data = pd.read_csv('/Users/andreeagiurgiu/Desktop/Thesis/New_filter_sections.csv')
final_data = manin_conversation(input_data)


# Display final datasl
print("\nReduced dataset based on your selections:")
print(final_data)