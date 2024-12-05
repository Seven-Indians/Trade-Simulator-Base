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
        
        self.configure(bg="gray1")

        # Load and display logo image
        self.logo_image = Image.open("media/logo.png")
        self.logo_photo = ImageTk.PhotoImage(self.logo_image)
        self.logo_label = tk.Label(self, image=self.logo_photo, bg="gray1")
        self.logo_label.pack(pady=(20, 1))

        # Create a frame for the chart
        self.chart_frame = tk.Frame(self, bg="gray1")
        self.chart_frame.pack(fill=tk.BOTH, expand=True, padx=100)

        # Create a figure for the chart
        self.fig, self.ax = plt.subplots()
        self.fig.patch.set_facecolor('lightgrey')  
        self.ax.set_facecolor('white') 
        self.ax.grid(True, which='both', linestyle='--', linewidth=0.5, color='gray')
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.chart_frame)
        self.canvas.get_tk_widget().pack(side = tk.LEFT, fill = tk.BOTH, expand = True)

        # Initialize data for the chart
        self.data = get_data()
        self.line, = self.ax.plot(self.data, color="blue")
        self.ax.set_xlim(0, len(self.data)+5)

        # Display Box
        self.info_frame_1 = tk.Frame(self.chart_frame, width=300, height=300, bg="lightgrey")
        self.info_frame_1.place(relx=1.0, rely=0.0, anchor="ne", x=-10, y=10)

        # Add some text and values to the info box
        self.info_label = tk.Label(self.info_frame_1, text="User Information", bg="lightgrey", font=("Helvetika", 20))
        self.info_label.pack(pady=10, padx=10, anchor="ne")

        self.user_label = tk.Label(self.info_frame_1, text="User: Default", bg="lightgrey", font=("Helvetika", 16))
        self.user_label.pack(pady=10, padx=10, anchor="ne")

        self.balance = 1000
        str1 = "Balance: ₹" + str(self.balance)
        self.balance_label = tk.Label(self.info_frame_1, text=str1, bg="lightgrey", font=("Helvetika", 16))
        self.balance_label.pack(pady=10, padx=10, anchor="ne")

        self.stocks_owned = 0
        str4 = "Stocks Owned: " + str(self.stocks_owned)
        self.stocks_owned_label = tk.Label(self.info_frame_1, text=str4, bg="lightgrey", font=("Helvetika", 16))
        self.stocks_owned_label.pack(pady=10, padx=10, anchor="ne")

        self.info_frame_2 = tk.Frame(self.chart_frame, width=300, height=300, bg="lightgrey")
        self.info_frame_2.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-10)

        self.info_label = tk.Label(self.info_frame_2, text="Stock Information", bg="lightgrey", font=("Helvetika", 20))
        self.info_label.pack(pady=10, padx=10, anchor="se")

        self.stock_value = 0
        str2 = "Stocks: ₹" + str(self.stock_value * 1000)
        self.net_worth_label = tk.Label(self.info_frame_2, text=str2, bg="lightgrey", font=("Helvetika", 16))
        self.net_worth_label.pack(pady=10, padx=10, anchor="se")

        str3 = "Current Value: ₹" + str(self.stock_value)
        self.current_stock_label = tk.Label(self.info_frame_2, text=str3, bg="lightgrey", font=("Helvetika", 16))
        self.current_stock_label.pack(pady=10, padx=10, anchor="se")
        
        # Style for buttons
        s = ttk.Style()
        s.configure("TButton", font=("Helvetica", 20))

        # Create Buy and Sell buttons
        self.button_frame = tk.Frame(self, bg="gray1")
        self.button_frame.pack(pady=10, padx=100)
        self.buy_button = ttk.Button(
            self.button_frame, 
            text="Buy",
            style="TButton",
            command=lambda: self.open_buy_popup(self.balance, self.stock_value, self.stocks_owned))
        
        self.buy_button.pack(side=tk.LEFT, padx=100, pady=20, ipadx=20, ipady=10, anchor="center")  
        self.sell_button = ttk.Button(
            self.button_frame, 
            text="Sell", 
            style="TButton",
            command=lambda: self.open_sell_popup(self.balance, self.stock_value, self.stocks_owned))
        self.sell_button.pack(side=tk.LEFT, padx=100, pady = 20, ipadx=20, ipady=10, anchor="center")

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
        self.net_worth_label.config(text=f"Net Worth: ₹ {str(((self.stock_value * 100000)//1)/100)}")
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