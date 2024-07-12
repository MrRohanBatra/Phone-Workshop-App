import tkinter as tk
from tkinter import messagebox
from tkinter import font as tkfont
from tkinter import ttk
import sqlite3
from datetime import datetime

def create_database():
    conn = sqlite3.connect('orders.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS orders (
                 id INTEGER PRIMARY KEY,
                 part_name TEXT,
                 supplier_name TEXT,
                 price REAL,
                 status TEXT,
                 date TEXT)''')
    conn.commit()
    conn.close()

create_database()

def add_order(part_name, supplier_name, price, status):
    conn = sqlite3.connect('orders.db')
    c = conn.cursor()
    order_date = datetime.now().strftime("%Y-%m-%d")
    c.execute("INSERT INTO orders (part_name, supplier_name, price, status, date) VALUES (?, ?, ?, ?, ?)",
              (part_name, supplier_name, float(price), status, order_date))
    conn.commit()
    conn.close()

def display_orders(filter_query=None):
    conn = sqlite3.connect('orders.db')
    c = conn.cursor()
    if filter_query:
        c.execute(filter_query)
    else:
        c.execute("SELECT * FROM orders")
    rows = c.fetchall()
    conn.close()

    display_window = tk.Toplevel()
    display_window.title("Display Orders")

    style = ttk.Style()
    style.configure("Treeview", font=("Helvetica", 14))
    style.configure("Treeview.Heading", font=("Helvetica", 16, "bold"))

    tree = ttk.Treeview(display_window, columns=("ID", "Part Name", "Supplier Name", "Price", "Status", "Date"), show='headings')
    tree.heading("ID", text="ID")
    tree.heading("Part Name", text="Part Name")
    tree.heading("Supplier Name", text="Supplier Name")
    tree.heading("Price", text="Price")
    tree.heading("Status", text="Status")
    tree.heading("Date", text="Date")

    for row in rows:
        tree.insert("", tk.END, values=row)

    tree.pack(fill=tk.BOTH, expand=True)

    scrollbar = ttk.Scrollbar(display_window, orient=tk.VERTICAL, command=tree.yview)
    tree.configure(yscroll=scrollbar.set)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

def submit():
    part_name = entry_part_name.get()
    supplier_name = entry_supplier_name.get()
    price = entry_price.get()
    status = entry_status.get()
    if part_name and supplier_name and price and status:
        add_order(part_name, supplier_name, float(price), status)
        messagebox.showinfo("Success", "Order added successfully!")
    else:
        messagebox.showwarning("Input Error", "Please fill all fields")

def filter_by_status():
    status_input = entry_filter_status.get().lower()
    today = datetime.now().strftime("%Y-%m-%d")
    
    if status_input == 'u' or status_input == 'used':
        filter_query = f"SELECT * FROM orders WHERE status='used' AND date='{today}'"
    elif status_input == 'f' or status_input == 'faulty':
        filter_query = f"SELECT * FROM orders WHERE status='faulty' AND date='{today}'"
    elif status_input == 'r' or status_input == 'returned':
        filter_query = f"SELECT * FROM orders WHERE status='returned' AND date='{today}'"
    else:
        messagebox.showwarning("Input Error", "Invalid status filter. Use 'u'/'used', 'f'/'faulty', 'r'/'returned'.")
        return
    
    display_orders(filter_query)

def filter_by_supplier():
    supplier = entry_filter_supplier.get()
    today = datetime.now().strftime("%Y-%m-%d")
    filter_query = f"SELECT * FROM orders WHERE supplier_name='{supplier}' AND date='{today}'"
    display_orders(filter_query)

def filter_by_date():
    date = entry_filter_date.get()
    filter_query = f"SELECT * FROM orders WHERE date='{date}'"
    display_orders(filter_query)

def display_summary():
    conn = sqlite3.connect('orders.db')
    c = conn.cursor()
    c.execute("SELECT supplier_name, status, SUM(price) FROM orders GROUP BY supplier_name, status")
    rows = c.fetchall()
    conn.close()

    summary_window = tk.Toplevel()
    summary_window.title("Summary")

    text = tk.Text(summary_window, font=("Helvetica", 14))
    text.pack(fill=tk.BOTH, expand=True)

    supplier_totals = {}
    for row in rows:
        supplier, status, total_price = row
        if supplier not in supplier_totals:
            supplier_totals[supplier] = {'used': 0, 'faulty': 0, 'returned': 0}
        supplier_totals[supplier][status] = total_price

    for supplier, totals in supplier_totals.items():
        text.insert(tk.END, f"Supplier: {supplier}\n")
        text.insert(tk.END, f"  Total Parts Price: {sum(totals.values()):.2f}\n")
        text.insert(tk.END, f"  Used Parts Price: {totals['used']:.2f}\n")
        text.insert(tk.END, f"  Returned Parts Price: {totals['returned']:.2f}\n")
        text.insert(tk.END, f"  Faulty Parts Price: {totals['faulty']:.2f}\n")
        text.insert(tk.END, "\n")

app = tk.Tk()
app.title("Phone WorkShop")

default_font = tkfont.Font(family="Helvetica", size=14)
large_font = tkfont.Font(family="Helvetica", size=16)

# Section: Add Order
frame_add_order = tk.Frame(app, padx=10, pady=10)
frame_add_order.grid(row=0, column=0, columnspan=3, sticky="ew")

tk.Label(frame_add_order, text="Add Order", font=("Helvetica", 18, "bold")).grid(row=0, column=0, columnspan=2, pady=10)

tk.Label(frame_add_order, text="Part Name", font=large_font).grid(row=1, column=0, padx=10, pady=5, sticky="e")
entry_part_name = tk.Entry(frame_add_order, font=large_font)
entry_part_name.grid(row=1, column=1, padx=10, pady=5)

tk.Label(frame_add_order, text="Supplier Name", font=large_font).grid(row=2, column=0, padx=10, pady=5, sticky="e")
entry_supplier_name = tk.Entry(frame_add_order, font=large_font)
entry_supplier_name.grid(row=2, column=1, padx=10, pady=5)

tk.Label(frame_add_order, text="Price", font=large_font).grid(row=3, column=0, padx=10, pady=5, sticky="e")
entry_price = tk.Entry(frame_add_order, font=large_font)
entry_price.grid(row=3, column=1, padx=10, pady=5)

tk.Label(frame_add_order, text="Status (u/used, f/faulty, r/returned)", font=large_font).grid(row=4, column=0, padx=10, pady=5, sticky="e")
entry_status = tk.Entry(frame_add_order, font=large_font)
entry_status.grid(row=4, column=1, padx=10, pady=5)

tk.Button(frame_add_order, text="Add Order", font=large_font, command=submit).grid(row=5, column=0, columnspan=2, pady=10)

# Section: Filter Orders
frame_filter_orders = tk.Frame(app, padx=10, pady=10)
frame_filter_orders.grid(row=1, column=0, columnspan=3, sticky="ew")

tk.Label(frame_filter_orders, text="Filter Orders", font=("Helvetica", 18, "bold")).grid(row=0, column=0, columnspan=3, pady=10)

tk.Label(frame_filter_orders, text="Filter by Status", font=large_font).grid(row=1, column=0, padx=10, pady=5, sticky="e")
entry_filter_status = tk.Entry(frame_filter_orders, font=large_font)
entry_filter_status.grid(row=1, column=1, padx=10, pady=5)
tk.Button(frame_filter_orders, text="Filter", font=large_font, command=filter_by_status).grid(row=1, column=2, padx=10, pady=5)

tk.Label(frame_filter_orders, text="Filter by Supplier", font=large_font).grid(row=2, column=0, padx=10, pady=5, sticky="e")
entry_filter_supplier = tk.Entry(frame_filter_orders, font=large_font)
entry_filter_supplier.grid(row=2, column=1, padx=10, pady=5)
tk.Button(frame_filter_orders, text="Filter", font=large_font, command=filter_by_supplier).grid(row=2, column=2, padx=10, pady=5)

tk.Label(frame_filter_orders, text="Filter by Date (YYYY-MM-DD)", font=large_font).grid(row=3, column=0, padx=10, pady=5, sticky="e")
entry_filter_date = tk.Entry(frame_filter_orders, font=large_font)
entry_filter_date.grid(row=3, column=1, padx=10, pady=5)
tk.Button(frame_filter_orders, text="Filter", font=large_font, command=filter_by_date).grid(row=3, column=2, padx=10, pady=5)

# Section: Display All Orders
frame_display_orders = tk.Frame(app, padx=10, pady=10)
frame_display_orders.grid(row=2, column=0, columnspan=3, sticky="ew")

tk.Button(frame_display_orders, text="Display All Orders", font=large_font, command=lambda: display_orders()).grid(row=0, column=0, pady=10)
tk.Button(frame_display_orders, text="Display Summary", font=large_font, command=display_summary).grid(row=1, column=0, pady=10)

app.mainloop()
