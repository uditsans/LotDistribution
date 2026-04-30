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
        self.root.title("Purchase Invoice Management App")
        self.root.geometry("1000x800")
        self.root.resizable(True, True)

        self.columns = ['Buyer', 'Tea Invoice Date', 'Auctioneer', 'Pkgs', 'Total KGs', 'Tea Invoice No', 'Tea Taxable Value',
       'SGST on Tea Value', 'CGST on Tea Value', 'Tea Invoice Value', 'Auctioneer Invoice No',
       'Auctioneer Services Taxable  Value', 'SGST on Auctioneer Services', 'CGST on Auctioneer Services', 
       'Auctioneer Invoice Value', 'TeaBoard Invoice No', 'Teaboard charges', 'SGST on Tea Board charges', 
       'CGST on Tea Board charges', 'Tea Board Invoice Value', 'Grand Total']
        self.buyer_columns = ["Buyer Code", "Auctioneer Code", "Total Bags", "Total Weight"]

        self.constants_conn = sqlite3.connect("constants.db")
        self.constants_cursor = self.constants_conn.cursor()
        self.sale_nos = [row[0] for row in self.constants_cursor.execute("SELECT sale_number FROM sales").fetchall()]
        self.constants_conn.close()

        self.create_widgets()
        self.update_db_selection()
        self.refresh_invoices_list()
        self.refresh_buyers_list()

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def update_db_selection(self, event=None):
        """
        Updates the database connection based on the selected sale number and refreshes the invoices list.
        """
        sale_no = self.sale_no_entry.get()
        if not sale_no:
            return
        db_path = os.path.join(os.getcwd(), "dbs", f"{sale_no}.db")
        try:
            self.conn = sqlite3.connect(db_path)
            self.cursor = self.conn.cursor()
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS invoices (
                    buyer TEXT,
                    t_inv_date TEXT NOT NULL,
                    auctioneer TEXT NOT NULL,
                    pkgs INT NOT NULL,
                    total_kgs REAL NOT NULL,
                    t_inv_no TEXT PRIMARY KEY,
                    t_value REAL NOT NULL,
                    t_sgst REAL NOT NULL,
                    t_cgst REAL NOT NULL,
                    t_inv_value REAL NOT NULL,
                    a_inv_no TEXT,
                    a_value REAL,
                    a_sgst REAL,
                    a_cgst REAL,
                    a_inv_value REAL,
                    tb_inv_no TEXT,
                    tb_value REAL,
                    tb_sgst REAL,
                    tb_cgst REAL,
                    tb_inv_value REAL,
                    grand_total REAL
                )
            """)
            self.conn.commit()
            self.refresh_invoices_list()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error connecting to database: {e}")

    def create_widgets(self):
        """
        Creates and arranges the GUI widgets for the invoices management application.
        """
        upload_frame = tk.Frame(self.root)
        upload_frame.pack(fill='both', expand=True)

        invoices_frame = tk.Frame(upload_frame)
        invoices_frame.pack(pady=10, fill=tk.X)

        invoices_label = tk.Label(invoices_frame, text="Invoice Registry:", font=("Arial", 12, "bold"))
        invoices_label.pack(side=tk.LEFT, padx=5)

        ttk.Label(invoices_frame, text="Sale No:").pack(side=tk.LEFT, padx=5)
        self.sale_no_entry = ttk.Combobox(invoices_frame, state="readonly", width=12)
        self.sale_no_entry['values'] = self.sale_nos
        if self.sale_nos:
            self.sale_no_entry.current(len(self.sale_nos) - 1)
        self.sale_no_entry.pack(side=tk.LEFT, padx=5)
        self.sale_no_entry.bind("<<ComboboxSelected>>", self.update_db_selection)

        tk.Label(invoices_frame, text="Buyer Code:").pack(side=tk.LEFT, padx=5)
        self.buyer_info = ttk.Combobox(invoices_frame, state="readonly", width=12)
        self.buyer_info['values'] = ["J039", "K057", "T082"]
        self.buyer_info.current(1)
        self.buyer_info.pack(side=tk.LEFT, padx=5)   

        button_add = tk.Button(invoices_frame, text="Add Info (from file)", command=self.add_file)
        button_add.pack(side=tk.LEFT, padx=5)

        button_add_man = tk.Button(invoices_frame, text="Add Info (manual)", command=self.add_manual)
        button_add_man.pack(side=tk.LEFT, padx=5)

        button_delete = tk.Button(invoices_frame, text="Delete Items", command=self.delete_selected)
        button_delete.pack(side=tk.LEFT, padx=5)
        
        frame_invoices = tk.LabelFrame(upload_frame, text="Invoice Data")
        frame_invoices.pack(fill='both', expand=True)
        self.frame_invoices = frame_invoices

        self.tree_invoices = ttk.Treeview(frame_invoices, columns= self.columns, show="headings")
        for col in self.columns:
            self.tree_invoices.heading(col, text=col)
            self.tree_invoices.column(col, anchor=tk.CENTER, width=75)
        self.tree_invoices.pack(fill='both', expand=True)
        self.tree_invoices_scroll = ttk.Scrollbar(frame_invoices, orient ="horizontal",
                                command = self.tree_invoices.xview)
        self.tree_invoices_scroll.pack(side ='bottom', fill ='y')
        self.tree_invoices_scroll.place(y=500, x=0, width=1000)
        self.tree_invoices.configure(yscrollcommand=self.tree_invoices_scroll.set)

        frame_buyers = tk.LabelFrame(upload_frame, text="Sale Buyers Data")
        frame_buyers.pack(fill='both', expand=True)
        self.frame_buyers = frame_buyers

        self.tree_buyers = ttk.Treeview(frame_buyers, columns= self.buyer_columns, show="headings")
        for col in self.buyer_columns:
            self.tree_buyers.heading(col, text=col)
            self.tree_buyers.column(col, anchor=tk.CENTER, width=100)
        self.tree_buyers.pack(fill='both', expand=True)


    def refresh_invoices_list(self):
        """
        Refreshes the list of invoices displayed in the treeview.
        """
        for item in self.tree_invoices.get_children():
            self.tree_invoices.delete(item)
        
        try:
            self.cursor.execute("SELECT * FROM invoices")
            invoices = self.cursor.fetchall()
            for invoice in invoices:
                self.tree_invoices.insert("", "end", values=invoice)

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error fetching invoices: {e}")

    def refresh_buyers_list(self):
        """
        Refreshes the list of invoices displayed in the treeview.
        """
        for item in self.tree_buyers.get_children():
            self.tree_buyers.delete(item)
        
        try:
            bought = pd.DataFrame(self.cursor.execute("SELECT BuyerCode, LotNo, BoughtQty, TotalWt FROM purchases").fetchall(), 
                                  columns=["BuyerCode", "Auc", "Pkg", "Wt"])
            bought["Auc"] = bought["Auc"].apply(lambda x: x[:2])
            bought_agg = bought.groupby(by=["BuyerCode", "Auc"]).sum().reset_index()
            # bought_agg["Ref_in"] = bought_agg.apply(lambda x: x.BuyerCode+"/"+x.Auc)

            for buyer_agg in bought_agg:
                self.tree_invoices.insert("", "end", values=buyer_agg)

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error fetching purchase info: {e}")
                    

    def add_file(self):
        """
        Opens a file dialog to select an Excel file, reads the data, and adds it to the database.
        """
        buyer = self.buyer_info.get()
        filepath = filedialog.askopenfilename(filetypes=[("Excel Files", "*.xls")])
        if filepath and buyer:
            try:
                temp_df = pd.read_table(filepath)
                select_col = ['Buyer', 'Tea Invoice Date', 'Auctioneer', 'Pkgs', 'Total KGs', 'Tea Invoice No', 'Tea Taxable Value',
       'SGST on Tea Value', 'CGST on Tea Value', 'Tea Invoice value', 'Auctioneer Invoice No', 'Auctioneer Services Taxable  Value', 
       'SGST on Auctioneer Services', 'CGST on Auctioneer Services', 'Auctioneer Invoice value', 'TeaBoard Invoice No',
       'Teaboard Charges', 'SGST on Tea Board charges', 'CGST on Tea Board charges', 'Tea Board Invoice value', 'Grand Total']
                try:
                    assert str(temp_df["Sale No"].unique()[0])==self.sale_no_entry.get()

                    temp_df["Buyer"]=buyer
                    temp_df = temp_df[select_col]
                    temp_df.columns = self.columns

                    exit

                    for index, row in temp_df.iterrows():
                        try:
                            # Check if the t_inv_no already exists
                            self.cursor.execute(f"SELECT t_inv_no FROM invoices WHERE t_inv_no='{list(row)[4]}'")
                            existing_record = self.cursor.fetchone()
                            if existing_record:
                                # t_inv_no exists, no need to insert again, old data persists
                                continue
                            else:
                                # t_inv_no doesn't exist, insert the new record
                                self.cursor.execute("""
                                    INSERT INTO invoices (buyer, t_inv_date, auctioneer, pkgs, total_kgs, t_inv_no, t_value, t_sgst, t_cgst, t_inv_value, a_inv_no, a_value, a_sgst, a_cgst, a_inv_value, 
                                                    tb_inv_no, tb_value, tb_sgst, tb_cgst, tb_inv_value, grand_total)
                                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                                """, tuple(list(row)))
                        except sqlite3.Error as e:
                            messagebox.showerror("Database Error", f"Error inserting record for t_inv_no {row['Tea Invoice No']}: {e}")
                            continue  # Skip the rest of the loop for this row.

                    self.conn.commit()
                    self.refresh_invoices_list()
                    messagebox.showinfo("Success", f"File '{filepath}' processed successfully. Existing data persisted.")
                except KeyError as e:
                    messagebox.showerror("Error", f"Required column '{e.args[0]}' not found in the uploaded file.")
                except AssertionError as e:
                    messagebox.showerror("Error", f"Incorrect Sale Number.")
                except Exception as e:
                    messagebox.showerror("Error", f"An unexpected error occurred while processing the file: {e}")
            except Exception as e:
                messagebox.showerror("Error", f"Error reading file '{filepath}': {e}")

    def delete_selected(self):
        """
        Deletes the selected purchase items from the database.
        """
        selected_items = self.tree_invoices.selection()
        if selected_items:
            for item in selected_items:
                values = self.tree_invoices.item(item, 'values')
                self.cursor.execute(f"DELETE FROM invoices WHERE t_inv_no='{list(values)[5]}'")
            self.conn.commit()
            self.refresh_invoices_list()
        else:
            messagebox.showinfo("Info", "No rows selected.")

    def modify_selected(self):
        """
        Opens a dialog to modify the details of the selected purchase item.
        """
        selected_items = self.tree_invoices.selection()
        if not selected_items:
            messagebox.showinfo("Info", "No rows selected.")
            return
        
        item = selected_items[0]
        values = self.tree_invoices.item(item, 'values')
        
        columns = self.columns

        modify_dialog = tk.Toplevel(self.root)
        modify_dialog.title("Modify Record")

        entries = {}
        for i, col in enumerate(columns):
            tk.Label(modify_dialog, text=col).grid(row=i, column=0, sticky=tk.W)
            entry = tk.Entry(modify_dialog)
            entry.insert(tk.END, values[i])
            if i>0 and i<6:
                entry.config(state='readonly')
            entry.grid(row=i, column=1, padx=5, pady=2)
            entries[col] = entry

        def save_changes():
            """Saves the modified values to the database."""
            new_values = [entry.get() for entry in entries.values()]
            try:
                # Update both BoughtQty and Qty for simplicity in this context
                self.cursor.execute("""
                    UPDATE invoices SET buyer=?, t_inv_date=?, auctioneer=?, pkgs=?, total_kgs=?, t_inv_no=?, t_value=?, 
                                    t_sgst=?, t_cgst=?, t_inv_value=?, a_inv_no=?, a_value=?, a_sgst=?, a_cgst=?, 
                                    a_inv_value=?, tb_inv_no=?, tb_value=?, tb_sgst=?, tb_cgst=?, tb_inv_value=?, grand_total=?
                    WHERE t_inv_no=?
                """, tuple(new_values + list(values[5])))
                self.conn.commit()
                self.refresh_invoices_list()
                modify_dialog.destroy()
            except sqlite3.Error as e:
                messagebox.showerror("Database Error", f"Error updating record: {e}")

        save_button = tk.Button(modify_dialog, text="Save Changes", command=save_changes)
        save_button.grid(row=len(columns), column=0, columnspan=2, pady=10)

    def add_manual(self):
        """
        Opens a dialog to manually add details of an invoice.
        """

        columns = self.columns

        modify_dialog = tk.Toplevel(self.root)
        modify_dialog.title("Add Record")

        entries = {}
        for i, col in enumerate(columns):
            tk.Label(modify_dialog, text=col).grid(row=i, column=0, sticky=tk.W)
            entry = tk.Entry(modify_dialog)
            entry.insert(tk.END, [0])
            entry.grid(row=i, column=1, padx=5, pady=2)
            entries[col] = entry

        def save_changes():
            """Saves the modified values to the database."""
            new_values = [entry.get() for entry in entries.values()]
            try:
                # Update both BoughtQty and Qty for simplicity in this context
                self.cursor.execute("""
                    INSERT INTO invoices (buyer, t_inv_date, auctioneer, pkgs, total_kgs, 
                                                    t_inv_no, t_value, t_sgst, t_cgst, t_inv_value, 
                                                    a_inv_no, a_value, a_sgst, a_cgst, a_inv_value, 
                                                    tb_inv_no, tb_value, tb_sgst, tb_cgst, tb_inv_value, grand_total)
                                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", tuple(new_values))
                self.conn.commit()
                self.refresh_invoices_list()
                modify_dialog.destroy()
            except sqlite3.Error as e:
                messagebox.showerror("Database Error", f"Error updating record: {e}")

        save_button = tk.Button(modify_dialog, text="Save Changes", command=save_changes)
        save_button.grid(row=len(columns), column=0, columnspan=2, pady=10)

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