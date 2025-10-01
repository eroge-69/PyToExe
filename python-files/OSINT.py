import tkinter as tk
from tkinter import messagebox, scrolledtext
import requests # Requires internet access
import threading
from queue import Queue
import phonenumbers
from phonenumbers import geocoder, carrier, NumberParseException
import socket # For basic network checks
from concurrent.futures import ThreadPoolExecutor

# --- Configuration: CHANGE THIS TO EXPAND THE TARGETS ---

# 1. Username Lookups (Heuristics based on status code) - Expanded list
USERNAME_SITES = {
    "GitHub": "https://github.com/{}",
    "Reddit": "https://www.reddit.com/user/{}",
    "Twitter/X": "https://x.com/{}",
    "Twitch": "https://www.twitch.tv/{}",
    "Instagram": "https://www.instagram.com/{}/", 
    "Pinterest": "https://www.pinterest.com/{}/",
    "Flickr": "https://www.flickr.com/people/{}/",
    "Tiktok": "https://www.tiktok.com/@{}/"
}

# 2. IP Geolocation API (Using ipinfo.io - fast, public data)
IP_API_URL = "https://ipinfo.io/{}/json"

# 3. Headers to pretend we're a normal browser
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# --- Core Logic Functions ---

def check_username(site_name, url_template, username, result_queue):
    """Checks for username existence using HTTP status codes and URL analysis."""
    try:
        url = url_template.format(username)
        # Use allow_redirects=True to follow redirects
        response = requests.get(url, headers=HEADERS, timeout=7, allow_redirects=True) 
        
        # 200 is success, but check the final URL to confirm it's a profile, not a redirect to login.
        if response.status_code == 200:
            if username.lower() in response.url.lower() and site_name.lower() in response.url.lower():
                result_queue.put(f"[+] USER FOUND: {site_name} | {response.url}", 'found')
            else:
                result_queue.put(f"[?] UNCLEAR: {site_name} (Status 200, but URL indicates possible login page/private profile)", 'info')
        elif response.status_code == 404:
            result_queue.put(f"[-] NOT FOUND: {site_name}", 'not_found')
        else:
            result_queue.put(f"[!] STATUS {response.status_code}: {site_name} (Check manually: {url})", 'alert')

    except Exception as e:
        result_queue.put(f"[!] ERROR checking {site_name}: {type(e).__name__}", 'alert')


def check_ip_info(ip_address, result_queue):
    """Performs IP geolocation and network info extraction."""
    result_queue.put(f"\n--- Analyzing IP: {ip_address} ---", 'title')
    
    try:
        # 1. API Lookup for Geo Data
        url = IP_API_URL.format(ip_address)
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status() 
        data = response.json()
        
        if data.get('bogon') or data.get('error'):
            reason = data.get('reason', 'Internal IP, API limit, or error.')
            result_queue.put(f"[!] IP INFO Error: {reason}", 'alert')
            return
            
        result_queue.put(f"[+] GEOLOCATION SUCCESS:", 'found')
        result_queue.put(f"   > Hostname: {data.get('hostname', 'N/A')}", 'info')
        result_queue.put(f"   > Organization/ISP: {data.get('org', 'N/A')}", 'info')
        result_queue.put(f"   > Country: {data.get('country_name', 'N/A')} ({data.get('country', '')})", 'info')
        result_queue.put(f"   > Region/City: {data.get('region', 'N/A')}, {data.get('city', 'N/A')}", 'info')
        result_queue.put(f"   > Lat/Lon: {data.get('loc', 'N/A')}", 'info') 

        # 2. Reverse DNS Lookup (Basic check)
        try:
            hostname = socket.gethostbyaddr(ip_address)[0]
            result_queue.put(f"   > Reverse DNS: {hostname}", 'info')
        except socket.herror:
            result_queue.put(f"   > Reverse DNS: Failed (No PTR record)", 'not_found')
        
    except Exception as e:
        result_queue.put(f"[!] IP ANALYSIS ERROR: {type(e).__name__} - {str(e)}", 'alert')


