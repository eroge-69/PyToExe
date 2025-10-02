import tkinter as tk
from tkinter import ttk, messagebox, colorchooser
import mysql.connector

db_host = "localhost"
db_user = "root"
db_pass = "1234"
db_name = "car"

class CarApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Car Info - MySQL")
        self.geometry("980x560")
        self.resizable(False, False)

        self.con = mysql.connector.connect(
            host=db_host,
            user=db_user,
            password=db_pass,
            database=db_name
        )
        self.cur = self.con.cursor()

        self.rowid = None
        self.saved = False
        self.editing = False

        self.company = tk.StringVar()
        self.model = tk.StringVar()
        self.year = tk.StringVar()
        self.color = tk.StringVar(value="Choice")
        self.passenger = tk.IntVar(value=2)
        self.price = tk.StringVar()
        self.petrol = tk.IntVar(value=0)
        self.gas = tk.IntVar(value=0)
        self.electric = tk.IntVar(value=0)
        self.trunk = tk.IntVar(value=-1)
        self.transmission = tk.StringVar()
        self.distance = tk.StringVar()
        self.fuel_tank = tk.IntVar(value=10)

        self.build_ui()
        self.protocol("WM_DELETE_WINDOW", self.do_close)

    def build_ui(self):
        padx, pady = 20, 10

        ttk.Label(self, text="Company:").grid(row=0, column=0, sticky="w", padx=padx, pady=pady)
        self.ent_company = ttk.Entry(self, textvariable=self.company, width=36)
        self.ent_company.grid(row=0, column=0, sticky="e", padx=(200,20))

        ttk.Label(self, text="Product Year:").grid(row=1, column=0, sticky="w", padx=padx, pady=pady)
        self.ent_year = ttk.Entry(self, textvariable=self.year, width=36)
        self.ent_year.grid(row=1, column=0, sticky="e", padx=(200,20))

        ttk.Label(self, text="Passenger Capacity:").grid(row=2, column=0, sticky="w", padx=padx, pady=pady)
        self.spin_passenger = tk.Spinbox(self, from_=2, to=8, textvariable=self.passenger, width=34)
        self.spin_passenger.grid(row=2, column=0, sticky="e", padx=(200,20))

        chk_frame = ttk.Frame(self)
        chk_frame.grid(row=3, column=0, sticky="w", padx=padx, pady=pady)
        ttk.Label(chk_frame, text="Fuel:").pack(side="left")
        ttk.Checkbutton(chk_frame, text="Petrol", variable=self.petrol).pack(side="left", padx=6)
        ttk.Checkbutton(chk_frame, text="Gas", variable=self.gas).pack(side="left", padx=6)
        ttk.Checkbutton(chk_frame, text="Electric", variable=self.electric).pack(side="left", padx=6)

        ttk.Label(self, text="Distance:").grid(row=6, column=0, sticky="w", padx=padx, pady=pady)
        self.ent_distance = ttk.Entry(self, textvariable=self.distance, width=36)
        self.ent_distance.grid(row=6, column=0, sticky="e", padx=(200,20))

        ttk.Button(self, text="close", command=self.do_close).grid(row=8, column=0, sticky="w", padx=85, pady=(30,6))
        ttk.Button(self, text="clear", command=self.do_clear).grid(row=9, column=0, sticky="w", padx=85, pady=6)

        ttk.Label(self, text="Model:").grid(row=0, column=1, sticky="w", padx=padx, pady=pady)
        self.ent_model = ttk.Entry(self, textvariable=self.model, width=36)
        self.ent_model.grid(row=0, column=1, sticky="e", padx=(180,20))

        ttk.Label(self, text="Color:").grid(row=1, column=1, sticky="w", padx=padx, pady=pady)
        color_frame = ttk.Frame(self)
        color_frame.grid(row=1, column=1, sticky="e", padx=(180,20))
        self.ent_color = ttk.Entry(color_frame, textvariable=self.color, width=28)
        self.ent_color.pack(side="left")
        ttk.Button(color_frame, text="Pick", command=self.pick_color).pack(side="left", padx=6)

        ttk.Label(self, text="Price:").grid(row=2, column=1, sticky="w", padx=padx, pady=pady)
        self.ent_price = ttk.Entry(self, textvariable=self.price, width=36)
        self.ent_price.grid(row=2, column=1, sticky="e", padx=(180,20))

        trunk_frame = ttk.Frame(self)
        trunk_frame.grid(row=3, column=1, sticky="w", padx=padx, pady=pady)
        ttk.Label(trunk_frame, text="Trunk:").pack(side="left")
        ttk.Radiobutton(trunk_frame, text="Yes", variable=self.trunk, value=1).pack(side="left", padx=6)
        ttk.Radiobutton(trunk_frame, text="No", variable=self.trunk, value=0).pack(side="left", padx=6)

        trans_frame = ttk.Frame(self)
        trans_frame.grid(row=4, column=0, columnspan=2, sticky="ew", padx=20, pady=10)
        ttk.Label(trans_frame, text="Transmission:").pack(side="left", padx=6)
        for val in ["Manual","Automatic","CVT","DCT","Semi-Automatic"]:
            ttk.Radiobutton(trans_frame, text=val, variable=self.transmission, value=val).pack(side="left", padx=6)

        ttk.Label(self, text="Fuel Tank:").grid(row=6, column=1, sticky="w", padx=padx, pady=pady)
        self.spin_fuel = tk.Spinbox(self, from_=10, to=140, textvariable=self.fuel_tank, width=34)
        self.spin_fuel.grid(row=6, column=1, sticky="e", padx=(180,20))

        ttk.Button(self, text="submit", command=self.do_submit).grid(row=8, column=1, sticky="e", padx=85, pady=(30,6))
        self.btn_edit = ttk.Button(self, text="edit", command=self.do_edit)
        self.btn_edit.grid(row=9, column=1, sticky="e", padx=85, pady=6)

    def pick_color(self):
        res = colorchooser.askcolor(title="choose color")
        if res and res[1]:
            self.color.set(res[1])

    def validate(self):
        errs = []
        if len(self.company.get().strip()) < 2: errs.append("Company too short")
        if len(self.model.get().strip()) < 2: errs.append("Model too short")
        if not self.year.get().isdigit(): errs.append("Year invalid")
        else:
            y = int(self.year.get())
            if y < 1995 or y > 2025: errs.append("Year out of range")
        if len(self.color.get().strip()) < 3: errs.append("Color invalid")
        if not (2 <= self.passenger.get() <= 8): errs.append("Passenger range")
        if not self.price.get().isdigit(): errs.append("Price must be int")
        elif int(self.price.get()) <= 1000: errs.append("Price too low")
        if self.trunk.get() not in (0,1): errs.append("Trunk missing")
        if not self.transmission.get(): errs.append("Transmission required")
        try:
            d = float(self.distance.get())
            if d <= 0: errs.append("Distance must be >0")
        except: errs.append("Distance invalid")
        try:
            f = int(self.fuel_tank.get())
            if not (10 <= f <= 140): errs.append("Fuel tank range")
        except: errs.append("Fuel tank invalid")
        return errs
