import sqlite3

conn = sqlite3.connect('reminders.db')

# Create a cursor object to execute SQL commands
cursor = conn.cursor()

# Create a table to store reminders
cursor.execute('''
    CREATE TABLE IF NOT EXISTS reminders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        date TEXT,
        method TEXT,
        message TEXT
    )
''')

# Commit the changes and close the connection
conn.commit()
conn.close()
