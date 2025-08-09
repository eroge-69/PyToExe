import requests
import csv
import openpyxl
from bs4 import BeautifulSoup
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
from PIL import Image, ImageTk
import locale
import re

def convert_market_value(market_value, remove_euro_sign, convert_to_expanded_form):
    if market_value == "N/A":
        return "N/A"

    if remove_euro_sign:
        market_value = market_value.replace("€", "").strip()

    if convert_to_expanded_form:
        match = re.match(r"(\d+\.\d+)([KkMm])", market_value)
        if match:
            value, unit = match.groups()
            value = float(value)
            if unit.lower() == "k":
                value *= 1000
            elif unit.lower() == "m":
                value *= 1000000
            return "{:,.0f}".format(value).replace(",", "")

    return market_value

def extract_players_data(url, selected_fields, remove_euro_sign, convert_to_expanded_form):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise Exception("Unable to fetch the page.")

    soup = BeautifulSoup(response.content, "html.parser")
    players_data = []
    player_rows = soup.select("table.items > tbody > tr")

    for row in player_rows:
        player_info = {}
        if 'Shirt Number' in selected_fields:
            shirt_number_element = row.select_one("div.tm-shirt-number")
            shirt_number = shirt_number_element.text.strip() if shirt_number_element else "N/A"
            player_info["Shirt Number"] = shirt_number

        if 'Name' in selected_fields:
            name_element = row.select_one("td.hauptlink > a")
            if name_element:
                name = name_element.get("title", name_element.get_text()).strip()
            else:
                name = "N/A"
            player_info["Name"] = name

        if 'Position' in selected_fields:
            position_element = row.select_one("td:nth-of-type(2) > table tr:nth-of-type(2) td")
            position = position_element.text.strip() if position_element else "N/A"
            player_info["Position"] = position

        if 'Age' in selected_fields:
            age_element = row.select_one("td:nth-of-type(4)")
            age = age_element.text.strip() if age_element else "N/A"
            age = age.split("(")[-1].replace(")", "").strip()
            player_info["Age"] = age

        if 'Nationality' in selected_fields:
            nationality_element = row.select_one("img.flaggenrahmen")
            nationality = nationality_element.get("title", "N/A")
            player_info["Nationality"] = nationality

        if 'Market Value' in selected_fields:
            market_value_element = row.select_one("td.rechts.hauptlink > a")
            market_value = market_value_element.text.strip() if market_value_element else "N/A"
            if not market_value == "N/A":
                market_value = convert_market_value(market_value, remove_euro_sign, convert_to_expanded_form)
            player_info["Market Value"] = market_value

        players_data.append(player_info)

    return players_data

