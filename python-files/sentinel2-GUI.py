import requests
import os
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading

# ---------------- CONFIG ----------------
CLIENT_ID = "sh-998c20f4-622b-4823-9e7b-f9fea19bc29c"
CLIENT_SECRET = "BeTOiueXuYnVaRUx6bZsq4Ta6OklGk9y"
BASE_URL = "https://catalogue.dataspace.copernicus.eu/odata/v1"
TOKEN_URL = "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token"
# ----------------------------------------

TOKEN_INFO = {"access_token": None, "expires_at": None}


def get_token():
    now = datetime.utcnow()
    if TOKEN_INFO["access_token"] and TOKEN_INFO["expires_at"] > now:
        return TOKEN_INFO["access_token"]

    resp = requests.post(
        TOKEN_URL,
        data={
            "grant_type": "client_credentials",
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
        },
    )
    resp.raise_for_status()
    token_json = resp.json()
    TOKEN_INFO["access_token"] = token_json["access_token"]
    TOKEN_INFO["expires_at"] = now + timedelta(seconds=token_json["expires_in"] - 60)
    return TOKEN_INFO["access_token"]


def search_products(granule_id, start_date, end_date, product_level, cloud_cover, max_results=50):
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}

    filter_query = (
        f"Collection/Name eq 'SENTINEL-2' "
        f"and ContentDate/Start ge {start_date}Z "
        f"and ContentDate/End le {end_date}Z "
        f"and Attributes/OData.CSC.StringAttribute/any(att:att/Name eq 'tileId' and att/Value eq '{granule_id}') "
        f"and Attributes/OData.CSC.DoubleAttribute/any(att:att/Name eq 'cloudCover' and att/Value le {cloud_cover})"
    )

    if product_level == "L1C":
        filter_query += " and Attributes/OData.CSC.StringAttribute/any(att:att/Name eq 'productType' and att/Value eq 'S2MSI1C')"
    elif product_level == "L2A":
        filter_query += " and Attributes/OData.CSC.StringAttribute/any(att:att/Name eq 'productType' and att/Value eq 'S2MSI2A')"

    url = f"{BASE_URL}/Products?$filter={filter_query}&$top={max_results}&$select=Id,Name,ContentLength"
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    return resp.json().get("value", [])


def human_readable_size(size_bytes):
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB")
    i = int((len(str(size_bytes)) - 1) / 3)
    p = 1024 ** i
    s = round(size_bytes / p, 2)
    return f"{s} {size_name[i]}"


