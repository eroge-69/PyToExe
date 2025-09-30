import tkinter as tk
from tkinter import messagebox
import urllib.parse
import pyperclip # For easier clipboard access, though Tkinter's is also available.

# --- Global Configuration and Setup ---
# The primary window object (root) is initialized later in the main block

def decode_url():
    """
    Handles the decoding logic: retrieves input, replaces '&amp;',
    performs URL unescaping, and displays the result or an error.
    """
    input_url = input_text.get("1.0", tk.END).strip()

    if not input_url:
        messagebox.showwarning("Input Required", "Please enter a URL or string to decode.")
        return

    # Clear previous output
    output_text.delete("1.0", tk.END)

    try:
        # 1. Convert HTML entity for ampersand (&amp;) to actual ampersand (&)
        # This addresses the requirement for cleaning up HTML-copied URLs.
        unescaped_amp_url = input_url.replace('&amp;', '&')

        # 2. Perform standard URL percent-decoding (unescaping)
        # unquote() handles common URL encoding like %20, %2F, etc.
        decoded_url = urllib.parse.unquote(unescaped_amp_url)

        # Display the result
        output_text.insert(tk.END, decoded_url)
        messagebox.showinfo("Success", "Decoding successful! &amp; entities were converted to &.")

    except Exception as e:
        error_message = f"Decoding Error: The input string is malformed or an unexpected error occurred.\nDetails: {e}"
        output_text.insert(tk.END, error_message)
        messagebox.showerror("Error", error_message)

def copy_output():
    """
    Copies the content of the output text box to the system clipboard.
    """
    output = output_text.get("1.0", tk.END).strip()

    if not output:
        messagebox.showwarning("Copy Failed", "There is no output to copy.")
        return

    try:
        # Use Tkinter's native clipboard functionality
        root.clipboard_clear()
        root.clipboard_append(output)
        messagebox.showinfo("Copied", "Output copied to clipboard!")
    except Exception as e:
        # Fallback error handling if clipboard fails
        messagebox.showerror("Copy Error", f"Failed to copy to clipboard: {e}")


# --- GUI Construction ---

# 1. Initialize the main window
root = tk.Tk()
root.title("URL Decoder Tool (Python GUI)")
root.geometry("600x480")
root.minsize(400, 300)
root.configure(bg='#f0f0f0') # Match the PowerShell script's light gray background

# Configure grid weight to make columns and rows resize dynamically
root.grid_columnconfigure(0, weight=1)
root.grid_rowconfigure(2, weight=1) # Input text area row
root.grid_rowconfigure(5, weight=1) # Output text area row

# --- Input Section ---

# Input Label
tk.Label(root, 
         text="Input URL / String (Can contain '&amp;'):", 
         font=("Segoe UI", 10, "bold"), 
         bg='#f0f0f0', 
         fg='#333333').grid(row=0, column=0, sticky='w', padx=20, pady=(20, 5))

# Input Text Box
input_text = tk.Text(root, 
                     height=7, 
                     font=("Consolas", 9), 
                     wrap=tk.WORD,
                     borderwidth=2,
                     relief="groove")
input_text.grid(row=1, column=0, sticky='ew', padx=20, pady=(0, 10))

# --- Controls Section ---

# Decode Button
decode_button = tk.Button(root, 
                          text="Decode (Unescape)", 
                          command=decode_url, 
                          bg='#10b981', # Emerald 500
                          fg='white', 
                          font=("Segoe UI", 10, "bold"),
                          relief=tk.FLAT,
                          borderwidth=0,
                          activebackground='#059669',
                          cursor="hand2")
decode_button.grid(row=3, column=0, sticky='w', padx=20, pady=(5, 15))


# --- Output Section ---

# Output Label
tk.Label(root, 
         text="Output (Unescaped Ampersands and Percent Encoding):", 
         font=("Segoe UI", 10, "bold"), 
         bg='#f0f0f0', 
         fg='#333333').grid(row=4, column=0, sticky='w', padx=20, pady=(15, 5))

# Output Text Box
output_text = tk.Text(root, 
                      height=7, 
                      font=("Consolas", 9), 
                      wrap=tk.WORD,
                      state=tk.DISABLED, # Start as read-only
                      bg='#e5e7eb', # Gray 200
                      fg='#333333',
                      borderwidth=2,
                      relief="groove")

# Tkinter requires state to be set to NORMAL to insert text, and DISABLED to prevent editing
# We use a wrapper function for safer access.
def set_output_text(text):
    output_text.config(state=tk.NORMAL)
    output_text.delete("1.0", tk.END)
    output_text.insert(tk.END, text)
    output_text.config(state=tk.DISABLED)

# Re-link the decode function to use the safer text update method (although Tkinter handles it fine)
decode_button.config(command=decode_url)

output_text.grid(row=5, column=0, sticky='nsew', padx=20, pady=(0, 10))


# Copy Button
copy_button = tk.Button(root, 
                        text="Copy Output", 
                        command=copy_output, 
                        bg='#60a5fa', # Blue 400
                        fg='white', 
                        font=("Segoe UI", 10, "bold"),
                        relief=tk.FLAT,
                        borderwidth=0,
                        activebackground='#3b82f6',
                        cursor="hand2")
copy_button.grid(row=6, column=0, sticky='e', padx=20, pady=(5, 20))


# --- Main Loop ---

if __name__ == "__main__":
    # Start the application's main event loop
    root.mainloop()
