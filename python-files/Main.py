import customtkinter as ctk
import tkinter as tk
from PIL import Image
import csv
from tkinter import messagebox
import os
import subprocess
import sys
import re
import xml.etree.ElementTree as ET

#Program: Weightlifting Assistance Program
#Author: Wilfred Johnson wjoh0035@mhs.vic.edu.au
#Summary: This program takes user information related to their weightlifting capabilities, 
#         and uses it to extrapolate the heaviest weight they an theoretically lift, 
#         users can store their data and compare it against others on the leaderboard. 
#Updated 17/08/2025
#Version: Alpha 0.4
#License: Python, CustomTKinter, Visual Studio Code

#program setup
ctk.set_appearance_mode("dark")
root = ctk.CTk()
root.geometry('960x540')
root.title("Weightlifting Assistance Program")
root.minsize(960, 540)
font_name = "Arial"  


#grid for placing objects on screen
root.grid_rowconfigure(0, weight=0)
root.grid_rowconfigure(1, weight=1)
root.grid_columnconfigure(0, weight=1)

#Program header/frame for navigation buttons
headerFrame = ctk.CTkFrame(root)
headerFrame.grid(row=0, column=0, sticky="nesw")
headerFrame.grid_rowconfigure(0, weight=1)
for i in range(10):
    headerFrame.grid_columnconfigure(i, weight=1)

#program logo (top left)
logo_path = os.path.join(os.path.dirname(__file__), "icon.png")
pil_image = Image.open(logo_path)
aspect_ratio = pil_image.width / pil_image.height
scaled_width = int(50 * aspect_ratio)
logo_image = ctk.CTkImage(light_image=pil_image, dark_image=pil_image, size=(scaled_width, 60))


ctk.CTkLabel(headerFrame, image=logo_image, text="", fg_color="#0a0a0a")\
    .grid(row=0, column=0, columnspan=2, sticky="nsew")

#determines active tab when navigation buttons are pressed
def set_active(button):
    for btn in (topNavCalcBtn, topNavLeadBtn):
        btn.configure(fg_color="#121212")
    button.configure(fg_color="#1e1e1e")

def show_calc_tab():
    calcTab.lift()
    set_active(topNavCalcBtn)

def show_lead_tab():
    leadTab.lift()
    set_active(topNavLeadBtn)
    populate_leaderboard()



#Navigation Buttons
topNavCalcBtn = ctk.CTkButton(headerFrame, text="1RM Calculator", command=show_calc_tab,
                              corner_radius=0, fg_color="#121212", hover=False,
                              text_color="white", height=70)
topNavCalcBtn.grid(row=0, column=2, columnspan=3, sticky="nesw")

topNavLeadBtn = ctk.CTkButton(headerFrame, text="Leaderboard", command=show_lead_tab,
                               corner_radius=0, fg_color="#121212", hover=False,
                               text_color="white", height=70)
topNavLeadBtn.grid(row=0, column=5, columnspan=3, sticky="nesw")

ctk.CTkLabel(headerFrame, text="", fg_color="#0a0a0a")\
    .grid(row=0, column=8, columnspan=2, sticky="nesw")

#set up for seperate tabs
tabFrame = ctk.CTkFrame(root, fg_color="#1e1e1e")
tabFrame.grid(row=1, column=0, sticky="nesw")
tabFrame.grid_rowconfigure(0, weight=1)
tabFrame.grid_columnconfigure(0, weight=1)

calcTab = ctk.CTkFrame(tabFrame, fg_color="#1e1e1e")
leadTab = ctk.CTkFrame(tabFrame, fg_color="#1e1e1e")
calcTab.grid(row=0, column=0, sticky="nesw")
leadTab.grid(row=0, column=0, sticky="nesw")

#set up for 'Input' screen
input_frame = ctk.CTkFrame(calcTab, fg_color="#1e1e1e")
input_frame.pack(expand=True, fill="both")
input_frame.grid_columnconfigure((0, 1), weight=1)
input_frame.grid_rowconfigure(tuple(range(7)), weight=1)

ctk.CTkLabel(input_frame, text="One-Repetition-Maximum Weight Calculator",
             font=(font_name, 24, "bold"), text_color="white")\
    .grid(row=0, column=0, columnspan=2, pady=(20, 10))
ctk.CTkLabel(
    input_frame,
    text=(
        "Enter the weight you lifted for your set along with the number of repetitions "
        "(reps) you completed. This information allows us to calculate the maximum weight "
        "you should be able to lift as well as provide you with advice."
    ),
    font=(font_name, 14),
    text_color="#c0c0c0",
    wraplength=500,   # Wrap text at 500 pixels
    justify="left"    # Align text to the left
).grid(row=1, column=0, columnspan=2, pady=(0, 10))

