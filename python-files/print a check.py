import tkinter as tk
from tkinter import messagebox, filedialog
from datetime import datetime
import json
import os
import inflect
import win32print
import win32api


class ChequePrinter:
    def __init__(self, root):
        self.root = root
        self.root.title("SFEIR - Print A Check")
        self.root.geometry("700x600")

        # Variables
        self.margin_top = tk.IntVar(value=10)
        self.margin_left = tk.IntVar(value=10)
        self.show_micr = tk.BooleanVar(value=True)
        self.bank_micr_data = {
        "Fransabank": "123456789",
        "Bank Audi": "987654321",
        "Bank of Beirut": "135791357",
        "SGBL": "246802468",
        "BLF": "112233445",
        "Byblos Bank": "556677889",
        "IBL Bank": "998877665",
        "Arab Bank PLC": "778899001"
        # ← Add this line
     }

        self.setup_fields()

    def setup_fields(self):
        tk.Label(self.root, text="SFEIR Print A Check", font=("Helvetica", 16, "bold")).place(x=230, y=10)

        self.bank_var = tk.StringVar(value="Fransabank")  # Initialize correctly
        tk.OptionMenu(self.root, self.bank_var, *self.bank_micr_data.keys()).place(x=150, y=285)


        tk.Label(text="Check Number:").place(x=30, y=50)
        self.check_number_entry = tk.Entry(width=20)
        self.check_number_entry.place(x=150, y=50)

        tk.Label(text="Payee Name:").place(x=30, y=90)
        self.payee_entry = tk.Entry(width=40)
        self.payee_entry.place(x=150, y=90)

        tk.Label(text="Amount:").place(x=30, y=130)
        self.amount_entry = tk.Entry(width=20)
        self.amount_entry.place(x=150, y=130)

        tk.Label(text="Currency:").place(x=350, y=130)
        self.currency_var = tk.StringVar(value="USD")
        tk.OptionMenu(self.root, self.currency_var, "USD", "LBP").place(x=420, y=125)
        tk.OptionMenu(self.root, self.bank_var, *self.bank_micr_data.keys())

        tk.Label(text="Memo:").place(x=30, y=170)
        self.memo_entry = tk.Entry(width=40)
        self.memo_entry.place(x=150, y=170)

        tk.Label(text="Date:").place(x=30, y=210)
        self.date_var = tk.StringVar(value=datetime.today().strftime("%d/%m/%Y"))
        self.date_entry = tk.Entry(width=20, textvariable=self.date_var)
        self.date_entry.place(x=150, y=210)

        tk.Label(text="Top Margin:").place(x=30, y=250)
        tk.Entry(self.root, textvariable=self.margin_top, width=5).place(x=150, y=250)

        tk.Label(text="Left Margin:").place(x=230, y=250)
        tk.Entry(self.root, textvariable=self.margin_left, width=5).place(x=320, y=250)


        tk.Label(text="Account Number:").place(x=30, y=330)
        self.account_entry = tk.Entry(width=30)
        self.account_entry.place(x=150, y=330)

        self.show_micr = tk.BooleanVar()
        self.show_micr.set(False)  # Default: MICR disabled

        tk.Label(text="MICR Code:").place(x=30, y=370)
        self.micr_entry = tk.Entry(width=40)
        self.micr_entry.place(x=150, y=370)

        tk.Checkbutton(self.root, text="Show MICR in Preview", variable=self.show_micr).place(x=150, y=400)


        self.words_label = tk.Label(text="", fg="blue", wraplength=500, justify="left")
        self.words_label.place(x=30, y=470)
        
        tk.Button(text="Enable MICR Code", command=self.insert_micr_code).place(x=30, y=440)
        tk.Button(text="Preview Cheque", command=self.print_preview).place(x=180, y=440)
        tk.Button(text="Save Cheque", command=self.save_cheque_data).place(x=370, y=540)
        tk.Button(text="Load Cheque", command=self.load_cheque_data).place(x=490, y=540)
        tk.Button(text="Show Numbers and Letters", command=self.show_amount_in_words).place(x=330, y=440)
        tk.Button(text="Print Cheque", command=self.print_cheque).place(x=590, y=540)
        tk.Button(text="Preview Cheque", command=self.print_preview).place(x=180, y=440)
        tk.Button(text="Export as PDF", command=self.export_pdf).place(x=580, y=450)
        
    def insert_micr_code(self):
        if self.show_micr.get():  # Only update if MICR is enabled
           bank = self.bank_var.get()
           micr = self.bank_micr_data.get(bank, "(No MICR found)")
           self.micr_entry.delete(0, tk.END)
           self.micr_entry.insert(0, micr)
        else:
           self.micr_entry.delete(0, tk.END)  # Clear MICR if disabled

    def show_amount_in_words(self):
        try:
            amount = float(self.amount_entry.get())
            currency = self.currency_var.get()

            words = self.convert_number_to_words(amount)
            display_text = f"{words} {currency}".upper()
            self.words_label.config(text=display_text)
        except ValueError:
            messagebox.showerror("Error", "Invalid amount entered.")

    def convert_number_to_words(self, num):
        import inflect
        p = inflect.engine()
        words = p.number_to_words(num, andword="", zero="zero", decimal="point")
        return words.capitalize()
    
    def print_preview(self):
        preview = tk.Toplevel(self.root)
        preview.title("Cheque Preview")
        preview.geometry("650x320")

        try:
            amount_value = self.amount_entry.get().strip() 
            amount = float(amount_value)
            currency = self.currency_var.get()

        # Convert amount to words
            p = inflect.engine()
            amount_words = p.number_to_words(amount, andword="", zero="zero", decimal="point")
            amount_words = f"{amount_words} {currency}".upper()

        # Debugging print (Remove after testing)
            print(f"Amount value: {amount_value}")
            print(f"Amount in words: {amount_words}")

        except ValueError:
            amount_value = "0.00"
            amount_words = "(Invalid amount)"
            currency = self.currency_var.get()

    # Display amount in preview
        tk.Label(preview, text=f"Pay to the Order of: {self.payee_entry.get()}", font=("Helvetica", 12)).place(x=30, y=30)
        tk.Label(preview, text=f"Amount: {amount_value} {currency}", font=("Helvetica", 12)).place(x=30, y=60)
        tk.Label(preview, text=f"In Words: {amount_words}", font=("Helvetica", 10, "italic")).place(x=30, y=90)
        tk.Label(preview, text=f"Date: {self.date_var.get()}", font=("Helvetica", 12)).place(x=400, y=30)
        tk.Label(preview, text=f"Memo: {self.memo_entry.get()}", font=("Helvetica", 10)).place(x=30, y=120)
        tk.Label(preview, text=f"Bank: {self.bank_var.get()}", font=("Helvetica", 10)).place(x=30, y=150)
        tk.Label(preview, text=f"Account #: {self.account_entry.get()}", font=("Helvetica", 10)).place(x=30, y=180)

        if self.show_micr.get():
            tk.Label(preview, text=f"MICR: {self.micr_entry.get()}", font=("Courier New", 12, "bold"), fg="green").place(x=30, y=220)   

        tk.Button(preview, text="Close Preview", command=preview.destroy).place(x=250, y=260)

    def load_cheque_data(self):
        try:
            with open("cheque_data.txt", "r") as file:
                data = file.readlines()

                cheque_info = {}
            for line in data:
                key, value = line.strip().split(": ", 1)
                cheque_info[key] = value

        # Populate fields with loaded data
            self.payee_entry.delete(0, tk.END)
            self.payee_entry.insert(0, cheque_info.get("Payee", ""))

            self.amount_entry.delete(0, tk.END)
            self.amount_entry.insert(0, cheque_info.get("Amount", ""))

            self.currency_var.set(cheque_info.get("Currency", "USD"))
            self.date_var.set(cheque_info.get("Date", ""))
            self.memo_entry.delete(0, tk.END)
            self.memo_entry.insert(0, cheque_info.get("Memo", ""))

            self.bank_var.set(cheque_info.get("Bank", "Fransabank"))
            self.account_entry.delete(0, tk.END)
            self.account_entry.insert(0, cheque_info.get("Account", ""))

            micr_code = cheque_info.get("MICR", "")
            if micr_code != "MICR Disabled":
               self.show_micr.set(True)
               self.micr_entry.delete(0, tk.END)
               self.micr_entry.insert(0, micr_code)
            else:
               self.show_micr.set(False)
               self.micr_entry.delete(0, tk.END)

               messagebox.showinfo("Success", "Cheque data loaded successfully!")

        except FileNotFoundError:
            messagebox.showerror("Error", "No saved cheque data found!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load cheque data: {e}")
         

    def print_cheque(self):
        messagebox.showinfo("Print", "Printing cheque... (This is a placeholder.)")
    # You can implement actual print logic here using PDF export or canvas drawing

    def export_pdf(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
        if not file_path:
            return

            c = canvas.Canvas(file_path, pagesize=LETTER)
            c.setFont("Helvetica", 12)
            c.drawString(50, 750, f"Pay to the Order of: {self.payee_entry.get()}")
            c.drawString(50, 730, f"Amount: {self.amount_entry.get()} {self.currency_var.get()}")

        try:
            amt = float(self.amount_entry.get())
            p = inflect.engine()
            words = p.number_to_words(amt, andword="", zero="zero", decimal="point").upper()
        except:
            words = "(Invalid amount)"

            c.drawString(50, 710, f"In Words: {words} {self.currency_var.get()}")
            c.drawString(400, 750, f"Date: {self.date_var.get()}")
            c.drawString(50, 670, f"Bank: {self.bank_var.get()}")

        if self.show_micr.get():
            c.setFont("Courier-Bold", 12)
            c.setFillColorRGB(0, 0.5, 0)
            c.drawString(50, 620, f"MICR: {self.micr_entry.get()}")

            c.save()

    def save_cheque_data(self):
        cheque_data = {
        "Payee": self.payee_entry.get(),
        "Amount": self.amount_entry.get(),
        "Currency": self.currency_var.get(),
        "Date": self.date_var.get(),
        "Memo": self.memo_entry.get(),
        "Bank": self.bank_var.get(),
        "Account": self.account_entry.get(),
        "MICR": self.micr_entry.get() if self.show_micr.get() else "MICR Disabled"
    }

        with open("cheque_data.txt", "w") as file:
            for key, value in cheque_data.items():
                file.write(f"{key}: {value}\n")

                messagebox.showinfo("Success", "Cheque data saved successfully!")

    # **Open the generated PDF for preview**
                os.startfile(file_path)  # Works for Windows
    
                messagebox.showinfo("PDF Export", f"Cheque preview generated:\n{file_path}")

    # **Optional: Print to Default Printer**
                print_to_default_printer(file_path)

    def print_to_default_printer(file_path):
        printer_name = win32print.GetDefaultPrinter()  # Get default printer
        win32api.ShellExecute(0, "print", file_path, f'"{printer_name}"', ".", 0)

    

    def save_cheque_data(self):
        data = {
            "cheque_number": self.check_number_entry.get(),
            "payee": self.payee_entry.get(),
            "amount": self.amount_entry.get(),
            "currency": self.currency_var.get(),
            "memo": self.memo_entry.get(),
            "date": self.date_entry.get(),
            "bank": self.bank_var.get(),
            "account": self.account_entry.get(),
            "micr": self.micr_entry.get()
        }

        os.makedirs("checks", exist_ok=True)
        filename = f"checks/{data['cheque_number']}_{data['payee'].replace(' ', '_')}.json"

        try:
            with open(filename, "w") as f:
                json.dump(data, f, indent=4)
            messagebox.showinfo("Saved", f"Cheque saved successfully:\n{filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Could not save cheque:\n{str(e)}")

    def load_cheque_data(self):
        filepath = filedialog.askopenfilename(
            initialdir="checks",
            filetypes=[("JSON files", "*.json")]
        )

        if not filepath:
            return

        try:
            with open(filepath, "r") as f:
                data = json.load(f)

            self.check_number_entry.delete(0, tk.END)
            self.check_number_entry.insert(0, data.get("cheque_number", ""))

            self.payee_entry.delete(0, tk.END)
            self.payee_entry.insert(0, data.get("payee", ""))

            self.amount_entry.delete(0, tk.END)
            self.amount_entry.insert(0, data.get("amount", ""))

            self.currency_var.set(data.get("currency", "USD"))
            self.memo_entry.delete(0, tk.END)
            self.memo_entry.insert(0, data.get("memo", ""))

            self.date_var.set(data.get("date", ""))
            self.bank_var.set(data.get("bank", "Fransabank"))

            self.account_entry.delete(0, tk.END)
            self.account_entry.insert(0, data.get("account", ""))

            self.micr_entry.delete(0, tk.END)
            self.micr_entry.insert(0, data.get("micr", ""))

        except Exception as e:
            messagebox.showerror("Load Error", f"Could not load cheque:\n{str(e)}")

# Run the app
if __name__ == "__main__":
    root = tk.Tk()
    app = ChequePrinter(root)
    root.mainloop()
