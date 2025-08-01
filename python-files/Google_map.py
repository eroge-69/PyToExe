import tkinter as tk
from tkinter import messagebox
from gui_styles import COLORS, FONTS, WIDGET_STYLES, TOPLEVEL_WINDOW
import webbrowser
import qrcode
from PIL import ImageTk, Image
import requests
import json

class GoogleMapsModule:
    def __init__(self, event_bus=None, module_manager=None):
        self.event_bus = event_bus
        self.module_manager = module_manager
        print("GoogleMapsModule: Moduł zainicjalizowany.")

        self.start_entry_widget = None
        self.end_entry_widget = None
        self.waypoints_entry_widget = None

        self.api_key = None
        self.distance_label = None

    def run(self):
        messagebox.showinfo("GoogleMapsModule", "Metoda 'run' modułu GoogleMapsModule została wywołana!")
        print("GoogleMapsModule: Metoda 'run' wykonana.")

    def get_gui_widget(self, parent_frame):
        frame = tk.Frame(parent_frame, bg=COLORS["secondary_bg"])
        frame.grid_columnconfigure(0, weight=1)

        button_width = WIDGET_STYLES["button_width"]
        button_height = WIDGET_STYLES["button_height"]

        button = tk.Button(frame, text="Google Maps - Trasa",
                            command=self._open_Maps_window,
                            font=FONTS["button"],
                            bg=COLORS["button_bg"],
                            fg="blue",
                            activebackground=COLORS["button_active_bg"],
                            activeforeground="blue",
                            width=button_width,
                            height=button_height,
                            bd=WIDGET_STYLES["border_width"],
                            relief=WIDGET_STYLES["relief_style"])

        button.grid(row=0, column=0, padx=WIDGET_STYLES["padding_x"], pady=WIDGET_STYLES["padding_y"], sticky="ew")

        return frame

    def _open_Maps_window(self):
        map_window = tk.Toplevel(self.module_manager.get_main_app_window())
        map_window.title("Wyznaczanie Trasy Google Maps")
        map_window.configure(bg=COLORS["primary_bg"])
        map_window.resizable(True, True)

        map_window.transient(master=self.module_manager.get_main_app_window())
        map_window.grab_set()

        map_window.grid_rowconfigure(0, weight=1)
        map_window.grid_rowconfigure(1, weight=0)
        map_window.grid_rowconfigure(2, weight=0)
        map_window.grid_rowconfigure(3, weight=0)
        map_window.grid_rowconfigure(4, weight=0)
        map_window.grid_rowconfigure(5, weight=0)
        map_window.grid_rowconfigure(6, weight=0)
        map_window.grid_rowconfigure(7, weight=0)
        map_window.grid_rowconfigure(8, weight=0)
        map_window.grid_rowconfigure(9, weight=0)
        map_window.grid_rowconfigure(10, weight=0)
        map_window.grid_rowconfigure(11, weight=0)
        map_window.grid_rowconfigure(12, weight=0)
        map_window.grid_rowconfigure(13, weight=0)
        map_window.grid_rowconfigure(14, weight=1)


        map_window.grid_columnconfigure(0, weight=1)
        map_window.grid_columnconfigure(1, weight=0)
        map_window.grid_columnconfigure(2, weight=1)

        tk.Label(map_window, text="Punkt startowy (adres/współrzędne):",
                 font=FONTS["default"], fg=COLORS["text_color"], bg=COLORS["primary_bg"]).grid(row=1, column=1, sticky="w", padx=WIDGET_STYLES["padding_x"], pady=WIDGET_STYLES["padding_y"])
        self.start_entry_widget = tk.Text(map_window,
                                      font=FONTS["default"], bg=COLORS["entry_bg"], fg=COLORS["text_color"],
                                      width=WIDGET_STYLES["button_width"], height=1, # Zmieniono wysokość na 1 linię
                                      bd=WIDGET_STYLES["border_width"], relief=WIDGET_STYLES["relief_style"])
        self.start_entry_widget.grid(row=2, column=1, sticky="ew", padx=WIDGET_STYLES["padding_x"], pady=WIDGET_STYLES["padding_y"])

        tk.Label(map_window, text="Punkty pośrednie (opcjonalnie, oddziel średnikiem ';'):",
                 font=FONTS["default"], fg=COLORS["text_color"], bg=COLORS["primary_bg"]).grid(row=3, column=1, sticky="w", padx=WIDGET_STYLES["padding_x"], pady=WIDGET_STYLES["padding_y"])
        self.waypoints_entry_widget = tk.Text(map_window,
                                      font=FONTS["default"], bg=COLORS["entry_bg"], fg=COLORS["text_color"],
                                      width=WIDGET_STYLES["button_width"], height=10,
                                      bd=WIDGET_STYLES["border_width"], relief=WIDGET_STYLES["relief_style"])
        self.waypoints_entry_widget.grid(row=4, column=1, sticky="ew", padx=WIDGET_STYLES["padding_x"], pady=WIDGET_STYLES["padding_y"])

        tk.Label(map_window, text="Punkt końcowy (adres/współrzędne):",
                 font=FONTS["default"], fg=COLORS["text_color"], bg=COLORS["primary_bg"]).grid(row=5, column=1, sticky="w", padx=WIDGET_STYLES["padding_x"], pady=WIDGET_STYLES["padding_y"])
        self.end_entry_widget = tk.Text(map_window,
                                      font=FONTS["default"], bg=COLORS["entry_bg"], fg=COLORS["text_color"],
                                      width=WIDGET_STYLES["button_width"], height=1, # Zmieniono wysokość na 1 linię
                                      bd=WIDGET_STYLES["border_width"], relief=WIDGET_STYLES["relief_style"])
        self.end_entry_widget.grid(row=6, column=1, sticky="ew", padx=WIDGET_STYLES["padding_x"], pady=WIDGET_STYLES["padding_y"])

        route_button = tk.Button(map_window, text="Wyznacz Trasę",
                                        command=self._open_route_url,
                                        font=FONTS["button"],
                                        bg=COLORS["button_bg"],
                                        fg=COLORS["text_color"],
                                        activebackground=COLORS["button_active_bg"],
                                        activeforeground=COLORS["text_color"],
                                        width=WIDGET_STYLES["button_width"],
                                        height=WIDGET_STYLES["button_height"],
                                        bd=WIDGET_STYLES["border_width"],
                                        relief=WIDGET_STYLES["relief_style"])
        route_button.grid(row=7, column=1, padx=WIDGET_STYLES["padding_x"], pady=WIDGET_STYLES["padding_y"])

        show_map_button = tk.Button(map_window, text="Pokaż Mapę (Punkt Startowy)",
                                     command=self._open_map_for_start_location,
                                     font=FONTS["button"],
                                     bg=COLORS["button_bg"],
                                     fg=COLORS["text_color"],
                                     activebackground=COLORS["button_active_bg"],
                                     activeforeground=COLORS["text_color"],
                                     width=WIDGET_STYLES["button_width"],
                                     height=WIDGET_STYLES["button_height"],
                                     bd=WIDGET_STYLES["border_width"],
                                     relief=WIDGET_STYLES["relief_style"])
        show_map_button.grid(row=8, column=1, padx=WIDGET_STYLES["padding_x"], pady=WIDGET_STYLES["padding_y"])

        send_to_phone_button = tk.Button(map_window, text="Wyślij Trasę na Telefon (QR)",
                                          command=self._send_route_to_phone,
                                          font=FONTS["button"],
                                          bg=COLORS["button_bg"],
                                          fg=COLORS["text_color"],
                                          activebackground=COLORS["button_active_bg"],
                                          activeforeground=COLORS["text_color"],
                                          width=WIDGET_STYLES["button_width"],
                                          height=WIDGET_STYLES["button_height"],
                                          bd=WIDGET_STYLES["border_width"],
                                          relief=WIDGET_STYLES["relief_style"])
        send_to_phone_button.grid(row=9, column=1, padx=WIDGET_STYLES["padding_x"], pady=WIDGET_STYLES["padding_y"])

        self.distance_label = tk.Label(map_window, text="Dystans: N/A",
                                        font=FONTS["default"], fg=COLORS["text_color"], bg=COLORS["primary_bg"])
        self.distance_label.grid(row=10, column=1, sticky="w", padx=WIDGET_STYLES["padding_x"], pady=WIDGET_STYLES["padding_y"])

        show_distance_button = tk.Button(map_window, text="Pokaż Dystans",
                                        command=self._display_route_distance,
                                        font=FONTS["button"],
                                        bg=COLORS["button_bg"],
                                        fg=COLORS["text_color"],
                                        activebackground=COLORS["button_active_bg"],
                                        activeforeground=COLORS["text_color"],
                                        width=WIDGET_STYLES["button_width"],
                                        height=WIDGET_STYLES["button_height"],
                                        bd=WIDGET_STYLES["border_width"],
                                        relief=WIDGET_STYLES["relief_style"])
        show_distance_button.grid(row=11, column=1, padx=WIDGET_STYLES["padding_x"], pady=WIDGET_STYLES["padding_y"])

        api_key_button = tk.Button(map_window, text="Wprowadź API Key",
                                    command=self._open_api_key_entry,
                                    font=FONTS["button"],
                                    bg=COLORS["button_bg"],
                                    fg=COLORS["text_color"],
                                    activebackground=COLORS["button_active_bg"],
                                    activeforeground=COLORS["text_color"],
                                    width=WIDGET_STYLES["button_width"],
                                    height=WIDGET_STYLES["button_height"],
                                    bd=WIDGET_STYLES["border_width"],
                                    relief=WIDGET_STYLES["relief_style"])
        api_key_button.grid(row=12, column=1, padx=WIDGET_STYLES["padding_x"], pady=WIDGET_STYLES["padding_y"])

        close_button = tk.Button(map_window, text="Zamknij", command=map_window.destroy,
                                font=FONTS["button"],
                                bg=COLORS["button_bg"],
                                fg=COLORS["text_color"],
                                activebackground=COLORS["button_active_bg"],
                                activeforeground=COLORS["text_color"],
                                width=WIDGET_STYLES["button_width"])
        close_button.grid(row=13, column=1, pady=10)

        map_window.update_idletasks()
        window_width = map_window.winfo_width()
        window_height = map_window.winfo_height()

        screen_width = self.module_manager.get_main_app_window().winfo_screenwidth()
        screen_height = self.module_manager.get_main_app_window().winfo_screenheight()

        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)

        map_window.geometry(f"+{x}+{y}")
        map_window.wait_window(map_window)


    def _open_api_key_entry(self):
        api_key_window = tk.Toplevel(self.module_manager.get_main_app_window())
        api_key_window.title("Wprowadź API Key")
        api_key_window.configure(bg=COLORS["primary_bg"])
        
        api_key_window.transient(master=self.module_manager.get_main_app_window())
        api_key_window.grab_set()

        api_key_window.grid_rowconfigure(0, weight=1)
        api_key_window.grid_rowconfigure(3, weight=1)
        api_key_window.grid_columnconfigure(0, weight=1)
        api_key_window.grid_columnconfigure(2, weight=1)

        tk.Label(api_key_window, text="Wprowadź swój API Key:",
                 font=FONTS["default"], fg=COLORS["text_color"], bg=COLORS["primary_bg"]).grid(row=1, column=1, pady=WIDGET_STYLES["padding_y"])

        self.api_key_entry_var = tk.StringVar()
        api_key_entry = tk.Entry(api_key_window, textvariable=self.api_key_entry_var,
                                 font=FONTS["default"], bg=COLORS["entry_bg"], fg=COLORS["text_color"],
                                 width=WIDGET_STYLES["button_width"],
                                 bd=WIDGET_STYLES["border_width"], relief=WIDGET_STYLES["relief_style"])
        api_key_entry.grid(row=2, column=1, padx=WIDGET_STYLES["padding_x"], pady=WIDGET_STYLES["padding_y"])

        tk.Button(api_key_window, text="Zapisz", command=lambda: self._save_api_key(api_key_window),
                  font=FONTS["button"], bg=COLORS["button_bg"], fg=COLORS["text_color"],
                  activebackground=COLORS["button_active_bg"], activeforeground=COLORS["text_color"]).grid(row=3, column=1, pady=WIDGET_STYLES["padding_y"])

        api_key_window.update_idletasks()
        window_width = api_key_window.winfo_width()
        window_height = api_key_window.winfo_height()
        screen_width = self.module_manager.get_main_app_window().winfo_screenwidth()
        screen_height = self.module_manager.get_main_app_window().winfo_screenheight()
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)
        api_key_window.geometry(f"+{x}+{y}")

        api_key_window.wait_window(api_key_window)

    def _save_api_key(self, window):
        self.api_key = self.api_key_entry_var.get().strip()
        if self.api_key:
            messagebox.showinfo("API Key", "API Key został zapisany.")
            print(f"API Key został zapisany: {self.api_key[:5]}...")
        else:
            messagebox.showwarning("API Key", "Nie wprowadzono API Key.")
            self.api_key = None
        window.destroy()

    def _get_text_from_widget(self, widget):
        return widget.get("1.0", tk.END).strip()

    def _generate_route_url(self):
        start = self._get_text_from_widget(self.start_entry_widget)
        end = self._get_text_from_widget(self.end_entry_widget)
        waypoints = self._get_text_from_widget(self.waypoints_entry_widget)

        if not start or not end:
            return None, "Proszę podać punkt startowy i końcowy."

        start_encoded = start.replace(' ', '+')
        end_encoded = end.replace(' ', '+')

        route_url = f"https://www.google.com/maps/dir/{start_encoded}/{end_encoded}"

        if waypoints:
            waypoints_list = [wp.strip().replace(' ', '+') for wp in waypoints.split(';') if wp.strip()]
            if waypoints_list:
                route_url += f"/{'/'.join(waypoints_list)}"
        
        return route_url, None

    def _open_route_url(self):
        route_url, error_message = self._generate_route_url()

        if error_message:
            messagebox.showwarning("Wyznaczanie Trasy", error_message)
            return

        try:
            webbrowser.open_new_tab(route_url)
            messagebox.showinfo("Wyznaczanie Trasy", "Otwieram trasę w Google Maps.")
        except Exception as e:
            messagebox.showerror("Błąd", f"Nie można otworzyć przeglądarki: {e}")
            
    def _open_map_for_start_location(self):
        start = self._get_text_from_widget(self.start_entry_widget)

        if not start:
            messagebox.showwarning("Pokaż Mapę", "Proszę podać punkt startowy, aby wyświetlić mapę.")
            return

        start_encoded = start.replace(' ', '+')
        map_url = f"https://www.google.com/maps/place/{start_encoded}"

        try:
            webbrowser.open_new_tab(map_url)
            messagebox.showinfo("Pokaż Mapę", f"Otwieram mapę dla: {start}")
        except Exception as e:
            messagebox.showerror("Błąd", f"Nie można otworzyć przeglądarki: {e}")

    def _send_route_to_phone(self):
        route_url, error_message = self._generate_route_url()

        if error_message:
            messagebox.showwarning("Wyślij Trasę", error_message)
            return

        try:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(route_url)
            qr.make(fit=True)

            img = qr.make_image(fill_color="black", back_color="white")

            img_width, img_height = img.size
            max_size = 300
            if img_width > max_size or img_height > max_size:
                ratio = min(max_size / img_width, max_size / img_height)
                img = img.resize((int(img_width * ratio), int(img_height * ratio)), Image.LANCZOS)
            elif img_width < 150:
                img = img.resize((150, 150), Image.LANCZOS)


            qr_window = tk.Toplevel(self.module_manager.get_main_app_window())
            qr_window.title("Zeskanuj trasę na telefon")
            qr_window.configure(bg=COLORS["primary_bg"])
            qr_window.transient(master=self.module_manager.get_main_app_window())
            qr_window.grab_set()

            qr_photo = ImageTk.PhotoImage(img)

            qr_label = tk.Label(qr_window, image=qr_photo, bg=COLORS["primary_bg"])
            qr_label.image = qr_photo
            qr_label.pack(padx=20, pady=20)

            tk.Label(qr_window, text="Zeskanuj ten kod QR telefonem, aby otworzyć trasę w Google Maps.",
                     font=FONTS["default"], fg=COLORS["text_color"], bg=COLORS["primary_bg"], wraplength=300).pack(pady=5)

            close_button = tk.Button(qr_window, text="Zamknij", command=qr_window.destroy,
                                     font=FONTS["button"], bg=COLORS["button_bg"], fg=COLORS["text_color"])
            close_button.pack(pady=10)

            qr_window.update_idletasks()
            center_window_toplevel(qr_window, self.module_manager.get_main_app_window())
            qr_window.wait_window(qr_window)

        except Exception as e:
            messagebox.showerror("Błąd QR Code", f"Nie udało się wygenerować kodu QR: {e}")

    def _fetch_route_details_from_api(self):
        start = self._get_text_from_widget(self.start_entry_widget)
        end = self._get_text_from_widget(self.end_entry_widget)
        waypoints = self._get_text_from_widget(self.waypoints_entry_widget)

        if not self.api_key:
            messagebox.showwarning("API Key", "Proszę wprowadzić API Key Google Maps, aby pobrać dystans.")
            return None, "Brak API Key."

        if not start or not end:
            return None, "Proszę podać punkt startowy i końcowy."

        base_url = "https://maps.googleapis.com/maps/api/directions/json?"
        params = {
            "origin": start,
            "destination": end,
            "key": self.api_key
        }

        if waypoints:
            waypoints_list = [wp.strip() for wp in waypoints.split(';') if wp.strip()]
            if waypoints_list:
                params["waypoints"] = "|".join(waypoints_list)

        try:
            response = requests.get(base_url, params=params)
            response.raise_for_status()
            data = response.json()

            if data["status"] == "OK":
                total_distance_meters = 0
                total_duration_seconds = 0
                
                for route in data["routes"]:
                    for leg in route["legs"]:
                        total_distance_meters += leg["distance"]["value"]
                        total_duration_seconds += leg["duration"]["value"]
                
                distance_km = total_distance_meters / 1000
                return distance_km, None
            else:
                return None, f"Błąd API: {data['status']}. {data.get('error_message', '')}"
        except requests.exceptions.RequestException as e:
            return None, f"Błąd połączenia z API Google Maps: {e}"
        except json.JSONDecodeError:
            return None, "Błąd parsowania odpowiedzi API."
        except Exception as e:
            return None, f"Nieoczekiwany błąd podczas pobierania dystansu: {e}"

    def _display_route_distance(self):
        distance_km, error_message = self._fetch_route_details_from_api()

        if error_message:
            self.distance_label.config(text=f"Dystans: Błąd - {error_message}")
            messagebox.showerror("Błąd Dystansu", error_message)
        elif distance_km is not None:
            self.distance_label.config(text=f"Dystans: {distance_km:.2f} km")
            messagebox.showinfo("Dystans Trasy", f"Szacowany dystans trasy: {distance_km:.2f} km")
        else:
            self.distance_label.config(text="Dystans: N/A")


    def get_full_gui_widget(self, parent_frame):
        frame = tk.Frame(parent_frame, bg=COLORS["primary_bg"])
        frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        parent_frame.grid_rowconfigure(0, weight=1)
        parent_frame.grid_columnconfigure(0, weight=1)

        frame.grid_rowconfigure(0, weight=1)
        frame.grid_rowconfigure(1, weight=0)
        frame.grid_rowconfigure(2, weight=0)
        frame.grid_rowconfigure(3, weight=0)
        frame.grid_rowconfigure(4, weight=1)

        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=0)
        frame.grid_columnconfigure(2, weight=1)

        tk.Label(frame, text="Pełne GUI Google Maps Module",
                    font=FONTS["header"], fg=COLORS["header_color"], bg=COLORS["primary_bg"]).grid(row=1, column=1, pady=10)

        tk.Label(frame, text="To jest miejsce na bardziej złożony interfejs modułu Google Maps.",
                    font=FONTS["default"], fg=COLORS["text_color"], bg=COLORS["primary_bg"]).grid(row=2, column=1, pady=5)

        tk.Button(frame, text="Zamknij to okno", command=parent_frame.winfo_toplevel().destroy,
                    font=FONTS["button"], bg=COLORS["button_bg"], fg=COLORS["text_color"],
                    activebackground=COLORS["button_active_bg"], activeforeground=COLORS["text_color"],
                    width=WIDGET_STYLES["button_width"]).grid(row=3, column=1, pady=10)
        return frame

def center_window_toplevel(toplevel_window, parent_window):
    toplevel_window.update_idletasks()
    window_width = toplevel_window.winfo_width()
    window_height = toplevel_window.winfo_height()

    parent_x = parent_window.winfo_x()
    parent_y = parent_window.winfo_y()
    parent_width = parent_window.winfo_width()
    parent_height = parent_window.winfo_height()

    x = parent_x + (parent_width // 2) - (window_width // 2)
    y = parent_y + (parent_height // 2) - (window_height // 2)

    toplevel_window.geometry(f"+{x}+{y}")