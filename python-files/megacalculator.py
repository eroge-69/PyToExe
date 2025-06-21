from tkinter import *
from tkinter import messagebox

class MegaCalculator:
    def __init__(self):
        self.window = Tk()
        self.window.title("Mega Calculator")
        self.window.geometry("800x600")
        self.window.config(bg="#00ff00")
        
        self.create_main_interface()
        
    def create_main_interface(self):
        # Main title
        title_label = Label(self.window, 
                          text="MEGA CALCULATOR", 
                          font=("Impact", 40, "bold"), 
                          bg="#00ff00",
                          fg="blue")
        title_label.pack(pady=20)
        
        # Calculator buttons frame
        buttons_frame = Frame(self.window, bg="#00ff00")
        buttons_frame.pack(pady=30)
        
        # Acceleration Calculator Button
        accel_button = Button(buttons_frame,
                            text="Acceleration Calculator",
                            font=("Impact", 25),
                            bg="blue",
                            fg="red",
                            activebackground="red",
                            activeforeground="blue",
                            command=self.open_acceleration_calculator)
        accel_button.grid(row=0, column=0, padx=20, pady=20)
        
        # Weight Calculator Button
        weight_button = Button(buttons_frame,
                             text="Weight Calculator",
                             font=("Impact", 25),
                             bg="blue",
                             fg="red",
                             activebackground="red",
                             activeforeground="blue",
                             command=self.open_weight_calculator)
        weight_button.grid(row=0, column=1, padx=20, pady=20)
        
        # Percentage Calculator Button
        percent_button = Button(buttons_frame,
                              text="Percentage Calculator",
                              font=("Impact", 25),
                              bg="blue",
                              fg="red",
                              activebackground="red",
                              activeforeground="blue",
                              command=self.open_percentage_calculator)
        percent_button.grid(row=1, column=0, padx=20, pady=20)
        
        # Standard Calculator Button
        standard_button = Button(buttons_frame,
                               text="Standard Calculator",
                               font=("Impact", 25),
                               bg="blue",
                               fg="red",
                               activebackground="red",
                               activeforeground="blue",
                               command=self.open_standard_calculator)
        standard_button.grid(row=1, column=1, padx=20, pady=20)
        
        # Credits Button
        credits_button = Button(self.window,
                              text="Credits",
                              font=("Impact", 25),
                              bg="blue",
                              fg="red",
                              activebackground="red",
                              activeforeground="blue",
                              command=self.show_credits)
        credits_button.pack(pady=20)
        
    def open_acceleration_calculator(self):
        AccelerationCalculator()
        
    def open_weight_calculator(self):
        WeightCalculator()
        
    def open_percentage_calculator(self):
        PercentageCalculator()
        
    def open_standard_calculator(self):
        StandardCalculator()
        
    def show_credits(self):
        credit_window = Toplevel(self.window)
        credit_window.title("Credits")
        credit_window.geometry("400x200")
        credit_window.config(bg="#00ff00")
        
        Label(credit_window, 
             text="Creator: Ayan Ashraf", 
             font=("Impact", 30), 
             bg="#00ff00",
             fg="red").pack(pady=50)
        
    def run(self):
        self.window.mainloop()

class AccelerationCalculator:
    def __init__(self):
        self.window = Toplevel()
        self.window.title("Acceleration Calculator")
        self.window.geometry("900x530")
        self.window.config(bg="#00ff00")
        
        self.create_interface()
        
    def create_interface(self):
        # Final Velocity
        Label(self.window, 
             text="Enter Final Velocity (km/h):", 
             font=("Impact", 35), 
             bg="#00ff00").grid(row=0, column=0)
        self.final_velocity_entry = Entry(self.window, font=("Impact", 25))
        self.final_velocity_entry.grid(row=0, column=1)
        
        # Initial Velocity
        Label(self.window, 
             text="Enter Initial Velocity (km/h):", 
             font=("Impact", 35), 
             bg="#00ff00").grid(row=1, column=0)
        self.initial_velocity_entry = Entry(self.window, font=("Impact", 25))
        self.initial_velocity_entry.grid(row=1, column=1)
        
        # Time
        Label(self.window, 
             text="Enter Time (s):", 
             font=("Impact", 35), 
             bg="#00ff00").grid(row=2, column=0)
        self.time_entry = Entry(self.window, font=("Impact", 25))
        self.time_entry.grid(row=2, column=1)
        
        # Calculate Button
        Button(self.window,
              text="Calculate",
              font=("Impact", 25),
              bg="blue",
              fg="red",
              activebackground="red",
              activeforeground="blue",
              command=self.calculate).grid(row=3, column=0, columnspan=2, pady=20)
        
        # Result Label
        self.result_label = Label(self.window,
                                text="",
                                font=("Impact", 38),
                                bg="#00ff00")
        self.result_label.grid(row=4, column=0, columnspan=2)
        
    def calculate(self):
        try:
            final = float(self.final_velocity_entry.get())
            initial = float(self.initial_velocity_entry.get())
            time = float(self.time_entry.get())
            
            if time == 0:
                messagebox.showerror("Error", "Time cannot be zero")
                return
                
            # Convert km/h to m/s
            final_ms = final / 3.6
            initial_ms = initial / 3.6
            
            acceleration = (final_ms - initial_ms) / time
            self.result_label.config(text=f"{acceleration:.2f} m/s²")
            
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers")

