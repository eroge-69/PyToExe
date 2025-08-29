import tkinter as tk
from tkinter import filedialog, messagebox
import requests
from bs4 import BeautifulSoup
import os
import zipfile
import shutil

# Function to get all products and download links
def get_available_versions():
    update_url = "https://аэронавигатор.рф/airac-updates"  # URL of the products page
    try:
        response = requests.get(update_url)
        response.raise_for_status()

        # Using BeautifulSoup to parse the page
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all rows with products and links
        products = []
        rows = soup.find_all('tr')  # Table rows
        for row in rows:
            cols = row.find_all('td')
            if len(cols) > 1:
                product_name = cols[0].text.strip()
                download_link = cols[1].find('a')['href'] if cols[1].find('a') else None
                if download_link:
                    products.append({'name': product_name, 'download_link': download_link})
        return products

    except requests.exceptions.RequestException as e:
        messagebox.showerror("Error", f"Failed to fetch products: {e}")
        return []

# Function to choose folder for saving
def choose_save_folder():
    folder_selected = filedialog.askdirectory(title="Choose a folder to save")
    return folder_selected

# Function to download selected updates
def download_selected_updates(selected_updates, save_folder):
    for update in selected_updates:
        download_url = update['download_link']
        save_path = os.path.join(save_folder, f"{update['name']}.zip")

        try:
            response = requests.get(download_url)
            response.raise_for_status()

            # Save the file
            with open(save_path, "wb") as f:
                f.write(response.content)

            messagebox.showinfo("Download Complete", f"Update {update['name']} downloaded to {save_path}")

            # Extract and install
            extract_and_install(save_path, update['name'])

        except requests.exceptions.RequestException as e:
            messagebox.showerror("Error", f"Failed to download {update['name']}: {e}")

# Function to extract archive and install
def extract_and_install(archive_path, product_name):
    # Define the folder for installation
    target_folder = os.path.join(os.getcwd(), "Custom Data", product_name)

    if not os.path.exists(target_folder):
        os.makedirs(target_folder)

    with zipfile.ZipFile(archive_path, "r") as zip_ref:
        # Filter files to exclude .index files
        for file_name in zip_ref.namelist():
            if not file_name.endswith(".index"):  # Exclude .index files
                zip_ref.extract(file_name, target_folder)
    
    messagebox.showinfo("Installation Complete", f"Update {product_name} installed to {target_folder}")

# Main window of the program
def main_window():
    window = tk.Tk()
    window.title("X-Plane 12 AIRAC Updates")

    # Get available products
    products = get_available_versions()

    if not products:
        messagebox.showerror("Error", "Failed to get product list.")
        window.quit()
        return

    # List of checkboxes for selecting updates
    selected_updates = []

    def update_selected():
        selected_updates.clear()
        for i, var in enumerate(update_vars):
            if var.get():
                selected_updates.append(products[i])

    # Frame for displaying available products
    frame = tk.Frame(window)
    frame.pack(pady=10)

    update_vars = []
    for i, product in enumerate(products):
        var = tk.BooleanVar()
        update_vars.append(var)
        checkbox = tk.Checkbutton(frame, text=product['name'], variable=var)
        checkbox.grid(row=i, column=0, sticky="w")

    # Button to choose save folder
    save_button = tk.Button(window, text="Choose Save Folder", command=lambda: choose_save_folder())
    save_button.pack(pady=10)

    # Button to download selected updates
    download_button = tk.Button(window, text="Download Selected Updates", command=lambda: download_selected_updates(selected_updates, choose_save_folder()))
    download_button.pack(pady=10)

    # Button to select all products
    def select_all():
        for var in update_vars:
            var.set(True)

    select_all_button = tk.Button(window, text="Select All", command=select_all)
    select_all_button.pack(pady=5)

    # Button to deselect all products
    def deselect_all():
        for var in update_vars:
            var.set(False)

    deselect_all_button = tk.Button(window, text="Deselect All", command=deselect_all)
    deselect_all_button.pack(pady=5)

    # Quit button
    quit_button = tk.Button(window, text="Quit", command=window.quit)
    quit_button.pack(pady=10)

    # Update button
    update_button = tk.Button(window, text="Update Selected", command=update_selected)
    update_button.pack(pady=10)

    window.mainloop()

if __name__ == "__main__":
    main_window()
