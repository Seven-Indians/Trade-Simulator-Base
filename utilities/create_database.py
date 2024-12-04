import sqlite3

# Connect to the database (or create it if it doesn't exist)
conn = sqlite3.connect('databases/trade_simulator.db')

# Create a cursor object
cursor = conn.cursor()

# Create the table
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    user TEXT PRIMARY KEY,
    stocks TEXT,
    balance REAL NOT NULL
)
''')

# Commit the changes and close the connection
conn.commit()
conn.close()

print("Database and table created successfully.")