def download_product(product, download_dir, update_progress, update_status, update_file_progress):
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}

    product_id = product["Id"]
    product_name = product["Name"]
    product_size = int(product.get("ContentLength", 0))
    filename = os.path.join(download_dir, f"{product_name}.zip")

    if os.path.exists(filename):
        update_status(f"✔ Already downloaded: {product_name}")
        update_progress(product_size)
        return

    url = f"https://download.dataspace.copernicus.eu/odata/v1/Products({product_id})/$value"
    update_status(f"⬇ Downloading {product_name} ({human_readable_size(product_size)})")

    with requests.get(url, headers=headers, stream=True) as r:
        if r.status_code == 401:
            headers = {"Authorization": f"Bearer {get_token()}"}
            r = requests.get(url, headers=headers, stream=True)
        r.raise_for_status()

        total_size = int(r.headers.get("Content-Length", product_size))
        downloaded = 0

        with open(filename, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total_size > 0:
                        percent = (downloaded / total_size) * 100
                        update_file_progress(percent, downloaded, total_size)

    update_status(f"✅ Downloaded: {product_name}")
    update_progress(product_size)
    update_file_progress(0, 0, 0)


def worker(download_dir, granules, start_date, end_date, product_level, cloud_cover):
    all_products = []
    for granule in granules:
        granule = granule.strip()
        products = search_products(granule, start_date, end_date, product_level, cloud_cover)
        all_products.extend(products)

    if not all_products:
        root.after(0, lambda: status_label.config(text="⚠ No products found."))
        return

    total_size = sum(int(p.get("ContentLength", 0)) for p in all_products)
    total_files = len(all_products)

    root.after(
        0,
        lambda: status_label.config(
            text=f"✅ Found {total_files} products | Total size: {human_readable_size(total_size)}"
        ),
    )
    root.after(0, lambda: overall_progress_bar.config(maximum=total_size, value=0))

    accumulated = {"downloaded": 0}

    def update_progress(size):
        accumulated["downloaded"] += size
        root.after(0, lambda: overall_progress_bar.config(value=accumulated["downloaded"]))
        percent = (accumulated["downloaded"] / total_size) * 100
        root.after(0, lambda: overall_percent_label.config(text=f"Overall: {percent:.2f}%"))

    def update_status(msg):
        root.after(0, lambda: status_label.config(text=msg))

    def update_file_progress(percent, downloaded, total):
        if total > 0:
            root.after(0, lambda: file_progress_bar.config(value=percent))
            root.after(
                0,
                lambda: file_percent_label.config(
                    text=f"File: {percent:.2f}% ({human_readable_size(downloaded)} / {human_readable_size(total)})"
                ),
            )
        else:
            root.after(0, lambda: file_progress_bar.config(value=0))
            root.after(0, lambda: file_percent_label.config(text="File: Idle"))

    for p in all_products:
        download_product(p, download_dir, update_progress, update_status, update_file_progress)

    root.after(0, lambda: messagebox.showinfo("Done", "✅ All downloads completed!"))


def start_download():
    download_dir = folder_var.get()
    granules = granules_var.get().split(",")
    start_date = start_var.get()
    end_date = end_var.get()
    product_level = level_var.get()
    cloud_cover = cloud_var.get()

    if not download_dir:
        messagebox.showerror("Error", "Please select a download folder.")
        return

    os.makedirs(download_dir, exist_ok=True)

    status_label.config(text="🔍 Starting search...")
    overall_progress_bar["value"] = 0
    file_progress_bar["value"] = 0
    file_percent_label.config(text="File: Idle")
    overall_percent_label.config(text="Overall: 0%")

    threading.Thread(
        target=worker,
        args=(download_dir, granules, start_date, end_date, product_level, cloud_cover),
        daemon=True,
    ).start()


# ---------------- GUI ----------------
root = tk.Tk()
root.title("Sentinel-2 Downloader")
root.geometry("700x600")

# Folder picker
tk.Label(root, text="Download Folder:").pack(anchor="w", padx=10, pady=5)
folder_var = tk.StringVar()
tk.Entry(root, textvariable=folder_var, width=60).pack(anchor="w", padx=10)
tk.Button(root, text="Browse", command=lambda: folder_var.set(filedialog.askdirectory())).pack(anchor="w", padx=10)

# Granules input
tk.Label(root, text="Granule IDs (comma separated):").pack(anchor="w", padx=10, pady=5)
granules_var = tk.StringVar(value="43SCS,32TMR,32TMS")
tk.Entry(root, textvariable=granules_var, width=50).pack(anchor="w", padx=10)

# Cloud cover
tk.Label(root, text="Max Cloud Cover (%):").pack(anchor="w", padx=10, pady=5)
cloud_var = tk.IntVar(value=20)
tk.Entry(root, textvariable=cloud_var, width=10).pack(anchor="w", padx=10)

# Dates
tk.Label(root, text="Start Date (YYYY-MM-DDTHH:MM:SS.000):").pack(anchor="w", padx=10, pady=5)
start_var = tk.StringVar(value="2023-05-01T00:00:00.000")
tk.Entry(root, textvariable=start_var, width=30).pack(anchor="w", padx=10)

tk.Label(root, text="End Date (YYYY-MM-DDTHH:MM:SS.999):").pack(anchor="w", padx=10, pady=5)
end_var = tk.StringVar(value="2023-05-31T23:59:59.999")
tk.Entry(root, textvariable=end_var, width=30).pack(anchor="w", padx=10)

# Product level dropdown
tk.Label(root, text="Product Level:").pack(anchor="w", padx=10, pady=5)
level_var = tk.StringVar(value="L1C")
ttk.Combobox(root, textvariable=level_var, values=["L1C", "L2A", "BOTH"]).pack(anchor="w", padx=10)

# Overall progress
tk.Label(root, text="Overall Progress:").pack(anchor="w", padx=10)
overall_progress_bar = ttk.Progressbar(root, length=600, maximum=100)
overall_progress_bar.pack(pady=5)
overall_percent_label = tk.Label(root, text="Overall: 0%")
overall_percent_label.pack()

# File progress
tk.Label(root, text="Current File Progress:").pack(anchor="w", padx=10)
file_progress_bar = ttk.Progressbar(root, length=600, maximum=100)
file_progress_bar.pack(pady=5)
file_percent_label = tk.Label(root, text="File: Idle")
file_percent_label.pack()

# Status label
status_label = tk.Label(root, text="Status: Idle", fg="blue")
status_label.pack(pady=10)

# Start button
tk.Button(root, text="Start Download", command=start_download, bg="green", fg="white").pack(pady=20)

root.mainloop()
