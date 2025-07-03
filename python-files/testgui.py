import tkinter as tk

class DivisionAnimator:
    def __init__(self, master):
        self.master = master
        master.title("Împărțire în coloană")

        self.label = tk.Label(master, text="Împărțit:")
        self.label.grid(row=0, column=0)
        self.dividend_entry = tk.Entry(master)
        self.dividend_entry.grid(row=0, column=1)

        self.label2 = tk.Label(master, text="Împărțitor:")
        self.label2.grid(row=1, column=0)
        self.divisor_entry = tk.Entry(master)
        self.divisor_entry.grid(row=1, column=1)

        self.start_button = tk.Button(master, text="Start", command=self.start_division)
        self.start_button.grid(row=2, column=0, columnspan=2)

        self.text = tk.Text(master, height=15, width=40, font=("Courier", 14))
        self.text.grid(row=3, column=0, columnspan=2)

        self.next_button = tk.Button(master, text="Pas următor", command=self.next_step, state="disabled")
        self.next_button.grid(row=4, column=0)
        self.prev_button = tk.Button(master, text="Înapoi", command=self.prev_step, state="disabled")
        self.prev_button.grid(row=4, column=1)

        self.steps = []
        self.current_step = 0

    def start_division(self):
        self.text.delete(1.0, tk.END)
        dividend = self.dividend_entry.get()
        divisor = self.divisor_entry.get()

        if not dividend.isdigit() or not divisor.isdigit() or int(divisor) == 0:
            self.text.insert(tk.END, "Valori invalide.")
            return

        self.steps = self.generate_division_steps(int(dividend), int(divisor))
        self.current_step = 0
        self.show_step()
        self.next_button["state"] = "normal"
        self.prev_button["state"] = "normal"

    def show_step(self):
        self.text.delete(1.0, tk.END)
        self.text.insert(tk.END, self.steps[self.current_step])

    def next_step(self):
        if self.current_step < len(self.steps) - 1:
            self.current_step += 1
            self.show_step()

    def prev_step(self):
        if self.current_step > 0:
            self.current_step -= 1
            self.show_step()

    def generate_division_steps(self, dividend, divisor):
        dividend_str = str(dividend)
        result = ""
        steps = []
        current = 0
        result_line = ""

        for i, digit in enumerate(dividend_str):
            current = current * 10 + int(digit)
            if current >= divisor:
                quotient_digit = current // divisor
                subtract = quotient_digit * divisor
                result_line += str(quotient_digit)
                step_text = f"Pas {i + 1}:\n"
                step_text += f"Împart {current} la {divisor} => {quotient_digit}\n"
                step_text += f"{' ' * (i)}-{subtract}\n"
                step_text += f"{' ' * (i)}{'-' * len(str(subtract))}\n"
                current -= subtract
            else:
                result_line += "0"
                step_text = f"Pas {i + 1}:\n"
                step_text += f"{current} nu se împarte, punem 0\n"

            step_text += f"Rezultat parțial: {result_line}\n"
            steps.append(step_text)

        final = f"Rezultat final: {dividend} ÷ {divisor} = {int(dividend) // int(divisor)}, rest {current}"
        steps.append(final)
        return steps

root = tk.Tk()
app = DivisionAnimator(root)
root.mainloop()
