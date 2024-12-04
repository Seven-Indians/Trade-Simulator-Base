import sqlite3

def clear_table(db_name, table_name):
    conn = None
    try:
        # Connect to the database
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        
        # Clear the table
        cursor.execute(f"DELETE FROM {table_name}")
        cursor.execute(f"DELETE FROM sqlite_sequence WHERE name='{table_name}'")
        conn.commit()
        
        print(f"Table {table_name} cleared successfully.")
    except sqlite3.Error as error:
        print(f"Error while clearing table {table_name}: {error}")
    finally:
        if conn:
            conn.close()

# Example usage
clear_table('databases/stock.db', 'users')