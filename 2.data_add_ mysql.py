import pandas as pd
import mysql.connector
from mysql.connector import Error

# Load CSV data into a pandas DataFrame
csv_file_path = 'D:/Demo/Sample_Data.csv'

df = pd.read_csv(csv_file_path)

# Define the function to insert data into the database
def insert_data_into_db(df):
    try:
        # Establish the connection
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='1010',
            database='final'
        )

        if connection.is_connected():
            cursor = connection.cursor()

            # Create the insert query
            insert_query = """
            INSERT INTO app_record (student_id, first_name, last_name, school_name, email, gender, standard, section, phone, block, city, state, funder)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """

            # Iterate over DataFrame rows and insert into the database
            for _, row in df.iterrows():
                cursor.execute(insert_query, tuple(row))

            # Commit the transaction
            connection.commit()
            print("Data inserted successfully")

    except Error as e:
        print(f"Error: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed")

# Call the function to insert data
insert_data_into_db(df)