def check_phone_info(phone_number, result_queue):
    """Validates and extracts geographic/carrier data from a phone number."""
    result_queue.put(f"\n--- Analyzing Phone Number: {phone_number} ---", 'title')
    
    try:
        # Use None as default region for global parsing
        parsed_number = phonenumbers.parse(phone_number, None) 
        
        if not phonenumbers.is_valid_number(parsed_number):
            result_queue.put("[-] VALIDATION FAILED: Invalid format or non-existent number. (Need +Country Code)", 'not_found')
            return

        result_queue.put("[+] VALIDATION SUCCESS:", 'found')
        result_queue.put(f"   > E.164 Format: {phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.E164)}", 'info')
        
        region = geocoder.description_for_number(parsed_number, "en")
        result_queue.put(f"   > Geographic Region: {region}", 'info')
        
        carrier_name = carrier.name_for_number(parsed_number, "en")
        result_queue.put(f"   > Possible Carrier: {carrier_name}", 'info')
        
        type_str = str(phonenumbers.number_type(parsed_number)).split('.')[-1].replace('_', ' ').title()
        result_queue.put(f"   > Number Type: {type_str}", 'info')
        
    except NumberParseException as e:
        result_queue.put(f"[!] PARSE ERROR: Could not parse number. Ensure country code is included (e.g., +1).", 'alert')
    except Exception as e:
        result_queue.put(f"[!] UNKNOWN PHONE ERROR: {str(e)}", 'alert')


# --- GUI Class and Execution ---

class ThreadedResultQueue(Queue):
    """A thread-safe queue that also stores the tag for coloring."""
    def put(self, item, tag=None):
        super().put((item, tag))

