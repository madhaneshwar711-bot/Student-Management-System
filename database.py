"""
database.py
------------
This file is responsible for everything related to talking to MySQL:
- Connecting to the MySQL server
- Creating the database automatically if it does not exist
- Creating the required tables (admins, students) if they do not exist
- Closing the connection cleanly when the app exits
"""

import mysql.connector
from mysql.connector import Error

from config import HOST, USER, PASSWORD, DATABASE


class Database:
    """
    Handles the MySQL connection lifecycle:
    connect -> create tables -> (app runs) -> close connection.
    """

    def __init__(self):
        self.connection = None
        self.cursor = None

    def connect(self):
        try:
            temp_connection = mysql.connector.connect(
                host=HOST,
                user=USER,
                password=PASSWORD,
            )
            temp_cursor = temp_connection.cursor()

            temp_cursor.execute(
                f"CREATE DATABASE IF NOT EXISTS {DATABASE}"
            )

            temp_cursor.close()
            temp_connection.close()

            self.connection = mysql.connector.connect(
                host=HOST,
                user=USER,
                password=PASSWORD,
                database=DATABASE,
            )
            self.cursor = self.connection.cursor()

            print(f"[INFO] Connected to MySQL database '{DATABASE}' successfully.")
            return True

        except Error as e:
            print(f"[ERROR] Could not connect to MySQL: {e}")
            return False

    def create_tables(self):
        if self.cursor is None:
            print("[ERROR] No database connection. Call connect() first.")
            return False

        try:
            create_admins_table = """
                CREATE TABLE IF NOT EXISTS admins (
                    admin_id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(50) NOT NULL UNIQUE,
                    password VARCHAR(255) NOT NULL
                )
            """
            self.cursor.execute(create_admins_table)

            create_students_table = """
                CREATE TABLE IF NOT EXISTS students (
                    student_id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    age INT NOT NULL,
                    gender VARCHAR(20) NOT NULL,
                    course VARCHAR(100) NOT NULL,
                    email VARCHAR(100) NOT NULL UNIQUE,
                    phone VARCHAR(20) NOT NULL,
                    address TEXT
                )
            """
            self.cursor.execute(create_students_table)

            self.connection.commit()
            print("[INFO] Tables verified/created successfully.")
            return True

        except Error as e:
            print(f"[ERROR] Could not create tables: {e}")
            return False

    def close_connection(self):
        try:
            if self.cursor is not None:
                self.cursor.close()
            if self.connection is not None and self.connection.is_connected():
                self.connection.close()
                print("[INFO] MySQL connection closed.")
        except Error as e:
            print(f"[ERROR] Problem while closing connection: {e}")


if __name__ == "__main__":
    db = Database()
    if db.connect():
        db.create_tables()
        db.close_connection()