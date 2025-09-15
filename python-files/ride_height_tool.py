
import tkinter as tk
from tkinter import filedialog, messagebox
from fpdf import FPDF
import os
from datetime import datetime

class RideHeightApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Ride Height Measurement Tool")
        self.screenshot_path = ""

        self.fields = {}
        self.create_form()

    def create_form(self):
        labels = ["Vehicle", "Brand", "Project", "Model", "Rim Diameter"]
        for i, label in enumerate(labels):
            tk.Label(self.root, text=label).grid(row=i, column=0, sticky="e")
            self.fields[label] = tk.Entry(self.root)
            self.fields[label].grid(row=i, column=1)

        self.corners = ["FL", "FR", "RL", "RR"]
        self.corner_fields = {}
        tk.Label(self.root, text="Corner").grid(row=0, column=3)
        tk.Label(self.root, text="Measured").grid(row=0, column=4)
        tk.Label(self.root, text="ECU").grid(row=0, column=5)
        tk.Label(self.root, text="Target").grid(row=0, column=6)

        for i, corner in enumerate(self.corners):
            tk.Label(self.root, text=corner).grid(row=i+1, column=3)
            self.corner_fields[corner] = {
                "Measured": tk.Entry(self.root),
                "ECU": tk.Entry(self.root),
                "Target": tk.Entry(self.root)
            }
            self.corner_fields[corner]["Measured"].grid(row=i+1, column=4)
            self.corner_fields[corner]["ECU"].grid(row=i+1, column=5)
            self.corner_fields[corner]["Target"].grid(row=i+1, column=6)
            self.corner_fields[corner]["Target"].insert(0, "500")

        tk.Button(self.root, text="Check", command=self.check).grid(row=6, column=4)
        tk.Button(self.root, text="Clear", command=self.clear).grid(row=6, column=5)
        tk.Button(self.root, text="Import Screenshot", command=self.import_screenshot).grid(row=6, column=0)
        tk.Button(self.root, text="Save as PDF", command=self.save_pdf).grid(row=6, column=1)

    def clear(self):
        for field in self.fields.values():
            field.delete(0, tk.END)
        for corner in self.corner_fields.values():
            for entry in corner.values():
                entry.delete(0, tk.END)
                entry.config(bg="white")
        self.screenshot_path = ""

    def import_screenshot(self):
        path = os.path.join(os.environ["USERPROFILE"], "Pictures", "Screenshots")
        file_path = filedialog.askopenfilename(initialdir=path, title="Select Screenshot",
                                               filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
        if file_path:
            self.screenshot_path = file_path
            messagebox.showinfo("Import Screenshot", "Screenshot imported successfully!")

    def check(self):
        try:
            rim_dia = float(self.fields["Rim Diameter"].get())
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid Rim Diameter.")
            return

        for corner in self.corners:
            try:
                measured = float(self.corner_fields[corner]["Measured"].get())
                ecu = float(self.corner_fields[corner]["ECU"].get())
                target = float(self.corner_fields[corner]["Target"].get())
            except ValueError:
                continue

            ride_height = measured - (rim_dia / 2)
            is_measured_ok = target - 3 < ride_height < target + 3
            is_ecu_ok = -3 < ecu < 3

            self.corner_fields[corner]["Measured"].config(bg="#C6EFCE" if is_measured_ok else "#FFC7CE")
            self.corner_fields[corner]["ECU"].config(bg="#C6EFCE" if is_ecu_ok else "#FFC7CE")

            if is_measured_ok and is_ecu_ok:
                color = "#C6EFCE"
            elif is_measured_ok or is_ecu_ok:
                color = "#FFEB9C"
            else:
                color = "#FFC7CE"
            self.corner_fields[corner]["Target"].config(bg=color)

    def save_pdf(self):
        missing = [k for k, v in self.fields.items() if not v.get().strip()]
        for corner in self.corners:
            for key in ["Measured", "ECU", "Target"]:
                if not self.corner_fields[corner][key].get().strip():
                    missing.append(f"{corner} {key}")

        if missing:
            messagebox.showerror("Missing Fields", "Please fill in all fields:
" + "
".join(missing))
            return

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        vehicle = self.fields["Vehicle"].get()
        brand = self.fields["Brand"].get()
        project = self.fields["Project"].get()
        model = self.fields["Model"].get()
        rim_dia = float(self.fields["Rim Diameter"].get())
        date_str = datetime.now().strftime("%m/%d/%Y")

        pdf.cell(200, 10, txt=f"Ride Height Measurement – V{vehicle}", ln=True, align="L")
        pdf.cell(200, 10, txt=f"Vehicle: {vehicle}", ln=True)
        pdf.cell(200, 10, txt=f"Project: {project}", ln=True)
        pdf.cell(200, 10, txt=f"Brand: {brand}", ln=True)
        pdf.cell(200, 10, txt=f"Model: {model}", ln=True)
        pdf.cell(200, 10, txt=f"Date: {date_str}", ln=True)

        pdf.ln(10)
        pdf.cell(200, 10, txt="Corner Measurements:", ln=True)
        pdf.set_font("Arial", size=10)
        pdf.cell(200, 10, txt="Corner | Measured | Ride Height | ECU | Target", ln=True)

        for corner in self.corners:
            measured = float(self.corner_fields[corner]["Measured"].get())
            ecu = float(self.corner_fields[corner]["ECU"].get())
            target = float(self.corner_fields[corner]["Target"].get())
            ride_height = measured - (rim_dia / 2)
            pdf.cell(200, 10, txt=f"{corner} | {measured} | {ride_height:.2f} | {ecu} | {target}", ln=True)

        pdf.ln(10)
        pdf.cell(200, 10, txt=f"Rim Diameter: {rim_dia}", ln=True)

        if self.screenshot_path:
            pdf.ln(10)
            pdf.cell(200, 10, txt="ECU readings after clamp:", ln=True)
            pdf.image(self.screenshot_path, w=100)

        folder_path = os.path.join(os.environ["OneDrive"],
            f"JLR/NVH Laboratory Operations - Open Access - Vehicle Dynamics Rigs/1.0 K+C/1.1 K+C Data/Dyn-Rig-K+C-{project}")
        if os.path.isdir(folder_path):
            pdf_path = os.path.join(folder_path, f"Ride Height Measurement – V{vehicle}.pdf")
        else:
            pdf_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
            if not pdf_path:
                messagebox.showwarning("Cancelled", "PDF save cancelled.")
                return

        pdf.output(pdf_path)
        messagebox.showinfo("Saved", f"PDF saved successfully to:
{pdf_path}")

if __name__ == "__main__":
    root = tk.Tk()
    app = RideHeightApp(root)
    root.mainloop()
