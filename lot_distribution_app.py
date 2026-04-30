"""
Main application module for Lot Distribution & Management.

This module creates the main Tkinter window and menu for the application.
It imports and integrates various sub-modules for sales, party, purchase,
distribution, and PDF generation functionalities.
"""

import tkinter as tk

from sale_info_entry import SaleInfoApp
from party_entry import PartyApp
from purchase_entry import PurchaseApp
from distribution import DistributionApp
from pdf_generation import PDFCreatorApp

def add_sales_info():
    """Displays the sales entry window."""
    menu()
    SaleInfoApp(root)

def show_party():
    """Displays the party entry window."""
    menu()
    PartyApp(root)

def add_purchase():
    """Displays the purchase entry window."""
    menu()
    PurchaseApp(root)

def do_distribution():
    """Displays the distribution window."""
    menu()
    DistributionApp(root)

def party_sales():
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

    # Create Purchase Menu
    purchase_menu = tk.Menu(menu_bar, tearoff=0)
    menu_bar.add_cascade(label="Purchase Management", menu=purchase_menu)
    purchase_menu.add_command(label="Sale Information", command=add_sales_info)
    purchase_menu.add_separator()
    purchase_menu.add_command(label="Upload Purchase Data", command=add_purchase)
    # purchase_menu.add_command(label="Upload Purchase Invoices", command=show_invoices)

    # Create Sales Menu
    sales_menu = tk.Menu(menu_bar, tearoff=0)
    menu_bar.add_cascade(label="Sales Management", menu=sales_menu)
    sales_menu.add_command(label="Lots Distribution", command=do_distribution)
    sales_menu.add_separator()
    sales_menu.add_command(label="Party-wise Sales", command=party_sales)
    # sales_menu.add_command(label="Upload Sales Invoices", command=show_bills)

    # Create Mangement Menu
    manage_menu = tk.Menu(menu_bar, tearoff=0)
    menu_bar.add_cascade(label="Management", menu=manage_menu)
    manage_menu.add_command(label="Party Info", command=show_party)
    manage_menu.add_separator()
    manage_menu.add_command(label="Exit", command=root.quit)

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Lot Distribution & Management")
    root.geometry("900x600")
    root.resizable(True, True)

    menu()  # Call menu directly, no return value needed
    root.mainloop()
