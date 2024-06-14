import pandas as pd
import openai
import numpy as np
import csv

# Configure your OpenAI API key here
openai.api_key = None



# Load your dataset
data = pd.read_csv('/Users/andreeagiurgiu/Desktop/Thesis/New_filter_sections3.csv')

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

def manin_conversation(dataframe):

    #first question
    new_dataframe  = dataframe
    colloms_filter = []
    

    #loop until last 10 rows in order for the chat to be able to see all the data
    while len(new_dataframe ) > 10:

       #most variant collom
       collom, values = get_most_frequent_column(filter_columns(new_dataframe))
       print(collom)
       colloms_filter.append(collom)

       if collom in ['wheelchair','takeaway', 'internet_access','private_bath' , 'air_conditioning', 'balcony', 'kitchen', 'tv']:
           questions = openai.chat.completions.create(
               model="gpt-3.5-turbo",
               messages=[
                   {"role": "system", "content": f"Create a simple question that just asked a person if they need the amenity given by the user "},
                   {"role": "user", "content": f"'{collom}'"}
               ]
           )

           questions_2 = questions.choices[0].message.content
           print(questions_2)
           user_input = input("Just say yes or no: ") 
           if user_input.lower() == 'yes':  # Use '==' for comparison instead of 'is'
               new_dataframe = filter_data_by_column_value(new_dataframe, collom, user_input)
               new_dataframe = new_dataframe.drop(columns=[collom])
           else:
               new_dataframe = new_dataframe
       else:
           if len(values) > 2:
               for idx, value in enumerate(values, start=1):
                   print(f"{idx}. {value}")

               # Ask the user to choose a filtering value
               user_input = int(input("Choose a number corresponding to the value you want to filter by: ")) - 1
               user_input = values[user_input]
           else:
               user_input = values[0]
            
            #filter basen on value
           new_dataframe = filter_data_by_column_value(new_dataframe,collom,user_input)
           print(new_dataframe)
           new_dataframe = new_dataframe.drop(columns=[collom])

    
    #return new_dataframe

    # let chat see all the data and choose tope 3 questions
    if len(new_dataframe) > 1:
        merged_dataframe = pd.merge(new_dataframe, dataframe, on='title', how='inner')
        questions = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
               {"role": "system", "content": f"You are a travel agents that want to find the perfect place for the user. You need to asimilate the dataframe given by the user and look only at the possible fill colloms that you have the data and that are different from each other so that the user can choose, and create 3 question that will help you find the perfect location. Try to not ask about this colloms '{colloms_filter}' as the user alredy filter on this "},
               {"role": "user", "content": f"'{merged_dataframe}'" }
        ]
    )
        questions_ = questions.choices[0].message.content
        print(questions_)
        
    
        #based on user answers chat chose the perfect place to go
        user_input = input("Type your response here: ")
        final_answer = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": f"You are a travel agents that want to find the perfect place for the user. You need to asimilate theis database '{merged_dataframe}'and based on the user answer to choose exactly one place that you think will be best to recomand. Make sure that you specify the name of the place that is found on the title or name collom if existed. Also make everything in a sentance specifying only the colloms with value. If there is unknow value just not mention it"},
                {"role": "user", "content": f"'{user_input}'" }
        ]
    )
        top_value = final_answer.choices[0].message.content
        return top_value
    else: 
        final_answer = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": f"You are a travel agents that want to find the perfect place for the user. You need to asimilate the database given by the user and explain the two possible option. Make sure that you first say the name that you find in the title or name collom of the places and then a short explanation. Give a cursive explanation. Say just thing that make sense for the place. Just explain the name, where can I find it and if it has a wibsite please also share it"},
                 {"role": "user", "content": f"'{new_dataframe}'" }
        ]
    )
        top_value = final_answer.choices[0].message.content
        return top_value




input_data = pd.read_csv('/Users/andreeagiurgiu/Desktop/Thesis/New_filter_sections3.csv')
final_data = manin_conversation(input_data)


# Display final datasl
print("\nReduced dataset based on your selections:")
print(final_data)