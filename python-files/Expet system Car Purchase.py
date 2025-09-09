import tkinter as tk
from tkinter import ttk, messagebox

class CarKnowledgeBase:
    def __init__(self):
        self.cars = [
            # Economic / Small Cars (expanded)
            {"model": "Hyundai i10", "price": 12000, "fuel": "Petrol", "economy": "Excellent", "seats": 4, "type": "Small"},
            {"model": "Kia Picanto", "price": 13000, "fuel": "Petrol", "economy": "Excellent", "seats": 4, "type": "Small"},
            {"model": "Toyota Aygo", "price": 12500, "fuel": "Petrol", "economy": "Excellent", "seats": 4, "type": "Small"},
            {"model": "Volkswagen Up", "price": 14000, "fuel": "Petrol", "economy": "Excellent", "seats": 4, "type": "Small"},
            {"model": "Fiat 500", "price": 14500, "fuel": "Petrol", "economy": "Very Good", "seats": 4, "type": "Small"},
            {"model": "Suzuki Swift", "price": 15000, "fuel": "Petrol", "economy": "Very Good", "seats": 5, "type": "Small"},
            {"model": "Ford Fiesta", "price": 16000, "fuel": "Petrol", "economy": "Very Good", "seats": 5, "type": "Small"},
            {"model": "Mazda 2", "price": 16500, "fuel": "Petrol", "economy": "Very Good", "seats": 5, "type": "Small"},
            {"model": "Renault Clio", "price": 15500, "fuel": "Petrol", "economy": "Good", "seats": 5, "type": "Small"},
            {"model": "Peugeot 208", "price": 17000, "fuel": "Petrol", "economy": "Good", "seats": 5, "type": "Small"},

            # Sedans (expanded)
            {"model": "Toyota Corolla", "price": 20000, "fuel": "Petrol", "economy": "Good", "seats": 5, "type": "Sedan"},
            {"model": "Honda Civic", "price": 22000, "fuel": "Petrol", "economy": "Very Good", "seats": 5, "type": "Sedan"},
            {"model": "Nissan Altima", "price": 25000, "fuel": "Petrol", "economy": "Good", "seats": 5, "type": "Sedan"},
            {"model": "Hyundai Elantra", "price": 19000, "fuel": "Petrol", "economy": "Good", "seats": 5, "type": "Sedan"},
            {"model": "Kia Cerato", "price": 21000, "fuel": "Petrol", "economy": "Good", "seats": 5, "type": "Sedan"},
            {"model": "Mazda 3", "price": 23000, "fuel": "Petrol", "economy": "Very Good", "seats": 5, "type": "Sedan"},
            {"model": "Volkswagen Jetta", "price": 21500, "fuel": "Petrol", "economy": "Good", "seats": 5, "type": "Sedan"},
            {"model": "Subaru Impreza", "price": 22500, "fuel": "Petrol", "economy": "Average", "seats": 5, "type": "Sedan"},
            {"model": "Skoda Octavia", "price": 24000, "fuel": "Petrol", "economy": "Very Good", "seats": 5, "type": "Sedan"},
            {"model": "BMW 3 Series", "price": 42000, "fuel": "Petrol", "economy": "Average", "seats": 5, "type": "Sedan"},

            # SUVs (expanded)
            {"model": "Toyota RAV4", "price": 30000, "fuel": "Hybrid", "economy": "Very Good", "seats": 5, "type": "SUV"},
            {"model": "Hyundai Tucson", "price": 28000, "fuel": "Petrol", "economy": "Good", "seats": 5, "type": "SUV"},
            {"model": "Toyota Highlander", "price": 40000, "fuel": "Hybrid", "economy": "Good", "seats": 7, "type": "SUV"},
            {"model": "Ford Explorer", "price": 42000, "fuel": "Petrol", "economy": "Average", "seats": 7, "type": "SUV"},
            {"model": "Honda CR-V", "price": 32000, "fuel": "Hybrid", "economy": "Very Good", "seats": 5, "type": "SUV"},
            {"model": "Mazda CX-5", "price": 31000, "fuel": "Petrol", "economy": "Good", "seats": 5, "type": "SUV"},
            {"model": "Nissan Rogue", "price": 29000, "fuel": "Petrol", "economy": "Good", "seats": 5, "type": "SUV"},
            {"model": "Subaru Forester", "price": 33000, "fuel": "Petrol", "economy": "Average", "seats": 5, "type": "SUV"},
            {"model": "Kia Sorento", "price": 35000, "fuel": "Petrol", "economy": "Good", "seats": 7, "type": "SUV"},
            {"model": "Volkswagen Tiguan", "price": 34000, "fuel": "Petrol", "economy": "Good", "seats": 5, "type": "SUV"},
            {"model": "Audi Q5", "price": 45000, "fuel": "Petrol", "economy": "Average", "seats": 5, "type": "SUV"},
            {"model": "Mercedes GLC", "price": 48000, "fuel": "Petrol", "economy": "Average", "seats": 5, "type": "SUV"},
            {"model": "Jeep Wrangler", "price": 38000, "fuel": "Petrol", "economy": "Poor", "seats": 5, "type": "SUV"},
            {"model": "Land Rover Discovery", "price": 55000, "fuel": "Petrol", "economy": "Poor", "seats": 7, "type": "SUV"},

            # Electric Cars (expanded)
            {"model": "Tesla Model 3", "price": 35000, "fuel": "Electric", "economy": "Excellent", "seats": 5, "type": "Electric"},
            {"model": "Nissan Leaf", "price": 32000, "fuel": "Electric", "economy": "Excellent", "seats": 5, "type": "Electric"},
            {"model": "Chevrolet Bolt", "price": 33000, "fuel": "Electric", "economy": "Excellent", "seats": 5, "type": "Electric"},
            {"model": "Hyundai Kona Electric", "price": 38000, "fuel": "Electric", "economy": "Excellent", "seats": 5, "type": "Electric"},
            {"model": "Kia Niro EV", "price": 40000, "fuel": "Electric", "economy": "Excellent", "seats": 5, "type": "Electric"},
            {"model": "Tesla Model Y", "price": 45000, "fuel": "Electric", "economy": "Excellent", "seats": 7, "type": "Electric"},
            {"model": "Ford Mustang Mach-E", "price": 44000, "fuel": "Electric", "economy": "Excellent", "seats": 5, "type": "Electric"},
            {"model": "Audi e-tron", "price": 67000, "fuel": "Electric", "economy": "Excellent", "seats": 5, "type": "Electric"},
            {"model": "Porsche Taycan", "price": 82000, "fuel": "Electric", "economy": "Excellent", "seats": 4, "type": "Electric"},
            {"model": "Volkswagen ID.4", "price": 41000, "fuel": "Electric", "economy": "Excellent", "seats": 5, "type": "Electric"},

            # Luxury (expanded)
            {"model": "BMW 5 Series", "price": 55000, "fuel": "Petrol", "economy": "Average", "seats": 5, "type": "Luxury"},
            {"model": "Mercedes-Benz E-Class", "price": 60000, "fuel": "Hybrid", "economy": "Good", "seats": 5, "type": "Luxury"},
            {"model": "Audi A6", "price": 58000, "fuel": "Petrol", "economy": "Average", "seats": 5, "type": "Luxury"},
            {"model": "Lexus ES", "price": 42000, "fuel": "Hybrid", "economy": "Very Good", "seats": 5, "type": "Luxury"},
            {"model": "Jaguar XF", "price": 45000, "fuel": "Petrol", "economy": "Average", "seats": 5, "type": "Luxury"},
            {"model": "Genesis G80", "price": 48000, "fuel": "Petrol", "economy": "Average", "seats": 5, "type": "Luxury"},
            {"model": "BMW 7 Series", "price": 86000, "fuel": "Petrol", "economy": "Poor", "seats": 5, "type": "Luxury"},
            {"model": "Mercedes S-Class", "price": 95000, "fuel": "Hybrid", "economy": "Average", "seats": 5, "type": "Luxury"},
            {"model": "Audi A8", "price": 87000, "fuel": "Petrol", "economy": "Average", "seats": 5, "type": "Luxury"},
            {"model": "Porsche Panamera", "price": 89000, "fuel": "Petrol", "economy": "Poor", "seats": 4, "type": "Luxury"},

            # Hybrid Cars (new category)
            {"model": "Toyota Prius", "price": 25000, "fuel": "Hybrid", "economy": "Excellent", "seats": 5, "type": "Hybrid"},
            {"model": "Honda Insight", "price": 24000, "fuel": "Hybrid", "economy": "Excellent", "seats": 5, "type": "Hybrid"},
            {"model": "Hyundai Ioniq", "price": 23000, "fuel": "Hybrid", "economy": "Excellent", "seats": 5, "type": "Hybrid"},
            {"model": "Kia Niro Hybrid", "price": 26000, "fuel": "Hybrid", "economy": "Excellent", "seats": 5, "type": "Hybrid"},
            {"model": "Ford Fusion Hybrid", "price": 28000, "fuel": "Hybrid", "economy": "Very Good", "seats": 5, "type": "Hybrid"},
            {"model": "Toyota Camry Hybrid", "price": 30000, "fuel": "Hybrid", "economy": "Very Good", "seats": 5, "type": "Hybrid"},
            {"model": "Lexus RX Hybrid", "price": 48000, "fuel": "Hybrid", "economy": "Good", "seats": 5, "type": "Hybrid"},
            {"model": "Hyundai Sonata Hybrid", "price": 28000, "fuel": "Hybrid", "economy": "Very Good", "seats": 5, "type": "Hybrid"},

            # Sports Cars (new category)
            {"model": "Mazda MX-5 Miata", "price": 27000, "fuel": "Petrol", "economy": "Good", "seats": 2, "type": "Sports"},
            {"model": "Ford Mustang", "price": 35000, "fuel": "Petrol", "economy": "Poor", "seats": 4, "type": "Sports"},
            {"model": "Chevrolet Camaro", "price": 37000, "fuel": "Petrol", "economy": "Poor", "seats": 4, "type": "Sports"},
            {"model": "Subaru BRZ", "price": 29000, "fuel": "Petrol", "economy": "Average", "seats": 4, "type": "Sports"},
            {"model": "Toyota GR86", "price": 30000, "fuel": "Petrol", "economy": "Average", "seats": 4, "type": "Sports"},
            {"model": "Nissan Z", "price": 42000, "fuel": "Petrol", "economy": "Poor", "seats": 2, "type": "Sports"},
            {"model": "Porsche 718 Cayman", "price": 62000, "fuel": "Petrol", "economy": "Average", "seats": 2, "type": "Sports"},
            {"model": "Chevrolet Corvette", "price": 65000, "fuel": "Petrol", "economy": "Poor", "seats": 2, "type": "Sports"},
            {"model": "BMW Z4", "price": 52000, "fuel": "Petrol", "economy": "Average", "seats": 2, "type": "Sports"},
            {"model": "Audi TT", "price": 46000, "fuel": "Petrol", "economy": "Average", "seats": 4, "type": "Sports"},
        ]