ctk.CTkLabel(input_frame, text="Username:").grid(row=2, column=0, padx=20, sticky="e")
username_entry = ctk.CTkEntry(input_frame, width=200)
username_entry.grid(row=2, column=1, sticky="w")

ctk.CTkLabel(input_frame, text="Weight: (Kg or Lbs)").grid(row=3, column=0, padx=20, sticky="e")
weight_frame = ctk.CTkFrame(input_frame, fg_color="transparent")
weight_frame.grid(row=3, column=1, sticky="w")
weight_entry = ctk.CTkEntry(weight_frame, width=100)
weight_entry.pack(side="left", padx=(0, 10))
unit_dropdown = ctk.CTkOptionMenu(weight_frame, values=["Metric", "Imperial"])
unit_dropdown.set("Metric")
unit_dropdown.pack(side="left")

ctk.CTkLabel(input_frame, text="Repetitions:").grid(row=4, column=0, padx=20, sticky="e")
reps_entry = ctk.CTkEntry(input_frame, width=100)
reps_entry.grid(row=4, column=1, sticky="w")

ctk.CTkLabel(input_frame, text="Save my Data?").grid(row=5, column=0, padx=20, sticky="e")
save_checkbox = ctk.CTkCheckBox(input_frame, text="")
save_checkbox.grid(row=5, column=1, sticky="w")

#set up for "Results" Screen
results_frame = ctk.CTkFrame(calcTab, fg_color="#1e1e1e")
results_frame.pack_forget()
results_frame.grid_columnconfigure((0, 1), weight=1)
results_frame.grid_rowconfigure(0, weight=1)

left_col = ctk.CTkFrame(results_frame, fg_color="#2a2a2a")
right_col = ctk.CTkFrame(results_frame, fg_color="#2a2a2a")
left_col.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
right_col.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

ctk.CTkLabel(left_col, text="Your 1RM Estimate", font=(font_name, 20, "bold"))\
    .pack(pady=(20, 10))
scrollable_result = ctk.CTkScrollableFrame(left_col, fg_color="#2a2a2a", width=400, height=200)
scrollable_result.grid_columnconfigure(0, weight=1)  # centers content horizontally
scrollable_result.pack(expand=True, fill="both", padx=10, pady=10)

advice_level_label = ctk.CTkLabel(right_col, text="", font=(font_name, 16, "bold"))
advice_level_label.pack(padx=10,pady=10)


advice_label = ctk.CTkLabel(right_col, text="", wraplength=350, justify="left", font=(font_name, 14))
advice_label.pack(padx=10, pady=10)

action_button_frame = ctk.CTkFrame(results_frame, fg_color="transparent")
action_button_frame.grid(row=1, column=0, columnspan=2, pady=(0, 20))
save_btn = ctk.CTkButton(action_button_frame, text="Save Results", width=200)
save_btn.pack(side="left", padx=10)

#resets screen when return button is pressed
def return_to_input():
    results_frame.pack_forget()
    input_frame.pack(expand=True, fill="both")
    username_entry.delete(0, tk.END)
    weight_entry.delete(0, tk.END)
    reps_entry.delete(0, tk.END)
    save_btn.configure(state="normal")

return_btn = ctk.CTkButton(action_button_frame, text="Return", width=200, command=return_to_input)
return_btn.pack(side="left", padx=10)


