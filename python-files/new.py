import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import datetime
import pdfplumber
import re
from typing import Dict, List, Tuple, Optional, Set
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='return_viewer.log'
)

# Global variables
current_folder: str = ""
all_files: List[str] = []
masked_to_original: Dict[Tuple[str, str], List[Tuple[str, str]]] = {}
processing_files: bool = False

# Constants
VALID_DRAW_PREFIXES: Tuple[str, ...] = ("MSE", "GSE", "MPE", "DNE", "NJE", "HAE", "ADE", "SDE")
VALID_DEALER_PREFIXES: Tuple[str, ...] = ("A", "E", "S")
REFRESH_INTERVAL: int = 5000  # 5 seconds
MAX_WORKERS: int = 4  # For thread pool

# Load draw numbers from Today.txt
def load_today_draw_numbers() -> Set[str]:
    """Load today's draw numbers from Today.txt file.
    
    Returns:
        Set of draw numbers in uppercase.
    """
    draw_numbers: Set[str] = set()
    try:
        with open("Today.txt", "r") as file:
            for line in file:
                clean = line.strip().upper()
                if clean:
                    draw_numbers.add(clean)
        logging.info(f"Loaded {len(draw_numbers)} draw numbers from Today.txt")
    except FileNotFoundError:
        messagebox.showwarning("Missing File", "Today.txt not found in app folder.")
        logging.warning("Today.txt not found")
    except Exception as e:
        messagebox.showerror("Error", f"Error reading Today.txt:\n{e}")
        logging.error(f"Error reading Today.txt: {e}")
    return draw_numbers

today_draws: Set[str] = load_today_draw_numbers()

def browse_folder() -> None:
    """Open folder dialog and load PDF files from selected folder."""
    global current_folder, all_files, processing_files
    
    folder_selected = filedialog.askdirectory()
    if not folder_selected:
        return
    
    current_folder = folder_selected
    try:
        processing_files = True
        update_status("Scanning folder...")
        root.update()  # Force UI update
        
        files = [
            f for f in os.listdir(current_folder)
            if os.path.isfile(os.path.join(current_folder, f)) and f.lower().endswith(".pdf")
        ]
        files.sort()
        all_files = files
        apply_search_filter()
        update_status(f"Loaded {len(files)} files from {os.path.basename(current_folder)}")
        logging.info(f"Loaded {len(files)} files from {current_folder}")
    except Exception as e:
        messagebox.showerror("Error", f"Could not open folder:\n{e}")
        logging.error(f"Error opening folder {current_folder}: {e}")
        update_status("Error loading folder")
    finally:
        processing_files = False

def refresh_file_list() -> None:
    """Refresh the file list periodically."""
    if current_folder and not processing_files:
        try:
            files = [
                f for f in os.listdir(current_folder)
                if os.path.isfile(os.path.join(current_folder, f)) and f.lower().endswith(".pdf")
            ]
            files.sort()
            
            if files != all_files:  # Only update if files changed
                global all_files
                all_files = files
                apply_search_filter()
                logging.debug("Refreshed file list")
        except Exception as e:
            logging.error(f"Could not refresh folder: {e}")
    
    root.after(REFRESH_INTERVAL, refresh_file_list)

def get_pdf_total(filepath: str) -> str:
    """Extract total amount from PDF file.
    
    Args:
        filepath: Path to PDF file
        
    Returns:
        Extracted total as string, or "N/A" if not found
    """
    try:
        with pdfplumber.open(filepath) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    # Look for total in various formats
                    matches = re.finditer(
                        r"(?i)(?:total|amount)[:\s]*([$\s]*[\d,]+\.\d{2})", 
                        text
                    )
                    for match in matches:
                        amount = match.group(1).replace("$", "").replace(" ", "")
                        if amount:
                            return amount
    except Exception as e:
        logging.error(f"Error reading {filepath}: {e}")
    return "N/A"

def process_file(filename: str) -> Optional[Tuple[str, Tuple[str, str], str]]:
    """Process a single file to extract and format information.
    
    Args:
        filename: Name of the file to process
        
    Returns:
        Tuple of (display_text, (dealer_code, draw_no), dealer_code) or None if invalid
    """
    filename_no_ext = os.path.splitext(filename)[0]
    parts = filename_no_ext.strip().split()
    if len(parts) != 4:
        return None

    dealer_code, keyword, draw_no, file_date = parts

    # Validate components
    if not dealer_code.startswith(VALID_DEALER_PREFIXES):
        return None
    if keyword.lower() != "returns":
        return None
    if not draw_no.startswith(VALID_DRAW_PREFIXES):
        return None
    if draw_no.upper() not in today_draws:
        return None

    filepath = os.path.join(current_folder, filename)
    total = get_pdf_total(filepath)

    display_text = f"{dealer_code:<10}{draw_no:<12}{file_date:<12}Total: {total}"
    return display_text, (dealer_code.upper(), draw_no.upper()), dealer_code.upper()

def apply_search_filter() -> None:
    """Filter and display files based on search query."""
    query = search_var.get().strip().lower()
    filtered = [f for f in all_files if f.lower().startswith(query)] if query else all_files

    processed = []
    masked_to_original.clear()
    dealer_file_count = 0
    dealer_code_found = None

    # Use thread pool to process files faster
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = [executor.submit(process_file, f) for f in filtered]
        
        for future in as_completed(futures):
            result = future.result()
            if result:
                visible, key, dealer_code = result
                masked_to_original.setdefault(key, []).append((visible, f))
                processed.append(visible)
                
                if dealer_code and dealer_code.lower() == query:
                    dealer_file_count += 1
                    dealer_code_found = dealer_code

    processed.sort(key=lambda x: x[:10].strip())  # Sort by dealer code
    update_listbox(processed)

    if dealer_code_found:
        count_label.config(text=f"Dealer {dealer_code_found} - Total Files: {dealer_file_count}")
    else:
        count_label.config(text=f"Total Files: {len(processed)}" if processed else "No files found")

