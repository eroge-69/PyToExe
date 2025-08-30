import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import requests
import base64
import json
import threading
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

APPSCRIPT_URL = "https://script.google.com/macros/s/AKfycbx7exruxsEFMMyzA_Y-GjH7jQtkCUW6PdrOjxTVpRsxi6pP4Yfc8mz_JyArY4hs_vFH/exec"
POST_PAYLOAD = {"type": "getPendingSubsidies"}


# ========== Utility Functions ==========

def fetch_pending_subsidies():
    try:
        resp = requests.post(APPSCRIPT_URL, json=POST_PAYLOAD, timeout=15)
        resp.raise_for_status()
        root = resp.json()
        raw_b64 = root.get("data", "")
        decoded = base64.b64decode(raw_b64).decode("utf-8")


        return decoded
    except Exception as e:
        return f"Error: {str(e)}"


def add_zeros(input_string: str) -> str:
    if len(input_string) >= 2:
        return input_string[:2] + '000000' + input_string[2:]
    return input_string


def extract_table_data_as_json(driver):
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.ID, "pt1:r1:0:t1::ch::t"))
    )

    table_header = driver.find_element(By.ID, "pt1:r1:0:t1::ch::t")
    th_elements = table_header.find_elements(By.TAG_NAME, "th")
    raw_headers = [th.text.strip() for th in th_elements]
    headers = [h for h in raw_headers if h and h.upper() != "SELECT"]

    tbody = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.ID, "pt1:r1:0:t1::db"))
    )

    rows = tbody.find_elements(By.TAG_NAME, "tr")
    json_data = []

    for row in rows:
        cells = row.find_elements(By.TAG_NAME, "td")
        values = [cell.text.strip() for cell in cells]
        row_dict = dict(zip(headers, values[:len(headers)]))
        json_data.append(row_dict)

    return json.dumps(json_data, indent=2)


def automate_browser(headless=False, consumer_id="7088298982"):
    chrome_options = Options()
    if headless:
        chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")

    driver = webdriver.Chrome(options=chrome_options)
    result = {"consumer_id": consumer_id, "success": False}

    try:
        driver.get("https://cx.indianoil.in/EPICIOCL/faces/GrievanceMainPage.jspx")

        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "pt1:r1:0:cil2::icon"))
        ).click()
        time.sleep(.4)

        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "pt1:r1:0:i1:6:l1111::text"))
        ).click()
        time.sleep(.4)

        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "pt1:r1:0:i2:0:l1311::text"))
        ).click()
        time.sleep(.4)

        consumer_No = add_zeros(consumer_id)
        chunks = [consumer_No[i:i + 4] for i in range(0, len(consumer_No), 4)]
        con1, con2, con3, con4 = chunks

        for idx, val in enumerate((con1, con2, con3, con4), start=1):
            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, f"pt1:r1:0:it{idx}::content"))
            ).send_keys(val)

        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "pt1:r1:0:b11112"))
        ).click()

        json_response = extract_table_data_as_json(driver)
        result["subsidy_b64"] = base64.b64encode(json_response.encode()).decode()
        result["success"] = True

        fname = driver.find_element(By.ID, "pt1:r1:0:it7::content").get_attribute("value")
        lname = driver.find_element(By.ID, "pt1:r1:0:it21::content").get_attribute("value")
        result["user_name"] = f"{fname} {lname}"

    except Exception as e:
        print(str(e))
        result["error"] = str(e)
    finally:
        driver.quit()

    return result


# ========== GUI Application ==========

class SubsidyCheckerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("LPG Subsidy Checker")
        self.root.geometry("1000x600")
        self.root.resizable(True, True)
        self.setup_style()
        self.create_widgets()
        self.pending_data = []
        self.results = []
        self.running = False
        self.current_index = 0

    def setup_style(self):
        style = ttk.Style()
        style.theme_use('clam')

        # Configure colors
        bg_color = "#2d2d2d"
        fg_color = "#e6e6e6"
        accent_color = "#3498db"
        header_color = "#1a1a1a"
        tree_bg = "#3d3d3d"
        tree_selected = "#4a6984"

        style.configure('.', background=bg_color, foreground=fg_color, font=('Segoe UI', 10))
        style.configure('TFrame', background=bg_color)
        style.configure('TButton', background=accent_color, foreground=fg_color,
                        borderwidth=1, focusthickness=3, focuscolor='none')
        style.map('TButton', background=[('active', '#2980b9')])
        style.configure('Header.TLabel', background=header_color, foreground='white',
                        font=('Segoe UI', 14, 'bold'), padding=10)
        style.configure('TCheckbutton', background=bg_color)
        style.configure('Treeview', background=tree_bg, fieldbackground=tree_bg,
                        foreground=fg_color, rowheight=25)
        style.configure('Treeview.Heading', background=header_color,
                        foreground='white', font=('Segoe UI', 10, 'bold'))
        style.map('Treeview', background=[('selected', tree_selected)])
        style.configure('TProgressbar', troughcolor=bg_color, background=accent_color)

    def create_widgets(self):
        # Header
        header_frame = ttk.Frame(self.root)
        header_frame.pack(fill=tk.X)
        ttk.Label(header_frame, text="LPG Subsidy Checker",
                  style='Header.TLabel').pack(fill=tk.X)

        # Control Panel
        control_frame = ttk.Frame(self.root, padding=(10, 10))
        control_frame.pack(fill=tk.X, padx=10, pady=5)

        self.start_btn = ttk.Button(control_frame, text="Start Processing",
                                   command=self.start_processing)
        self.start_btn.pack(side=tk.LEFT, padx=5)

        self.refresh_btn = ttk.Button(control_frame, text="Refresh List",
                                      command=self.refresh_list)
        self.refresh_btn.pack(side=tk.LEFT, padx=5)

        self.invisible_var = tk.BooleanVar()
        self.invisible_chk = ttk.Checkbutton(control_frame, text="Invisible Mode",
                                             variable=self.invisible_var)
        self.invisible_chk.pack(side=tk.LEFT, padx=20)

        # Progress Bar
        self.progress_var = tk.DoubleVar()
        progress_frame = ttk.Frame(self.root, padding=(10, 0))
        progress_frame.pack(fill=tk.X, padx=10, pady=5)
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var,
                                           mode='determinate')
        self.progress_bar.pack(fill=tk.X)

        # Treeview
        tree_frame = ttk.Frame(self.root, padding=(10, 0))
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        columns = ("user_id", "user_name", "time", "status")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings', selectmode='browse')

        # Configure columns
        self.tree.heading("user_id", text="User ID", anchor=tk.W)
        self.tree.heading("user_name", text="User Name", anchor=tk.W)
        self.tree.heading("time", text="Time", anchor=tk.W)
        self.tree.heading("status", text="Status", anchor=tk.CENTER)

        self.tree.column("user_id", width=150, anchor=tk.W)
        self.tree.column("user_name", width=200, anchor=tk.W)
        self.tree.column("time", width=200, anchor=tk.W)
        self.tree.column("status", width=100, anchor=tk.CENTER)

        # Add scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(fill=tk.BOTH, expand=True)

        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = ttk.Label(self.root, textvariable=self.status_var,
                               relief=tk.SUNKEN, anchor=tk.W, padding=(10, 5))
        status_bar.pack(fill=tk.X, side=tk.BOTTOM)

    def refresh_list(self):
        self.status_var.set("Fetching pending subsidies...")
        self.root.update()

        try:
            response = fetch_pending_subsidies()
            if response.startswith("Error:"):
                messagebox.showerror("Error", response)
                return

            self.pending_data = json.loads(response)
            self.update_treeview()
            self.status_var.set(f"Loaded {len(self.pending_data)} records")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load data: {str(e)}")
            self.status_var.set("Error loading data")

    def update_treeview(self):
        self.tree.delete(*self.tree.get_children())
        for item in self.pending_data:
            status = "Pending" if not item.get("processed", False) else "Completed"
            self.tree.insert("", tk.END, values=(
                item["user_id"],
                item["user_name"],
                item["time"],
                status
            ))

    def start_processing(self):
        if not self.pending_data:
            messagebox.showwarning("Warning", "No records to process. Please refresh the list first.")
            return

        if self.running:
            messagebox.showinfo("Info", "Processing is already running")
            return

        self.running = True
        self.results = []
        self.current_index = 0
        self.progress_var.set(0)
        self.start_btn.config(state=tk.DISABLED)
        self.refresh_btn.config(state=tk.DISABLED)

        threading.Thread(target=self.process_records, daemon=True).start()

    def process_records(self):
        total = len(self.pending_data)
        headless = self.invisible_var.get()

        for idx, item in enumerate(self.pending_data):
            if not self.running:
                break

            self.current_index = idx
            self.status_var.set(f"Processing {idx+1}/{total}: {item['user_id']}")
            self.progress_var.set((idx / total) * 100)
            self.update_tree_item(idx, "Processing")

            result = automate_browser(headless=headless, consumer_id=item["user_id"])

            if result["success"]:
                self.results.append({
                    "consumer_id": result["consumer_id"],
                    "user_name": result.get("user_name", ""),
                    "subsidy_b64": result["subsidy_b64"]
                })
                self.pending_data[idx]["processed"] = True
                self.update_tree_item(idx, "Completed")
            else:
                self.update_tree_item(idx, f"Failed: {result.get('error', 'Unknown error')}")
                print(f"Failed: {result.get('error', 'Unknown error')}")

            self.root.update()

        self.progress_var.set(100)
        self.running = False
        self.start_btn.config(state=tk.NORMAL)
        self.refresh_btn.config(state=tk.NORMAL)
        self.status_var.set(f"Processing complete. {len(self.results)}/{total} succeeded")

        self.post_subsidy_results(self.results)
        self.show_results()

    def update_tree_item(self, index, status):
        item = self.pending_data[index]
        item_id = self.tree.get_children()[index]
        self.tree.item(item_id, values=(
            item["user_id"],
            item["user_name"],
            item["time"],
            status
        ))

    def post_subsidy_results(self, result):
        url = APPSCRIPT_URL
        headers = {"Content-Type": "application/json"}
        payload = {"type": "addSubsidyResults", "results": result}

        try:
            response = requests.post(url, headers=headers, data=json.dumps(payload))
            response.raise_for_status()

            print("✅ POST successful:", response.status_code)
            print( response)
            try:
                print("Response:", response.json())  # Try to parse JSON
            except ValueError:
                print("⚠️ Response is not JSON. Raw response:")
                print(response.text)
        except requests.exceptions.RequestException as e:
            print("❌ POST failed:", e)


    def show_results(self):
        if not self.results:
            return

        result_window = tk.Toplevel(self.root)
        result_window.title("Processing Results")
        result_window.geometry("700x500")
        result_window.transient(self.root)
        result_window.grab_set()

        ttk.Label(result_window, text=f"Completed {len(self.results)} subsidies",
                  font=('Segoe UI', 12, 'bold')).pack(pady=10)

        frame = ttk.Frame(result_window)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        text_area = scrolledtext.ScrolledText(frame, wrap=tk.WORD, font=('Consolas', 10))
        text_area.pack(fill=tk.BOTH, expand=True)

        formatted_json = json.dumps(self.results, indent=2)
        text_area.insert(tk.INSERT, formatted_json)
        text_area.config(state=tk.DISABLED)

        ttk.Button(result_window, text="Close",
                  command=result_window.destroy).pack(pady=10)


# ========== Main Application ==========
if __name__ == "__main__":
    root = tk.Tk()
    app = SubsidyCheckerApp(root)
    root.mainloop()
