import random
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox

def generate_user_agent(device, os_choice, browser_choice, count):
    user_agents = []
    
    # Desktop Browsers
    desktop_browsers = {
        "Chrome": "Mozilla/5.0 ({os}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{chrome_version} Safari/537.36",
        "Firefox": "Mozilla/5.0 ({os}; rv:{firefox_version}) Gecko/20100101 Firefox/{firefox_version}",
        "Edge": "Mozilla/5.0 ({os}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{chrome_version} Safari/537.36 Edg/{edge_version}",
        "Safari": "Mozilla/5.0 (Macintosh; Intel Mac OS X {os_version}) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/{safari_version} Safari/605.1.15"
    }

    # Mobile Browsers
    mobile_browsers = {
        "Chrome": "Mozilla/5.0 (Linux; Android {android_version}; {device}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{chrome_version} Mobile Safari/537.36",
        "Safari": "Mozilla/5.0 (iPhone; CPU iPhone OS {ios_version} like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/{safari_version} Mobile/15E148 Safari/604.1"
    }

    for _ in range(count):
        if device == "Desktop":
            template = desktop_browsers[browser_choice]
            os = random.choice(["Windows NT 10.0; Win64; x64", "Macintosh; Intel Mac OS X 10_15_7", "X11; Linux x86_64"])
            ua = template.format(
                os=os,
                chrome_version=f"{(141.0.7390.43)} ",
                firefox_version=f"{random.randint(80, 110)}.0",
                edge_version=f"{random.randint(80, 110)}.0.{random.randint(4000, 5000)}",
                safari_version=f"{random.randint(14, 16)}.0"
            )
        elif device == "Mobile":
            template = mobile_browsers[browser_choice]
            if os_choice == "Android":
                ua = template.format(
                    android_version=random.choice(["10", "11", "12", "13"]),
                    device=random.choice(["Pixel 5", "Galaxy S21", "OnePlus 9", "Huawei P40"]),
                    chrome_version=f"{random.randint(80, 110)}.0.{random.randint(4000, 5000)}.{random.randint(50, 150)}"
                )
            elif os_choice == "iOS":
                ua = template.format(
                    ios_version=random.choice(["14_8", "15_0", "16_1"]),
                    safari_version=f"{random.randint(12, 16)}.0"
                )
        user_agents.append(ua)
    return user_agents

# GUI
def display_user_agents():
    try:
        count = int(entry_count.get())
        if count <= 0:
            raise ValueError
    except ValueError:
        messagebox.showerror("Invalid Input", "Please enter a valid positive number!")
        return
    
    device = device_choice.get()
    os_choice = os_dropdown.get()
    browser_choice = browser_dropdown.get()

    user_agents = generate_user_agent(device, os_choice, browser_choice, count)
    text_area.delete("1.0", tk.END)
    for i, ua in enumerate(user_agents, 1):
        text_area.insert(tk.END, f"{i}: {ua}\n")

def copy_to_clipboard():
    user_agents = text_area.get("1.0", tk.END).strip()
    if user_agents:
        root.clipboard_clear()
        root.clipboard_append(user_agents)
        root.update()
        messagebox.showinfo("Copied", "User-Agents copied to clipboard!")
    else:
        messagebox.showwarning("Empty", "No User-Agents to copy!")

# Main GUI
root = tk.Tk()
root.title("Advanced User-Agent Generator")
root.geometry("900x700")
root.config(bg="#282c34")

# Header
title_label = tk.Label(root, text="Advanced User-Agent Generator", font=("Helvetica", 18, "bold"), bg="#61afef", fg="white", pady=10)
title_label.pack(fill=tk.X)

# Input Frame
frame_input = tk.Frame(root, bg="#282c34", pady=20)
frame_input.pack()

# Device Choice
label_device = tk.Label(frame_input, text="Device:", font=("Helvetica", 14), bg="#282c34", fg="white")
label_device.grid(row=0, column=0, padx=10, pady=5, sticky="e")
device_choice = ttk.Combobox(frame_input, values=["Mobile", "Desktop"], state="readonly", font=("Helvetica", 14), width=12)
device_choice.grid(row=0, column=1, padx=10, pady=5)
device_choice.current(0)

# OS Dropdown
label_os = tk.Label(frame_input, text="OS:", font=("Helvetica", 14), bg="#282c34", fg="white")
label_os.grid(row=1, column=0, padx=10, pady=5, sticky="e")
os_dropdown = ttk.Combobox(frame_input, values=["Android", "iOS", "Windows", "Linux", "MacOS"], state="readonly", font=("Helvetica", 14), width=12)
os_dropdown.grid(row=1, column=1, padx=10, pady=5)
os_dropdown.current(0)

# Browser Dropdown
label_browser = tk.Label(frame_input, text="Browser:", font=("Helvetica", 14), bg="#282c34", fg="white")
label_browser.grid(row=2, column=0, padx=10, pady=5, sticky="e")
browser_dropdown = ttk.Combobox(frame_input, values=["Chrome", "Firefox", "Safari", "Edge"], state="readonly", font=("Helvetica", 14), width=12)
browser_dropdown.grid(row=2, column=1, padx=10, pady=5)
browser_dropdown.current(0)

# Count Entry
label_count = tk.Label(frame_input, text="Count:", font=("Helvetica", 14), bg="#282c34", fg="white")
label_count.grid(row=3, column=0, padx=10, pady=5, sticky="e")
entry_count = ttk.Entry(frame_input, font=("Helvetica", 14), width=10)
entry_count.grid(row=3, column=1, padx=10, pady=5)
entry_count.insert(0, "10")

# Buttons
button_generate = ttk.Button(frame_input, text="Generate", command=display_user_agents)
button_generate.grid(row=4, column=0, columnspan=2, pady=10)

button_copy = ttk.Button(frame_input, text="Copy to Clipboard", command=copy_to_clipboard)
button_copy.grid(row=4, column=2, pady=10)

# Output Area
text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, font=("Courier", 12), bg="#1e2127", fg="#dcdcdc", insertbackground="white", height=20)
text_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

# Run the App
root.mainloop()

#if you interested in seo just join to our group: #https://www.facebook.com/groups/seo.pro.tools/