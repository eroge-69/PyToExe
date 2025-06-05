import tkinter as tk # imports the tkinter library
from tkinter import messagebox # used for showing error messages
from abc import ABC, abstractmethod

class BaseCalulator(ABC):
    @abstractmethod
    def calculatePayment(self):
        pass

class Car:
    def __init__(self, price):
        self.price = price

    def getPrice(self):
        return self.price

class Loan:
    def __init__(self, car, downPayment, loanTerm, apr):
        self.loanAmount = car.getPrice() - downPayment
        self.loanTerm = loanTerm
        self.apr = apr / 100

    def calculateMonthlyPayment(self):

        if self.apr == 0:
            return self.loanAmount / (self.loanTerm * 12)

        monthlyRate = self.apr / 12
        monthlyPayment = (self.loanAmount * monthlyRate) / (1 - (1 + monthlyRate) ** (-self.loanTerm * 12))
        numberOfPayments = self.loanTerm / 12
        return monthlyPayment

    def calculateTotalPayment(self):

        return self.calculateMonthlyPayment() * self.loanTerm * 12

    def calculateInterestPaid(self):
            
        return self.calculateTotalPayment() - self.loanAmount

class FinanceCalculator(BaseCalulator):
    def __init__(self, loan):
        self.loan = loan

    def calculatePayment(self):
        return {
            "monthlyPayment": round(self.loan.calculateMonthlyPayment(), 2),
            "totalPayment": round(self.loan.calculateTotalPayment(), 2),
            "interestPaid": round(self.loan.calculateInterestPaid(), 2)
        }

car = Car(20000)
loan = Loan(car, 5000, 5, 5.0)
print(loan.loanAmount)

calc = FinanceCalculator(loan)
print(calc.calculatePayment())

class FinanceCalculatorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Carr's Cars Finance Calculator")
        self.root.configure(bg="#add8e6")
        self.root.geometry("280x400")

        tk.Label(root, text="Car Price (£):", bg="#9cc6e0", font=("Helvetica", 16), bd=2, relief="solid").grid(row=0, column=0, pady=10)
        self.carPriceEntry = tk.Entry(root)
        self.carPriceEntry.grid(row=1, column=0)

        tk.Label(root, text="Down Payment Amount (£):", bg="#9cc6e0", font=("Helvetica", 16), bd=2, relief="solid").grid(row=2, column=0, pady=10)
        self.downPaymentEntry = tk.Entry(root)
        self.downPaymentEntry.grid(row=3, column=0)

        tk.Label(root, text="Loan Term (Years):", bg="#9cc6e0", font=("Helvetica", 16), bd=2, relief="solid").grid(row=4, column=0, pady=10)
        self.loanTermEntry = tk.Entry(root)
        self.loanTermEntry.grid(row=5, column=0)

        tk.Label(root, text="Annual Percentage Rate (%):", bg="#9cc6e0", font=("Helvetica", 16), bd=2, relief="solid").grid(row=6, column=0, pady=10)
        self.aprEntry = tk.Entry(root)
        self.aprEntry.grid(row=7, column=0)

        self.calculateButton = tk.Button(root, text="Calculate", command=self.calculate, font=("Helvetica", 16), bg="#90ee90")
        self.calculateButton.grid(row=8, column=0, columnspan=2, pady=20)

    def calculate(self): # calculate function
        try:
            carPrice = float(self.carPriceEntry.get())
            downPayment = float(self.downPaymentEntry.get())
            loanTerm = int(self.loanTermEntry.get())
            apr = float(self.aprEntry.get())

            if loanTerm < 1:
                raise ValueError("Loan term must be at least 1 year.")

            if downPayment > carPrice:
                raise ValueError("Down payment cannot be greater than the car price.")

            car = Car(carPrice)
            loan = Loan(car, downPayment, loanTerm, apr)
            calculator = FinanceCalculator(loan)
            results = calculator.calculatePayment()

            messagebox.showinfo("Results", f"Monthly Payment: £{results['monthlyPayment']:,.2f}\nTotal Payment: £{results['totalPayment']:,.2f}\nInterest Paid: £{results['interestPaid']:,.2f}")
        except ValueError as e:
            messagebox.showerror("Input Error", str(e))
        except Exception:
            messagebox.showerror("Error", "Please fill in all fields with valid values.")

if __name__ == "__main__":
    root = tk.Tk()
    app = FinanceCalculatorGUI(root)
    root.mainloop()


            