class CarAdvisor:
    def __init__(self, knowledge_base):
        self.knowledge_base = knowledge_base

    def recommend(self, budget, fuel, seats, economy, car_type, sort_by):
        matches = []
        for car in self.knowledge_base.cars:
            if (car["price"] <= budget and
                (fuel == "Any" or car["fuel"] == fuel) and
                car["seats"] >= seats and
                (economy == "Any" or car["economy"] == economy) and
                (car_type == "Any" or car["type"] == car_type)):
                matches.append(car)
        
        # Sort by selected criteria
        if sort_by == "Price (Low to High)":
            matches.sort(key=lambda x: x["price"])
        elif sort_by == "Price (High to Low)":
            matches.sort(key=lambda x: x["price"], reverse=True)
        elif sort_by == "Economy":
            economy_order = {"Excellent": 4, "Very Good": 3, "Good": 2, "Average": 1, "Poor": 0}
            matches.sort(key=lambda x: economy_order.get(x["economy"], 0), reverse=True)
        
        return matches if matches else None

class CarAdvisorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Car Purchase Advisor")
        self.root.geometry("800x700")
        self.root.resizable(True, True)

        # Configure style
        self.style = ttk.Style()
        self.style.configure('TFrame', background='#f0f0f0')
        self.style.configure('TLabel', background='#f0f0f0', font=('Arial', 10))
        self.style.configure('TButton', font=('Arial', 10))
        self.style.configure('Header.TLabel', font=('Arial', 16, 'bold'))

        self.kb = CarKnowledgeBase()
        self.engine = CarAdvisor(self.kb)

        self.create_widgets()

    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Header
        header = ttk.Label(main_frame, text="Car Purchase Advisor", style='Header.TLabel')
        header.grid(row=0, column=0, columnspan=2, pady=(0, 20))

        # Budget input
        ttk.Label(main_frame, text="Enter Budget ($):").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.budget_entry = ttk.Entry(main_frame)
        self.budget_entry.grid(row=1, column=1, padx=10, pady=10, sticky="ew")
        
        # Budget slider
        self.budget_var = tk.IntVar(value=50000)
        budget_slider = ttk.Scale(main_frame, from_=10000, to=150000, variable=self.budget_var, 
                                 orient=tk.HORIZONTAL, command=self.update_budget_entry)
        budget_slider.grid(row=2, column=0, columnspan=2, padx=10, pady=5, sticky="ew")

        # Fuel type
        ttk.Label(main_frame, text="Preferred Fuel Type:").grid(row=3, column=0, padx=10, pady=10, sticky="w")
        self.fuel_var = tk.StringVar(value="Any")
        fuel_combo = ttk.Combobox(main_frame, textvariable=self.fuel_var, 
                                 values=["Any", "Petrol", "Hybrid", "Electric", "Diesel"], state="readonly")
        fuel_combo.grid(row=3, column=1, padx=10, pady=10, sticky="ew")

        # Seats
        ttk.Label(main_frame, text="Minimum Seats:").grid(row=4, column=0, padx=10, pady=10, sticky="w")
        self.seats_var = tk.StringVar(value="5")
        seats_spinbox = ttk.Spinbox(main_frame, from_=2, to=9, textvariable=self.seats_var, width=10)
        seats_spinbox.grid(row=4, column=1, padx=10, pady=10, sticky="w")

        # Economy
        ttk.Label(main_frame, text="Fuel Economy Preference:").grid(row=5, column=0, padx=10, pady=10, sticky="w")
        self.economy_var = tk.StringVar(value="Any")
        economy_combo = ttk.Combobox(main_frame, textvariable=self.economy_var, 
                                    values=["Any", "Excellent", "Very Good", "Good", "Average", "Poor"], state="readonly")
        economy_combo.grid(row=5, column=1, padx=10, pady=10, sticky="ew")

        # Car type
        ttk.Label(main_frame, text="Car Type:").grid(row=6, column=0, padx=10, pady=10, sticky="w")
        self.type_var = tk.StringVar(value="Any")
        type_combo = ttk.Combobox(main_frame, textvariable=self.type_var, 
                                 values=["Any", "Small", "Sedan", "SUV", "Electric", "Luxury", "Hybrid", "Sports"], state="readonly")
        type_combo.grid(row=6, column=1, padx=10, pady=10, sticky="ew")
        
        # Sort by
        ttk.Label(main_frame, text="Sort By:").grid(row=7, column=0, padx=10, pady=10, sticky="w")
        self.sort_var = tk.StringVar(value="Price (Low to High)")
        sort_combo = ttk.Combobox(main_frame, textvariable=self.sort_var, 
                                 values=["Price (Low to High)", "Price (High to Low)", "Economy"], state="readonly")
        sort_combo.grid(row=7, column=1, padx=10, pady=10, sticky="ew")

        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=8, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="Find Cars", command=self.recommend).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="Clear", command=self.clear_form).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="Show All Cars", command=self.show_all).pack(side=tk.LEFT, padx=10)

        # Results frame
        results_frame = ttk.LabelFrame(main_frame, text="Recommended Cars", padding="10")
        results_frame.grid(row=9, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)

        # Create a treeview for results
        columns = ("model", "price", "fuel", "economy", "seats", "type")
        self.tree = ttk.Treeview(results_frame, columns=columns, show="headings", height=15)
        
        # Define headings
        self.tree.heading("model", text="Model")
        self.tree.heading("price", text="Price")
        self.tree.heading("fuel", text="Fuel")
        self.tree.heading("economy", text="Economy")
        self.tree.heading("seats", text="Seats")
        self.tree.heading("type", text="Type")
        
        # Define columns
        self.tree.column("model", width=180)
        self.tree.column("price", width=100)
        self.tree.column("fuel", width=80)
        self.tree.column("economy", width=100)
        self.tree.column("seats", width=60)
        self.tree.column("type", width=80)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

        # Configure grid weights
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(9, weight=1)
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

    def update_budget_entry(self, value):
        self.budget_entry.delete(0, tk.END)
        self.budget_entry.insert(0, str(int(float(value))))

    def recommend(self):
        try:
            budget = int(self.budget_entry.get())
            seats = int(self.seats_var.get())
            fuel = self.fuel_var.get()
            economy = self.economy_var.get()
            car_type = self.type_var.get()
            sort_by = self.sort_var.get()
        except ValueError:
            messagebox.showerror("Input Error", "Please enter valid numbers for budget and seats.")
            return

        results = self.engine.recommend(budget, fuel, seats, economy, car_type, sort_by)

        # Clear previous results
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        if results:
            for car in results:
                self.tree.insert("", tk.END, values=(
                    car["model"], 
                    f"${car['price']:,}", 
                    car["fuel"], 
                    car["economy"], 
                    car["seats"], 
                    car["type"]
                ))
        else:
            messagebox.showinfo("No Results", "No cars match your criteria. Try adjusting your filters.")

    def show_all(self):
        # Show all cars without filters
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        for car in self.kb.cars:
            self.tree.insert("", tk.END, values=(
                car["model"], 
                f"${car['price']:,}", 
                car["fuel"], 
                car["economy"], 
                car["seats"], 
                car["type"]
            ))

    def clear_form(self):
        self.budget_entry.delete(0, tk.END)
        self.budget_entry.insert(0, "50000")
        self.budget_var.set(50000)
        self.seats_var.set("5")
        self.fuel_var.set("Any")
        self.economy_var.set("Any")
        self.type_var.set("Any")
        self.sort_var.set("Price (Low to High)")
        
        for item in self.tree.get_children():
            self.tree.delete(item)

if __name__ == "__main__":
    root = tk.Tk()
    app = CarAdvisorGUI(root)
    root.mainloop()