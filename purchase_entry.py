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
from read_files import read_xml
from datetime import date

class PurchaseApp:
    """
    A Tkinter application for managing purchase data.
    """

    def __init__(self, root):
        """
        Initializes the PurchaseApp with the given root window.
        """
        self.root = root
        self.root.title("Purchase Management App")
        self.root.geometry("1000x800")
        self.root.resizable(True, True)

        self.constants_conn = sqlite3.connect("constants.db")
        self.constants_cursor = self.constants_conn.cursor()
        self.sale_nos = [row[0] for row in self.constants_cursor.execute("SELECT sale_number FROM sales").fetchall()]
        self.constants_conn.close()

        self.create_widgets()
        self.update_db_selection()
        self.refresh_purchases_list()

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def update_db_selection(self, event=None):
        """
        Updates the database connection based on the selected sale number and refreshes the purchase list.
        """
        sale_no = self.sale_no_entry.get()
        if not sale_no:
            return
        db_path = os.path.join(os.getcwd(), "dbs", f"{sale_no}.db")
        try:
            self.conn = sqlite3.connect(db_path)
            self.cursor = self.conn.cursor()
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS purchases (
                    id INTEGER PRIMARY KEY,
                    BuyerCode TEXT,
                    LotNo TEXT,
                    Category TEXT,
                    InvNo TEXT,
                    Mark TEXT,
                    Grade TEXT,
                    BoughtQty INTEGER,
                    Qty INTEGER,
                    PkgWt INTEGER,
                    TotalWt REAL,
                    PriceKg INTEGER
                )
            """)
            self.conn.commit()
            self.refresh_purchases_list()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error connecting to database: {e}")

    def create_widgets(self):
        """
        Creates and arranges the GUI widgets for the purchase management application.
        """
        upload_frame = tk.Frame(self.root)
        upload_frame.pack(fill='both', expand=True)

        buyer_frame = tk.Frame(upload_frame)
        buyer_frame.pack(pady=10, fill=tk.X)

        buyer_label = tk.Label(buyer_frame, text="Purchase Actions:", font=("Arial", 12, "bold"))
        buyer_label.pack(side=tk.LEFT, padx=5)

        ttk.Label(buyer_frame, text="Sale No:").pack(side=tk.LEFT, padx=5)
        self.sale_no_entry = ttk.Combobox(buyer_frame, state="readonly", width=12)
        self.sale_no_entry['values'] = self.sale_nos
        if self.sale_nos:
            self.sale_no_entry.current(len(self.sale_nos) - 1)
        self.sale_no_entry.pack(side=tk.LEFT, padx=5)
        self.sale_no_entry.bind("<<ComboboxSelected>>", self.update_db_selection)

        button_add = tk.Button(buyer_frame, text="Add Items", command=self.add_file)
        button_add.pack(side=tk.LEFT, padx=5)

        button_delete = tk.Button(buyer_frame, text="Delete Items", command=self.delete_selected)
        button_delete.pack(side=tk.LEFT, padx=5)

        button_modify = tk.Button(buyer_frame, text="Modify Item", command=self.modify_selected)
        button_modify.pack(side=tk.LEFT, padx=5)

        frame_buyer = tk.LabelFrame(upload_frame, text="Purchase Data")
        frame_buyer.pack(fill='both', expand=True)
        self.frame_buyer = frame_buyer

        self.tree_buyer = ttk.Treeview(frame_buyer, columns=(
            "BuyerCode", "LotNo", "InvNo", "Mark", "Grade", "Qty", "PkgWt", "TotalWt", "PriceKg"), show="headings")
        for col in ("BuyerCode", "LotNo", "InvNo", "Mark", "Grade", "Qty", "PkgWt", "TotalWt", "PriceKg"):
            self.tree_buyer.heading(col, text=col)
            self.tree_buyer.column(col, anchor=tk.CENTER, width=int(1000/9))
        self.tree_buyer.pack(fill='both', expand=True)

        frame_buyer_summary = tk.LabelFrame(upload_frame, text="Purchase Summary")
        frame_buyer_summary.pack(fill='both', expand=True)
        self.frame_buyer_summary = frame_buyer_summary


        self.tree_buyer_summary = ttk.Treeview(frame_buyer_summary, columns=(
            "BuyerCode", "Qty", "Kgs", "Avg. Amt.", "Tot. Amt"), show="headings")
        for col in ("BuyerCode", "Qty", "Kgs", "Avg. Amt.", "Tot. Amt"):
            self.tree_buyer_summary.heading(col, text=col)
            self.tree_buyer_summary.column(col, anchor=tk.CENTER, width=int(1000/5))
        self.tree_buyer_summary.pack(fill='both', expand=True)

    def refresh_purchases_list(self):
        """
        Refreshes the list of purchases displayed in the treeview.
        """
        for item in self.tree_buyer.get_children():
            self.tree_buyer.delete(item)
        
        for item in self.tree_buyer_summary.get_children():
            self.tree_buyer_summary.delete(item)

        try:
            self.cursor.execute("SELECT Category, BuyerCode, LotNo, InvNo, Mark, Grade, BoughtQty, PkgWt, TotalWt, PriceKg FROM purchases ORDER BY Category, LotNo")
            purchases = self.cursor.fetchall()
            for purchase in purchases:
                # Display BoughtQty as Qty in the treeview
                self.tree_buyer.insert("", "end", values=purchase[1:])

            buyer_codes = set(self.cursor.execute("SELECT DISTINCT(BuyerCode) FROM purchases").fetchall())

            for buyer in buyer_codes:
                self.tree_buyer_summary.insert("", "end", values=[buyer,
                    self.cursor.execute("SELECT SUM(BoughtQty) FROM purchases WHERE BuyerCode=?", buyer).fetchone()[0],
                    self.cursor.execute("SELECT SUM(TotalWt) FROM purchases WHERE BuyerCode=?", buyer).fetchone()[0],
                    self.cursor.execute("SELECT SUM(TotalWt*PriceKg)/SUM(TotalWt) FROM purchases WHERE BuyerCode=?", buyer).fetchone()[0],
                    self.cursor.execute("SELECT SUM(TotalWt*PriceKg) FROM purchases WHERE BuyerCode=?", buyer).fetchone()[0]])

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error fetching purchases: {e}")

    def add_file(self):
        """
        Opens a file dialog to select an Excel file, reads the data, and adds it to the database.
        """
        filepath = filedialog.askopenfilename(filetypes=[("Excel Files", "*.xls")])
        if filepath:
            try:
                temp_df = read_xml(filepath)
                select_col = ['BuyersExportAddressCode', 'LotNo', 'Invoice No', 'Mark',
                              'Grade', 'Qty (Pkgs)', 'Packages Wt/Pkg', 'Total NtWt', 'Price/Kg']
                try:
                    temp_df = temp_df[select_col]
                    temp_df.columns = ['BuyerCode', 'LotNo', 'InvNo', 'Mark', 'Grade', 'BoughtQty',
                                        'PkgWt', 'TotalWt', 'PriceKg']
                    for index, row in temp_df.iterrows():
                        try:
                            # Check if the LotNo already exists
                            self.cursor.execute("SELECT Qty FROM purchases WHERE BuyerCode=? AND LotNo=? AND InvNo=? AND Mark=?", list(row)[:4])
                            existing_record = self.cursor.fetchone()
                            if existing_record:
                                # LotNo exists, no need to insert again, old data persists
                                continue
                            else:
                                # LotNo doesn't exist, insert the new record
                                self.cursor.execute("""
                                    INSERT INTO purchases (BuyerCode, LotNo, InvNo, Mark, Grade, Qty, PkgWt, TotalWt, PriceKg, BoughtQty, Category)
                                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                                """, tuple(list(row) + [list(row)[5], "Dust" if row[0].rsplit("-",1)[1]=="SD" else "Leaf"]))
                        except sqlite3.Error as e:
                            messagebox.showerror("Database Error", f"Error inserting record for LotNo {row['LotNo']}: {e}")
                            continue  # Skip the rest of the loop for this row.

                    self.conn.commit()
                    self.refresh_purchases_list()
                    messagebox.showinfo("Success", f"File '{filepath}' processed successfully. Existing data persisted.")
                except KeyError as e:
                    messagebox.showerror("Error", f"Required column '{e.args[0]}' not found in the uploaded file.")
                except Exception as e:
                    messagebox.showerror("Error", f"An unexpected error occurred while processing the file: {e}")
            except Exception as e:
                messagebox.showerror("Error", f"Error reading file '{filepath}': {e}")

    def delete_selected(self):
        """
        Deletes the selected purchase items from the database.
        """
        selected_items = self.tree_buyer.selection()
        if selected_items:
            for item in selected_items:
                values = self.tree_buyer.item(item, 'values')
                self.cursor.execute("DELETE FROM purchases WHERE BuyerCode=? AND LotNo=? AND InvNo=? AND Mark=?", values[:4])
            self.conn.commit()
            self.refresh_purchases_list()
        else:
            messagebox.showinfo("Info", "No rows selected.")

    def modify_selected(self):
        """
        Opens a dialog to modify the details of the selected purchase item.
        """
        selected_items = self.tree_buyer.selection()
        if not selected_items:
            messagebox.showinfo("Info", "No rows selected.")
            return
        
        item = selected_items[0]
        values = self.tree_buyer.item(item, 'values')
        purchase_record = self.cursor.execute("SELECT BoughtQty, Qty FROM purchases WHERE LotNo=? AND InvNo=? AND Mark=?", values[1:4]).fetchone()

        bought_qty = int(purchase_record[0])
        current_qty = int(purchase_record[1])

        if bought_qty != current_qty:
            messagebox.showerror("Error", "Modification is only allowed for lots that have not been distributed.")
            return
        
        columns = ["BuyerCode", "LotNo", "InvNo", "Mark", "Grade", "Qty", "PkgWt", "TotalWt", "PriceKg"]

        modify_dialog = tk.Toplevel(self.root)
        modify_dialog.title("Modify Record")

        entries = {}
        for i, col in enumerate(columns):
            tk.Label(modify_dialog, text=col).grid(row=i, column=0, sticky=tk.W)
            entry = tk.Entry(modify_dialog)
            entry.insert(tk.END, values[i])
            if i<4:
                entry.config(state='readonly')
            entry.grid(row=i, column=1, padx=5, pady=2)
            entries[col] = entry

        def save_changes():
            """Saves the modified values to the database."""
            new_values = [entry.get() for entry in entries.values()]
            try:
                # Update both BoughtQty and Qty for simplicity in this context
                self.cursor.execute("""
                    UPDATE purchases SET BuyerCode=?, LotNo=?, InvNo=?, Mark=?, Grade=?, BoughtQty=?, Qty=?, PkgWt=?, TotalWt=?, PriceKg=?
                    WHERE BuyerCode=? AND LotNo=? AND InvNo=? AND Mark=?
                """, tuple(new_values[:5] + [new_values[5], new_values[5]] + new_values[6:] + list(values[:4])))
                self.conn.commit()
                self.refresh_purchases_list()
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
    app = PurchaseApp(root)
    root.mainloop()