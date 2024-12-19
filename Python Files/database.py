import mysql.connector
import os
from dotenv import load_dotenv
from timetable import *
from scrape_course import *

def connect_to_database():
    """
    Connect to the MySQL database using the credentials from environment variables.

    Returns:
        connection: A connection object to the MySQL database.
        cursor: A cursor object to execute queries.
    """
    # Load environment variables
    load_dotenv()

    try:
        connection = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )
        cursor = connection.cursor()
        print("Connected to the database successfully!")
        return connection, cursor
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None, None