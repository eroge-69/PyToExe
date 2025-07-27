import requests
import base64
import pandas as pd
import time
import threading
import os
import json
import re  # Import re for regular expressions
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
from bs4 import BeautifulSoup

class PwCTheme:
    BG_COLOR = "#F3F3F3"
    CONTAINER_COLOR = "#FFFFFF"
    PRIMARY_COLOR = "#E0301E"
    SUB_HEADER_COLOR = "#D04A02"
    BUTTON_BG = "#a1a8b3"
    BUTTON_FG = "#000000"  # Change text color to black
    BUTTON_BORDER_COLOR = "#B0B0B0"
    DIVIDER_COLOR = "#FFFFFF"
    TEXT_COLOR = "#252525"
    HOVER_COLOR = "#C52A1A"

    @staticmethod
    def apply_theme(root):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TFrame', background=PwCTheme.BG_COLOR)
        style.configure('Container.TFrame', background=PwCTheme.CONTAINER_COLOR)
        style.configure('TLabel', background=PwCTheme.BG_COLOR, foreground=PwCTheme.TEXT_COLOR)
        style.configure('SubHeader.TLabel', foreground=PwCTheme.SUB_HEADER_COLOR, font=('Segoe UI', 11, 'bold'))
        style.configure('TButton',
                        background=PwCTheme.BUTTON_BG,
                        foreground=PwCTheme.BUTTON_FG,
                        borderwidth=0,
                        relief="flat",
                        padding=6,
                        bordercolor=PwCTheme.BUTTON_BORDER_COLOR,
                        focuscolor=PwCTheme.BUTTON_BORDER_COLOR,
                        highlightbackground=PwCTheme.BUTTON_BORDER_COLOR,
                        highlightcolor=PwCTheme.BUTTON_BORDER_COLOR,
                        highlightthickness=2)
        style.map('TButton',
                  background=[('active', PwCTheme.HOVER_COLOR), ('disabled', PwCTheme.BUTTON_BG)],
                  foreground=[('disabled', '#8C8C8C')])
        style.configure('TProgressbar',
                        thickness=15,
                        background=PwCTheme.PRIMARY_COLOR,
                        troughcolor=PwCTheme.BG_COLOR,
                        borderwidth=0)
        root.configure(bg=PwCTheme.BG_COLOR)
        return style

class QuickTaxLookupApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Tax Info Extractor - Tracuunnt")
        self.setup_ui()
        self.cancel_requested = False
        self.current_thread = None
        self.captcha_api_key = '337439d35b1cab249ca44ffe5e1940ca'  # Update with your key

    def setup_ui(self):
        self.style = PwCTheme.apply_theme(self.root)
        self.header_container = ttk.Frame(self.root, style='Container.TFrame')
        self.header_container.pack(fill="x", padx=15, pady=5)

        self.header_frame = ttk.Frame(self.header_container, style='Container.TFrame')
        self.header_frame.pack(fill="x", pady=(10, 10))
        logo_image = Image.open("pwc_logo.png").resize((50, 50), Image.LANCZOS)
        logo_photo = ImageTk.PhotoImage(logo_image)
        logo_label = tk.Label(self.header_frame, image=logo_photo, bg=PwCTheme.CONTAINER_COLOR)
        logo_label.image = logo_photo 
        logo_label.pack(side="left", padx=10)

        title_frame = tk.Frame(self.header_frame, bg=PwCTheme.CONTAINER_COLOR)
        title_frame.pack(side="left", padx=(10, 0))

        ttk.Label(title_frame, text="Tax Info Extractor - Tracuunnt", font=("Segoe UI", 20, "bold"), background=PwCTheme.CONTAINER_COLOR).pack(anchor="w")
        ttk.Label(title_frame, text="Quickly lookup company names and tax filing addresses with ease", font=("Segoe UI", 10), background=PwCTheme.CONTAINER_COLOR).pack(anchor="w")

        self.divider()
        self.create_file_selection()
        self.create_progress_ui()
        self.create_footer()

    def divider(self):
        divider = tk.Frame(self.root, height=4, bg=PwCTheme.DIVIDER_COLOR, relief="ridge")
        divider.pack(fill='x', padx=15, pady=5)

    def create_file_selection(self):
        self.file_frame = ttk.Frame(self.root)
        self.file_frame.pack(fill="x", padx=15, pady=(5, 15))
        ttk.Label(self.file_frame, text="SELECT EXCEL FILE", style='SubHeader.TLabel').pack(anchor="w", padx=15, pady=5)

        file_frame = ttk.Frame(self.file_frame)
        file_frame.pack(fill="x", padx=15)
        
        self.file_path = tk.StringVar()
        ttk.Entry(file_frame, textvariable=self.file_path, width=60).pack(side="left", fill="x", expand=True)
        ttk.Button(file_frame, text="Browse", command=self.browse_file).pack(side="left", padx=5)

        ttk.Label(self.file_frame, text="Supported formats: Excel (.xlsx)", font=("Segoe UI", 9)).pack(anchor="w", padx=15)

    def create_progress_ui(self):
        progress_frame = ttk.Frame(self.root)
        progress_frame.pack(fill="x", padx=15, pady=5)
        ttk.Label(progress_frame, text="LOOKUP PROGRESS", style='SubHeader.TLabel').pack(anchor="w", padx=15, pady=5)

        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill="x", side="left", expand=True, padx=15, pady=(5, 2))

        self.progress_percent = ttk.Label(progress_frame, text="0%", width=5, font=("Segoe UI", 9))
        self.progress_percent.pack(side="left", padx=(5, 15))

        self.status_var = tk.StringVar()
        self.status_var.set("Status:\nReady")
        ttk.Label(progress_frame, textvariable=self.status_var, font=("Segoe UI", 9)).pack(padx=15, pady=(0, 10))

        button_container = ttk.Frame(self.root, style='Container.TFrame')
        button_container.pack(fill="x", padx=15, pady=5)

        button_frame = ttk.Frame(button_container, style='Container.TFrame')
        button_frame.pack(fill="x", padx=15, pady=10)

        self.lookup_button = ttk.Button(button_frame, text="Start", command=self.start_lookup, width=15)
        self.cancel_button = ttk.Button(button_frame, text="Cancel", command=self.set_cancel_requested, state='disabled', width=15)

        self.lookup_button.pack(side="left", expand=True, padx=10, pady=(5, 5))
        self.cancel_button.pack(side="left", expand=True, padx=10, pady=(5, 5))

    def create_footer(self):
        footer_container = ttk.Frame(self.root, style='Container.TFrame')
        footer_container.pack(fill="x", side="bottom", pady=(1, 0))

        footer_frame = ttk.Frame(footer_container, style='Container.TFrame')
        footer_frame.pack(fill="x", pady=(5, 0))
        ttk.Label(footer_frame, text="© 2025 PWC VN TLS - Tax Tech Team - Tax Info Extractor - Tracuunnt", font=("Segoe UI", 9)).pack(anchor="w", padx=15, pady=(5, 0))

    def browse_file(self):
        filename = filedialog.askopenfilename(title='Select a file', filetypes=[('Excel files', '*.xlsx')])
        if filename:
            self.file_path.set(filename)

    def set_cancel_requested(self):
        self.cancel_requested = True

    def update_progress(self, value, current, total):
        self.progress_var.set(value)
        self.progress_percent.config(text=f"{int(value)}%")
        self.status_var.set(f"Status:\nRunning... {current}/{total} TaxCodes")
        self.root.update_idletasks()

    def start_lookup(self):
        if not self.file_path.get():
            messagebox.showwarning("No File Selected", "Please select a valid Excel file.")
            return

        self.lookup_button.config(state='disabled')
        self.cancel_button.config(state='normal')
        self.status_var.set("Status:\nFetching Started...")

        self.current_thread = threading.Thread(target=self.lookup_file)
        self.cancel_requested = False
        self.current_thread.start()

    def lookup_file(self):
        df = pd.read_excel(self.file_path.get(), dtype=str)
        tax_codes = df.iloc[:, 0].dropna().tolist()

        session = requests.Session()
        output = []

        for i, tax_code in enumerate(tax_codes, start=1):
            if self.cancel_requested:
                print("Lookup canceled")
                break

            print(f"Processing {tax_code}...")  # Print the current tax code being processed
            info = self.get_company_info(session, tax_code)
            output.append(info)

            progress = (i / len(tax_codes)) * 100
            self.update_progress(progress, i, len(tax_codes))

            if i < len(tax_codes):
                time.sleep(2)  # Sleep for 2 seconds

        if not self.cancel_requested:
            output_file_path = self.save_output(output)
            self.show_complete_popup(output_file_path)

        self.lookup_button.config(state='normal')
        self.cancel_button.config(state='disabled')
        self.status_var.set("Status:\nReady")

    def get_company_info(self, session, tax_code):
        headers = {
            'User-Agent': ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                           '(KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36')
        }
        try:
            resp = session.get('https://tracuunnt.gdt.gov.vn/tcnnt/captcha.png?uid=', headers=headers)
            base64_image = base64.b64encode(resp.content).decode('utf-8')

            solved_captcha = self.solve_captcha_from_html(str(base64_image))

            if not solved_captcha:
                print(f"Captcha failed for {tax_code}")
                return {"Tax code": tax_code, "Company name": "Error", "Address": "Captcha failed"}

            data = {
                'cm': 'cm',
                'mst': tax_code,
                'captcha': solved_captcha
            }
            post_resp = session.post('https://tracuunnt.gdt.gov.vn/tcnnt/mstdn.jsp', data=data, headers=headers)
            soup = BeautifulSoup(post_resp.text, 'html.parser')
            scripts = soup.find_all("script")

            nnt_json_data = None
            for script in scripts:
                if script.string and 'var nntJson =' in script.string:
                    match = re.search(r'var nntJson\s*=\s*(\{.*\});', script.string, re.DOTALL)
                    if match:
                        json_str = match.group(1)
                        try:
                            nnt_json_data = json.loads(json_str)
                            print("Successfully parsed JSON")
                        except json.JSONDecodeError as e:
                            print("JSON parsing error:", e)
                    break

            if not nnt_json_data:
                raise ValueError("JSON data not available")

            company_info = {
                "Tax code": tax_code,
                "Company name": nnt_json_data['DATA'][0]['TEN_NNT'],
                "Address": nnt_json_data['DATA'][0]['DKT_DIA_CHI'][2]['DIA_CHI'] + ', ' +
                           nnt_json_data['DATA'][0]['DKT_DIA_CHI'][2]['PHUONG_XA'] + ', ' +
                           nnt_json_data['DATA'][0]['DKT_DIA_CHI'][2]['TINH_TP']
            }
            return company_info

        except Exception as e:
            print(f"Error for {tax_code}: {e}")
            return {"Tax code": tax_code, "Company name": "Error", "Address": str(e)}

    def solve_captcha_from_html(self, html):
        r = requests.post("http://2captcha.com/in.php", data={
            'key': self.captcha_api_key,
            'method': 'base64',
            'body': html,
            'json': 1
        }).json()

        if r.get("status") != 1:
            print("Failed to send captcha:", r)
            return None

        captcha_id = r["request"]
        print(f"Captcha ID: {captcha_id}")

        time.sleep(3)
        res = requests.get(f"http://2captcha.com/res.php?key={self.captcha_api_key}&action=get&id={captcha_id}&json=1").json()
        if res.get("status") == 1:
            print(f"Captcha solved: {res['request']}")
            return res["request"]
        print("Failed to solve captcha.")
        return None

    def save_output(self, output):
        input_file = self.file_path.get()
        input_file_name = os.path.basename(input_file)
        input_dir = os.path.dirname(input_file)
        output_file_name = f"Fetched_{os.path.splitext(input_file_name)[0]}.xlsx"
        output_file_path = os.path.join(input_dir, output_file_name)

        pd.DataFrame(output).to_excel(output_file_path, index=False)
        return output_file_path

    def show_complete_popup(self, output_file_path):
        def open_file():
            try:
                os.startfile(output_file_path)
            except AttributeError:
                subprocess.call(('xdg-open', output_file_path))
            except Exception as e:
                messagebox.showerror("Open File Error", f"Unable to open the file: {e}")

        output_file_name = os.path.basename(output_file_path)
        location = os.path.dirname(output_file_path)

        popup = tk.Toplevel(self.root)
        popup.title("Lookup Complete")
        
        width, height = 300, 170
        popup.geometry(f"{width}x{height}")
        popup.configure(bg="SystemButtonFace")

        self.root.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (width // 2)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (height // 2)
        popup.geometry(f"+{x}+{y}")

        message_text = f"The tax information has been successfully retrieved!\n\n"
        message_text += f"📄Output: {output_file_name}\n"
        message_text += f"📂Location: {location}\n"
        message_text += "*Note: Ensure all details are verified for accuracy.\n"

        message = tk.Message(
            popup,
            text=message_text,
            width=280,
            font=("Segoe UI", 9),
            justify="left"
        )
        message.grid(row=0, column=0, columnspan=2, padx=10, pady=(10, 5), sticky="w")

        style = ttk.Style()
        style.configure("TButton", font=("Segoe UI", 8))

        open_button = ttk.Button(popup, text="Open File", command=open_file, width=10, style="TButton")
        open_button.grid(row=1, column=0, padx=(20, 10), pady=(5, 10), sticky="w")

        ok_button = ttk.Button(popup, text="OK", command=popup.destroy, width=8, style="TButton")
        ok_button.grid(row=1, column=1, padx=(10, 20), pady=(5, 10), sticky="e")


def main():
    root = tk.Tk()
    app = QuickTaxLookupApp(root)
    root.geometry("800x450")
    root.minsize(800, 450)
    root.mainloop()

if __name__ == "__main__":
    main()