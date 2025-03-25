"""
DistributionApp: A Tkinter application for managing the distribution of purchased items to parties.

This module provides a GUI to select purchased items, specify the quantity to
distribute to a selected party, and record these distributions as sales. It also
allows for deleting sales records and reverting the quantity back to the purchase
inventory.
"""

import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
import os

class DistributionApp:
    def __init__(self, root):
        """
        Initializes the DistributionApp with the given root window.
        """
        self.root = root
        self.root.title("Distribution App")
        self.root.geometry("1200x800")
        self.root.resizable(True, True)

        self.constants_conn = sqlite3.connect("constants.db")
        self.constants_cursor = self.constants_conn.cursor()
        self.sale_nos = [row[0] for row in self.constants_cursor.execute("SELECT sale_number FROM sales").fetchall()]
        self.party = [row[0] for row in self.constants_cursor.execute("SELECT code FROM party").fetchall()]
        self.constants_conn.close()

        self.columns = ["LotNo", "InvNo", "Mark", "Grade", "Qty", "PkgWt", "PriceKg"]

        self.create_widgets()
        self.update_db_selection()
        self.refresh_purchases_list()
        self.refresh_qty_list()
        self.refresh_sales_list()

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def update_db_selection(self, event=None):
        """
        Updates the database connection and refreshes the lists based on the selected sale number.
        """
        sale_no = self.sale_no_entry.get()
        if not sale_no:
            return
        db_path = os.path.join(os.getcwd(), "dbs", f"{sale_no}.db")
        try:
            self.conn = sqlite3.connect(db_path)
            self.cursor = self.conn.cursor()
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS sales (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    LotNo TEXT,
                    InvNo TEXT,
                    Mark TEXT,
                    Grade TEXT,
                    Qty INTEGER,
                    PkgWt REAL,
                    PriceKg REAL,
                    Party TEXT
                )
            """)
            self.conn.commit()
            self.refresh_purchases_list()
            self.refresh_qty_list()
            self.refresh_sales_list()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error connecting to database: {e}")

    def create_widgets(self):
        """
        Creates and arranges the GUI widgets for the distribution application.
        """
        # Purchase Section
        purchase_frame = tk.LabelFrame(self.root, text="Purchase Data (From Purchase App)")
        purchase_frame.pack(pady=10, padx=10, fill='both', expand=True)

        ttk.Label(purchase_frame, text="Sale No:").pack(side=tk.LEFT, padx=5)
        self.sale_no_entry = ttk.Combobox(purchase_frame, state="readonly", width=12)
        self.sale_no_entry['values'] = self.sale_nos
        if self.sale_nos:
            self.sale_no_entry.current(len(self.sale_nos) - 1)
        self.sale_no_entry.pack(side=tk.LEFT, padx=5)
        self.sale_no_entry.bind("<<ComboboxSelected>>", self.update_db_selection)

        self.tree_purchases = ttk.Treeview(purchase_frame,
                                            columns=self.columns,
                                            show="headings")
        for col in self.columns:
            self.tree_purchases.heading(col, text=col)
            self.tree_purchases.column(col, width=int(1200/7))
        self.tree_purchases.pack(fill='both', expand=True)
        self.tree_purchases.bind("<<TreeviewSelect>>", self.show_lot_info)

        # Distribution Controls and Lot Info
        dist_info_frame = tk.Frame(self.root)
        dist_info_frame.pack(pady=5, padx=10, fill='x')

        self.lot_info = tk.Frame(dist_info_frame)
        self.lot_info.pack(side=tk.LEFT, fill=tk.BOTH)

        self.lot_info_labels = []
        for label_text in ["Lot No", "Mark", "Grade", "Remaining Qty", "Price/Kg"]:
            tk.Label(self.lot_info, text=f"{label_text}:").pack(side=tk.LEFT)
            entry = ttk.Entry(self.lot_info, width=15, state='readonly')
            entry.pack(side=tk.LEFT)
            self.lot_info_labels.append(entry)

        dist_controls_frame = tk.Frame(dist_info_frame)
        dist_controls_frame.pack(side=tk.LEFT, fill=tk.BOTH, padx=10)

        tk.Label(dist_controls_frame, text="Quantity:").pack(side=tk.LEFT)
        self.qty_combobox = ttk.Combobox(dist_controls_frame, values=[0], width=10)
        self.qty_combobox.pack(side=tk.LEFT, padx=5)

        tk.Label(dist_controls_frame, text="Party:").pack(side=tk.LEFT)
        self.party_combobox = ttk.Combobox(dist_controls_frame, values=self.party, width=15)
        self.party_combobox.pack(side=tk.LEFT, padx=5)

        button_distribute = tk.Button(dist_controls_frame, text="Distribute",
                                        command=self.distribute_items)
        button_distribute.pack(side=tk.LEFT)

        # Sales Section
        sales_frame = tk.LabelFrame(self.root, text="Sales Data")
        sales_frame.pack(pady=10, padx=10, fill='both', expand=True)

        self.tree_sales = ttk.Treeview(sales_frame, columns=self.columns + ["Party"], show="headings")
        for col in self.columns + ["Party"]:
            self.tree_sales.heading(col, text=col)
            self.tree_sales.column(col, width=int(1200/8))
        self.tree_sales.pack(fill='both', expand=True)

        delete_revert_frame = tk.Frame(self.root)
        delete_revert_frame.pack(pady=5, padx=10, fill='x')

        button_delete_revert = tk.Button(delete_revert_frame, text="Delete Sales & Revert Purchase", command=self.delete_sales_revert_purchase)
        button_delete_revert.pack(side=tk.LEFT)

    def refresh_purchases_list(self):
        """
        Refreshes the list of available purchases in the treeview.
        """
        for item in self.tree_purchases.get_children():
            self.tree_purchases.delete(item)

        try:
            self.cursor.execute("SELECT LotNo, InvNo, Mark, Grade, Qty, PkgWt, PriceKg FROM purchases WHERE Qty>0")
            purchases = self.cursor.fetchall()
            for purchase in purchases:
                self.tree_purchases.insert("", "end", values=purchase)
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error fetching purchases: {e}")

    def refresh_sales_list(self):
        """
        Refreshes the list of distributed sales in the treeview.
        """
        for item in self.tree_sales.get_children():
            self.tree_sales.delete(item)

        try:
            self.cursor.execute("SELECT LotNo, InvNo, Mark, Grade, Qty, PkgWt, PriceKg, Party FROM sales")
            sales = self.cursor.fetchall()
            for sale in sales:
                self.tree_sales.insert("", "end", values=sale)
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error fetching sales: {e}")

    def refresh_qty_list(self):
        """
        Resets the lot information entries and the quantity combobox.
        """
        for entry in self.lot_info_labels:
            entry.config(state='normal')
            entry.delete(0, tk.END)
            entry.insert(0, '-')
            entry.config(state='readonly')
        if self.party:
            self.party_combobox.current(0)
        self.qty_combobox['values'] = [0]
        self.qty_combobox.current(0)

    def show_lot_info(self, event):
        """
        Displays information of the selected lot from the purchases treeview.
        """
        selected_items = self.tree_purchases.selection()
        if selected_items:
            item = selected_items[0]
            values = self.tree_purchases.item(item, 'values')
            lot_info_values = [values[i] for i in [0, 2, 3, 4, 6]]  # LotNo, Mark, Grade, Qty, PriceKg
            for i, value in enumerate(lot_info_values):
                self.lot_info_labels[i].config(state='normal')
                self.lot_info_labels[i].delete(0, tk.END)
                self.lot_info_labels[i].insert(0, value)
                self.lot_info_labels[i].config(state='readonly')
            available_qty = int(values[4])
            self.qty_combobox['values'] = [i for i in range(1, available_qty + 1)]
            self.qty_combobox.current(available_qty - 1)
        else:
            self.refresh_qty_list()

    def distribute_items(self):
        """
        Distributes the selected quantity of an item to the chosen party.
        """
        selected_items = self.tree_purchases.selection()
        if not selected_items:
            messagebox.showinfo("Info", "Select a purchase item to distribute.")
            return

        item = selected_items[0]
        values = self.tree_purchases.item(item, 'values')
        LotNo, InvNo, Mark, Grade, PkgWt, PriceKg = values[0], values[1], values[2], values[3], values[5], values[6]
        try:
            qty = int(self.qty_combobox.get())
            party = self.party_combobox.get()
        except ValueError:
            messagebox.showerror("Error", "Invalid quantity.")
            return

        if not party:
            messagebox.showerror("Error", "Please select a party.")
            return

        try:
            self.cursor.execute("SELECT Qty FROM purchases WHERE LotNo=? AND InvNo=? AND Mark=? AND Grade=? AND PkgWt=? AND PriceKg=?",
                                (LotNo, InvNo, Mark, Grade, PkgWt, PriceKg))
            purchase_record = self.cursor.fetchone()
            if purchase_record:
                remaining_qty = purchase_record[0]
                if qty > remaining_qty:
                    messagebox.showerror("Error", "Quantity exceeds available stock.")
                    return

                self.cursor.execute("""
                    INSERT INTO sales (LotNo, InvNo, Mark, Grade, Qty, PkgWt, PriceKg, Party)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (LotNo, InvNo, Mark, Grade, qty, PkgWt, PriceKg, party))

                new_qty = remaining_qty - qty
                self.cursor.execute("UPDATE purchases SET Qty = ? WHERE LotNo=? AND InvNo=? AND Mark=? AND Grade=? AND PkgWt=? AND PriceKg=?",
                                    (new_qty, LotNo, InvNo, Mark, Grade, PkgWt, PriceKg))

                self.conn.commit()
                self.refresh_purchases_list()
                self.refresh_qty_list()
                self.refresh_sales_list()
                messagebox.showinfo("Success", "Items distributed successfully.")
            else:
                messagebox.showerror("Error", "Purchase record not found.")

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error during distribution: {e}")
            self.conn.rollback()

    def delete_sales_revert_purchase(self):
        """
        Deletes a selected sales record and reverts the quantity back to the purchase inventory.
        """
        selected_items = self.tree_sales.selection()
        if not selected_items:
            messagebox.showinfo("Info", "Select a sales item to delete and revert.")
            return

        item = selected_items[0]
        values = self.tree_sales.item(item, 'values')
        LotNo, InvNo, Mark, Grade, Qty, PkgWt, PriceKg, Party = values

        confirm = messagebox.askyesno("Confirm", "Are you sure you want to delete this sale and revert the purchase?")
        if not confirm:
            return

        try:
            # Delete the sale
            self.cursor.execute("DELETE FROM sales WHERE LotNo=? AND InvNo=? AND Mark=? AND Grade=? AND Qty=? AND PkgWt=? AND PriceKg=? AND Party=?",
                                (LotNo, InvNo, Mark, Grade, Qty, PkgWt, PriceKg, Party))

            # Revert the purchase
            self.cursor.execute("SELECT Qty FROM purchases WHERE LotNo=? AND InvNo=? AND Mark=? AND Grade=? AND PkgWt=? AND PriceKg=?",
                                (LotNo, InvNo, Mark, Grade, PkgWt, PriceKg))
            purchase_record = self.cursor.fetchone()

            if purchase_record:
                current_purchase_qty = purchase_record[0]
                self.cursor.execute("UPDATE purchases SET Qty = ? WHERE LotNo=? AND InvNo=? AND Mark=? AND Grade=? AND PkgWt=? AND PriceKg=?",
                                    (current_purchase_qty + int(Qty), LotNo, InvNo, Mark, Grade, PkgWt, PriceKg))
            else:
                # If purchase record doesn't exist, insert a new one.
                self.cursor.execute("INSERT INTO purchases (LotNo, InvNo, Mark, Grade, Qty, PkgWt, PriceKg) VALUES (?, ?, ?, ?, ?, ?, ?)",
                                    (LotNo, InvNo, Mark, Grade, Qty, PkgWt, PriceKg))

            self.conn.commit()
            self.refresh_purchases_list()
            self.refresh_sales_list()
            messagebox.showinfo("Success", "Sale deleted and purchase reverted successfully.")

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred: {e}")
            self.conn.rollback()

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
    app = DistributionApp(root)
    root.mainloop()