#chatgpt
    def do_submit(self):
        errs = self.validate()
        if errs:
            messagebox.showerror("Error", "\n".join(errs))
            return
        sql = """insert into cars
                 (company,model,product_year,color,passenger_capacity,price,
                  petrol,gas,electric,trunk,transmission,distance,fuel_tank)
                 values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
        vals = (self.company.get(),self.model.get(),int(self.year.get()),self.color.get(),
                self.passenger.get(),int(self.price.get()),self.petrol.get(),self.gas.get(),
                self.electric.get(),self.trunk.get(),self.transmission.get(),
                float(self.distance.get()),int(self.fuel_tank.get()))
#——————
        self.cur.execute(sql, vals)
        self.con.commit()
        self.rowid = self.cur.lastrowid
        self.saved = True
        self.editing = False
        messagebox.showinfo("OK","Saved!")

    def do_edit(self):
        if not self.saved:
            messagebox.showinfo("Info","Submit first")
            return
        errs = self.validate()
        if errs:
            messagebox.showerror("Error","\n".join(errs))
            return
        sql = """update cars set
                 company=%s,model=%s,product_year=%s,color=%s,passenger_capacity=%s,price=%s,
                 petrol=%s,gas=%s,electric=%s,trunk=%s,transmission=%s,distance=%s,fuel_tank=%s
                 where id=%s"""
        vals = (self.company.get(),self.model.get(),int(self.year.get()),self.color.get(),
                self.passenger.get(),int(self.price.get()),self.petrol.get(),self.gas.get(),
                self.electric.get(),self.trunk.get(),self.transmission.get(),
                float(self.distance.get()),int(self.fuel_tank.get()),self.rowid)
        self.cur.execute(sql, vals)
        self.con.commit()
        messagebox.showinfo("OK","Updated")

    def do_clear(self):
        self.company.set(""); self.model.set(""); self.year.set("")
        self.color.set("Choice"); self.passenger.set(2); self.price.set("")
        self.petrol.set(0); self.gas.set(0); self.electric.set(0)
        self.trunk.set(-1); self.transmission.set(""); self.distance.set("")
        self.fuel_tank.set(10)
        self.saved = False; self.editing = False; self.rowid = None

    def do_close(self):
        if messagebox.askyesno("Close","Exit?"):
            self.cur.close()
            self.con.close()
            self.destroy()

if __name__ == "__main__":
    CarApp().mainloop()
