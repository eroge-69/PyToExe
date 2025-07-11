import tkinter as tk
from tkinter import messagebox, simpledialog
import requests

# Enter your actual Meraki API key and network ID
API_KEY = '88fb699ff0e98e3238c94700cad892ce19c305ba'
NETWORK_ID = 'L_676665844012432364'

headers = {
    'X-Cisco-Meraki-API-Key': API_KEY,
    'Content-Type': 'application/json'
}

def get_ssids():
    """Fetch existing SSIDs."""
    url = f"https://api.meraki.com/api/v1/networks/{NETWORK_ID}/wireless/ssids"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        messagebox.showerror("Error", f"Failed to fetch SSIDs: {response.text}")
        return []

def refresh_ssids_listbox(listbox):
    listbox.delete(0, tk.END)
    ssids = get_ssids()
    if ssids:
        for ssid in ssids:
            listbox.insert(tk.END, f"{ssid['number']}: {ssid['name']}")
    else:
        listbox.insert(tk.END, "No SSIDs found.")

def view_ssids():
    refresh_ssids_listbox(ssids_listbox)

def add_ssid():
    try:
        number = simpledialog.askinteger("Add SSID", "Enter SSID number (1-100):")
        if number is None:
            return
        name = simpledialog.askstring("Add SSID", "Enter SSID name:")
        if name is None:
            return
        security = simpledialog.askstring("Security Type", "Type (open / psk / enterprise):").lower()

        data = {
            "number": number,
            "name": name,
            "enabled": True
        }

        if security == 'psk':
            psk = simpledialog.askstring("PSK", "Enter WPA2 PSK:")
            if psk is None:
                return
            data["security"] = "psk"
            data["psk"] = psk
        elif security == 'enterprise':
            data["security"] = "WPA2 Enterprise"
        else:
            data["security"] = "open"

        vlan_str = simpledialog.askstring("VLAN", "Enter VLAN ID (leave blank if none):")
        if vlan_str:
            data["ap_tags_and_vlan"] = {"vlanId": int(vlan_str)}

        response = requests.post(
            f"https://api.meraki.com/api/v1/networks/{NETWORK_ID}/wireless/ssids",
            headers=headers,
            json=data
        )
        if response.status_code == 201:
            messagebox.showinfo("Success", "SSID added successfully.")
            view_ssids()
        else:
            messagebox.showerror("Error", f"Failed to add SSID: {response.text}")
    except Exception as e:
        messagebox.showerror("Error", str(e))

def update_ssid():
    try:
        selected = ssids_listbox.curselection()
        if not selected:
            messagebox.showwarning("Warning", "Please select an SSID to update.")
            return
        ssid_text = ssids_listbox.get(selected)
        ssid_number = int(ssid_text.split(':')[0])

        name = simpledialog.askstring("Update SSID", "Enter new SSID name (leave blank to skip):")
        security = simpledialog.askstring("Security Type", "Type (open / psk / enterprise), leave blank to skip:")

        updates = {}
        if name:
            updates["name"] = name
        if security:
            security = security.lower()
            if security == 'psk':
                psk = simpledialog.askstring("PSK", "Enter WPA2 PSK:")
                if psk is None:
                    return
                updates["security"] = "psk"
                updates["psk"] = psk
            elif security == 'enterprise':
                updates["security"] = "WPA2 Enterprise"
            elif security == 'open':
                updates["security"] = "open"
            else:
                messagebox.showwarning("Warning", "Invalid security type. Skipping security update.")

        vlan_str = simpledialog.askstring("VLAN", "Enter VLAN ID (leave blank to skip):")
        if vlan_str:
            updates["ap_tags_and_vlan"] = {"vlanId": int(vlan_str)}

        response = requests.put(
            f"https://api.meraki.com/api/v1/networks/{NETWORK_ID}/wireless/ssids/{ssid_number}",
            headers=headers,
            json=updates
        )
        if response.status_code == 200:
            messagebox.showinfo("Success", "SSID updated.")
            view_ssids()
        else:
            messagebox.showerror("Error", f"Failed to update: {response.text}")
    except Exception as e:
        messagebox.showerror("Error", str(e))
def delete_ssid():
    try:
        selected_idx = ssids_listbox.curselection()
        if not selected_idx:
            messagebox.showwarning("Warning", "Please select an SSID to delete.")
            return
        ssid_text = ssids_listbox.get(selected_idx)
        ssid_number = int(ssid_text.split(':')[0])
        confirm = messagebox.askyesno("Confirm Delete", f"Are you sure to delete SSID {ssid_number}?")
        if not confirm:
            return
        response = requests.delete(
            f"https://api.meraki.com/api/v1/networks/{NETWORK_ID}/wireless/ssids/{ssid_number}",
            headers=headers
        )
        if response.status_code == 204:
            messagebox.showinfo("Success", f"SSID {ssid_number} deleted.")
            view_ssids()
        else:
            messagebox.showerror("Error", f"Failed: {response.text}")
    except Exception as e:
        messagebox.showerror("Error", str(e))

