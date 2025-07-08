import tkinter as tk
from tkinter import messagebox
import phonenumbers
from phonenumbers import geocoder, carrier, timezone
import requests

def track():
    number = entry.get()
    try:
        phone = phonenumbers.parse(number)
        if not phonenumbers.is_valid_number(phone):
            messagebox.showerror("Invalid", "Invalid phone number.")
            return

        country = geocoder.country_name_for_number(phone, "en")
        provider = carrier.name_for_number(phone, "en")
        zones = timezone.time_zones_for_number(phone)
        city = geocoder.description_for_number(phone, "en")
        country_code = phone.country_code
        national_number = phone.national_number

        ipdetails = requests.get("https://ipapi.co/json/").json()
        ip = ipdetails.get("ip", "N/A")
        ipcity = ipdetails.get("city", "N/A")
        region = f"{ipdetails.get('region', 'N/A')}, {ipdetails.get('country_name', 'N/A')}"
        lat = ipdetails.get("latitude", "N/A")
        lon = ipdetails.get("longitude", "N/A")

        output = f"""Phone Number: {number}
Country: {country}
Country Code: +{country_code}
National Number: {national_number}
Carrier: {provider}
Timezone: {', '.join(zones)}
Location: {city}
Google Maps: https://www.google.com/maps/search/{city}

IP Address: {ip}
IP City: {ipcity}
IP Region: {region}
Coords: {lat}, {lon}
Google Maps (IP): https://www.google.com/maps?q={lat},{lon}
"""

        text.delete(1.0, tk.END)
        text.insert(tk.END, output)

    except Exception as e:
        messagebox.showerror("Error", str(e))

root = tk.Tk()
root.title("📍 Phone Number Tracker")
root.geometry("600x500")

tk.Label(root, text="Enter Phone Number (with country code, e.g. +1..., +44..., +91...):", font=("Segoe UI", 12)).pack(pady=10)
entry = tk.Entry(root, font=("Segoe UI", 12), width=30)
entry.pack()

tk.Button(root, text="Track", command=track, font=("Segoe UI", 12), bg="#4CAF50", fg="white").pack(pady=10)
text = tk.Text(root, font=("Consolas", 10), wrap="word")
text.pack(padx=10, pady=10, fill="both", expand=True)

root.mainloop()