import sys
import os
import time
import sqlite3
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from PIL import Image, ImageTk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))
import bot #type: ignore
import stock_manager #type: ignore

def get_data():
    conn = sqlite3.connect('databases/stock.db')
    cursor = conn.cursor()

    cursor.execute('SELECT stock_value FROM users ORDER BY serial DESC LIMIT 60')
    raw_data = cursor.fetchall()
    data = []
    for i in range(-1, -len(raw_data)-1, -1):
        data.append(raw_data[i][0])

    return data

class TradeSimulatorApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Trade Simulator")
        self.attributes("-fullscreen", True)

        # Load and display logo image
        self.logo_image = Image.open("media/logo.png")
        self.logo_photo = ImageTk.PhotoImage(self.logo_image)
        self.logo_label = tk.Label(self, image=self.logo_photo)
        self.logo_label.pack(pady=5)

        # Create a frame for the chart
        self.chart_frame = tk.Frame(self)
        self.chart_frame.pack(fill=tk.BOTH, expand=True)

        # Create a figure for the chart
        self.fig, self.ax = plt.subplots()
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.chart_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Initialize data for the chart
        self.data = get_data()
        self.line, = self.ax.plot(self.data)

        # Display Box
        self.info_frame = tk.Frame(self.chart_frame, width=200, bg="lightgrey")
        self.info_frame.pack(side=tk.RIGHT, fill=tk.Y)

        # Add some text and values to the info box
        self.info_label = tk.Label(self.info_frame, text="User Information", bg="lightgrey", font=("Arial", 14))
        self.info_label.pack(pady=10)

        self.user_label = tk.Label(self.info_frame, text="User: Default", bg="lightgrey", font=("Arial", 12))
        self.user_label.pack(pady=5)

        self.balance = 1000
        str1 = "Balance: ₹" + str(self.balance)
        self.balance_label = tk.Label(self.info_frame, text=str1, bg="lightgrey", font=("Arial", 12))
        self.balance_label.pack(pady=5)

        self.stocks_owned = 0
        str4 = "Stocks Owned: " + str(self.stocks_owned)
        self.stocks_owned_label = tk.Label(self.info_frame, text=str4, bg="lightgrey", font=("Arial", 12))
        self.stocks_owned_label.pack(pady=5)

        self.info_label = tk.Label(self.info_frame, text="Stock Information", bg="lightgrey", font=("Arial", 14))
        self.info_label.pack(pady=10)

        self.stock_value = 0
        str2 = "Stocks: ₹" + str(self.stock_value * 1000)
        self.net_worth_label = tk.Label(self.info_frame, text=str2, bg="lightgrey", font=("Arial", 12))
        self.net_worth_label.pack(pady=5)

        str3 = "Current Value: ₹" + str(self.stock_value)
        self.current_stock_label = tk.Label(self.info_frame, text=str3, bg="lightgrey", font=("Arial", 12))
        self.current_stock_label.pack(pady=5)

        # Create Buy and Sell buttons
        self.button_frame = tk.Frame(self)
        self.button_frame.pack(pady=10)
        self.buy_button = ttk.Button(
            self.button_frame, 
            text="Buy", 
            command=lambda: self.open_buy_popup(self.balance, self.stock_value, self.stocks_owned))
        self.buy_button.pack(side=tk.LEFT, padx=100)
        self.sell_button = ttk.Button(
            self.button_frame, 
            text="Sell", 
            command=lambda: self.open_sell_popup(self.balance, self.stock_value, self.stocks_owned))
        self.sell_button.pack(side=tk.LEFT, padx=100)

        # Start updating the chart
        self.update_chart()

    def update_chart(self):
        # Update data
        b, s = bot.main()
        self.stock_value = stock_manager.main(b, s)
        self.data.append(self.stock_value)
        self.data.pop(0)
        self.line.set_ydata(self.data)
        self.ax.relim()
        self.ax.autoscale_view()
        self.canvas.draw()

        # Update stock information
        self.net_worth_label.config(text=f"Net Worth: ₹ {str(((self.stock_value * 100000)//1)*100)}")
        self.current_stock_label.config(text=f"Current Value: ₹{self.stock_value}")

        # Schedule the next update
        self.after(1000, self.update_chart)

    def open_buy_popup(self, balance, stock_value, stocks_owned):
        self.open_popup("Buy", balance, stock_value, stocks_owned)

    def open_sell_popup(self, balance, stock_value, stocks_owned):
        self.open_popup("Sell", balance, stock_value, stocks_owned)

    def open_popup(self, action, balance, stock_value, stocks_owned):
        popup = tk.Toplevel(self)
        popup.title(f"{action} Stocks")

        label = tk.Label(popup, text=f"Enter number of stocks to {action.lower()}:")
        label.pack(pady=10)

        entry = tk.Entry(popup)
        entry.pack(pady=5)

        confirm_button = ttk.Button(popup, text="Confirm", command=lambda: self.confirm_action(action, entry.get(), popup, balance, stock_value, stocks_owned))
        confirm_button.pack(pady=10)

    def confirm_action(self, action, num_stocks, popup, balance, stock_value, stocks_owned):
        try:
            num_stocks = int(num_stocks)
            if action == "Buy":
                if num_stocks * stock_value <= balance:
                    self.balance -= num_stocks * stock_value
                    self.balance = (self.balance*100//1)/100
                    self.stocks_owned += num_stocks
                    self.balance_label.config(text=f"Balance: ₹{self.balance}")
                    self.stocks_owned_label.config(text=f"Stocks Owned: {self.stocks_owned}")
                    popup.destroy()
                    messagebox.showinfo("Success", f"Successfully bought {num_stocks} stocks.")
                else:
                    messagebox.showerror("Insufficient Balance", "You do not have enough balance to complete this transaction.")

            elif action == "Sell":
                if num_stocks <= stocks_owned:
                    self.balance += num_stocks * stock_value
                    self.stocks_owned -= num_stocks
                    self.balance_label.config(text=f"Balance: ₹{self.balance}")
                    self.stocks_owned_label.config(text=f"Stocks Owned: {self.stocks_owned}")
                    popup.destroy()
                    messagebox.showinfo("Success", f"Successfully sold {num_stocks} stocks.")
                else:
                    messagebox.showerror("Insufficient Stocks", "You do not have enough stocks to complete this transaction.")
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid number of stocks.")


if __name__ == "__main__":
    app = TradeSimulatorApp()
    app.mainloop()