def update_listbox(display_list: List[str]) -> None:
    """Update the listbox with the provided items."""
    listbox.delete(0, tk.END)
    
    if not display_list:
        listbox.insert(tk.END, "No matching files found.")
        return

    for i, line in enumerate(display_list):
        listbox.insert(tk.END, line)
        # Alternate row colors for better readability
        listbox.itemconfig(i, bg='#f0f0f0' if i % 2 else 'white')

def on_double_click(event) -> None:
    """Handle double-click event on listbox items."""
    selection = listbox.curselection()
    if not selection:
        return

    clicked_line = listbox.get(selection[0]).strip()
    parts = clicked_line.split()
    if len(parts) < 3:
        return

    dealer_code = parts[0].upper()
    draw_no = parts[1].upper()
    key = (dealer_code, draw_no)

    if key in masked_to_original:
        original_files = [orig_file for _, orig_file in masked_to_original[key]]
        message = "\n".join(original_files)
        
        # Create a scrollable dialog for large lists
        dialog = tk.Toplevel(root)
        dialog.title(f"All files for {dealer_code} {draw_no}")
        
        frame = tk.Frame(dialog)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        scrollbar = tk.Scrollbar(frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        text = tk.Text(frame, wrap=tk.WORD, yscrollcommand=scrollbar.set)
        text.pack(fill=tk.BOTH, expand=True)
        text.insert(tk.END, message)
        text.config(state=tk.DISABLED)
        
        scrollbar.config(command=text.yview)
        
        close_btn = tk.Button(dialog, text="Close", command=dialog.destroy)
        close_btn.pack(pady=5)
    else:
        messagebox.showinfo("Not found", "No original files available for selection.")

def update_time() -> None:
    """Update the time display."""
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    time_label.config(text=now)
    root.after(1000, update_time)

def update_status(message: str) -> None:
    """Update the status bar."""
    status_var.set(message)
    root.update_idletasks()

def open_selected_file() -> None:
    """Open the selected PDF file with default application."""
    selection = listbox.curselection()
    if not selection:
        return

    clicked_line = listbox.get(selection[0]).strip()
    parts = clicked_line.split()
    if len(parts) < 3:
        return

    dealer_code = parts[0].upper()
    draw_no = parts[1].upper()
    key = (dealer_code, draw_no)

    if key in masked_to_original:
        original_files = [os.path.join(current_folder, orig_file) for _, orig_file in masked_to_original[key]]
        if original_files:
            try:
                os.startfile(original_files[0])  # Open first matching file
            except Exception as e:
                messagebox.showerror("Error", f"Could not open file:\n{e}")
                logging.error(f"Error opening file {original_files[0]}: {e}")

# ---------------------- GUI SETUP ----------------------
root = tk.Tk()
root.title("Return File Viewer")
root.geometry("1100x650")

# Configure styles
style = ttk.Style()
style.configure("TButton", padding=6, relief="flat", background="#ccc")
style.configure("TEntry", padding=5)
style.map("TButton", background=[("active", "#ddd")])

# Top frame
top_frame = ttk.Frame(root, padding="10")
top_frame.pack(fill=tk.X)

browse_btn = ttk.Button(top_frame, text="Browse Folder", command=browse_folder)
browse_btn.pack(side=tk.LEFT, padx=5)

search_label = ttk.Label(top_frame, text="Search (Dealer Code):")
search_label.pack(side=tk.RIGHT, padx=5)

search_var = tk.StringVar()
search_entry = ttk.Entry(top_frame, textvariable=search_var, width=20)
search_entry.pack(side=tk.RIGHT)
search_var.trace_add("write", lambda *args: apply_search_filter())

time_label = ttk.Label(top_frame, text="", foreground="gray")
time_label.pack(side=tk.RIGHT, padx=10)

# Listbox with scrollbar
list_frame = ttk.Frame(root)
list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

scrollbar = ttk.Scrollbar(list_frame)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

listbox = tk.Listbox(
    list_frame, 
    width=120, 
    height=25, 
    font=("Courier New", 12),
    yscrollcommand=scrollbar.set,
    selectbackground="#4a6984",
    selectforeground="#ffffff"
)
listbox.pack(fill=tk.BOTH, expand=True)
listbox.bind("<Double-Button-1>", on_double_click)
listbox.bind("<Return>", on_double_click)

scrollbar.config(command=listbox.yview)

# Bottom frame
bottom_frame = ttk.Frame(root, padding="10")
bottom_frame.pack(fill=tk.X)

count_label = ttk.Label(bottom_frame, text="", font=("Calibri", 12), foreground="blue")
count_label.pack(side=tk.LEFT)

open_btn = ttk.Button(bottom_frame, text="Open Selected File", command=open_selected_file)
open_btn.pack(side=tk.LEFT, padx=10)

status_var = tk.StringVar()
status_label = ttk.Label(bottom_frame, textvariable=status_var, foreground="gray")
status_label.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=10)

credit_label = ttk.Label(bottom_frame, text="Developed by Order Processing Unit", foreground="gray")
credit_label.pack(side=tk.RIGHT)

# Start timers
refresh_file_list()
update_time()
update_status("Ready")

# Set focus to search entry
search_entry.focus_set()

# Start app
root.mainloop()