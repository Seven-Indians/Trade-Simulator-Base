import sqlite3
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog

def display_database(file_path):
    conn = sqlite3.connect(file_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    if not tables:
        print("No tables found in the database.")
        return
    
    table_name = tables[0][0]
    cursor.execute(f"SELECT * FROM {table_name}")
    rows = cursor.fetchall()
    columns = [description[0] for description in cursor.description]
    
    conn.close()
    
    root = tk.Tk()
    root.title("Database Viewer")
    
    tree = ttk.Treeview(root, columns=columns, show='headings')
    tree.pack(expand=True, fill='both')
    
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=100, anchor = 'center')
    
    for row in rows:
        tree.insert('', 'end', values=row)
    
    root.mainloop()

def open_file():
    file_path = filedialog.askopenfilename(filetypes=[("SQLite Database Files", "*.db"), ("All Files", "*.*")])
    if file_path:
        display_database(file_path)

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    open_file()