def configure_captive_portal():
    try:
        selected_idx = ssids_listbox.curselection()
        if not selected_idx:
            messagebox.showwarning("Warning", "Select an SSID to configure.")
            return
        ssid_text = ssids_listbox.get(selected_idx)
        ssid_number = int(ssid_text.split(':')[0])
        splash_type = simpledialog.askstring("Splash Page Type", "Type (Click-through / Sign-on / External URL):").lower()

        data = {}
        if splash_type == 'click-through':
            data["splashPage"] = "Click-through"
        elif splash_type == 'sign-on':
            data["splashPage"] = "Sign-on"
        elif splash_type == 'external url':
            url = simpledialog.askstring("External URL", "Enter the URL:")
            data["splashPage"] = "URL"
            data["externalSplashUrl"] = url
        else:
            messagebox.showwarning("Warning", "Invalid splash page type.")
            return

        response = requests.put(
            f"https://api.meraki.com/api/v1/networks/{NETWORK_ID}/wireless/ssids/{ssid_number}",
            headers=headers,
            json=data
        )
        if response.status_code == 200:
            messagebox.showinfo("Success", "Captive portal configured.")
            view_ssids()
        else:
            messagebox.showerror("Error", f"Failed to configure: {response.text}")
    except Exception as e:
        messagebox.showerror("Error", str(e))

def configure_traffic_shaping():
    try:
        ssid_number = simpledialog.askinteger("Traffic Shaping", "Enter SSID number:")
        if ssid_number is None:
            return
        downstream = simpledialog.askinteger("Downstream (kbps)", "Enter download limit (0 for unlimited):")
        if downstream is None:
            return
        upstream = simpledialog.askinteger("Upstream (kbps)", "Enter upload limit (0 for unlimited):")
        if upstream is None:
            return
        data = {
            "trafficShaping": {
                "speedLimits": {
                    "downstream": downstream,
                    "upstream": upstream
                }
            }
        }
        response = requests.put(
            f"https://api.meraki.com/api/v1/networks/{NETWORK_ID}/wireless/ssids/{ssid_number}",
            headers=headers,
            json=data
        )
        if response.status_code == 200:
            messagebox.showinfo("Success", "Traffic shaping updated.")
        else:
            messagebox.showerror("Error", f"Failed: {response.text}")
    except Exception as e:
        messagebox.showerror("Error", str(e))

def configure_radio_settings():
    try:
        ssid_number = simpledialog.askinteger("Radio Settings", "Enter SSID number:")
        if ssid_number is None:
            return
        band = simpledialog.askstring("Band", "Band (2.4 / 5):").lower()
        if band not in ['2.4', '5']:
            messagebox.showwarning("Warning", "Band must be '2.4' or '5'.")
            return
        channel = simpledialog.askinteger("Channel", "Channel number:")
        if channel is None:
            return
        power = simpledialog.askinteger("Power", "Transmit power (1-100):")
        if power is None or not (1 <= power <= 100):
            messagebox.showwarning("Warning", "Power must be between 1 and 100.")
            return
        data = {
            "radioSettings": {
                "band": band,
                "channel": channel,
                "power": power
            }
        }
        response = requests.put(
            f"https://api.meraki.com/api/v1/networks/{NETWORK_ID}/wireless/ssids/{ssid_number}",
            headers=headers,
            json=data
        )
        if response.status_code == 200:
            messagebox.showinfo("Success", "Radio settings updated.")
        else:
            messagebox.showerror("Error", f"Failed: {response.text}")
    except Exception as e:
        messagebox.showerror("Error", str(e))

def toggle_client_enforcement():
    try:
        ssid_number = simpledialog.askinteger("Client Enforcement", "Enter SSID number:")
        if ssid_number is None:
            return
        enable = messagebox.askyesno("Client Enforcement", "Enable client enforcement (client isolation)?")
        data = {"clientEnforcement": enable}
        response = requests.put(
            f"https://api.meraki.com/api/v1/networks/{NETWORK_ID}/wireless/ssids/{ssid_number}",
            headers=headers,
            json=data
        )
        if response.status_code == 200:
            status = "enabled" if enable else "disabled"
            messagebox.showinfo("Success", f"Client enforcement {status}.")
        else:
            messagebox.showerror("Error", f"Failed: {response.text}")
    except Exception as e:
        messagebox.showerror("Error", str(e))

# --- GUI Setup ---
app = tk.Tk()
app.title("Meraki SSID Manager")
app.geometry("700x500")

# Listbox with scrollbar
frame = tk.Frame(app)
frame.pack(fill=tk.BOTH, expand=True)

ssids_listbox = tk.Listbox(frame, height=20)
ssids_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

scrollbar = tk.Scrollbar(frame, command=ssids_listbox.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
ssids_listbox.config(yscrollcommand=scrollbar.set)

# Buttons frame
button_frame = tk.Frame(app)
button_frame.pack(fill=tk.X, pady=10)

# Buttons
tk.Button(button_frame, text="Refresh", command=lambda: refresh_ssids_listbox(ssids_listbox)).pack(side=tk.LEFT, padx=5)
tk.Button(button_frame, text="Add SSID", command=add_ssid).pack(side=tk.LEFT, padx=5)
tk.Button(button_frame, text="Update SSID", command=update_ssid).pack(side=tk.LEFT, padx=5)
tk.Button(button_frame, text="Delete SSID", command=delete_ssid).pack(side=tk.LEFT, padx=5)
tk.Button(button_frame, text="Config Captive Portal", command=configure_captive_portal).pack(side=tk.LEFT, padx=5)
tk.Button(button_frame, text="Traffic Shaping", command=configure_traffic_shaping).pack(side=tk.LEFT, padx=5)
tk.Button(button_frame, text="Radio Settings", command=configure_radio_settings).pack(side=tk.LEFT, padx=5)
tk.Button(button_frame, text="Client Enforcement", command=toggle_client_enforcement).pack(side=tk.LEFT, padx=5)

# Initial load
refresh_ssids_listbox(ssids_listbox)

app.mainloop()