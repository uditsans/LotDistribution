"""
PartyApp: A Tkinter application for managing party information.

This module provides a GUI for entering, displaying, modifying, and deleting
party data. It uses an SQLite database to store party information.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

class PartyApp:
    def __init__(self, root):
        """
        Initializes the PartyApp with the given root window.
        """
        self.root = root
        self.root.title("Party Management")
        self.columns = ["Code", "Name", "Address", "Contact"]
        self.entry = ['' for _ in self.columns]

        self.conn = sqlite3.connect("constants.db")
        self.cursor = self.conn.cursor()

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS party (
                code TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                address TEXT,
                contact INTEGER
            )
        """)
        self.conn.commit()

        self.create_widgets()
        self.refresh_parties_list()

        root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_widgets(self):
        """
        Creates and arranges the GUI widgets for party information.
        """
        party_frame = ttk.LabelFrame(self.root, text="Party Information")
        party_frame.grid(row=0, column=0, padx=10, pady=10, sticky="we")

        for i, col in enumerate(self.columns):
            ttk.Label(party_frame, text=col).grid(row=i, column=0, padx=5, pady=2, sticky="w")
            self.entry[i] = tk.Entry(party_frame, width=100)
            self.entry[i].grid(row=i, column=1, padx=5, pady=2, sticky=tk.EW)

        ttk.Button(party_frame, text="Add Party", command=self.add_info).grid(row=0, rowspan=4, column=4, padx=15, pady=5)

        self.parties_tree = ttk.Treeview(self.root, columns=self.columns, show="headings")

        for col in self.columns:
            self.parties_tree.heading(col, text=col, anchor=tk.CENTER)
            self.parties_tree.column(col, anchor=tk.CENTER, stretch=tk.YES)

        self.parties_tree.grid(row=1, column=0, columnspan=2, padx=5, pady=2, sticky="we")

        modify_frame = ttk.Frame(self.root)
        modify_frame.grid(row=2, column=0, columnspan=2, padx=10, pady=5, sticky="we")

        ttk.Button(modify_frame, text="Delete Party", command=self.delete_info).pack(side=tk.LEFT, padx=10, pady=5)
        ttk.Button(modify_frame, text="Modify Party", command=self.modify_info).pack(side=tk.LEFT, padx=10, pady=5)

    def refresh_parties_list(self):
        """
        Refreshes the parties list in the treeview.
        """
        for item in self.parties_tree.get_children():
            self.parties_tree.delete(item)

        self.cursor.execute("SELECT * FROM party")
        parties = self.cursor.fetchall()

        for party in parties:
            self.parties_tree.insert("", "end", values=party)

    def clear_entries(self):
        """
        Clears the entry fields.
        """
        for entry in self.entry:
            entry.delete(0, tk.END)

    def on_closing(self):
        """
        Closes the database connection and destroys the root window.
        """
        try:
            self.conn.close()
        except Exception:
            pass
        self.root.destroy()

    def add_info(self):
        """
        Adds a new party to the database and refreshes the parties list.
        """
        code = self.entry[0].get()
        name = self.entry[1].get()
        address = self.entry[2].get()
        contact = self.entry[3].get()

        if not code or not name:
            messagebox.showerror("Error", "Code and Name are required.")
            return

        try:
            self.cursor.execute("INSERT INTO party (code, name, address, contact) VALUES (?, ?, ?, ?)",
                                (code, name, address, contact))
            self.conn.commit()
            messagebox.showinfo("Success", "Party added successfully.")
            self.refresh_parties_list()
            self.clear_entries()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Party code already exists.")
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Database error: {e}")

    def modify_info(self):
        """
        Modifies the selected party's information.
        """
        selected_item = self.parties_tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Select a party to modify.")
            return

        item = self.parties_tree.item(selected_item)
        code = item["values"][0]

        modify_window = tk.Toplevel(self.root)
        modify_window.title(f"Modify Party ({code})")

        ttk.Label(modify_window, text="Code").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        code_entry = tk.Entry(modify_window, width=100)
        code_entry.insert(0, code)
        code_entry.config(state='readonly')
        code_entry.grid(row=0, column=1, padx=5, pady=2, sticky=tk.EW)

        modify_entry = ['' for _ in self.columns[1:]]
        for i, col in enumerate(self.columns[1:]):
            ttk.Label(modify_window, text=col).grid(row=i + 1, column=0, padx=5, pady=2, sticky="w")
            modify_entry[i] = tk.Entry(modify_window, width=100)
            modify_entry[i].grid(row=i + 1, column=1, padx=5, pady=2, sticky=tk.EW)

        def modify_party():
            name = modify_entry[0].get()
            address = modify_entry[1].get()
            contact = modify_entry[2].get()

            if not name:
                messagebox.showerror("Error", "Name is required.")
                return

            try:
                self.cursor.execute("UPDATE party SET name=?, address=?, contact=? WHERE code=?",
                                    (name, address, contact, code))
                self.conn.commit()
                messagebox.showinfo("Success", "Party modified successfully.")
                self.refresh_parties_list()
                self.clear_entries()
                modify_window.destroy()
            except sqlite3.Error as e:
                messagebox.showerror("Error", f"Database error: {e}")

        ttk.Button(modify_window, text="Modify", command=modify_party).grid(row=4, column=0, columnspan=2, pady=5)

        self.cursor.execute("SELECT name, address, contact FROM party WHERE code=?", (code,))
        party_data = self.cursor.fetchone()
        if party_data:
            for i, data in enumerate(party_data):
                modify_entry[i].insert(0, data)

    def delete_info(self):
        """
        Deletes the selected party from the database and refreshes the parties list.
        """
        selected_item = self.parties_tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Select a party to delete.")
            return

        item = self.parties_tree.item(selected_item)
        code = item["values"][0]

        if messagebox.askyesno("Confirm", "Are you sure you want to delete this party?"):
            try:
                self.cursor.execute("DELETE FROM party WHERE code=?", (code,))
                self.conn.commit()
                messagebox.showinfo("Success", "Party deleted successfully.")
                self.refresh_parties_list()
                self.clear_entries()
            except sqlite3.Error as e:
                messagebox.showerror("Error", f"Database error: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = PartyApp(root)
    root.mainloop()