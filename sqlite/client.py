import sqlite3


# Connect to SQLite database
conn = sqlite3.connect("library.db")
cursor = conn.cursor()


def select(*, column, query='*'):
    cursor.execute("SELECT * FROM " + column)
    result = cursor.fetchall()
    return result