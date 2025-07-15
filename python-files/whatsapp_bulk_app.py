import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
import pywhatkit
import pyautogui
import time

# Function to format phone numbers
def format_number(phone):
    phone = str(phone).strip()
    if not phone.startswith("+"):
        phone = "+91" + phone
    return phone

# Function to send messages
def send_messages():
    path = csv_path.get()
    if not path:
        messagebox.showerror("Error", "Please select a CSV file.")
        return

    # Try multiple encodings to handle Excel-saved files
    for encoding in ['utf-8', 'utf-8-sig', 'ISO-8859-1']:
        try:
            df = pd.read_csv(path, encoding=encoding)
            break
        except Exception:
            continue
    else:
        messagebox.showerror("Error", "Failed to read the CSV file. Try saving it as UTF-8.")
        return

    # Normalize column names
    df.columns = [col.strip().lower() for col in df.columns]
    
    if 'phone' not in df.columns or 'message' not in df.columns:
        messagebox.showerror("Error", f"CSV must have 'phone' and 'message' columns.\nFound: {df.columns.tolist()}")
        return

    # Format numbers
    df['phone'] = df['phone'].apply(format_number)

    for index, row in df.iterrows():
        phone = row['phone']
        original_msg = str(row['message'])

        # Create popup window to preview/edit message
        msg_window = tk.Toplevel()
        msg_window.title(f"Edit Message for {phone}")
        tk.Label(msg_window, text=f"Sending to: {phone}").pack(pady=5)
        
        msg_box = tk.Text(msg_window, width=60, height=6)
        msg_box.insert(tk.END, original_msg)
        msg_box.pack(padx=10)

        def send_this_message():
            edited_msg = msg_box.get("1.0", tk.END).strip()
            msg_window.destroy()
            try:
                pywhatkit.sendwhatmsg_instantly(phone, edited_msg, wait_time=10, tab_close=False)
                time.sleep(8)  # Wait for chat window to load
                pyautogui.press("enter")  # Press enter to send
                print(f"✅ Message sent to {phone}")
                time.sleep(1)
            except Exception as e:
                print(f"❌ Failed to send to {phone}: {e}")

        tk.Button(msg_window, text="Send Message", command=send_this_message, bg="green", fg="white").pack(pady=10)
        msg_window.wait_window()

    messagebox.showinfo("Done", "All messages have been sent!")

# Function to browse and select CSV
def browse_file():
    file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
    csv_path.set(file_path)

# Setup GUI
root = tk.Tk()
root.title("📤 WhatsApp Bulk Message Sender")
root.geometry("500x250")

csv_path = tk.StringVar()

tk.Label(root, text="📄 Select CSV with 'phone' & 'message' columns").pack(pady=15)
tk.Entry(root, textvariable=csv_path, width=60).pack()
tk.Button(root, text="Browse CSV", command=browse_file).pack(pady=10)
tk.Button(root, text="🚀 Send Messages", command=send_messages, bg="green", fg="white", height=2, width=20).pack(pady=20)

root.mainloop()
