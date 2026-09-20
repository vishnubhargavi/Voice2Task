import sqlite3


DATABASE = "voice2task.db"


def get_connection():

    connection = sqlite3.connect(
        DATABASE
    )

    connection.row_factory = sqlite3.Row

    return connection


def create_tables():

    connection = get_connection()

    cursor = connection.cursor()


    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            title TEXT NOT NULL,

            deadline TEXT,

            source TEXT,

            completed INTEGER DEFAULT 0

        )
    """)


    connection.commit()

    connection.close()