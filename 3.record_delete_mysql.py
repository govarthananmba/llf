import mysql.connector
from mysql.connector import Error

def delete_all_data():
    try:
        # Establish a connection to the MySQL database
        connection = mysql.connector.connect(
            host='localhost',  # e.g., 'localhost' or '127.0.0.1'
            database='final',
            user='root',
            password='1010'
        )

        if connection.is_connected():
            cursor = connection.cursor()
            # Replace 'your_table_name' with the name of your table
            delete_query = "DELETE FROM app_formresponse"
            cursor.execute(delete_query)
            connection.commit()  # Make sure to commit the changes
            print("All data has been deleted successfully")

    except Error as e:
        print(f"Error: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed")

if __name__ == "__main__":
    delete_all_data()
