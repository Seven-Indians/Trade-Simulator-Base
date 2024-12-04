import sqlite3

def add_user_to_database(username, database_file='databases/user.db'):
    conn = sqlite3.connect(database_file)
    cursor = conn.cursor()

    # Insert user data
    cursor.execute('''
        INSERT INTO users (user, balance, stocks)
        VALUES (?, ?, ?)
    ''', (username, 10000, 0))

    conn.commit()
    conn.close()

if __name__ == "__main__":
    username = input("Enter username: ")
    add_user_to_database(username)
    print(f"User {username} added to the database with balance 10000 and 0 stocks.")
