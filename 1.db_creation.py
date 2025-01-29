# Install Mysql on your computer
# https://dev.mysql.com/downloads/installer/
# pip install mysql

# pip install mysql-connector-python 



import mysql.connector

# Establish the connection
dataBase = mysql.connector.connect(
    host='localhost',
    user='root',
    password='1010'
)

# Create a cursor object
cursorObject = dataBase.cursor()

# Execute a SQL query to create a database
cursorObject.execute("CREATE DATABASE final")

# Print confirmation message
print("All done")

# Close the cursor and the connection
cursorObject.close()
dataBase.close()