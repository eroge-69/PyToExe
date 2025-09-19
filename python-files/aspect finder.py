import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from datetime import datetime, timedelta, timezone
import swisseph as swe
import threading
import os

# --- Configuration ---
# You must download the Swiss Ephemeris files and place them in a directory.
# Download from: https://www.astro.com/ftp/swisseph/ephe/
# Create a folder named 'ephe' in the same directory as this script,
# and place the downloaded files (e.g., sepl_18.se1, semo_18.se1, etc.) inside it.
EPHEMERIS_PATH = 'ephe'

# Planet definitions for Swiss Ephemeris
PLANETS = {
    'Sun': swe.SUN,
    'Moon': swe.MOON,
    'Mercury': swe.MERCURY,
    'Venus': swe.VENUS,
    'Mars': swe.MARS,
    'Jupiter': swe.JUPITER,
    'Saturn': swe.SATURN,
    'Uranus': swe.URANUS,
    'Neptune': swe.NEPTUNE,
    'Pluto': swe.PLUTO,
}

# Aspect definitions (angle, orb)
ASPECTS = {
    'Conjunction': 0.0,
    'Sextile': 60.0,
    'Square': 90.0,
    'Trine': 120.0,
    'Opposition': 180.0,
}

ZODIAC_SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

class AspectFinderApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Planetary Aspect Finder")
        self.geometry("800x600")
        self.configure(bg="#2E2E2E")

        # --- Check for Ephemeris Files ---
        if not os.path.exists(EPHEMERIS_PATH) or not os.listdir(EPHEMERIS_PATH):
             messagebox.showerror(
                "Ephemeris Files Not Found",
                f"Please download the Swiss Ephemeris files and place them in a folder named '{EPHEMERIS_PATH}' in the same directory as this program.\n\n"
                "You can download them from ftp://ftp.astro.com/pub/swisseph/ephe/"
            )
             self.destroy()
             return

        swe.set_ephe_path(EPHEMERIS_PATH)

        self.create_widgets()

    def create_widgets(self):
        main_frame = ttk.Frame(self, padding="20", style='TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Style configuration
        self.style = ttk.Style(self)
        self.style.theme_use('clam')
        self.style.configure('TFrame', background='#2E2E2E')
        self.style.configure('TLabel', background='#2E2E2E', foreground='white', font=('Arial', 10))
        self.style.configure('TButton', background='#4A4A4A', foreground='white', font=('Arial', 10, 'bold'), borderwidth=1)
        self.style.map('TButton', background=[('active', '#6A6A6A')])
        self.style.configure('TCombobox', fieldbackground='#4A4A4A', background='#3E3E3E', foreground='white')
        self.style.configure('TEntry', fieldbackground='#4A4A4A', foreground='white')

        # --- Input Frame ---
        input_frame = ttk.Frame(main_frame, style='TFrame')
        input_frame.pack(fill=tk.X, pady=10)

        # Date inputs
        ttk.Label(input_frame, text="Start Date (YYYY-MM-DD):").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.start_date_var = tk.StringVar(value="2024-01-01")
        ttk.Entry(input_frame, textvariable=self.start_date_var, width=12).grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(input_frame, text="End Date (YYYY-MM-DD):").grid(row=0, column=2, padx=5, pady=5, sticky='w')
        self.end_date_var = tk.StringVar(value="2024-12-31")
        ttk.Entry(input_frame, textvariable=self.end_date_var, width=12).grid(row=0, column=3, padx=5, pady=5)
        
        # Planet and Aspect selectors
        ttk.Label(input_frame, text="Planet 1:").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.planet1_var = tk.StringVar(value='Moon')
        ttk.Combobox(input_frame, textvariable=self.planet1_var, values=list(PLANETS.keys()), state='readonly').grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(input_frame, text="Planet 2:").grid(row=1, column=2, padx=5, pady=5, sticky='w')
        self.planet2_var = tk.StringVar(value='Sun')
        ttk.Combobox(input_frame, textvariable=self.planet2_var, values=list(PLANETS.keys()), state='readonly').grid(row=1, column=3, padx=5, pady=5)

        ttk.Label(input_frame, text="Aspect:").grid(row=1, column=4, padx=5, pady=5, sticky='w')
        self.aspect_var = tk.StringVar(value='Trine')
        ttk.Combobox(input_frame, textvariable=self.aspect_var, values=list(ASPECTS.keys()), state='readonly').grid(row=1, column=5, padx=5, pady=5)

        # --- Controls ---
        control_frame = ttk.Frame(main_frame, style='TFrame')
        control_frame.pack(fill=tk.X, pady=10)
        self.calculate_button = ttk.Button(control_frame, text="Calculate Aspects", command=self.start_calculation_thread)
        self.calculate_button.pack(side=tk.LEFT, padx=5)
        self.progress = ttk.Progressbar(control_frame, orient=tk.HORIZONTAL, length=300, mode='determinate')
        self.progress.pack(side=tk.LEFT, padx=10, expand=True, fill=tk.X)
        self.status_label = ttk.Label(control_frame, text="Ready")
        self.status_label.pack(side=tk.LEFT, padx=5)


        # --- Results Display ---
        self.results_text = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, height=20, bg="#1E1E1E", fg="white", font=("Courier New", 10))
        self.results_text.pack(fill=tk.BOTH, expand=True, pady=10)

    def get_julian_day(self, dt_obj):
        """Converts a datetime object to a Julian Day number."""
        return swe.utc_to_jd(dt_obj.year, dt_obj.month, dt_obj.day, dt_obj.hour, dt_obj.minute, dt_obj.second, 1)[1]

    def get_planet_longitude(self, jd, planet_id):
        """Gets the ecliptic longitude of a planet."""
        # The flags mean: geocentric, sidereal mode (0), no speed calculation
        return swe.calc_ut(jd, planet_id, swe.FLG_SWIEPH | swe.FLG_SPEED)[0][0]

    def get_zodiac_sign(self, longitude):
        """Gets the zodiac sign for a given longitude."""
        return ZODIAC_SIGNS[int(longitude / 30)]

    def calculate_angular_separation(self, lon1, lon2):
        """Calculates the shortest angle between two longitudes."""
        angle = abs(lon1 - lon2)
        if angle > 180:
            angle = 360 - angle
        return angle

    def start_calculation_thread(self):
        """Starts the calculation in a separate thread to keep the GUI responsive."""
        try:
            self.start_date = datetime.strptime(self.start_date_var.get(), '%Y-%m-%d').replace(tzinfo=timezone.utc)
            self.end_date = datetime.strptime(self.end_date_var.get(), '%Y-%m-%d').replace(tzinfo=timezone.utc)
            if self.start_date >= self.end_date:
                messagebox.showerror("Invalid Date", "Start date must be before end date.")
                return
        except ValueError:
            messagebox.showerror("Invalid Date Format", "Please use YYYY-MM-DD format.")
            return
            
        self.calculate_button.config(state=tk.DISABLED)
        self.results_text.delete('1.0', tk.END)
        self.status_label.config(text="Calculating...")
        
        calc_thread = threading.Thread(target=self.find_aspects, daemon=True)
        calc_thread.start()

    def find_aspects(self):
        """The main logic for finding aspects."""
        planet1_id = PLANETS[self.planet1_var.get()]
        planet2_id = PLANETS[self.planet2_var.get()]
        aspect_angle = ASPECTS[self.aspect_var.get()]
        
        current_date = self.start_date
        total_days = (self.end_date - self.start_date).days
        
        day_count = 0
        while current_date < self.end_date:
            # Update progress bar
            progress_val = (day_count / total_days) * 100
            self.progress['value'] = progress_val
            self.status_label.config(text=f"Checking {current_date.strftime('%Y-%m-%d')}...")

            jd_start_of_day = self.get_julian_day(current_date)
            lon1_start = self.get_planet_longitude(jd_start_of_day, planet1_id)
            lon2_start = self.get_planet_longitude(jd_start_of_day, planet2_id)
            
            # We check the angular separation every few minutes
            for minute_of_day in range(0, 1440, 10): # Check every 10 minutes
                time_offset = timedelta(minutes=minute_of_day)
                check_time = current_date + time_offset
                jd_check = self.get_julian_day(check_time)
                
                lon1_now = self.get_planet_longitude(jd_check, planet1_id)
                lon2_now = self.get_planet_longitude(jd_check, planet2_id)

                # Check the separation in the previous step to see if we crossed the aspect
                prev_time = check_time - timedelta(minutes=10)
                jd_prev = self.get_julian_day(prev_time)
                lon1_prev = self.get_planet_longitude(jd_prev, planet1_id)
                lon2_prev = self.get_planet_longitude(jd_prev, planet2_id)

                # This logic checks if the target aspect angle was crossed between the previous and current step
                # It handles both applying (moving towards) and separating (moving away) aspects
                prev_diff = self.calculate_angular_separation(lon1_prev, lon2_prev) - aspect_angle
                now_diff = self.calculate_angular_separation(lon1_now, lon2_now) - aspect_angle
                
                if prev_diff * now_diff < 0:
                    # Aspect was crossed. Now we find the exact minute.
                    exact_time = self.binary_search_for_aspect(prev_time, check_time, planet1_id, planet2_id, aspect_angle)
                    if exact_time:
                        self.display_result(exact_time, planet1_id, planet2_id)
                        break # Move to the next day once aspect is found

            day_count += 1
            current_date += timedelta(days=1)
        
        self.status_label.config(text="Calculation complete.")
        self.progress['value'] = 100
        self.calculate_button.config(state=tk.NORMAL)

    def binary_search_for_aspect(self, start_dt, end_dt, p1_id, p2_id, aspect_angle):
        """Finds the exact time of an aspect within a small time window."""
        low_dt = start_dt
        high_dt = end_dt
        
        for _ in range(15): # 15 iterations are enough to get second-level precision
            mid_dt = low_dt + (high_dt - low_dt) / 2
            jd_mid = self.get_julian_day(mid_dt)
            
            lon1 = self.get_planet_longitude(jd_mid, p1_id)
            lon2 = self.get_planet_longitude(jd_mid, p2_id)
            
            current_sep = self.calculate_angular_separation(lon1, lon2)
            
            jd_low = self.get_julian_day(low_dt)
            lon1_low = self.get_planet_longitude(jd_low, p1_id)
            lon2_low = self.get_planet_longitude(jd_low, p2_id)
            low_sep = self.calculate_angular_separation(lon1_low, lon2_low)
            
            if (low_sep - aspect_angle) * (current_sep - aspect_angle) < 0:
                high_dt = mid_dt
            else:
                low_dt = mid_dt
        
        return low_dt

    def display_result(self, dt_obj, p1_id, p2_id):
        """Formats and displays a result in the text box."""
        jd = self.get_julian_day(dt_obj)
        lon1 = self.get_planet_longitude(jd, p1_id)
        lon2 = self.get_planet_longitude(jd, p2_id)
        
        sign1 = self.get_zodiac_sign(lon1)
        sign2 = self.get_zodiac_sign(lon2)
        
        date_str = dt_obj.strftime('%Y/%m/%d %H:%M:%S')
        day_of_week = dt_obj.strftime('%A')
        
        result_line = f"{date_str} {day_of_week} ({sign1}, {sign2})\n"
        
        # We need to schedule the GUI update from the main thread
        self.after(0, lambda: self.results_text.insert(tk.END, result_line))


if __name__ == "__main__":
    app = AspectFinderApp()
    app.mainloop()
