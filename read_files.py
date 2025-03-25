import pandas as pd
import xml.etree.ElementTree as ET
from tkinter import messagebox

def read_xml(file_name):
    """
    Reads an XML file and converts it into a Pandas DataFrame.

    Args:
        file_name (str): The path to the XML file.

    Returns:
        pandas.DataFrame: A DataFrame containing the data from the XML file,
                          or None if an error occurs.
    """
    try:
        tree = ET.parse(file_name)
        root = tree.getroot()
        table = root[1][0]
        data_rows = []
        for row in table:
            data_rows.append([element[0].text for element in row])
        data = pd.DataFrame(data_rows[1:], columns=data_rows[0])
        return data
    except Exception as e:
        messagebox.showerror("Error", f"Error reading XML: {e}")
        return None

def read_csv(file_name):
    """
    Reads an CSV file and converts it into a Pandas DataFrame.

    Args:
        file_name (str): The path to the CSV file.

    Returns:
        pandas.DataFrame: A DataFrame containing the data from the CSV file,
                          or None if an error occurs.
    """
    try:
        data = pd.read_csv(file_name)
        return data
    except Exception as e:
        messagebox.showerror("Error", f"Error reading CSV: {e}")
        return None