import tkinter as tk
from tkinter import scrolledtext, messagebox
import shlex
import json

# pyperclip library ko import karne ki koshish karein
try:
    import pyperclip
    PYPERCLIP_AVAILABLE = True
except ImportError:
    PYPERCLIP_AVAILABLE = False

def convert_curl_to_python(curl_command: str) -> str:
    """
    Ek cURL command string ko Python requests code mein convert karta hai.
    (Yeh function pehle wale script jaisa hi hai)
    """
    try:
        # shlex ka upyog command ko shell ki tarah arugments me todne ke liye
        # Windows par single quote ki samasya se bachne ke liye posix=False karein
        args = shlex.split(curl_command, posix=False)

        if args[0].lower() != 'curl':
            raise ValueError("Yeh ek valid cURL command nahi hai. 'curl' se shuru karein.")

        # Core components initialize karein
        method = 'get'
        url = ''
        headers = {}
        data = None
        is_json = False

        # URL ko dhundhein (jo 'http' se shuru hota hai)
        for arg in args:
            # quotes ('') ko hata dein
            clean_arg = arg.strip("'\"")
            if clean_arg.startswith('http'):
                url = clean_arg
                break
        
        if not url:
            # Kabhi kabhi URL command ke aakhri me hota hai
            if args[-1].startswith('http'):
                 url = args[-1].strip("'\"")
            else:
                raise ValueError("Command mein URL nahi mila.")

        # Command ke arguments ko parse karein
        i = 1
        while i < len(args):
            arg = args[i]
            if arg in ('-X', '--request'):
                method = args[i+1].lower()
                i += 1
            elif arg in ('-H', '--header'):
                header_line = args[i+1].strip("'\"")
                header_key, header_value = header_line.split(':', 1)
                headers[header_key.strip()] = header_value.strip()
                i += 1
            elif arg in ('-d', '--data', '--data-raw', '--data-binary'):
                data = args[i+1].strip("'\"")
                i += 1
            
            i += 1

        # Agar 'Content-Type' header 'application/json' hai, to JSON data maniye
        for key in headers:
            if key.lower() == 'content-type' and 'application/json' in headers[key].lower():
                is_json = True
                break

        # Python code generate karein
        python_code = []
        python_code.append("import requests")
        if is_json and data:
            python_code.append("import json")
        python_code.append("")

        if headers:
            python_code.append(f"headers = {json.dumps(headers, indent=4)}")
            python_code.append("")

        if data:
            if is_json:
                try:
                    json_data = json.loads(data)
                    python_code.append(f"json_data = {json.dumps(json_data, indent=4)}")
                except json.JSONDecodeError:
                    python_code.append(f"data = {repr(data)}") # Agar JSON invalid hai to raw string
                    is_json = False
            else:
                 python_code.append(f"data = {repr(data)}")
            python_code.append("")

        # requests call ko build karein
        request_line = f'response = requests.{method}("{url}"'
        if headers:
            request_line += ', headers=headers'
        if data:
            if is_json:
                request_line += ', json=json_data'
            else:
                request_line += ', data=data'
        
        request_line += ')'
        python_code.append(request_line)
        python_code.append("")
        python_code.append("# Response ko check aur print karein")
        python_code.append("print(f'Status Code: {response.status_code}')")
        python_code.append("print('Response Body:')")
        python_code.append("print(response.text)")

        return "\n".join(python_code)

    except Exception as e:
        return f"# Error: Command ko parse nahi kar paye.\n# Kripya valid cURL command dein.\n\n# Detail: {e}"

# --- GUI Functions ---

def handle_convert():
    """Convert button dabane par yeh function chalta hai."""
    curl_command = input_text.get("1.0", tk.END).strip()
    if not curl_command:
        messagebox.showwarning("Input Khali Hai", "Kripya cURL command paste karein.")
        return
        
    python_code = convert_curl_to_python(curl_command)
    
    # Output box ko clear karke naya code daalein
    output_text.config(state=tk.NORMAL) # Pehle writable banayein
    output_text.delete("1.0", tk.END)
    output_text.insert(tk.END, python_code)
    output_text.config(state=tk.DISABLED) # Phir se read-only kar dein

def handle_copy():
    """Copy button dabane par yeh function chalta hai."""
    if not PYPERCLIP_AVAILABLE:
        messagebox.showerror("Error", "Code copy karne ke liye 'pyperclip' library zaroori hai.\nInstall karein: pip install pyperclip")
        return
        
    code_to_copy = output_text.get("1.0", tk.END).strip()
    if code_to_copy and not code_to_copy.startswith("# Error:"):
        pyperclip.copy(code_to_copy)
        messagebox.showinfo("Success", "Python code clipboard par copy ho gaya hai!")
    elif not code_to_copy:
        messagebox.showwarning("Kuch Nahi Hai", "Copy karne ke liye pehle code generate karein.")
    else:
        messagebox.showerror("Error", "Error ko copy nahi kiya ja sakta.")

# --- GUI Setup ---

# Main window banayein
root = tk.Tk()
root.title("cURL to Python Requests Converter")
root.geometry("800x650") # Window ka size set karein

main_frame = tk.Frame(root, padx=10, pady=10)
main_frame.pack(fill=tk.BOTH, expand=True)

# Input section
input_label = tk.Label(main_frame, text="cURL Command Yahan Paste Karein:", font=("Helvetica", 12, "bold"))
input_label.pack(anchor="w", pady=(0, 5))

input_text = scrolledtext.ScrolledText(main_frame, height=10, wrap=tk.WORD, font=("Consolas", 10))
input_text.pack(fill=tk.BOTH, expand=True)

# Buttons
button_frame = tk.Frame(main_frame, pady=10)
button_frame.pack(fill=tk.X)

convert_button = tk.Button(button_frame, text="Convert Karein", command=handle_convert, font=("Helvetica", 11, "bold"), bg="#4CAF50", fg="white")
convert_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 5))

copy_button = tk.Button(button_frame, text="Code Copy Karein", command=handle_copy, font=("Helvetica", 11, "bold"), bg="#008CBA", fg="white")
copy_button.pack(side=tk.RIGHT, expand=True, fill=tk.X, padx=(5, 0))

# Output section
output_label = tk.Label(main_frame, text="Generated Python Code:", font=("Helvetica", 12, "bold"))
output_label.pack(anchor="w", pady=(10, 5))

output_text = scrolledtext.ScrolledText(main_frame, height=20, wrap=tk.WORD, font=("Consolas", 10), state=tk.DISABLED)
output_text.pack(fill=tk.BOTH, expand=True)

# GUI ko run karein
root.mainloop()