"""
Main application module for Lot Distribution & Management.

This module creates the main Tkinter window and menu for the application.
It imports and integrates various sub-modules for sales, party, purchase,
distribution, and PDF generation functionalities.
"""

import tkinter as tk

from sale_entry import SalesApp
from party_entry import PartyApp
from purchase_entry import PurchaseApp
from distribution import DistributionApp
from pdf_generation import PDFCreatorApp

def show_sales():
    """Displays the sales entry window."""
    menu()
    SalesApp(root)

def show_party():
    """Displays the party entry window."""
    menu()
    PartyApp(root)

def show_purchase():
    """Displays the purchase entry window."""
    menu()
    PurchaseApp(root)

def show_distribution():
    """Displays the distribution window."""
    menu()
    DistributionApp(root)

def pdf_generate():
    """Displays the PDF generation window."""
    menu()
    PDFCreatorApp(root)

def menu():
    """Creates and displays the main menu."""
    # Remove all tk elements
    for ele in root.winfo_children():
        ele.destroy()

    # Create a Menu Bar
    menu_bar = tk.Menu(root)
    root.config(menu=menu_bar)

    # Create Entry Menu
    entry_menu = tk.Menu(menu_bar, tearoff=0)
    menu_bar.add_cascade(label="Entry", menu=entry_menu)

    entry_menu.add_command(label="Sale Info", command=show_sales)
    entry_menu.add_command(label="Party Info", command=show_party)
    entry_menu.add_separator()
    entry_menu.add_command(label="Exit", command=root.quit)

    # Create Data Menu
    data_menu = tk.Menu(menu_bar, tearoff=0)
    menu_bar.add_cascade(label="Data", menu=data_menu)

    data_menu.add_command(label="Upload Data", command=show_purchase)
    data_menu.add_command(label="Distribution", command=show_distribution)
    data_menu.add_separator()
    data_menu.add_command(label="Create PDF", command=pdf_generate)

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Lot Distribution & Management")
    root.geometry("900x600")
    root.resizable(True, True)

    menu()  # Call menu directly, no return value needed
    root.mainloop()
