mport tkinter as tk
from tkinter import messagebox
import requests
import os


favorites = []


discord_webhook_url = "https://discord.com/api/webhooks/1397548596173340763/Sv5fBnyBja77_V-TED7nyH__FwGCA9tir1WMl0dXYR7tO1_MjvrwJYg52dk6murECFwk"


def style_button(button):
    button.configure(bg="black", fg="white", borderwidth=0)

def ip_lookup():
    ip_address = ip_entry.get()
    url = f"https://ipinfo.io/{ip_address}/json"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        result_text.set(
            f"IP Address: {data.get('ip')}\n"
            f"Hostname: {data.get('hostname')}\n"
            f"Location: {data.get('city')}, {data.get('region')}, {data.get('country')}\n"
            f"Postal Code: {data.get('postal')}\n"
            f"Network: {data.get('network')}"  
        )
        result_label.config(fg="white")
    else:
        messagebox.showerror("Error", "Error retrieving information for the provided IP address.")

def ip_pinger():
    ip_address = ip_entry.get()
    response = os.system(f"ping -n 4 {ip_address}")  
    
    if response == 0:
        result_text.set(f"Ping to {ip_address} successful!")
        result_label.config(fg="white")
    else:
        result_text.set(f"Ping to {ip_address} failed.")
        result_label.config(fg="white")

def clear_info():
    ip_entry.delete(0, tk.END)
    result_text.set("")
    result_label.config(fg="black")

def add_to_favorites():
    ip_address = ip_entry.get()
    if ip_address not in favorites:
        favorites.append(ip_address)
        favorites_listbox.insert(tk.END, ip_address)

def remove_from_favorites():
    selected_ip = favorites_listbox.curselection()
    if selected_ip:
        index = selected_ip[0]
        favorites_listbox.delete(index)
        favorites.pop(index)

def send_feedback():
    feedback_message = feedback_entry.get()
    
    if feedback_message:
        try:
            response = requests.post(discord_webhook_url, json={"content": feedback_message})
            if response.status_code == 204:
                messagebox.showinfo("Feedback Sent", "Your feedback has been sent successfully!")
                feedback_entry.delete(0, tk.END) 
            else:
                messagebox.showerror("Error", "Failed to send feedback.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
    else:
        messagebox.showwarning("No Feedback", "Please enter your feedback before sending.")

app = tk.Tk()
app.title("EthicalGeek's IP Tool")
app.geometry("400x500")  


app.configure(bg="black")

header_label = tk.Label(app, text="Wock's IP Tool", bg="black", fg="white", font=("Helvetica", 18, "bold"))
header_label.pack(pady=(20, 10))

ip_label = tk.Label(app, text="Enter an IP address:", bg="black", fg="white", font=("Helvetica", 12))
ip_label.pack()

ip_entry = tk.Entry(app, font=("Helvetica", 12))
ip_entry.pack(pady=5)

lookup_button = tk.Button(app, text="Lookup", command=ip_lookup, font=("Helvetica", 12))
style_button(lookup_button)
lookup_button.pack(pady=5)

pinger_button = tk.Button(app, text="IP Pinger", command=ip_pinger, font=("Helvetica", 12))
style_button(pinger_button)
pinger_button.pack(pady=5)

clear_button = tk.Button(app, text="Clear", command=clear_info, font=("Helvetica", 12))
style_button(clear_button)
clear_button.pack(pady=5)

result_text = tk.StringVar()
result_label = tk.Label(app, textvariable=result_text, bg="black", fg="black", font=("Helvetica", 12, "italic"))
result_label.pack(pady=10)

line_top = tk.Label(app, text="──────────────────────────────────────", bg="black", fg="white")
line_top.pack()


favorites_label = tk.Label(app, text="Favorites:", bg="black", fg="white", font=("Helvetica", 12))
favorites_label.pack()

favorites_listbox = tk.Listbox(app, bg="black", fg="white", font=("Helvetica", 12), selectbackground="gray")
favorites_listbox.pack()

add_favorite_button = tk.Button(app, text="Add to Favorites", command=add_to_favorites, font=("Helvetica", 12))
style_button(add_favorite_button)
add_favorite_button.pack(pady=5)

remove_favorite_button = tk.Button(app, text="Remove from Favorites", command=remove_from_favorites, font=("Helvetica", 12))
style_button(remove_favorite_button)
remove_favorite_button.pack(pady=5)


feedback_label = tk.Label(app, text="Feedback:", bg="black", fg="white", font=("Helvetica", 12))
feedback_label.pack()

feedback_entry = tk.Entry(app, font=("Helvetica", 12))
feedback_entry.pack(pady=5)

send_feedback_button = tk.Button(app, text="Send Feedback", command=send_feedback, font=("Helvetica", 12))
style_button(send_feedback_button)
send_feedback_button.pack(pady=5)

app.mainloop()