class WeightCalculator:
    def __init__(self):
        self.window = Toplevel()
        self.window.title("Weight Calculator")
        self.window.geometry("900x600")
        self.window.config(bg="#00ff00")
        
        self.planets = {
            "earth": 9.8,
            "mars": 3.7,
            "mercury": 3.7,
            "venus": 8.9,
            "jupiter": 24.7,
            "saturn": 9.0,
            "uranus": 8.7,
            "neptune": 11,
            "sun": 274
        }
        
        self.create_interface()
        
    def create_interface(self):
        # Mass Input
        Label(self.window,
             text="Enter your mass in KG:",
             font=("Impact", 35),
             bg="#00ff00").grid(row=0, column=0)
        self.mass_entry = Entry(self.window, font=("Impact", 25))
        self.mass_entry.grid(row=0, column=1)
        
        # Planet Input
        Label(self.window,
             text="Enter planet name:",
             font=("Impact", 35),
             bg="#00ff00").grid(row=1, column=0)
        self.planet_entry = Entry(self.window, font=("Impact", 25))
        self.planet_entry.grid(row=1, column=1)
        
        # Calculate Button
        Button(self.window,
              text="Calculate",
              font=("Impact", 25),
              bg="blue",
              fg="red",
              activebackground="red",
              activeforeground="blue",
              command=self.calculate).grid(row=2, column=0, columnspan=2, pady=20)
        
        # Result Label
        self.result_label = Label(self.window,
                                text="",
                                font=("Impact", 35),
                                bg="#00ff00")
        self.result_label.grid(row=3, column=0, columnspan=2)
        
    def calculate(self):
        try:
            mass = float(self.mass_entry.get())
            planet = self.planet_entry.get().strip().lower()
            
            gravity = self.planets.get(planet)
            if gravity is None:
                messagebox.showerror("Error", "Invalid planet name!")
                return
                
            weight = mass * gravity
            self.result_label.config(text=f"Weight: {weight:.2f} N")
            
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers")