#user class stores all the information related to user, it contains functions to validate user inputs and use them to calculate results.
class User:
    def __init__(self, username, weight, reps, unit):
        self.username = username #string, the users name.
        self.weight = weight     #int/float, the weight input by the user, can be a float if converted from lbs.
        self.reps = reps         #int, how many repetitions they could lift the inputted weight for.
        self.unit = unit         #str, can be 'metric' or 'imperial' if they are measuring in Kg or Lbs for input weight.
        self.oneRM = self.calculate_1rm()   #float, the calculated value which represents the highest weight they could lift for 1 repetition.
        self.original_weight = weight if unit == "Metric" else round(weight / 0.453592, 2) #converts weight to Kg if in Lbs.

    #function: validates user input using if statements and logic comparisons for existence, range, and type checking.
    #input: user data in 'self'
    #output: will return true if valid or a string error message
    def validate(self):
        print(str(self.unit))

        if not self.username or len(self.username) > 30 or self.username.isspace():
            return "Invalid username"
        if not re.fullmatch(r"[A-Za-z ]+", self.username): #re.fullmatch checks that all characters are alphabetical in upper or lowercase.
            return "Username can only contain letters and spaces"
    
        if not isinstance(self.weight, int) or not (1 <= self.weight <= 1000):
            return "Invalid weight"
        if not isinstance(self.reps, int) or not (1 <= self.reps <= 30):    
            return "Invalid reps"
        return True

    #Function:Calculates the users theoretical 'one repetition maximum' (1RM) weight they can lift by using the Landers 1RM formula.
    #Input: weight and reps (Int)
    #Output: 1RM using landers formula (Float)
    def calculate_1rm(self):
        weight_kg = self.weight if self.unit == "Metric" else self.weight * 0.453592 #checks for unit of measurement
        print(f"Calculating 1RM with weight_kg ={weight_kg}, reps={self.reps}") #debugging statement for developers.

         # If only one rep, return exact entered weight (no rounding error)
        if self.reps == 1:
             return round(weight_kg, 2)

        return round((weight_kg * 100) / (101.3 - (2.67123 * self.reps)), 2) #approximation of landers formula.

    #Function: gets maximum liftable weight estimates for 1-20 reps with for loop structure.
    #Input: 1RM (Float)
    #Ouput: list of estimated weight the user can lift for 1-20 repetitions
    def get_rep_estimates(self):
        estimates = []
        for rep in range(1, 21):
            if rep == 1:
                estimates.append(self.oneRM)  # uses exact 1RM so there is no rounding errors.
            else:
                est = round(self.oneRM * ((101.3 - (2.67123 * rep)) / 100), 2) #landers formula
                estimates.append(est)
        return estimates


#contains extensive debugging statements which will be necessary if the advice system is improved in future versions.
#try-except control sctucture used to catch exceptions and parseerros when loading advice.
#XML filetype is used because it is perfect for nested categories of data, like levels,
#  and can be quickly parsed to return advice, which can also easily be changed in the file itself if necessary

class AdviceManager:
    def __init__(self, filepath="advice.xml"):
        self.filepath = filepath #str, where the advice.xml file is stored relative to the python script.
        self.adviceFile = self.load_advice()

    def load_advice(self):
        # Default empty advice dictionary
        advice = {"Beginner": "", "Intermediate": "", "Advanced": ""}
        
        if not os.path.exists(self.filepath):
            print(f"advice file not found at: {self.filepath}")
            return advice

        try:
            print(f"parsing the advice XML: {self.filepath}")
            tree = ET.parse(self.filepath)
            root = tree.getroot()

            for level in root.findall("Level"):
                name = level.get("name")
                text_raw = level.text

                print(f"Found <Level name='{name}'>")
                print(f"raw text: {repr(text_raw)}")

                if name is None:
                    print("skipped a <Level> with missing 'name'")
                    continue

                if name not in advice: #must be in beginner, intermediate, or advanced.
                    print(f"unrecognized level '{name}'")
                    continue

                if text_raw is None or not text_raw.strip(): #if advice category is empty
                    print(f"no advice text found for '{name}'")
                    continue

                advice[name] = text_raw.strip()
                print(f"Loaded advice for {name}: {advice[name]}")

            print(f"final loaded advice dictionary: {advice}")

        except ET.ParseError as e:
            print(f"XML parsing failed: {e}")
        except Exception as e:
            print(f"error while loading advice: {e}")

        return advice

    #Funciton: Determines user level based on 1RM and uses it to find suitable advice.
    #Input: advice file and 1RM.
    #Output: user level and a string containing what advice is to be displayed.
    def get_advice(self, one_rm):
        if not self.adviceFile:
            print("advice file not loaded correctly.")
            return "Error", "advice file did not load correctly"
        
        #sorts users into 3 categories based on 1RM in Kg.
        if one_rm < 60:
            level = "Beginner"
        elif one_rm < 100:
            level = "Intermediate"
        else:
            level = "Advanced"

        advice_text = self.adviceFile.get(level, "No advice available.")
        print(f"User level: {level}")
        print(f"Advice Text: {advice_text}")
        return level, advice_text


#Contains functions for storing,reading and sorting user data.
#csv filetype is used because it is easily readable/sortable for a leaderbaord, performant, and can be opened in excel. 

