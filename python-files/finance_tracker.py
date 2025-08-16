import customtkinter as ctk
import tkinter.messagebox as messagebox
import tkinter.filedialog as filedialog
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import os

# ---------- Constants ----------
CSV_FILE = 'transactions.csv'
CATEGORIES = ["Food", "Transport", "Salary", "Rent", "Shopping", "Misc"]
MODES = ["Income", "Expense"]
CHART_TYPES = ["Category Pie", "Monthly Trend", "Income vs Expense", "Cumulative Balance"]
MONTHLY_BUDGET_LIMIT = 50000  # Default monthly budget alert

# ---------- Application ----------
class FinanceTracker(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Modern Finance Tracker")
        self.geometry("1200x700")
        
        # Theme toggle
        self.appearance_mode = ctk.BooleanVar(value=False)  # False = Light, True = Dark
        ctk.set_appearance_mode("Light")  # default
        ctk.CTkSwitch(self, text="🌗 Theme", variable=self.appearance_mode,
                      command=self.toggle_theme).pack(anchor="ne", padx=10, pady=5)
        
        # Data
        self.data = self.load_data()
        
        # Layout
        self.build_dashboard()
        self.build_transaction_form()
        self.build_transactions_table()
        self.build_chart_area()
    
    # ---------- Theme ----------
    def toggle_theme(self):
        if self.appearance_mode.get():  # True → Dark
            ctk.set_appearance_mode("Dark")
        else:  # False → Light
            ctk.set_appearance_mode("Light")
    
    # ---------- Data ----------
    def load_data(self):
        if os.path.exists(CSV_FILE):
            df = pd.read_csv(CSV_FILE, parse_dates=['Date'])
            df['Amount'] = df['Amount'].astype(float)
            return df
        return pd.DataFrame(columns=['Date', 'Description', 'Category', 'Type', 'Amount'])
    
    def save_data(self):
        self.data.to_csv(CSV_FILE, index=False)
        self.update_dashboard()
        self.update_table()
        self.check_budget_alert()
    
    # ---------- Dashboard ----------
    def build_dashboard(self):
        self.card_frame = ctk.CTkFrame(self)
        self.card_frame.pack(fill="x", padx=10, pady=10)
        self.cards = {}
        for title in ["Total Income", "Total Expense", "Net Balance"]:
            frame = ctk.CTkFrame(self.card_frame)
            frame.pack(side="left", expand=True, fill="x", padx=5)
            label = ctk.CTkLabel(frame, text=title, font=("Arial", 15, "bold"))
            label.pack(pady=(5,0))
            value = ctk.CTkLabel(frame, text="0", font=("Arial", 20))
            value.pack(pady=(0,5))
            self.cards[title] = value
        self.update_dashboard()
    
    def update_dashboard(self):
        income = self.data[self.data['Type']=="Income"]['Amount'].sum()
        expense = self.data[self.data['Type']=="Expense"]['Amount'].sum()
        balance = income - expense
        self.cards["Total Income"].configure(text=f"₹{income:.2f}")
        self.cards["Total Expense"].configure(text=f"₹{expense:.2f}")
        self.cards["Net Balance"].configure(text=f"₹{balance:.2f}")
    
    # ---------- Budget Alert ----------
    def check_budget_alert(self):
        now = pd.Timestamp.now()
        month_expense = self.data[(self.data['Type']=="Expense") & 
                                  (self.data['Date'].dt.month == now.month) &
                                  (self.data['Date'].dt.year == now.year)]['Amount'].sum()
        if month_expense > MONTHLY_BUDGET_LIMIT:
            messagebox.showwarning("Budget Alert",
                                   f"Monthly expenses ₹{month_expense:.2f} exceed limit ₹{MONTHLY_BUDGET_LIMIT:.2f}")
    
    # ---------- Form ----------
    def build_transaction_form(self):
        frame = ctk.CTkFrame(self)
        frame.pack(side="left", fill="y", padx=(10,0), pady=10)
        
        ctk.CTkLabel(frame, text="Add / Edit Transaction", font=("Arial",15,"bold")).pack(pady=5)
        self.date_entry = ctk.CTkEntry(frame, placeholder_text="YYYY-MM-DD")
        self.date_entry.pack(fill="x", padx=10, pady=5)
        self.desc_entry = ctk.CTkEntry(frame, placeholder_text="Description")
        self.desc_entry.pack(fill="x", padx=10, pady=5)
        self.category_box = ctk.CTkComboBox(frame, values=CATEGORIES)
        self.category_box.pack(fill="x", padx=10, pady=5)
        self.type_box = ctk.CTkComboBox(frame, values=MODES)
        self.type_box.pack(fill="x", padx=10, pady=5)
        self.amount_entry = ctk.CTkEntry(frame, placeholder_text="Amount")
        self.amount_entry.pack(fill="x", padx=10, pady=5)
        
        self.form_buttons_frame = ctk.CTkFrame(frame)
        self.form_buttons_frame.pack(pady=10)
        ctk.CTkButton(self.form_buttons_frame, text="Save", command=self.add_or_update).grid(row=0, column=0, padx=5)
        ctk.CTkButton(self.form_buttons_frame, text="Clear", command=self.clear_form).grid(row=0, column=1, padx=5)
        
        self.selected_row = None
    
    def clear_form(self):
        for w in [self.date_entry, self.desc_entry, self.amount_entry]:
            w.delete(0, "end")
        self.category_box.set("")
        self.type_box.set("")
        self.selected_row = None
    
    # ---------- Table ----------
    def build_transactions_table(self):
        frame = ctk.CTkFrame(self)
        frame.pack(side="left", fill="both", expand=True, pady=10, padx=10)
        
        self.table = ctk.CTkScrollableFrame(frame)
        self.table.pack(fill="both", expand=True)
        self.update_table()
        
        btn_frame = ctk.CTkFrame(frame)
        btn_frame.pack(fill="x")
        ctk.CTkButton(btn_frame, text="Delete Selected", command=self.delete_selected).pack(side="left", padx=5, pady=5)
    
    def update_table(self):
        for child in self.table.winfo_children():
            child.destroy()
        for idx, row in self.data.iterrows():
            row_frame = ctk.CTkFrame(self.table)
            row_frame.pack(fill="x")
            values = [row['Date'].strftime('%Y-%m-%d'), row['Description'], row['Category'], row['Type'], f"₹{row['Amount']}"]
            for v in values:
                ctk.CTkLabel(row_frame, text=v, fg_color="transparent").pack(side="left", expand=True)
            row_frame.bind("<Button-1>", lambda e, r=idx: self.load_to_form(r))
            for lbl in row_frame.winfo_children():
                lbl.bind("<Button-1>", lambda e, r=idx: self.load_to_form(r))
    
    def load_to_form(self, idx):
        row = self.data.loc[idx]
        self.date_entry.delete(0, "end")
        self.date_entry.insert(0, row['Date'].strftime('%Y-%m-%d'))
        self.desc_entry.delete(0, "end")
        self.desc_entry.insert(0, row['Description'])
        self.category_box.set(row['Category'])
        self.type_box.set(row['Type'])
        self.amount_entry.delete(0, "end")
        self.amount_entry.insert(0, str(row['Amount']))
        self.selected_row = idx
    
    def delete_selected(self):
        if self.selected_row is not None:
            self.data.drop(index=self.selected_row, inplace=True)
            self.data.reset_index(drop=True, inplace=True)
            self.save_data()
            self.clear_form()
        else:
            messagebox.showinfo("Info", "Please select a row first.")
    
    def add_or_update(self):
        try:
            date = datetime.strptime(self.date_entry.get(), "%Y-%m-%d")
        except:
            messagebox.showerror("Error", "Invalid date format")
            return
        try:
            amount = float(self.amount_entry.get())
        except:
            messagebox.showerror("Error", "Invalid amount")
            return
        
        new_row = {
            'Date': date,
            'Description': self.desc_entry.get(),
            'Category': self.category_box.get(),
            'Type': self.type_box.get(),
            'Amount': amount
        }
        
        if self.selected_row is None:
            self.data = pd.concat([self.data, pd.DataFrame([new_row])], ignore_index=True)
        else:
            for k,v in new_row.items():
                self.data.at[self.selected_row,k] = v
        self.save_data()
        self.clear_form()
    
    # ---------- Charts ----------
    def build_chart_area(self):
        frame = ctk.CTkFrame(self)
        frame.pack(side="right", fill="both", expand=True, padx=(0,10), pady=10)
        
        # Chart type menu
        top = ctk.CTkFrame(frame)
        top.pack(fill="x")
        self.chart_type = ctk.StringVar(value=CHART_TYPES[0])
        ctk.CTkOptionMenu(top, values=CHART_TYPES, variable=self.chart_type).pack(side="left", padx=5, pady=5)
        ctk.CTkButton(top, text="Show Chart", command=self.show_chart).pack(side="left", padx=5)
        ctk.CTkButton(top, text="Export Chart", command=self.export_chart).pack(side="right", padx=5)
        
        self.chart_frame = ctk.CTkFrame(frame)
        self.chart_frame.pack(fill="both", expand=True)
        self.current_figure = None
    
    def show_chart(self):
        chart = self.chart_type.get()
        if chart == "Category Pie":
            self.show_category_chart()
        elif chart == "Monthly Trend":
            self.show_monthly_trend()
        elif chart == "Income vs Expense":
            self.show_income_vs_expense()
        elif chart == "Cumulative Balance":
            self.show_cumulative_balance()
    
    def show_category_chart(self):
        cat = self.data[self.data['Type']=="Expense"].groupby('Category')['Amount'].sum()
        if cat.empty:
            messagebox.showinfo("Info", "No expense data")
            return
        fig, ax = plt.subplots(figsize=(6,4))
        ax.pie(cat, labels=cat.index, autopct='%1.1f%%')
        ax.set_title("Spending by Category")
        self.display_matplotlib(fig)
    
    def show_monthly_trend(self):
        df = self.data.copy()
        df['Month'] = df['Date'].dt.to_period('M')
        monthly = df[df['Type']=="Expense"].groupby('Month')['Amount'].sum()
        if monthly.empty:
            messagebox.showinfo("Info","No expense data")
            return
        fig, ax = plt.subplots(figsize=(6,4))
        ax.plot(monthly.index.astype(str), monthly.values, marker='o')
        ax.set_title("Monthly Expense Trend")
        ax.set_xlabel("Month")
        ax.set_ylabel("Expense")
        self.display_matplotlib(fig)
    
    def show_income_vs_expense(self):
        df = self.data.copy()
        df['Month'] = df['Date'].dt.to_period('M')
        monthly_income = df[df['Type']=="Income"].groupby('Month')['Amount'].sum()
        monthly_expense = df[df['Type']=="Expense"].groupby('Month')['Amount'].sum()
        all_months = monthly_income.index.union(monthly_expense.index)
        income_vals = [monthly_income.get(m,0) for m in all_months]
        expense_vals = [monthly_expense.get(m,0) for m in all_months]
        fig, ax = plt.subplots(figsize=(6,4))
        ax.bar([str(m) for m in all_months], income_vals, label="Income")
        ax.bar([str(m) for m in all_months], expense_vals, bottom=income_vals, label="Expense")
        ax.set_title("Income vs Expense")
        ax.set_xlabel("Month")
        ax.set_ylabel("Amount")
        ax.legend()
        self.display_matplotlib(fig)
    
    def show_cumulative_balance(self):
        df = self.data.copy().sort_values('Date')
        df['Balance'] = df.apply(lambda r: r['Amount'] if r['Type']=="Income" else -r['Amount'], axis=1).cumsum()
        fig, ax = plt.subplots(figsize=(6,4))
        ax.plot(df['Date'], df['Balance'], marker='o')
        ax.set_title("Cumulative Balance Over Time")
        ax.set_xlabel("Date")
        ax.set_ylabel("Balance")
        self.display_matplotlib(fig)
    
    def display_matplotlib(self, fig):
        self.current_figure = fig
        for widget in self.chart_frame.winfo_children():
            widget.destroy()
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        cnv = FigureCanvasTkAgg(self.current_figure, master=self.chart_frame)
        cnv.draw()
        cnv.get_tk_widget().pack(fill="both", expand=True)
    
    # ---------- Export ----------
    def export_chart(self):
        if not self.current_figure:
            messagebox.showwarning("Warning", "No chart to export")
            return
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG", "*.png"),("JPEG","*.jpg"),("PDF","*.pdf"),("All","*.*")]
        )
        if file_path:
            try:
                self.current_figure.savefig(file_path, dpi=300, bbox_inches='tight')
                messagebox.showinfo("Success", "Chart exported!")
            except Exception as e:
                messagebox.showerror("Error", str(e))

# ---------- Run ----------
if __name__ == "__main__":
    app = FinanceTracker()
    app.mainloop()
