import sqlite3

# Connect to the database (or create it if it doesn't exist)
conn = sqlite3.connect('databases/stock.db')

# Create a cursor object
cursor = conn.cursor()

# Create the table
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    serial INTEGER PRIMARY KEY AUTOINCREMENT,
    stock_value REAL NOT NULL
)
''')

# Commit the changes and close the connection
conn.commit()
conn.close()

print("Database and table created successfully.")
