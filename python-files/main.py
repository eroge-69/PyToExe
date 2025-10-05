import os
import json
import customtkinter as ctk
import requests
from tkinter import messagebox
import threading
import time

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Configuration file to store API key
CONFIG_FILE = "liconfig.json"

# API configuration
API_BASE_URL = "https://leakinsight-api.p.rapidapi.com/general/"

class LeakInsightApp:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("LeakInsight API")
        self.root.geometry("900x730")
        self.root.resizable(False, False)
        self.root.configure(fg_color="#2b2b2b")

        self.api_key_var = ctk.StringVar()
        self.query_var = ctk.StringVar()
        self.search_type_var = ctk.StringVar(value="email")
        self.account_mode_var = ctk.StringVar(value="single")
        self.progress_value = ctk.DoubleVar(value=0)

        # Load saved API key if exists
        self.load_api_key()

        self.setup_ui()

        # Bind mode change to update UI
        self.account_mode_var.trace('w', self.on_mode_change)

    def load_api_key(self):
        """Load API key from configuration file"""
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    config = json.load(f)
                    self.api_key_var.set(config.get('api_key', ''))
            except Exception:
                pass

    def save_api_key(self):
        """Save API key to configuration file"""
        try:
            config = {'api_key': self.api_key_var.get()}
            with open(CONFIG_FILE, 'w') as f:
                json.dump(config, f)
            messagebox.showinfo("Success", "API Key saved successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save API key: {str(e)}")

    def on_mode_change(self, *args):
        """Handle account mode change to adjust query field size and progress bar visibility"""
        mode = self.account_mode_var.get()
        if mode == "single":
            self.query_text.configure(height=40)
            # Hide progress bar and label for single mode
            self.progress_bar.place_forget()
            self.progress_label.place_forget()
            # Adjust result text area height
            self.result_text.configure(height=580)
            self.copy_btn.place(x=300, y=650)
        else:
            self.query_text.configure(height=100)
            # Show progress bar and label for bulk mode
            self.progress_bar.place(x=20, y=665)
            self.progress_label.place(x=180, y=635)
            # Adjust result text area height to make room for progress
            self.result_text.configure(height=550)
            self.copy_btn.place(x=300, y=630)

    def setup_ui(self):
        """Setup the user interface"""
        # Left frame for controls
        left_frame = ctk.CTkFrame(
            self.root, 
            width=380, 
            height=690,
            fg_color="#1e1e1e", 
            corner_radius=10
        )
        left_frame.place(x=20, y=20)

        # Title
        title_label = ctk.CTkLabel(
            left_frame, 
            text="LeakInsight API",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#ffffff"
        )
        title_label.place(x=20, y=20)

        # Account Mode section
        mode_label = ctk.CTkLabel(
            left_frame,
            text="Account Mode",
            font=ctk.CTkFont(size=14),
            text_color="#ffffff"
        )
        mode_label.place(x=20, y=70)

        single_radio = ctk.CTkRadioButton(
            left_frame,
            text="Single Account",
            variable=self.account_mode_var,
            value="single",
            font=ctk.CTkFont(size=12),
            text_color="#ffffff",
            fg_color="#8b5cf6",
            hover_color="#7c3aed"
        )
        single_radio.place(x=40, y=100)

        bulk_radio = ctk.CTkRadioButton(
            left_frame,
            text="Bulk Accounts (one per line)",
            variable=self.account_mode_var,
            value="bulk",
            font=ctk.CTkFont(size=12),
            text_color="#ffffff",
            fg_color="#8b5cf6",
            hover_color="#7c3aed"
        )
        bulk_radio.place(x=40, y=130)

        # Request Type section
        type_label = ctk.CTkLabel(
            left_frame,
            text="Request Type",
            font=ctk.CTkFont(size=14),
            text_color="#ffffff"
        )
        type_label.place(x=20, y=170)

        # Radio buttons for search types - Column 1
        email_radio = ctk.CTkRadioButton(
            left_frame,
            text="Email",
            variable=self.search_type_var,
            value="email",
            font=ctk.CTkFont(size=11),
            text_color="#ffffff",
            fg_color="#8b5cf6",
            hover_color="#7c3aed"
        )
        email_radio.place(x=40, y=200)

        username_radio = ctk.CTkRadioButton(
            left_frame,
            text="Username",
            variable=self.search_type_var,
            value="username",
            font=ctk.CTkFont(size=11),
            text_color="#ffffff",
            fg_color="#8b5cf6",
            hover_color="#7c3aed"
        )
        username_radio.place(x=40, y=230)

        phone_radio = ctk.CTkRadioButton(
            left_frame,
            text="Phone",
            variable=self.search_type_var,
            value="phone",
            font=ctk.CTkFont(size=11),
            text_color="#ffffff",
            fg_color="#8b5cf6",
            hover_color="#7c3aed"
        )
        phone_radio.place(x=40, y=260)

        keyword_radio = ctk.CTkRadioButton(
            left_frame,
            text="Keyword (Pro)",
            variable=self.search_type_var,
            value="keyword",
            font=ctk.CTkFont(size=11),
            text_color="#ffffff",
            fg_color="#8b5cf6",
            hover_color="#7c3aed"
        )
        keyword_radio.place(x=40, y=290)

        # Radio buttons for search types - Column 2
        domain_radio = ctk.CTkRadioButton(
            left_frame,
            text="Domain (Ultra)",
            variable=self.search_type_var,
            value="domain",
            font=ctk.CTkFont(size=11),
            text_color="#ffffff",
            fg_color="#8b5cf6",
            hover_color="#7c3aed"
        )
        domain_radio.place(x=190, y=200)

        hash_radio = ctk.CTkRadioButton(
            left_frame,
            text="Hash (Ultra)",
            variable=self.search_type_var,
            value="hash",
            font=ctk.CTkFont(size=11),
            text_color="#ffffff",
            fg_color="#8b5cf6",
            hover_color="#7c3aed"
        )
        hash_radio.place(x=190, y=230)

        password_radio = ctk.CTkRadioButton(
            left_frame,
            text="Password (Mega)",
            variable=self.search_type_var,
            value="password",
            font=ctk.CTkFont(size=11),
            text_color="#ffffff",
            fg_color="#8b5cf6",
            hover_color="#7c3aed"
        )
        password_radio.place(x=190, y=260)

        origin_radio = ctk.CTkRadioButton(
            left_frame,
            text="Origin (Mega)",
            variable=self.search_type_var,
            value="origin",
            font=ctk.CTkFont(size=11),
            text_color="#ffffff",
            fg_color="#8b5cf6",
            hover_color="#7c3aed"
        )
        origin_radio.place(x=190, y=290)

        phash_radio = ctk.CTkRadioButton(
            left_frame,
            text="PHash (Mega)",
            variable=self.search_type_var,
            value="phash",
            font=ctk.CTkFont(size=11),
            text_color="#ffffff",
            fg_color="#8b5cf6",
            hover_color="#7c3aed"
        )
        phash_radio.place(x=190, y=320)

        # API Key section
        api_key_label = ctk.CTkLabel(
            left_frame,
            text="API Key",
            font=ctk.CTkFont(size=14),
            text_color="#ffffff"
        )
        api_key_label.place(x=20, y=360)

        self.api_key_entry = ctk.CTkEntry(
            left_frame,
            textvariable=self.api_key_var,
            width=300,
            height=40,
            font=ctk.CTkFont(size=12),
            fg_color="#2b2b2b",
            border_color="#3b3b3b",
            show="•"
        )
        self.api_key_entry.place(x=20, y=390)

        # Toggle button to show/hide API key
        self.show_key_btn = ctk.CTkButton(
            left_frame,
            text="👁",
            width=30,
            height=30,
            font=ctk.CTkFont(size=16),
            fg_color="transparent",
            hover_color="#3b3b3b",
            command=self.toggle_api_key
        )
        self.show_key_btn.place(x=325, y=395)

        # Save API key button
        save_key_btn = ctk.CTkButton(
            left_frame,
            text="Save Key",
            width=120,
            height=30,
            font=ctk.CTkFont(size=12),
            fg_color="#22d3ee",
            hover_color="#06b6d4",
            text_color="#000000",
            corner_radius=8,
            command=self.save_api_key
        )
        save_key_btn.place(x=235, y=440)

        # Search Query section
        query_label = ctk.CTkLabel(
            left_frame,
            text="Search Query",
            font=ctk.CTkFont(size=14),
            text_color="#ffffff"
        )
        query_label.place(x=20, y=490)

        self.query_text = ctk.CTkTextbox(
            left_frame,
            width=340,
            height=40,  # Starts small for single account
            font=ctk.CTkFont(size=12),
            fg_color="#2b2b2b",
            border_color="#3b3b3b"
        )
        self.query_text.place(x=20, y=520)

        # Run scan button
        self.scan_btn = ctk.CTkButton(
            left_frame,
            text="RUN SCAN",
            width=340,
            height=50,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color="#22d3ee",
            hover_color="#06b6d4",
            text_color="#000000",
            corner_radius=8,
            command=self.run_scan
        )
        self.scan_btn.place(x=20, y=620)

        # Right frame for results
        right_frame = ctk.CTkFrame(
            self.root,
            width=460,
            height=690,
            fg_color="#1e1e1e",
            corner_radius=10
        )
        right_frame.place(x=420, y=20)

        # Results title
        result_label = ctk.CTkLabel(
            right_frame,
            text="Leak Results",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#ffffff"
        )
        result_label.place(x=20, y=20)

        # Results text area
        self.result_text = ctk.CTkTextbox(
            right_frame,
            width=420,
            height=580,  # Adjusted height
            font=ctk.CTkFont(size=11, family="Courier"),
            fg_color="#2b2b2b",
            border_color="#3b3b3b"
        )
        self.result_text.place(x=20, y=60)

        # Copy results button
        self.copy_btn = ctk.CTkButton(
            right_frame,
            text="📋 Copy Results",
            width=140,
            height=32,
            font=ctk.CTkFont(size=12),
            fg_color="#22d3ee",
            hover_color="#06b6d4",
            text_color="#000000",
            corner_radius=8,
            command=self.copy_results
        )
        self.copy_btn.place(x=300, y=650)

        # Progress label (hidden by default for single mode)
        self.progress_label = ctk.CTkLabel(
            right_frame,
            text="Ready",
            font=ctk.CTkFont(size=11),
            text_color="#888888"
        )

        # Progress bar (hidden by default for single mode)
        self.progress_bar = ctk.CTkProgressBar(
            right_frame,
            width=260,  # Reduced width to give space for button
            height=18,
            fg_color="#141414",
            progress_color="#22d3ee",
            corner_radius=6,
            variable=self.progress_value
        )

    def toggle_api_key(self):
        """Toggle API key visibility"""
        if self.api_key_entry.cget("show") == "•":
            self.api_key_entry.configure(show="")
        else:
            self.api_key_entry.configure(show="•")

    def run_scan(self):
        """Start the scanning process"""
        api_key = self.api_key_var.get().strip()
        query = self.query_text.get("1.0", "end").strip()
        search_type = self.search_type_var.get()
        account_mode = self.account_mode_var.get()

        if not api_key:
            messagebox.showerror("Error", "Please enter your API Key")
            return

        if not query:
            messagebox.showerror("Error", "Please enter a search query")
            return

        # Clear previous results
        self.result_text.delete("1.0", "end")
        self.result_text.insert("1.0", "Starting scan...\n\n")
        self.scan_btn.configure(state="disabled", text="SCANNING...")
        self.progress_value.set(0)

        # Show progress for bulk mode
        if account_mode == "bulk":
            self.progress_label.configure(text="Processing...")

        # Execute in separate thread
        thread = threading.Thread(
            target=self.perform_scan,
            args=(api_key, query, search_type, account_mode)
        )
        thread.daemon = True
        thread.start()

    def perform_scan(self, api_key, query, search_type, account_mode):
        """Perform the actual API scanning with rate limiting"""
        try:
            # Parse queries based on mode
            if account_mode == "single":
                queries = [query]
            else:
                queries = [q.strip() for q in query.split("\n") if q.strip()]

            total = len(queries)

            # Process each query with delay to avoid API saturation
            for idx, q in enumerate(queries, 1):
                # Update progress label for bulk mode
                if account_mode == "bulk":
                    self.root.after(0, self.progress_label.configure, 
                                   {"text": f"Processing {idx}/{total}..."})

                # Call API
                result = self.call_api(api_key, q, search_type)

                # Display result immediately as it comes
                self.display_single_result(q, result, idx, total)

                # Update progress bar for bulk mode
                if account_mode == "bulk":
                    self.root.after(0, self.progress_value.set, idx / total)

                # Wait 2 seconds before next request to avoid API saturation
                if idx < total:
                    time.sleep(2)

            # Update progress label for bulk mode
            if account_mode == "bulk":
                self.root.after(0, self.progress_label.configure, 
                               {"text": f"✅ Completed {total} queries"})

        except Exception as e:
            error_msg = f"\n\n❌ Error: {str(e)}\n"
            self.root.after(0, lambda: self.result_text.insert("end", error_msg))
            if account_mode == "bulk":
                self.root.after(0, self.progress_label.configure, {"text": "Error occurred"})
        finally:
            self.root.after(0, lambda: self.scan_btn.configure(state="normal", text="RUN SCAN"))
            if account_mode == "bulk":
                self.root.after(0, self.progress_value.set, 1)

    def call_api(self, api_key, query, search_type):
        """Make API request to LeakInsight API"""
        headers = {
            "x-rapidapi-key": api_key,
            "x-rapidapi-host": "leakinsight-api.p.rapidapi.com"
        }

        params = {
            "query": query,
            "type": search_type
        }

        try:
            response = requests.get(API_BASE_URL, headers=headers, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": f"Request failed: {str(e)}"}
        except json.JSONDecodeError:
            return {"error": f"Invalid JSON response: {response.text}"}

    def display_single_result(self, query, result, idx, total):
        """Display a single result immediately as it arrives"""
        output = ""

        output += f"{'='*60}\n"
        output += f"Query {idx}/{total}: {query}\n"
        output += f"{'='*60}\n\n"

        if "error" in result:
            output += f"❌ Error: {result['error']}\n\n"
        elif result.get("success") and result.get("results"):
            total_results = len(result["results"])
            output += f"🔴 Found {total_results} leak(s)\n\n"

            for leak_idx, leak in enumerate(result["results"], 1):
                output += f"[Leak #{leak_idx}]\n"
                output += f"  Email: {leak.get('email_address', 'N/A')}\n"
                output += f"  Username: {leak.get('user_name', 'N/A')}\n"
                output += f"  Password: {leak.get('password', 'N/A')}\n"

                if "source" in leak:
                    source = leak["source"]
                    output += f"  Source:\n"
                    output += f"    - Name: {source.get('name', 'N/A')}\n"
                    output += f"    - Breach Date: {source.get('breach_date', 'N/A')}\n"
                    output += f"    - Unverified: {source.get('unverified', 'N/A')}\n"
                    output += f"    - Passwordless: {source.get('passwordless', 'N/A')}\n"
                    output += f"    - Compilation: {source.get('compilation', 'N/A')}\n"

                output += "\n"
        else:
            output += "✅ No leaks found\n\n"

        # Insert result at the end and auto-scroll
        self.root.after(0, lambda: self.result_text.insert("end", output))
        self.root.after(0, lambda: self.result_text.see("end"))

    def copy_results(self):
        """Copy all results to clipboard"""
        self.root.clipboard_clear()
        text = self.result_text.get("1.0", "end").strip()
        if text:
            self.root.clipboard_append(text)
            messagebox.showinfo("Copied", "Results copied to clipboard!")
        else:
            messagebox.showwarning("Warning", "No results to copy")

    def run(self):
        """Start the application"""
        self.root.mainloop()

if __name__ == "__main__":
    app = LeakInsightApp()
    app.run()
