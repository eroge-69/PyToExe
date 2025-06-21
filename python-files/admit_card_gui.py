import pandas as pd
from fpdf import FPDF
import tkinter as tk
from tkinter import filedialog, messagebox
import os

class AdmitCardPDF(FPDF):
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=False)

    def generate_card(self, student, y):
        outer_x = 10
        outer_y = y
        outer_w = 190
        outer_h = 85

        inner_margin = 3
        inner_x = outer_x + inner_margin
        inner_y = outer_y + inner_margin
        inner_w = outer_w - (2 * inner_margin)
        inner_h = outer_h - (2 * inner_margin)

        # Draw outer sharp box
        self.set_draw_color(0, 100, 0)  # Dark green border
        self.rect(x=outer_x, y=outer_y, w=outer_w, h=outer_h)

        # Fill inner light green area
        self.set_fill_color(255, 255, 255)  # Light green
        self.rect(x=inner_x, y=inner_y, w=inner_w, h=inner_h, style='F')

        self.set_y(inner_y + 5)
        self.set_x(inner_x + 5)

        self.set_font("Arial", "B", 16)
        self.cell(0, 10, "Daffodil University School & College", ln=True, align="C")

        self.set_font("Arial", "", 12)
        self.set_x(inner_x + 5)
        self.cell(0, 10, "Admit Card", ln=True, align="C")
        self.ln(5)

        self.set_x(inner_x + 5)
        self.cell(0, 10, f"Name: {student['Name']}", ln=True)

        self.set_x(inner_x + 5)
        self.cell(95, 10, f"ID: {student['ID']}")
        self.cell(0, 10, f"Class: {student['Class']}", ln=True)

        self.set_x(inner_x + 5)
        self.cell(0, 10, "Accounts: __________________________         Principal: __________________________", ln=True, align="C")
        self.ln(2)

def generate_admit_cards(file_path):
    df = pd.read_excel(file_path)
    pdf = AdmitCardPDF()

    cards_per_page = 3
    card_height = 95
    card_count = 0

    for _, row in df.iterrows():
        if card_count % cards_per_page == 0:
            pdf.add_page()

        y_position = 10 + (card_count % cards_per_page) * card_height
        pdf.generate_card(row, y_position)
        card_count += 1

    output_folder = "admit_cards"
    os.makedirs(output_folder, exist_ok=True)
    pdf.output(os.path.join(output_folder, "All_Admit_Cards.pdf"))

    messagebox.showinfo("Success", f"Admit cards saved in '{output_folder}/All_Admit_Cards.pdf'.")

def browse_file():
    file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx")])
    if file_path:
        generate_admit_cards(file_path)

def main():
    window = tk.Tk()
    window.title("Admit Card Generator")
    window.geometry("450x250")
    window.configure(bg="#d0f0c0")  # Light green background

    label = tk.Label(
        window,
        text="Welcome to \n Daffodil University School and College \n Admit Card Generator",
        font=("Arial", 14, "bold"),
        bg="#d0f0c0",
        fg="#004d00"
    )
    label.pack(pady=20)

    browse_button = tk.Button(
        window,
        text="Browse Excel File",
        command=browse_file,
        font=("Arial", 12),
        bg="#66bb6a",
        fg="white",
        activebackground="#388e3c"
    )
    browse_button.pack(pady=10)

    credit_label = tk.Label(
        window,
        text="Developed by Md Shahriar Hasan Sabuj \n by the help of ChatGpt😁😁😁",
        font=("Arial", 10, "bold"),
        bg="#d0f0c0",
        fg="#004d00"
    )
    credit_label.pack(side="bottom", pady= 10)

    window.mainloop()

if __name__ == "__main__":
    main()