class DataStore:
    def __init__(self, file_path="userData.csv"): #where file is stored 
        self.file_path = file_path

    def save_user(self, user):
        #existence checks, creates new csv if not found
        if not os.path.exists(self.file_path):
            with open(self.file_path, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["Username", "1RM", "Weight", "Reps"])

        rows = []
        user_exists = False

        #opens in reader mode to check existing users.
        with open(self.file_path, "r", newline="") as f:
            reader = csv.reader(f)
            header = next(reader)#skips headers
            for row in reader:#loops through each of the rows in the csv file.
                if not row or len(row) < 4:#skips if empty or incomplete
                    continue

                #if current username matches existing username, mark as already existing and dont add it.
                if row[0] == user.username:
                    user_exists = True
                    continue
                rows.append(row)

        if user_exists:
            if not messagebox.askyesno("Confirm Overwrite", f"{user.username} already exists. Overwrite?"):
                return

        #if user input in lbs, it is converted to always save in Kg.
        if user.unit == "Imperial":
            weight_in_kg = round(user.weight * 0.453592, 2)
        else:
            weight_in_kg = round(user.weight, 2)

        rows.append([user.username, user.oneRM, weight_in_kg, user.reps])

        with open(self.file_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Username", "1RM", "Weight", "Reps"])
            writer.writerows(rows)

        save_btn.configure(state="disabled")
        messagebox.showinfo("Saved", "Results saved successfully.")


    def load_leaderboard(self):
        if not os.path.exists(self.file_path):#returns empty list if file path was incorrect.
            return []

        with open(self.file_path, "r") as f:
            reader = list(csv.DictReader(f))  # Converts reader to a list

        #Converts 1RM values to float
        for row in reader:
            row["1RM"] = float(row["1RM"])

        #Selection Sort Algorithm:
        n = len(reader)
        for i in range(n):
            # Assumes that the first unsorted element is the max
            max_index = i
            
            #Searches the unsorted portion for a higher 1RM:
            for j in range(i + 1, n):
                if reader[j]["1RM"] > reader[max_index]["1RM"]:
                    max_index = j  #Updates max_index if a higher 1RM is found
            
            #swap the larger 1RM with the first unsorted element
            if max_index != i:
                reader[i], reader[max_index] = reader[max_index], reader[i]
        
        #list should now be sorted
        return reader

def switch_to_results():
    input_frame.pack_forget()
    results_frame.pack(expand=True, fill="both")

#Function: does validation and gets advice to display on results screen.
#input: entry boxes, unit dropdown and check box on input screen.
#output: displays results screen with advice and calculations.
def validate_and_calculate():
    #validates user inputs using try-except structure to catch valueerrors that may arise during conversion.
    try:
        weight = int(weight_entry.get())
        reps = int(reps_entry.get())
    except ValueError:
        messagebox.showerror("Error", "Weight and Reps must be whole numbers.")
        return
    
        #Converts the  weight from lbs to kg if imperial is selected in dropdown menu
    unit = unit_dropdown.get()
    original_weight = weight  # store what the user typed

    # Only convert to kg for calculations and saving
    weight_kg = weight * 0.453592 if unit == "Imperial" else weight
    
    user = User(username_entry.get().strip(), weight_kg, reps, unit)



    user = User(username_entry.get().strip(), weight, reps, unit_dropdown.get())
    valid = user.validate() #calls more in-depth validation function
    if valid is not True:
        messagebox.showerror("Validation Error", valid)
        return

    for widget in scrollable_result.winfo_children():
        widget.destroy()

    #determines whether results screen is in Kg or Lbs
    unit_suffix = "kg" if user.unit == "Metric" else "lbs"

    for i, est in enumerate(user.get_rep_estimates(), 1):
        display_est = est if user.unit == "Metric" else round(est / 0.453592, 2) #kg/lbs conversion

        ctk.CTkLabel(scrollable_result, text=f"{i} reps: {display_est:.2f} {unit_suffix}", font=(font_name, 28))\
            .grid(row=i, column=0, sticky="n", pady=10)



    advice_manager = AdviceManager()
    level, advice = advice_manager.get_advice(user.oneRM) #requests advice then displays it
    advice_level_label.configure(text=f"{level} Advice:")
    advice_label.configure(text=advice)

    print(f"1RM = {user.oneRM}, Advice Level = {level}")
    print(f"advice Text: {advice}")

    

    switch_to_results()

    if save_checkbox.get():
        DataStore().save_user(user)

    save_btn.configure(command=lambda: DataStore().save_user(user))
    save_btn.configure(state="normal")

calc_button = ctk.CTkButton(input_frame, text="Calculate", width=200, command=validate_and_calculate)
calc_button.grid(row=6, column=0, columnspan=2, pady=30)

#Leaderboard setup
leadTab.grid_rowconfigure(1, weight=1)
leadTab.grid_columnconfigure(0, weight=1)

ctk.CTkLabel(leadTab, text="Highest PR Leaderboard", font=(font_name, 24, "bold"), text_color="white")\
    .grid(row=0, column=0, sticky="w", padx=20, pady=(20, 10))

# Unit dropdown for leaderboard
leaderboard_unit = ctk.StringVar(value="Metric")
def on_unit_change(*args):
    populate_leaderboard(search_entry.get().strip())

unit_dropdown_lead = ctk.CTkOptionMenu(
    leadTab,
    values=["Metric", "Imperial"],
    variable=leaderboard_unit,
    command=lambda _: populate_leaderboard(search_entry.get().strip())
)
unit_dropdown_lead.grid(row=0, column=1, sticky="e", padx=(0, 20), pady=(20, 10))

table_frame = ctk.CTkScrollableFrame(leadTab, fg_color="#2a2a2a", height=300, width=880, corner_radius=10)
table_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=20, pady=10)

