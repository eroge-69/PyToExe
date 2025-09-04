import geocoder
import threading
import requests
from io import BytesIO
from PIL import Image, ImageTk
import webbrowser
import os
import tempfile
import math
import time
from tkinter import Canvas
import customtkinter as ctk
import tkintermapview  # For embedded map display

class BravoApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Configure window
        self.title("Bravo - IP Geolocation Tool")
        self.geometry("1400x800")  # Increased width for better layout
        
        # Use dark grey and normal grey color scheme
        self.dark_grey = "#2b2b2b"
        self.normal_grey = "#666666"
        self.accent_red = "#ff0000"
        self.text_color = "#ffffff"
        
        self.configure(fg_color=self.dark_grey)
        
        # Configure grid layout with two columns
        self.grid_columnconfigure(0, weight=2)  # Map column (larger)
        self.grid_columnconfigure(1, weight=1)  # Info column
        self.grid_rowconfigure(0, weight=1)
        
        # Initialize variables
        self.current_location = None
        self.map_image = None
        self.animation_id = None
        self.geocoder_result = None
        self.map_widget = None
        
        # Create title label with COD style
        self.title_label = ctk.CTkLabel(
            self, 
            text="BRAVO IP TRACKER",
            text_color=self.accent_red,
            font=("Arial", 28, "bold")
        )
        self.title_label.grid(row=0, column=0, columnspan=2, pady=(20, 30))
        
        # Create input frame
        self.input_frame = ctk.CTkFrame(self, fg_color=self.normal_grey)
        self.input_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=20, pady=(0, 20))
        self.input_frame.grid_columnconfigure(1, weight=1)
        
        # IP input label
        self.ip_label = ctk.CTkLabel(
            self.input_frame,
            text="TARGET IP:",
            text_color=self.text_color,
            font=("Arial", 16, "bold")
        )
        self.ip_label.grid(row=0, column=0, padx=20, pady=20)
        
        # IP input entry
        self.ip_entry = ctk.CTkEntry(
            self.input_frame,
            placeholder_text="Enter IP address or leave blank for your own IP",
            fg_color=self.dark_grey,
            border_color=self.accent_red,
            text_color=self.text_color,
            height=40,
            font=("Arial", 14)
        )
        self.ip_entry.grid(row=0, column=1, padx=(0, 20), pady=20, sticky="ew")
        
        # Buttons frame
        self.button_frame = ctk.CTkFrame(self.input_frame, fg_color="transparent")
        self.button_frame.grid(row=0, column=2, padx=(0, 20), pady=20)
        
        # Track button
        self.track_button = ctk.CTkButton(
            self.button_frame,
            text="TRACK",
            command=self.track_ip,
            fg_color=self.accent_red,
            hover_color="#cc0000",
            text_color=self.text_color,
            font=("Arial", 14, "bold"),
            width=120,
            height=40
        )
        self.track_button.grid(row=0, column=0, padx=(0, 10))
        
        # Clear button
        self.clear_button = ctk.CTkButton(
            self.button_frame,
            text="CLEAR",
            command=self.clear_input,
            fg_color=self.dark_grey,
            hover_color="#3b3b3b",
            text_color=self.text_color,
            font=("Arial", 14, "bold"),
            width=120,
            height=40
        )
        self.clear_button.grid(row=0, column=1)
        
        # Create map display frame (left side)
        self.map_frame = ctk.CTkFrame(self, fg_color=self.normal_grey)
        self.map_frame.grid(row=2, column=0, sticky="nsew", padx=(20, 10), pady=(0, 20))
        self.map_frame.grid_columnconfigure(0, weight=1)
        self.map_frame.grid_rowconfigure(1, weight=1)
        
        # Map label
        self.map_label = ctk.CTkLabel(
            self.map_frame,
            text="SATELLITE SURVEILLANCE",
            text_color=self.text_color,
            font=("Arial", 18, "bold")
        )
        self.map_label.grid(row=0, column=0, pady=(20, 10))
        
        # Create map widget using tkintermapview
        self.map_widget = tkintermapview.TkinterMapView(
            self.map_frame,
            width=600,
            height=400,
            corner_radius=0
        )
        self.map_widget.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        
        # Set default tile server to satellite view
        self.map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=s&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=22)  # Google satellite
        
        # Create info display frame (right side)
        self.info_frame = ctk.CTkFrame(self, fg_color=self.normal_grey)
        self.info_frame.grid(row=2, column=1, sticky="nsew", padx=(10, 20), pady=(0, 20))
        self.info_frame.grid_columnconfigure(0, weight=1)
        self.info_frame.grid_rowconfigure(1, weight=1)
        
        # Info label
        self.info_label = ctk.CTkLabel(
            self.info_frame,
            text="TARGET INTEL",
            text_color=self.text_color,
            font=("Arial", 18, "bold")
        )
        self.info_label.grid(row=0, column=0, pady=(20, 10))
        
        # Info text area with scrollbar
        self.info_text = ctk.CTkTextbox(
            self.info_frame,
            fg_color=self.dark_grey,
            text_color=self.text_color,
            font=("Arial", 12),
            wrap="word",
            height=400
        )
        self.info_text.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        
        # Status label
        self.status_label = ctk.CTkLabel(
            self,
            text="STATUS: READY",
            text_color="#00ff00",
            font=("Arial", 14)
        )
        self.status_label.grid(row=3, column=0, columnspan=2, pady=(10, 20))
        
        # Set focus to entry
        self.ip_entry.focus()
        
        # Bind Enter key to track command
        self.bind("<Return>", lambda event: self.track_ip())

    def track_ip(self):
        """Track the IP address and display its location on the map"""
        ip_address = self.ip_entry.get().strip()
        
        if not ip_address:
            ip_address = None  # geocoder will use current IP
        
        # Update status
        self.status_label.configure(text="STATUS: TRACKING TARGET...", text_color="#ffff00")
        
        # Clear previous info
        self.info_text.delete("1.0", "end")
        self.info_text.insert("end", "Gathering intelligence...")
        
        # Run geolocation in a separate thread to prevent GUI freezing
        thread = threading.Thread(target=self._perform_geolocation, args=(ip_address,))
        thread.daemon = True
        thread.start()

    def _perform_geolocation(self, ip_address):
        """Perform the IP geolocation (run in separate thread)"""
        try:
            # Get location from IP
            g = geocoder.ip(ip_address)
            
            if g.ok:
                self.current_location = g.latlng
                self.geocoder_result = g
                
                # Update GUI in the main thread
                self.after(0, self._display_map)
                self.after(0, self._display_info)
                self.after(0, lambda: self.status_label.configure(
                    text=f"STATUS: TARGET ACQUIRED - {g.city}, {g.country}", 
                    text_color="#00ff00"
                ))
            else:
                self.after(0, lambda: self.status_label.configure(
                    text="STATUS: TARGET NOT FOUND", 
                    text_color=self.accent_red
                ))
                self.after(0, lambda: self.info_text.delete("1.0", "end"))
                self.after(0, lambda: self.info_text.insert("end", "Target not found. Please check the IP address and try again."))
                
        except Exception as e:
            self.after(0, lambda: self.status_label.configure(
                text=f"STATUS: ERROR - {str(e)}", 
                text_color=self.accent_red
            ))
            self.after(0, lambda: self.info_text.delete("1.0", "end"))
            self.after(0, lambda: self.info_text.insert("end", f"Error: {str(e)}"))

    def _display_map(self):
        """Display the map with the target location"""
        try:
            if not self.current_location:
                return
                
            lat, lng = self.current_location
            
            # Set the map position and add marker
            self.map_widget.set_position(lat, lng)
            self.map_widget.set_zoom(12)
            self.map_widget.set_marker(lat, lng, text="Target Location")
            
        except Exception as e:
            self.status_label.configure(
                text=f"Error displaying map: {str(e)}",
                text_color=self.accent_red
            )

    def _display_info(self):
        """Display all available information about the IP"""
        if not self.geocoder_result:
            return
            
        g = self.geocoder_result
        
        # Clear previous info
        self.info_text.delete("1.0", "end")
        
        # Display core information first
        info = f"📍 IP INFORMATION\n\n"
        info += f"🔹 IP Address: {g.ip if hasattr(g, 'ip') and g.ip else 'N/A'}\n\n"
        
        info += f"🌍 LOCATION DATA\n\n"
        info += f"• Country: {g.country if hasattr(g, 'country') and g.country else 'N/A'}\n"
        info += f"• Latitude: {g.lat if hasattr(g, 'lat') and g.lat else 'N/A'}\n"
        info += f"• Longitude: {g.lng if hasattr(g, 'lng') and g.lng else 'N/A'}\n\n"
        
        info += f"📡 NETWORK INFORMATION\n\n"
        info += f"• ISP: {g.org if hasattr(g, 'org') and g.org else 'N/A'}\n\n"
        
        # Add additional information if available
        additional_info = False
        info += f"📊 ADDITIONAL INFORMATION\n\n"
        
        if hasattr(g, 'city') and g.city:
            info += f"• City: {g.city}\n"
            additional_info = True
        if hasattr(g, 'state') and g.state:
            info += f"• State/Region: {g.state}\n"
            additional_info = True
        if hasattr(g, 'postal') and g.postal:
            info += f"• Postal Code: {g.postal}\n"
            additional_info = True
        if hasattr(g, 'timezone') and g.timezone:
            info += f"• Timezone: {g.timezone}\n"
            additional_info = True
        
        if not additional_info:
            info += "No additional information available\n"

        self.info_text.insert("end", info)

    def clear_input(self):
        """Clear the input field"""
        self.ip_entry.delete(0, 'end')
        self.status_label.configure(text="STATUS: READY", text_color="#00ff00")
        self.map_widget.delete_all_markers()
        self.info_text.delete("1.0", "end")
        
        # Stop animation
        if self.animation_id:
            self.after_cancel(self.animation_id)
            self.animation_id = None

if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    
    app = BravoApp()
    app.mainloop()