def save_data_to_file(data, file_name, file_type):
    if file_type == "CSV":
        with open(file_name, "w", newline="", encoding="utf-8") as csvfile:
            fieldnames = ["Shirt Number", "Name", "Age", "Position", "Nationality", "Market Value"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
    elif file_type == "Excel":
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.append(["Shirt Number", "Name", "Age", "Position", "Nationality", "Market Value"])

        for player_info in data:
            row_data = [player_info.get("Shirt Number", ""),
                        player_info.get("Name", ""),
                        player_info.get("Age", ""),
                        player_info.get("Position", ""),
                        player_info.get("Nationality", ""),
                        player_info.get("Market Value", "")]
            ws.append(row_data)

        wb.save(file_name)

def scrape_and_save():
    url = url_entry.get()
    selected_fields = [field for field, var in zip(field_names, checkbox_vars) if var.get()]
    remove_euro_sign = euro_sign_var.get()
    convert_to_expanded_form = expanded_form_var.get()
    
    if not url:
        messagebox.showerror("Error", "Please enter a valid URL.")
        return

    if not selected_fields:
        messagebox.showerror("Error", "Please select at least one field to extract.")
        return

    try:
        player_data_list = extract_players_data(url, selected_fields, remove_euro_sign, convert_to_expanded_form)
        if player_data_list:
            file_type = file_type_var.get()
            file_type_extension = ".csv" if file_type == "CSV" else ".xlsx"
            file_name = filedialog.asksaveasfilename(defaultextension=file_type_extension, filetypes=[(f"{file_type} files", f"*{file_type_extension}")])
            if file_name:
                save_data_to_file(player_data_list, file_name, file_type)
                messagebox.showinfo("Success", f"Data saved to '{file_name}' successfully.")
        else:
            messagebox.showerror("Error", "Data extraction failed. Please check if the website is accessible and try again.")
    except Exception as e:
        messagebox.showerror("Error", str(e))

root = tk.Tk()
root.title("Transfermarkt Player Data Scraper")
root.geometry("500x400")
root.resizable(False, False)

icon_path = "Transfermarkt_favicon.png"
try:
    img = Image.open(icon_path)
    icon_photo = ImageTk.PhotoImage(img)
    root.tk.call('wm', 'iconphoto', root._w, icon_photo)
except FileNotFoundError:
    pass

style = ttk.Style(root)
style.configure("TLabel", font=("Arial", 11))
style.configure("TButton", font=("Arial", 11))
style.configure("TCheckbutton", font=("Arial", 11))
style.configure("TRadiobutton", font=("Arial", 11))

title_label = ttk.Label(root, text="Transfermarkt Player Data Scraper", style="TLabel")
title_label.pack(pady=10)

url_frame = ttk.Frame(root)
url_frame.pack(pady=5)
url_label = ttk.Label(url_frame, text="Enter Team URL:")
url_label.pack(side=tk.LEFT)
url_entry = ttk.Entry(url_frame, width=40)
url_entry.insert(tk.END, "https://www.transfermarkt.com/real-madrid/startseite/verein/418")
url_entry.pack(side=tk.LEFT)

fields_frame = ttk.Frame(root)
fields_frame.pack(pady=5)
fields_label = ttk.Label(fields_frame, text="Select Fields to Extract:", style="TLabel")
fields_label.pack(anchor=tk.W)

field_names = ["Shirt Number", "Name", "Age", "Position", "Nationality", "Market Value"]
checkbox_vars = [tk.BooleanVar(value=True) for _ in field_names]

for i, field in enumerate(field_names):
    checkbox = ttk.Checkbutton(fields_frame, text=field, variable=checkbox_vars[i], onvalue=True, offvalue=False, style="TCheckbutton")
    checkbox.pack(anchor=tk.W)

options_frame = ttk.Frame(root)
options_frame.pack(pady=5)

euro_sign_var = tk.BooleanVar(value=True)
euro_sign_checkbox = ttk.Checkbutton(options_frame, text="Remove € Sign", variable=euro_sign_var, onvalue=True, offvalue=False, style="TCheckbutton")
euro_sign_checkbox.pack(side=tk.LEFT, padx=5)

expanded_form_var = tk.BooleanVar(value=True)
expanded_form_checkbox = ttk.Checkbutton(options_frame, text="Convert to Expanded Form (e.g. 6M to 6,000,000)", variable=expanded_form_var, onvalue=True, offvalue=False, style="TCheckbutton")
expanded_form_checkbox.pack(side=tk.LEFT)

file_type_frame = ttk.Frame(root)
file_type_frame.pack(pady=5)
file_type_label = ttk.Label(file_type_frame, text="Select Output File Type:", style="TLabel")
file_type_label.pack(side=tk.LEFT)

file_type_var = tk.StringVar(value="CSV")
csv_radio = ttk.Radiobutton(file_type_frame, text="CSV", variable=file_type_var, value="CSV", style="TRadiobutton")
excel_radio = ttk.Radiobutton(file_type_frame, text="Excel", variable=file_type_var, value="Excel", style="TRadiobutton")
csv_radio.pack(side=tk.LEFT, padx=5)
excel_radio.pack(side=tk.LEFT)

extract_button = ttk.Button(root, text="Extract Data and Save", command=scrape_and_save, style="TButton")
extract_button.pack(pady=10)

def open_github_page(event):
    github_url = "https://github.com/CoderRafay/TransfermarktPlayerDataScraper"
    import webbrowser
    webbrowser.open_new(github_url)

coder_label = ttk.Label(root, text="Made by CoderRafay", font=("Arial", 10), foreground="gray", cursor="hand2")
coder_label.pack(side=tk.BOTTOM, pady=5)
coder_label.bind("<Button-1>", open_github_page)

root.mainloop()
