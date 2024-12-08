import sys
import os
import sqlite3
import customtkinter as ctk
from tkinter import messagebox
from PIL import Image
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))
import bot  # type: ignore
import stock_manager  # type: ignore

def get_data():
    conn = sqlite3.connect('databases/stock.db')
    cursor = conn.cursor()

    cursor.execute('SELECT stock_value FROM users ORDER BY serial DESC LIMIT 60')
    raw_data = cursor.fetchall()
    data = []
    for i in range(-1, -len(raw_data)-1, -1):
        data.append(raw_data[i][0])

    return data

def get_user_info():
    conn = sqlite3.connect('databases/user.db')
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM users WHERE username = ?', ('Default',))
    user_info = cursor.fetchall()

    return user_info

def get_balance():
    user_info = get_user_info()
    return user_info[0][2]

def get_stocks_owned():
    user_info = get_user_info()
    return user_info[0][1]

def update_user_info(balance, stocks):
    conn = sqlite3.connect('databases/user.db')
    cursor = conn.cursor()

    cursor.execute('UPDATE users SET balance = ?, stocks = ? WHERE username = ?', (balance, stocks, 'Default'))
    conn.commit()
    conn.close()

class TradeSimulatorApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Trade Simulator")
        self.attributes("-fullscreen", True)

        ctk.set_appearance_mode("Dark")

        # Load and display logo image
        self.logo_image = ctk.CTkImage(Image.open("media/logo.png"), size=(1000, 100))
        self.logo_label = ctk.CTkLabel(self, image=self.logo_image, text="")
        self.logo_label.pack(pady=(20, 1))

        # Create a frame for the chart
        self.chart_frame = ctk.CTkFrame(self)
        self.chart_frame.pack(fill=ctk.BOTH, expand=True)

        # Create a figure for the chart
        self.fig, self.ax = plt.subplots()
        self.ax.grid(True, which='both', linestyle='--', linewidth=0.5)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.chart_frame)
        self.canvas.get_tk_widget().pack(side=ctk.LEFT, fill=ctk.BOTH, expand=True)

        # Initialize data for the chart
        self.data = get_data()
        self.line, = self.ax.plot(self.data, color="blue")
        self.ax.set_xlim(0, len(self.data))

        # Display Box
        self.info_frame_1 = ctk.CTkFrame(self.chart_frame, width=300, height=300)
        self.info_frame_1.place(relx=1.0, rely=0.0, anchor="ne", x=-10, y=10)

        # info box values
        self.info_label = ctk.CTkLabel(self.info_frame_1, text="User Information", font=("Helvetica", 20))
        self.info_label.pack(pady=10, padx=10, anchor="ne")

        self.user_label = ctk.CTkLabel(self.info_frame_1, text="User: Default", font=("Helvetica", 16))
        self.user_label.pack(pady=10, padx=10, anchor="ne")

        self.balance = get_balance()
        str1 = "Balance: ₹" + str(self.balance)
        self.balance_label = ctk.CTkLabel(self.info_frame_1, text=str1, font=("Helvetica", 16))
        self.balance_label.pack(pady=10, padx=10, anchor="ne")

        self.stocks_owned = get_stocks_owned()
        str4 = "Stocks Owned: " + str(self.stocks_owned)
        self.stocks_owned_label = ctk.CTkLabel(self.info_frame_1, text=str4, font=("Helvetica", 16))
        self.stocks_owned_label.pack(pady=10, padx=10, anchor="ne")

        self.info_frame_2 = ctk.CTkFrame(self.chart_frame, width=300, height=300)
        self.info_frame_2.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-10)

        self.info_label = ctk.CTkLabel(self.info_frame_2, text="Stock Information", font=("Helvetica", 20))
        self.info_label.pack(pady=10, padx=10, anchor="se")

        self.stock_value = 0
        str2 = "Stocks: ₹" + str(self.stock_value * 1000)
        self.net_worth_label = ctk.CTkLabel(self.info_frame_2, text=str2, font=("Helvetica", 16))
        self.net_worth_label.pack(pady=10, padx=10, anchor="se")

        str3 = "Current Value: ₹" + str(self.stock_value)
        self.current_stock_label = ctk.CTkLabel(self.info_frame_2, text=str3, font=("Helvetica", 16))
        self.current_stock_label.pack(pady=10, padx=10, anchor="se")

        # Create Buy and Sell buttons
        self.button_frame = ctk.CTkFrame(self)
        self.button_frame.pack(pady=10, padx=100)
        self.buy_button = ctk.CTkButton(
            self.button_frame, 
            text="Buy",
            command=lambda: self.open_buy_popup(self.balance, self.stock_value))
        self.buy_button.pack(side=ctk.LEFT, padx=100, pady=50, ipadx=20, ipady=10)
        self.sell_button = ctk.CTkButton(
            self.button_frame, 
            text="Sell", 
            command=lambda: self.open_sell_popup(self.balance, self.stock_value))
        self.sell_button.pack(side=ctk.LEFT, padx=100, pady=50, ipadx=20, ipady=10)

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
        self.net_worth_label.configure(text=f"Net Worth: ₹ {str(((self.stock_value * 100000)//1)/100)}")
        self.current_stock_label.configure(text=f"Current Value: ₹{self.stock_value}")

        # Schedule the next update
        self.after(500, self.update_chart)

    def open_buy_popup(self, balance, stock_value):
        self.open_popup("Buy", balance, stock_value)

    def open_sell_popup(self, balance, stock_value):
        self.open_popup("Sell", balance, stock_value)

    def open_popup(self, action, balance, stock_value):
        popup = ctk.CTkToplevel(self)
        popup.title(f"{action} Stocks")

        popup.geometry("300x200")
        popup.attributes("-topmost", True)
        popup.focus_force()

        label = ctk.CTkLabel(popup, text=f"Enter number of stocks to {action.lower()}:")
        label.pack(pady=10)

        entry = ctk.CTkEntry(popup)
        entry.pack(pady=5)

        confirm_button = ctk.CTkButton(popup, text="Confirm", command=lambda: self.confirm_action(action, entry.get(), popup, balance, stock_value))
        confirm_button.pack(pady=10)

    def confirm_action(self, action, num_stocks, popup, balance, stock_value):
        try:
            num_stocks = int(num_stocks)
            if action == "Buy":
                if num_stocks * stock_value <= balance:
                    balance -= num_stocks * stock_value
                    self.balance = ((balance*100)//1)/100
                    self.stocks_owned += num_stocks
                    update_user_info(self.balance, self.stocks_owned)
                    popup.destroy()
                    self.balance_label.configure(text=f"Balance: ₹ {self.balance}")
                    self.stocks_owned_label.configure(text=f"Stocks Owned: {self.stocks_owned}")
                    messagebox.showinfo("Success", f"Successfully bought {num_stocks} stocks.")
                else:
                    messagebox.showerror("Insufficient Balance", "You do not have enough balance to complete this transaction.")
            elif action == "Sell":
                if num_stocks <= self.stocks_owned:
                    balance += num_stocks * stock_value
                    self.balance = ((balance*100)//1)/100
                    self.stocks_owned -= num_stocks
                    update_user_info(self.balance, self.stocks_owned)
                    popup.destroy()
                    self.balance_label.configure(text=f"Balance: ₹ {self.balance}")
                    self.stocks_owned_label.configure(text=f"Stocks Owned: {self.stocks_owned}")
                    messagebox.showinfo("Success", f"Successfully sold {num_stocks} stocks.")
                else:
                    messagebox.showerror("Insufficient Stocks", "You do not have enough stocks to complete this transaction.")
            else:
                messagebox.showerror("Problem Detected", "Program Bugged")
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid number of stocks.")


if __name__ == "__main__":
    app = TradeSimulatorApp()
    app.mainloop()