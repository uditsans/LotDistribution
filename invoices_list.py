"""
PurchaseApp: A Tkinter application for managing purchase data.

This module provides a GUI to upload purchase data from Excel files,
display the data, delete selected items, and modify existing entries
in a local SQLite database.
"""

import sqlite3
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
# from read_files import read_xml
import pandas as pd
from datetime import date

class InvoiceApp:
    """
    A Tkinter application for managing purchase invoice data.
    """

    def __init__(self, root):
        """
        Initializes the InvoiceApp with the given root window.
        """
        self.root = root
        self.root.title("Invoice Management App")
        self.root.geometry("1000x800")
        self.root.resizable(True, True)
        self.columns = ['Buyer', 'Tea Invoice Date', 'Auctioneer', 'Pkgs', 'Total KGs', 'Tea Invoice No', 'Tea Taxable Value',
       'SGST on Tea Value', 'CGST on Tea Value', 'Tea Invoice Value', 'Auctioneer Invoice No',
       'Auctioneer Services Taxable  Value', 'SGST on Auctioneer Services', 'CGST on Auctioneer Services', 
       'Auctioneer Invoice Value', 'TeaBoard Invoice No', 'Teaboard charges', 'SGST on Tea Board charges', 
       'CGST on Tea Board charges', 'Tea Board Invoice Value', 'Grand Total']
        
        self.invoices = pd.DataFrame([], columns=self.columns)
        self.get_invoices()
        
        self.create_widgets()
        self.refresh_invoices_list()


        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def get_invoices(self, event=None):
        """
        Updates the database connection based on the selected sale number and refreshes the invoices list.
        """
        dbs_path = os.path.join(os.getcwd(), "dbs")

        for item in os.listdir(dbs_path):
            db_path = os.path.join(dbs_path, item)
            try:
                self.conn = sqlite3.connect(db_path)
                self.cursor = self.conn.cursor()
                self.cursor.execute("SELECT * FROM invoices")
                self.invoices = pd.concat([self.invoices, 
                                           pd.DataFrame(self.cursor.fetchall(), columns=self.columns)])
                self.conn.close()
            except sqlite3.Error as e:
                continue
            #     messagebox.showerror("Database Error", f"Error connecting to database {db_path}: {e}")

    def create_widgets(self):
        """
        Creates and arranges the GUI widgets for the invoices management application.
        """
        upload_frame = tk.Frame(self.root)
        upload_frame.pack(fill='both', expand=True)

        buyer_frame = tk.Frame(upload_frame)
        buyer_frame.pack(pady=10, fill=tk.X)

        buyer_label = tk.Label(buyer_frame, text="Invoices Registry:", font=("Arial", 12, "bold"))
        buyer_label.pack(side=tk.LEFT, padx=5)

        ttk.Label(buyer_frame, text="Start Date:").pack(side=tk.LEFT, padx=5)
        self.start_entry = ttk.Combobox(buyer_frame, state="readonly", width=12)
        self.start_entry['values'] = ['1', '2']
        self.start_entry.pack(side=tk.LEFT, padx=5)

        tk.Label(buyer_frame, text="End Date:").pack(side=tk.LEFT, padx=5)


        # button_add = tk.Button(buyer_frame, text="Show Selected", command=self.show_selected)
        # button_add.pack(side=tk.LEFT, padx=5)

        button_add_man = tk.Button(buyer_frame, text="Reset", command=self.refresh_invoices_list)
        button_add_man.pack(side=tk.LEFT, padx=5)

        frame_buyer = tk.LabelFrame(upload_frame, text="Invoice Data")
        frame_buyer.pack(fill='both', expand=True)
        self.frame_buyer = frame_buyer

        self.tree_buyer = ttk.Treeview(frame_buyer, columns= self.columns, show="headings")
        for col in self.columns:
            self.tree_buyer.heading(col, text=col)
            self.tree_buyer.column(col, anchor=tk.CENTER, width=75)
        self.tree_buyer.pack(fill='both', expand=True)
        self.tree_buyer_scroll = ttk.Scrollbar(frame_buyer, orient ="horizontal",
                                command = self.tree_buyer.xview)
        self.tree_buyer_scroll.pack(side ='bottom', fill ='y')
        self.tree_buyer_scroll.place(y=500, x=0, width=1000)
        self.tree_buyer.configure(yscrollcommand=self.tree_buyer_scroll.set)

    def refresh_invoices_list(self):
        """
        Refreshes the list of invoices displayed in the treeview.
        """
        for item in self.tree_buyer.get_children():
            self.tree_buyer.delete(item)
        
        try:
            invoices = self.invoices
            print(invoices)
            for i in range(len(invoices)):
                self.tree_buyer.insert("", "end", values=list(invoices.iloc[i]))

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error fetching invoices: {e}")
 
    def on_closing(self):
        """
        Closes the database connection and destroys the root window.
        """
        if hasattr(self, 'conn') and self.conn:
            self.conn.close()
        if hasattr(self, 'constants_conn') and self.constants_conn:
            self.constants_conn.close()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = InvoiceApp(root)
    root.mainloop()