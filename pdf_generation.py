"""
PDFCreatorApp: A Tkinter application for generating PDF reports from sales data.

This module provides a graphical user interface (GUI) for creating PDF documents
containing sales information. It allows users to select a sale number and party,
preview the sales data, and then generate a PDF report.

Key Features:
- Select sale number and party.
- Preview sales data.
- Generate and save PDF reports.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import sqlite3
import os

from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.units import inch


class PDFCreatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Lot Distribution PDF Generator")

        self.constants_db_path = "constants.db"
        self.sale_nos = self.fetch_sale_numbers()
        self.columns = ["Lot No", "Inv. No", "Mark", "Grade", "Qty", "Pkg. Wt", "Rate"]
        self.conn = None
        self.cursor = None

        self.create_widgets()

    def fetch_sale_numbers(self):
        """Fetches sale numbers from the constants database."""
        try:
            if not os.path.exists(self.constants_db_path):
                messagebox.showerror("Error", f"Constants database not found: {self.constants_db_path}")
                return []
            with sqlite3.connect(self.constants_db_path) as conn:
                cursor = conn.cursor()
                return [row[0] for row in cursor.execute("SELECT sale_number FROM sales").fetchall()]
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error fetching sale numbers: {e}")
            return []

    def update_db_selection(self, event=None):
        """Updates the database connection and party list based on the selected sale number."""
        sale_number = self.sale_combobox.get()
        if not sale_number:
            return

        db_path = os.path.join(os.getcwd(), "dbs", f"{sale_number}.db")

        try:
            if not os.path.exists(os.path.join(os.getcwd(), "dbs")):
                messagebox.showerror("Error", "Sale directory not found.")
                return

            if self.conn:
                self.conn.close()

            self.conn = sqlite3.connect(db_path)
            self.cursor = self.conn.cursor()
            self.party = [row[0] for row in self.cursor.execute("SELECT DISTINCT(party) FROM sales").fetchall()]
            self.party_combobox['values'] = self.party

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error connecting to database: {e}")

    def display_sales_data(self):
        """Displays sales data in the treeview based on the selected party."""
        party = self.party_combobox.get()
        if not party:
            messagebox.showerror("Input Error", "Please select a Party.")
            return

        try:
            for item in self.tree_sales.get_children():
                self.tree_sales.delete(item)

            query = "SELECT LotNo, InvNo, Mark, Grade, Qty, PkgWt, PriceKg FROM sales WHERE Party=?"
            sales = self.cursor.execute(query, (party,)).fetchall()

            for sale in sales:
                self.tree_sales.insert("", "end", values=sale)
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error retrieving sales data: {e}")

    def create_widgets(self):
        """Creates and arranges the GUI widgets."""
        heading_frame = ttk.LabelFrame(self.root, text="Distributed PDF Creation")
        heading_frame.pack(padx=10, pady=10, fill="x")

        tk.Label(heading_frame, text="Sale No:").pack(side=tk.LEFT)
        self.sale_combobox = ttk.Combobox(heading_frame, state="readonly", width=12)
        self.sale_combobox['values'] = self.sale_nos
        if self.sale_nos:
            self.sale_combobox.current(min(len(self.sale_nos) - 1,0))
        self.sale_combobox.pack(side=tk.LEFT, padx=5)
        self.sale_combobox.bind("<<ComboboxSelected>>", self.update_db_selection)

        tk.Label(heading_frame, text="Party:").pack(side=tk.LEFT)
        self.party_combobox = ttk.Combobox(heading_frame, width=15)
        self.party_combobox.pack(side=tk.LEFT, padx=5)
        self.update_db_selection()

        preview_button = ttk.Button(heading_frame, text="Preview", command=self.display_sales_data)
        preview_button.pack(side="left", padx=5, pady=5)

        sales_frame = tk.LabelFrame(self.root, text="Sales Data")
        sales_frame.pack(pady=10, padx=10, fill='both', expand=True)

        self.tree_sales = ttk.Treeview(sales_frame, columns=self.columns, show="headings")
        for col in self.columns:
            self.tree_sales.heading(col, text=col)
            self.tree_sales.column(col, width=100)
        self.tree_sales.pack(fill='both', expand=True)

        create_pdf_button = ttk.Button(heading_frame, text="Create and Save PDF", command=self.create_and_save_pdf)
        create_pdf_button.pack(side="left", padx=10)

    def generate_pdf(self, filepath="temp_preview.pdf"):
        """Generates a PDF document with sales data."""
        party = self.party_combobox.get()
        if not party:
            messagebox.showerror("Input Error", "Please select a Party.")
            return False

        try:
            with sqlite3.connect(self.constants_db_path) as constants_conn:
                cursor = constants_conn.cursor()
                heading_text = cursor.execute(f"SELECT name FROM party WHERE code='{party}'").fetchone()[0]
                address = cursor.execute(f"SELECT address FROM party WHERE code='{party}'").fetchone()[0]
                sale_info = cursor.execute(f"SELECT * FROM sales WHERE sale_number='{self.sale_combobox.get()}'").fetchone()

            doc = SimpleDocTemplate(filepath, pagesize=(612, 792), topMargin=0.5 * inch, bottomMargin=0.5 * inch)
            styles = getSampleStyleSheet()

            heading_style = styles['Heading1']
            heading_style.alignment = TA_CENTER
            heading_style.leading = 15

            sub_heading_style = styles['Heading2']
            sub_heading_style.alignment = TA_CENTER
            sub_heading_style.leading = 5
            sub_heading_style.spaceBefore = 0

            normal_style = styles['Normal']

            story = [Paragraph(heading_text, heading_style)]
            if address:
                story.append(Paragraph(address, sub_heading_style))
            story.append(Spacer(1, 0.1 * inch))

            if sale_info:
                sale_info_table = Table([f"Sale No: {sale_info[0]}\t\tSale Dt: {sale_info[1]}\t\tPrompt Dt: {sale_info[2]}".split("\t")])
                sale_info_table.hAlign = 'CENTER'
                sale_info_table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.white),
                                                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                                                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                                                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica'),
                                                        ('BOTTOMPADDING', (0, 0), (-1, 0), 0),
                                                        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                                                        ('GRID', (0, 0), (-1, -1), 1, colors.white)]))
                story.append(sale_info_table)
            story.append(Spacer(1, 0.1 * inch))

            try:
                query = "SELECT LotNo, InvNo, Mark, Grade, Qty, PkgWt, PriceKg FROM sales WHERE Party=?"
                sales = self.cursor.execute(query, (party,)).fetchall()

                table_data = [self.columns] + [[row[i] if i <= 3 else int(row[i]) for i in range(len(row))] for row in sales]
                if len(table_data) <= 1:
                    messagebox.showinfo("Info", "No data found in table")
                    return False

                table = Table(table_data)
                table.hAlign = 'CENTER'
                table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                                                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                                                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                                                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                                                        ('BOTTOMPADDING', (0, 0), (-1, 0), 0),
                                                        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                                                        ('GRID', (0, 0), (-1, -1), 1, colors.black)]))
                story.append(table)
                story.append(Spacer(1, 0.1 * inch))

                total_bags = sum(row[4] for row in sales)
                story.append(Paragraph(f"Total Bags: {total_bags}", sub_heading_style))
                story.append(Spacer(1, 0.1 * inch))
                story.append(Paragraph("***GST + other expenses extra.", normal_style))

                doc.build(story)
                return True

            except sqlite3.Error as e:
                messagebox.showerror("Database Error", f"Error retrieving sales data: {e}")
                return False

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error during PDF generation: {e}")
            return False
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")
            return False

    def create_and_save_pdf(self):
        """Creates and saves the PDF file."""
        try:
            filepath = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf")]
            )
            if filepath:
                if self.generate_pdf(filepath):
                    messagebox.showinfo("Success", f"PDF created successfully at: {filepath}")
        except Exception as file_err:
            messagebox.showerror("File Error", f"Error saving PDF: {file_err}")

    def on_closing(self):
        """Handles the application closing event."""
        if self.conn:
            self.conn.close() # Close the connection if it exists.
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = PDFCreatorApp(root)
    root.mainloop()
