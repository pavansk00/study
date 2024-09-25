import mysql.connector
from mysql.connector import Error
from config import MYSQL_CONFIG  # Import the MYSQL_CONFIG dictionary from config.py

def mysql_connect():
    connection = None  # Initialize the connection variable
    try:
        # Use the configuration from config.py
        connection = mysql.connector.connect(
            host=MYSQL_CONFIG['host'],
            database=MYSQL_CONFIG['database'],
            user=MYSQL_CONFIG['user'],
            password=MYSQL_CONFIG['password']
        )
        
        if connection.is_connected():
            print(f"Connected to MySQL database: {connection.get_server_info()}")
            
            # Create a cursor to execute SQL queries
            cursor = connection.cursor(dictionary=True, buffered=True)
            
            # Optional: Execute a sample query
            query = """
                    select * from student
                    """
            cursor.execute(query)
            current_db = cursor.fetchall()
            print(f"fetch data: {current_db}")
            return current_db

    except Error as e:
        print(f"Error: {e}")

    finally:
        if connection is not None and connection.is_connected():
            cursor.close()  # Ensure cursor is closed
            connection.close()  # Ensure connection is closed
            print("MySQL connection is closed")

# Optionally, add a way to run this script directly
if __name__ == "__main__":
    mysql_connect()