headers = ["Place", "Name", "Estimated 1RM", "Input Weight", "Input Reps"]
for col, title in enumerate(headers):
    table_frame.grid_columnconfigure(col, weight=1)
    ctk.CTkLabel(table_frame, text=title, text_color="white", font=(font_name, 14, "bold"))\
        .grid(row=0, column=col, sticky="nsew", padx=10, pady=(10, 5))

#function: displays leaderboard by filling in a table, also sorts based on position and search query.
#input: seach term, unit of measurement and leaderboard
#ouput: leaderboard with rankings, filtered by search query
def populate_leaderboard(search_term=""):
    leaderboard = DataStore().load_leaderboard()
    
    #Clears table rows except for headers
    for widget in table_frame.winfo_children()[len(headers):]:
        widget.destroy()

    # Filter if there's a search term by comparing the lowercase search query against usernames in the leaderboard.
    if search_term:
        leaderboard = [row for row in leaderboard if search_term.lower() in row["Username"].lower()]

    if not leaderboard:
        ctk.CTkLabel(table_frame, text="No data found.", text_color="white", fg_color="#2a2a2a")\
            .grid(row=1, column=0, columnspan=5, pady=10)
        return

    selected_unit = leaderboard_unit.get()

    #Determines the properties of the leaderboard positions, 1st-3rd have special colours and icons.
    for i, row in enumerate(leaderboard):
        if i == 0:
            place, color, size = "🥇", "#FFD700", 30
        elif i == 1:
            place, color, size = "🥈", "#C0C0C0", 30
        elif i == 2:
            place, color, size = "🥉", "#CD7F32", 30
        else:
            place, color, size = str(i + 1), "white", 15

        # Convert kg to lbs if imperial is selected
        one_rm = float(row["1RM"])
        weight = float(row["Weight"])
        if selected_unit == "Imperial":
            one_rm = round(one_rm / 0.453592, 2)
            weight = round(weight / 0.453592, 2)
            unit_suffix = "lbs"
        else:
            unit_suffix = "kg"

        row_values = [
            place,
            row["Username"],
            f"{one_rm} {unit_suffix}",
            f"{weight} {unit_suffix}",
            row["Reps"]
        ]

        #sets table aesthetics
        for c, val in enumerate(row_values): 
            ctk.CTkLabel(
                table_frame,
                text=val,
                text_color=color if c == 0 else "white",
                fg_color="#2a2a2a",
                font=(font_name, size if c == 0 else 13)
            ).grid(row=i + 1, column=c, sticky="nsew", padx=10, pady=5)

def update_leaderboard(*args):
    search_term = search_entry.get().strip()
    populate_leaderboard(search_term)

search_entry = ctk.CTkEntry(leadTab, placeholder_text="Search", width=200)
search_entry.grid(row=0, column=0, sticky="e", padx=(20, 5), pady=(20, 10))
search_entry.bind("<KeyRelease>", update_leaderboard)



#Opens userData csv file
#input: userData file location, filename is hardcoded, file path is relative to python file.
#output: opens the csv file using the operating systems default csv file viewer
def open_csv_file():
    file_path = os.path.join(os.getcwd(), "userData.csv")
    try:
        #if user has a Windows System
        if sys.platform == "win32":
            os.startfile(file_path)

        #MacOS system
        elif sys.platform == "darwin":  
            subprocess.call(["open", file_path])

        #linux system        
        else:  
            subprocess.call(["xdg-open", file_path])
    except Exception as e:
        messagebox.showerror(" Error", f"Error opening the User Data file:\n{e}")

open_button = ctk.CTkButton(
    leadTab,
    text="Open Results Spreads",
    width=200,
    height=40,
    font=(font_name, 14, "bold"),
    command=open_csv_file
)
open_button.grid(row=2, column=0, pady=20)


# Start the app
show_calc_tab()
root.mainloop()