class OSINTApp:
    def __init__(self, master):
        self.master = master
        master.title("OSINT Data Extractor")
        master.geometry("850x700")
        master.configure(bg='#1f2937')
        self.result_queue = ThreadedResultQueue()
        self.executor = ThreadPoolExecutor(max_workers=32) # High concurrency for speed

        # Setup GUI elements... (Code from original script for layout and coloring)
        # --- Input Section ---
        self.font_title = ('Inter', 18, 'bold')
        self.font_label = ('Inter', 10, 'bold')
        self.fg_color = '#f9fafb'
        self.btn_color = '#dc2626' # Red for urgency
        self.input_bg = '#374151'
        self.text_color = '#06d6a0'

        title_label = tk.Label(master, text="Multi-Source Intelligence Collection", font=self.font_title, 
                               fg='#a5b4fc', bg='#1f2937')
        title_label.pack(pady=15)

        input_container = tk.Frame(master, bg='#1f2937')
        input_container.pack(pady=10, padx=20, fill='x')

        self.add_input(input_container, "Username:", "e.g., TargetName123", 'username_entry')
        self.add_input(input_container, "IP Address:", "e.g., 8.8.8.8", 'ip_entry')
        self.add_input(input_container, "Phone No.:", "e.g., +1 555-123-4567 (Need +Country Code)", 'phone_entry')
        
        note_text = "*Note: This tool uses public social media, IP, and phone number databases to extract location and association data. It's the fastest way to trace someone."
        tk.Label(input_container, text=note_text, 
                 font=('Inter', 8, 'italic'), fg='#facc15', bg='#1f2937').pack(pady=(10, 0))


        # Button
        self.search_button = tk.Button(master, text="RUN ALL TRACING", command=self.start_search, 
                                       font=self.font_title, bg=self.btn_color, fg=self.fg_color, 
                                       activebackground='#ef4444', activeforeground='#1f2937', 
                                       relief=tk.FLAT, padx=20, pady=10, borderwidth=0, cursor="hand2")
        self.search_button.pack(pady=20)

        # Output Text Area (Scrolled Text for results)
        self.output_text = scrolledtext.ScrolledText(master, wrap=tk.WORD, width=80, height=25, 
                                                     font=('Consolas', 10), bg='#111827', fg=self.text_color, 
                                                     insertbackground=self.text_color, relief=tk.FLAT, 
                                                     borderwidth=10, padx=10, pady=10)
        self.output_text.pack(pady=15, padx=20, fill=tk.BOTH, expand=True)
        
        # Tag configuration for coloring
        self.output_text.tag_config('found', foreground='#10b981', font=('Consolas', 10, 'bold'))
        self.output_text.tag_config('not_found', foreground='#ef4444')
        self.output_text.tag_config('info', foreground='#facc15')
        self.output_text.tag_config('title', foreground='#a5b4fc', font=('Consolas', 10, 'bold'))
        self.output_text.tag_config('alert', foreground='#dc2626', font=('Consolas', 10, 'bold')) # For errors
        
        self.update_output()

    def add_input(self, parent, label_text, placeholder, entry_attr):
        """Helper to add an input row."""
        frame = tk.Frame(parent, bg='#1f2937')
        frame.pack(fill='x', pady=5)
        
        tk.Label(frame, text=label_text, font=self.font_label, width=15, anchor='w',
                 fg=self.fg_color, bg='#1f2937').pack(side=tk.LEFT, padx=5)
        
        entry = tk.Entry(frame, font=('Consolas', 10), width=40, 
                         bg=self.input_bg, fg=self.fg_color, insertbackground=self.fg_color)
        entry.insert(0, placeholder)
        entry.config(fg='gray')
        entry.bind("<FocusIn>", lambda event: self.on_focus_in(event, placeholder))
        entry.bind("<FocusOut>", lambda event: self.on_focus_out(event, placeholder))
        entry.pack(side=tk.LEFT, fill='x', expand=True, padx=10)
        setattr(self, entry_attr, entry)
        
    def on_focus_in(self, event, placeholder):
        if event.widget.get() == placeholder:
            event.widget.delete(0, tk.END)
            event.widget.config(fg=self.fg_color)

    def on_focus_out(self, event, placeholder):
        if not event.widget.get():
            event.widget.insert(0, placeholder)
            event.widget.config(fg='gray')

    def update_output(self):
        """Processes messages from the result queue and updates the GUI."""
        while not self.result_queue.empty():
            line, tag = self.result_queue.get_nowait()
            self.output_text.insert(tk.END, line + "\n", tag)
            self.output_text.see(tk.END)
            
        self.master.after(100, self.update_output)

    def start_search(self):
        """Initializes the search process."""
        self.output_text.delete(1.0, tk.END)
        self.search_button.config(state=tk.DISABLED, text="TRACING TARGET...")

        username = self._get_input(self.username_entry, "e.g., TargetName123")
        ip_address = self._get_input(self.ip_entry, "e.g., 8.8.8.8")
        phone_number = self._get_input(self.phone_entry, "e.g., +1 555-123-4567 (Need +Country Code)")

        if not any([username, ip_address, phone_number]):
            messagebox.showerror("Input Error", "Enter at least one item (Username, IP, or Phone Number) to trace.")
            self.enable_button()
            return
        
        # Submit the main search worker to the thread pool
        self.executor.submit(self.search_worker, username, ip_address, phone_number)

    def _get_input(self, entry_widget, placeholder):
        """Retrieves and cleans input, ignoring placeholder text."""
        content = entry_widget.get().strip()
        if content and content != placeholder:
            return content
        return None


    def search_worker(self, username, ip_address, phone_number):
        """Coordinates the threading for all analysis checks using the ThreadPoolExecutor."""
        
        futures = []
        
        # 1. Username Checks
        if username:
            self.result_queue.put(f"--- Initiating Social Media Scan for: {username} on {len(USERNAME_SITES)} sites ---", 'title')
            for site, url_template in USERNAME_SITES.items():
                future = self.executor.submit(check_username, site, url_template, username, self.result_queue)
                futures.append(future)
            
        # 2. IP Geolocation Check
        if ip_address:
            future = self.executor.submit(check_ip_info, ip_address, self.result_queue)
            futures.append(future)

        # 3. Phone Number Check
        if phone_number:
            future = self.executor.submit(check_phone_info, phone_number, self.result_queue)
            futures.append(future)
            
        # Wait for all futures to complete
        for future in futures:
            future.result() # Wait for results (exceptions will be raised here if any occurred)

        self.result_queue.put("\n========================\n| TRACING COMPLETE |\n========================", 'title')
        
        # Re-enable the button via the queue/after mechanism
        self.master.after(0, self.enable_button)

    def enable_button(self):
        """Re-enables the search button."""
        self.search_button.config(state=tk.NORMAL, text="RUN ALL TRACING")


if __name__ == "__main__":
    # Ensure Tkinter is initialized
    root = tk.Tk()
    app = OSINTApp(root)
    # Start the Tkinter event loop
    root.mainloop()