"""
SalesApp: A Tkinter application for managing sales information.

This module provides a GUI for entering, displaying, and deleting sales data.
It uses an SQLite database to store sales information and the tkcalendar
library for date selection.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import os
from datetime import date, timedelta
from tkcalendar import DateEntry

class SaleInfoApp:
    def __init__(self, root):
        """
        Initializes the SalesApp with the given root window.
        """
        self.root = root
        self.root.title("Sales Management")

        self.conn = sqlite3.connect("constants.db")
        self.cursor = self.conn.cursor()

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS sales (
                sale_number INTEGER PRIMARY KEY,
                sale_date TEXT NOT NULL,
                prompt_date TEXT NOT NULL
            )
        """)
        self.conn.commit()

        self.create_sales_widgets()
        self.refresh_sales_list()

    def create_new_sale_db(self):
        """
        Creates a new SQLite database for the sale.
        """
        try:
            db_path = os.path.join(os.getcwd(), "dbs", f"{self.sale_no_entry.get()}.db")
            sqliteConnection = sqlite3.connect(db_path)
            messagebox.showinfo("Success", "Sale database created successfully.")
        except sqlite3.Error as error:
            messagebox.showerror("Error", f"Failed to create Sale database: {error}")
        finally:
            if sqliteConnection:
                sqliteConnection.close()

    def create_sales_widgets(self):
        """
        Creates and arranges the GUI widgets for sales information.
        """
        sale_frame = ttk.LabelFrame(self.root, text="Sale Information")
        sale_frame.grid(row=0, column=0, padx=10, pady=10, sticky="we")

        ttk.Label(sale_frame, text="Sale No:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.sale_no_entry = ttk.Combobox(sale_frame, state="readonly", width=12)
        self.sale_no_entry['values'] = [str(i) for i in range(1, 53)]
        self.sale_no_entry.current((date.today().isocalendar().week) - 1)
        self.sale_no_entry.grid(row=0, column=1, padx=5, pady=2)

        ttk.Label(sale_frame, text="Sale Date:").grid(row=1, column=0, padx=5, pady=2, sticky="w")
        self.sale_date_entry = DateEntry(sale_frame, width=12, background='darkblue', foreground='white', borderwidth=2, date_pattern='dd-mm-yy')
        self.sale_date_entry.grid(row=1, column=1, padx=5, pady=2)
        self.sale_date_entry.bind("<<DateEntrySelected>>", self.update_prompt_date)

        ttk.Label(sale_frame, text="Prompt Date:").grid(row=2, column=0, padx=5, pady=2, sticky="w")
        self.prompt_date_entry = DateEntry(sale_frame, width=12, background='darkblue', foreground='white', borderwidth=2, date_pattern='dd-mm-yy')
        self.prompt_date_entry.grid(row=2, column=1, padx=5, pady=2)
        self.update_prompt_date()

        ttk.Button(sale_frame, text="Add Sale", command=self.add_sale_no).grid(row=3, column=0, pady=5)
        ttk.Button(sale_frame, text="Delete Sale", command=self.delete_sale_no).grid(row=3, column=1, pady=5)

        self.sales_tree = ttk.Treeview(sale_frame, columns=("Sale No", "Sale Date", "Prompt Date"), show="headings")
        self.sales_tree.heading("Sale No", text="Sale No")
        self.sales_tree.heading("Sale Date", text="Sale Date")
        self.sales_tree.heading("Prompt Date", text="Prompt Date")
        self.sales_tree.grid(row=0, rowspan=4, column=3, padx=10, pady=2, sticky="we")

    def refresh_sales_list(self):
        """
        Refreshes the sales list in the treeview.
        """
        for item in self.sales_tree.get_children():
            self.sales_tree.delete(item)

        self.cursor.execute("SELECT * FROM sales")
        sales = self.cursor.fetchall()

        for sale in sales:
            self.sales_tree.insert("", "end", values=sale)

    def add_sale_no(self):
        """
        Adds a new sale to the database and refreshes the sales list.
        """
        sale_number = self.sale_no_entry.get()
        sale_date = self.sale_date_entry.get_date()
        prompt_date = self.prompt_date_entry.get_date()

        if not sale_number or not sale_date or not prompt_date:
            messagebox.showerror("Error", "All fields are required.")
            return

        try:
            sale_date_str = sale_date.strftime('%d-%m-%y')
            prompt_date_str = prompt_date.strftime('%d-%m-%y')
            self.create_new_sale_db()
            self.cursor.execute("INSERT INTO sales (sale_number, sale_date, prompt_date) VALUES (?, ?, ?)",
                                (sale_number, sale_date_str, prompt_date_str))
            self.conn.commit()
            self.refresh_sales_list()

        except ValueError:
            messagebox.showerror("Error", "Invalid date format. Please use DD-MM-YY.")
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Database error: {e}")

    def delete_sale_no(self):
        """
        Deletes the selected sale from the database and refreshes the sales list.
        """
        selected_item = self.sales_tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Select a sale to delete.")
            return

        item = self.sales_tree.item(selected_item)
        sale_number = item["values"][0]

        if messagebox.askyesno("Confirm", "Are you sure you want to delete this sale?"):
            try:
                self.cursor.execute("DELETE FROM sales WHERE sale_number=?", (sale_number,))
                self.conn.commit()
                messagebox.showinfo("Success", "Sale deleted successfully.")
                self.refresh_sales_list()
            except sqlite3.Error as e:
                messagebox.showerror("Error", f"Database error: {e}")

    def update_prompt_date(self, event=None):
        """
        Updates the prompt date based on the selected sale date.
        """
        sale_date = self.sale_date_entry.get_date()
        prompt_date = sale_date + timedelta(days=13)
        self.prompt_date_entry.set_date(prompt_date)

if __name__ == "__main__":
    root = tk.Tk()
    app = SaleInfoApp(root)
    root.mainloop()