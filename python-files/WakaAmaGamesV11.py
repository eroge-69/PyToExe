# Importing all my libraries
import os
import tkinter as tk
from tkinter import messagebox

# Create the main setup
class WakaAmaApp(tk.Tk):
    def __init__(self):
        super().__init__()

        # Set up the main window which will be displayed
        self.title("Waka Ama Games")
        self.geometry("400x300")
        self.selected_year = None  # Store selected year for future use

        # Welcome screen
        self.show_welcome()

    # Clear screen for future purpose when we change screens
    def clear_screen(self):
        for widget in self.winfo_children():
            widget.destroy()

    # Show the welcome screen with input instead of buttons
    def show_welcome(self):
        self.clear_screen()

        # Welcome message (Will change font and sizes after feedback)
        tk.Label(self, text="Welcome to Waka Ama Games", font=("Arial Bold", 19)).pack(pady=10)
        tk.Label(self, text="Enter the year you want to analyse (e.g. 2017):", font=("Arial", 13)).pack(pady=10)

        # Entry field for user input
        self.year_entry = tk.Entry(self, font=("Arial", 12))
        self.year_entry.pack(pady=5)

        # Submit button
        tk.Button(self, text="Proceed", font=("Arial", 13), command=self.handle_year_input).pack(pady=10)

    # Handle input from the entry field
    def handle_year_input(self):
        year_input = self.year_entry.get().strip()

        # Check if input is a 4-digit number
        if not year_input.isdigit() or len(year_input) != 4:
            messagebox.showerror("Invalid Input", "Invalid year entered. Please enter a valid 4-digit year like 2019 and avoid using letters.")
            return

        self.analyze_year(year_input)

    # When a year is selected, it changes the Waka nats (year) to the year selected
    def analyze_year(self, year):
        folder = f"WakaNats{year}"

        # Check if the folder exists otherwise error message and returns to start once clicked okay
        if not os.path.exists(folder):
            messagebox.showerror("Folder Not Found", f"The Folder '{folder}' was not found. Make sure it is in the same folder as the program and is named WakaNats (Year)")
            self.show_welcome()
            return

        self.clear_screen()
        self.selected_year = year

        # Title and file count display
        tk.Label(self, text=f"Waka Ama {year}", font=("Arial Bold", 20)).pack(pady=20)

        files = os.listdir(folder)
        lif_files = [f for f in files if f.lower().endswith('.lif')]
        # to store the lif files so that when we filter to Finals only we use this and other future purpose
        self.lif_files = lif_files
        self.folder_path = folder  # store the folder path for later use

        tk.Label(self, text=f"Found {len(lif_files)} .lif files in '{folder}'", font=("Arial", 14)).pack(pady=10)

        # Analyse button which will analyze the lif files and filter to finals only (.pack auttomatically positions the buttons so that I dont do it manually)
        tk.Button(self, text="Analyse Year", font=("Arial", 12), command=self.analyze_finals).pack(pady=20)

    def analyze_finals(self):
        self.clear_screen()

        # Display "Loading..." screen (need to fix this as it isnt being displayed as it runs too fast)
        tk.Label(self, text="Loading...", font=("Arial", 14)).pack(pady=30)
        self.update()

        # Filter for only finals files
 
        finals_files = [f for f in self.lif_files if "final" in f.lower()]

      
        # Award points to organizations
        self.points = {}       




        # Go through each final file and check lines for w12 and other criteria
        for file in finals_files:
            path = os.path.join(self.folder_path, file)
            with open(path, 'r') as f:
                lines = f.readlines()

                race_info = lines[0].lower()
                is_w12 = "w12" in race_info

                for line in lines[1:]:
                    data = line.strip().split(',')

                    if len(data) < 6:
                        continue

                    place = data[0].strip()
                    club = data[5].strip()

                    if not place.isdigit():
                        continue

                    place = int(place)

                    # points system defined for how much each place gets
                    if place == 1:
                        points = 8
                    elif place == 2:
                        points = 7
                    elif place == 3:
                        points = 6
                    elif place == 4:
                        points = 5
                    elif place == 5:
                        points = 4
                    elif place == 6:
                        points = 3
                    elif place == 7:
                        points = 2
                    else:
                        points = 1

                    # Gives points to both teams if W12 with two orgs
                    if is_w12 and "/" in club:
                        both = [c.strip() for c in club.split("/")]
                        for c in both:
                            self.points[c] = self.points.get(c, 0) + points
                    else:
                        self.points[club] = self.points.get(club, 0) + points

        # Clear loading screen and show number of files
        self.clear_screen()
        tk.Label(self, text=f"Found {len(finals_files)} number of Final files", font=("Arial", 16)).pack(pady=20)


        
        # Show results button 
       
        tk.Button(self, text="Show Results", font=("Arial", 12), command=self.show_results).pack(pady=10)

    # Shows all results 
    def show_results(self):
        self.clear_screen()
        
        # Results title on top 
        tk.Label(self, text="Results", font=("Arial Bold", 16)).pack(pady=10)

        # Create a canvas where results will be displayed without this we cant add scrolling for results
        canvas = tk.Canvas(self)
        canvas.pack(fill="both", expand=True)

        # frame inside the canvas for results
        frame = tk.Frame(canvas)
        canvas.create_window((0, 0), window=frame, anchor="nw")

        # Code required to make the canvas thing scrollable so that all results can be viewed
        def update_scroll_area(event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        def scroll_with_mouse(event):
            canvas.yview_scroll(-1 * int(event.delta / 120), "units")

        frame.bind("<Configure>", update_scroll_area)
        canvas.bind_all("<MouseWheel>", scroll_with_mouse)

        # sort results from highest points to lowest
        sorted_results = sorted(self.points.items(), key=lambda x: x[1], reverse=True)

       # Display results
        for club, points in sorted_results:
            tk.Label(frame, text=f"{club}: {points} points", font=("Arial", 12)).pack(anchor="w", padx=10, pady=2)
        
        # export to csv file button
        tk.Button(frame, text="Export to CSV", font=("Arial", 12), command=self.export_to_csv).pack(pady=10)

    # defining the csv so that we can make the button for now
    def export_to_csv(self):
        filename = f"WakaAmaResults{self.selected_year}.csv"
        with open(filename, "w") as file:
            file.write("Club,Points\n")
            for club, points in self.points.items():
                file.write(f"{club},{points}\n")
        messagebox.showinfo("Exported", f"Results saved to same file directory as program")


# Start the program
if __name__ == "__main__":
    app = WakaAmaApp()
    app.mainloop()