class PercentageCalculator:
    def __init__(self):
        self.window = Toplevel()
        self.window.title("Percentage Calculator")
        self.window.geometry("1200x800")
        self.window.config(bg="#00ff00")
        
        self.create_main_interface()
        
    def create_main_interface(self):
        Label(self.window,
             text="Percentage Calculator",
             font=("Impact", 35),
             bg="#00ff00").pack(pady=20)
             
        Label(self.window,
             text="Enter up to 8 subjects (leave blank for unused subjects):",
             font=("Impact", 20),
             bg="#00ff00").pack()
             
        self.subject_entries = []
        entry_frame = Frame(self.window, bg="#00ff00")
        entry_frame.pack(pady=20)
        
        for i in range(8):
            Label(entry_frame,
                 text=f"Subject {i+1}:",
                 font=("Impact", 20),
                 bg="#00ff00").grid(row=i, column=0, padx=10, pady=5)
                 
            entry = Entry(entry_frame, font=("Impact", 20))
            entry.grid(row=i, column=1, padx=10, pady=5)
            self.subject_entries.append(entry)
            
        Button(self.window,
              text="Continue",
              font=("Impact", 25),
              bg="blue",
              fg="red",
              activebackground="red",
              activeforeground="blue",
              command=self.open_marks_window).pack(pady=20)
              
    def open_marks_window(self):
        subjects = [entry.get().strip() for entry in self.subject_entries if entry.get().strip()]
        if not subjects:
            messagebox.showerror("Error", "Please enter at least one subject")
            return
            
        self.marks_window = Toplevel(self.window)
        self.marks_window.title("Enter Marks")
        self.marks_window.geometry("1000x600")
        self.marks_window.config(bg="#00ff00")
        
        self.obtained_entries = []
        self.total_entries = []
        
        Label(self.marks_window,
             text="Enter Marks",
             font=("Impact", 30),
             bg="#00ff00").pack(pady=10)
             
        marks_frame = Frame(self.marks_window, bg="#00ff00")
        marks_frame.pack()
        
        for i, subject in enumerate(subjects):
            Label(marks_frame,
                 text=f"{subject}:",
                 font=("Impact", 20),
                 bg="#00ff00").grid(row=i, column=0, padx=10, pady=5)
                 
            Label(marks_frame,
                 text="Obtained:",
                 font=("Impact", 20),
                 bg="#00ff00").grid(row=i, column=1, padx=10, pady=5)
                 
            obtained_entry = Entry(marks_frame, font=("Impact", 20))
            obtained_entry.grid(row=i, column=2, padx=10, pady=5)
            self.obtained_entries.append(obtained_entry)
            
            Label(marks_frame,
                 text="Total:",
                 font=("Impact", 20),
                 bg="#00ff00").grid(row=i, column=3, padx=10, pady=5)
                 
            total_entry = Entry(marks_frame, font=("Impact", 20))
            total_entry.grid(row=i, column=4, padx=10, pady=5)
            self.total_entries.append(total_entry)
            
        Button(self.marks_window,
              text="Calculate Percentage",
              font=("Impact", 25),
              bg="blue",
              fg="red",
              activebackground="red",
              activeforeground="blue",
              command=self.calculate_percentage).pack(pady=20)
              
        self.result_label = Label(self.marks_window,
                                text="",
                                font=("Impact", 30),
                                bg="#00ff00")
        self.result_label.pack(pady=20)
        
    def calculate_percentage(self):
        try:
            total_obtained = 0
            total_max = 0
            
            for obtained_entry, total_entry in zip(self.obtained_entries, self.total_entries):
                obtained = obtained_entry.get().strip()
                total = total_entry.get().strip()
                
                if not obtained or not total:
                    continue
                    
                obtained_val = float(obtained)
                total_val = float(total)
                
                if obtained_val > total_val:
                    self.result_label.config(text="Error: Obtained marks > Total marks")
                    return
                    
                total_obtained += obtained_val
                total_max += total_val
                
            if total_max == 0:
                self.result_label.config(text="Error: Total marks cannot be zero")
                return
                
            percentage = (total_obtained / total_max) * 100
            self.result_label.config(text=f"Percentage: {percentage:.2f}%")
            
        except ValueError:
            self.result_label.config(text="Error: Please enter valid numbers")

class StandardCalculator:
    def __init__(self):
        self.window = Toplevel()
        self.window.title("Standard Calculator")
        self.window.geometry("500x600")
        self.window.resizable(False, False)
        
        self.equation_text = ""
        self.equation_label = StringVar()
        
        self.create_interface()
        
    def create_interface(self):
        # Display
        Label(self.window,
             textvariable=self.equation_label,
             font=("Consolas", 30),
             bg="white",
             width=20,
             height=2,
             relief="sunken",
             anchor="e").pack(pady=20)
             
        # Buttons Frame
        buttons_frame = Frame(self.window)
        buttons_frame.pack()
        
        # Number Buttons
        buttons = [
            ("7", 0, 0), ("8", 0, 1), ("9", 0, 2), ("/", 0, 3),
            ("4", 1, 0), ("5", 1, 1), ("6", 1, 2), ("*", 1, 3),
            ("1", 2, 0), ("2", 2, 1), ("3", 2, 2), ("-", 2, 3),
            ("0", 3, 0), (".", 3, 1), ("=", 3, 2), ("+", 3, 3)
        ]
        
        for (text, row, col) in buttons:
            Button(buttons_frame,
                  text=text,
                  font=("Consolas", 20),
                  width=5,
                  height=2,
                  command=lambda t=text: self.button_press(t)).grid(row=row, column=col)
                  
        # Clear Button
        Button(self.window,
              text="Clear",
              font=("Consolas", 20),
              width=20,
              height=2,
              command=self.clear).pack(pady=10)
              
    def button_press(self, num):
        self.equation_text += str(num)
        self.equation_label.set(self.equation_text)
        
    def clear(self):
        self.equation_text = ""
        self.equation_label.set(self.equation_text)
        
    def equals(self):
        try:
            total = str(eval(self.equation_text))
            self.equation_label.set(total)
            self.equation_text = total
        except ZeroDivisionError:
            messagebox.showerror("Error", "Cannot divide by zero")
            self.clear()
        except:
            messagebox.showerror("Error", "Invalid calculation")
            self.clear()

# Run the application
if __name__ == "__main__":
    app = MegaCalculator()
    app.run()
