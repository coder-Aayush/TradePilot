import os
import tkinter as tk
from tkinter import font, messagebox, simpledialog
import requests
import json
from dotenv import load_dotenv


load_dotenv()


API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")
BASE_URL = "https://paper-api.alpaca.markets"


def send_order(symbol, side, qty=1, order_type="market", time_in_force="gtc"):
    """
    Sends an order to the test trading API.
    """
    url = f"{BASE_URL}/v2/orders"
    headers = {
        "APCA-API-KEY-ID": API_KEY,
        "APCA-API-SECRET-KEY": API_SECRET,
        "Content-Type": "application/json",
    }
    order = {
        "symbol": symbol,
        "qty": qty,
        "side": side,
        "type": order_type,
        "time_in_force": time_in_force,
    }
    try:
        response = requests.post(url, headers=headers, data=json.dumps(order))
        if response.status_code in (200, 201):
            status_message = f"Order sent successfully: {order}"
        else:
            status_message = f"Failed to send order: {response.text}"
    except Exception as e:
        status_message = f"Error sending order: {e}"
    return status_message


def fetch_current_price(symbol):
    """
    Fetches the latest trade price for the given symbol using Alpaca's market data API (v2).
    """
    url = f"https://data.alpaca.markets/v2/stocks/{symbol}/trades/latest"
    headers = {
        "APCA-API-KEY-ID": API_KEY,
        "APCA-API-SECRET-KEY": API_SECRET,
    }
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            # Expected JSON: {"symbol": "AAPL", "trade": {"p": <price>, ...}}
            price = data.get("trade", {}).get("p", None)
            return price
        else:
            print(f"Error fetching price: {response.status_code} {response.text}")
            return None
    except Exception as e:
        print(f"Exception while fetching price: {e}")
        return None


def center_window(win, width=600, height=400):
    """
    Centers the window on the screen.
    """
    win.update_idletasks()
    screen_width = win.winfo_screenwidth()
    screen_height = win.winfo_screenheight()
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    win.geometry(f"{width}x{height}+{x}+{y}")


def key_pressed(event):
    """
    Map key presses to order functions.
    B - Buy (with confirmation and dynamic price), S - Sell, C - Close trade,
    P - Close % of trade, T - Trailing Stop.
    """
    key = event.char.lower()
    if key == "b":
        # Ask user which symbol they want to buy.
        symbol = simpledialog.askstring(
            "Input", "Enter the symbol you want to buy:", parent=root
        )
        if not symbol or symbol.strip() == "":
            messagebox.showerror("Error", "Invalid symbol.")
            return
        symbol = symbol.upper()
        # Ask user for the quantity.
        quantity = simpledialog.askinteger(
            "Input", f"Enter quantity for {symbol}:", parent=root, minvalue=1
        )
        if not quantity:
            messagebox.showerror("Error", "Invalid quantity.")
            return
        # Fetch current price dynamically.
        price = fetch_current_price(symbol)
        if price is None:
            messagebox.showerror("Error", f"Could not fetch price for {symbol}.")
            return

        info = f"{symbol}\nCurrent Price: ${price:.2f}\nQuantity: {quantity}"
        confirm = messagebox.askyesno(
            "Confirm Buy Order", f"Do you want to BUY?\n\n{info}"
        )
        if confirm:
            result = send_order(symbol, "buy", qty=quantity)
            # If order is successful, show a success dialog.
            if "Order sent successfully" in result:
                messagebox.showinfo(
                    "Success",
                    f"Buy order for {quantity} shares of {symbol} at ${price:.2f} executed successfully!",
                )
        else:
            result = "Buy order cancelled."
    elif key == "s":
        # For Sell, you could add similar dialogs if needed.
        result = send_order("AAPL", "sell", qty=1)
    elif key == "c":
        # Simulate closing a trade with a sell order.
        result = send_order("AAPL", "sell", qty=1)
    elif key == "p":
        # Simulate closing a percentage of a trade (demo: fixed order).
        result = send_order("AAPL", "sell", qty=1)
    elif key == "t":
        # Simulate a trailing stop order (basic sell order demo).
        result = send_order("AAPL", "sell", qty=1)
    else:
        result = "No action mapped to this key."

    # Update the status label with the result of the order attempt.
    status_label.config(text=result)


# Create the main Tkinter window and set its background
root = tk.Tk()
root.title("Trading Order Executor")
root.configure(bg="#f0f0f0")

# Center the window (600x400)
center_window(root, 600, 400)

# Define custom fonts
header_font = font.Font(family="Helvetica", size=20, weight="bold")
instr_font = font.Font(family="Helvetica", size=12)
status_font = font.Font(family="Helvetica", size=12, slant="italic")

# Header label
header_label = tk.Label(
    root, text="Trading Order Executor", font=header_font, bg="#f0f0f0", fg="#333"
)
header_label.pack(pady=10)

# Instruction frame
instr_frame = tk.Frame(root, bg="#f0f0f0")
instr_frame.pack(pady=10, fill="x", padx=20)

instruction_text = (
    "Press keys to execute orders:\n"
    "B: Buy (with confirmation & dynamic price)\n"
    "S: Sell\n"
    "C: Close Trade\n"
    "P: Close % of Trade\n"
    "T: Trailing Stop\n\n"
    "Press any other key for no action.\n"
    "Close the window to exit."
)
instruction_label = tk.Label(
    instr_frame,
    text=instruction_text,
    justify="left",
    font=instr_font,
    bg="#f0f0f0",
    fg="#555",
)
instruction_label.pack()

# Status frame for displaying order execution status
status_frame = tk.Frame(root, bg="#f0f0f0")
status_frame.pack(pady=20, fill="x", padx=20)

status_label = tk.Label(
    status_frame,
    text="Waiting for key press...",
    wraplength=550,
    fg="red",
    font=status_font,
    bg="#f0f0f0",
)
status_label.pack()

# Bind key press events to the key_pressed function
root.bind("<Key>", key_pressed)

# Start the Tkinter event loop
root.mainloop()
