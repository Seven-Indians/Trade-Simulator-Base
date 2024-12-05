import sys
import os
import time
import sqlite3

#functions
def current_stock_value():
    conn = sqlite3.connect('databases/stock.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT stock_value FROM users ORDER BY serial DESC LIMIT 1')
    stock_value = cursor.fetchone()[0]
    
    conn.close()
    
    return stock_value

def next_stock_value(stock_value):
    conn = sqlite3.connect('databases/stock.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO users (stock_value)
        VALUES (?)
    ''', (stock_value,))
    
    conn.commit()
    conn.close()

def main(bought, sold):
    x = (bought - sold)/1000
    k = current_stock_value()
    y = k*(x**2) + (3/2)*k*x + k
    n = ((y*100)//1)/100
    next_stock_value(n)
    return n

if __name__ == "__main__":
    sys.path.append(os.path.join(os.path.dirname(__file__), '/../modules'))
    import bot

    n = int(input("Enter the number of values to be generated: "))
    for i in range(n):
        bought, sold = bot.main()
        main(bought, sold)
        time.sleep(0.001)
        