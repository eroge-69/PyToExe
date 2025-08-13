# -*- coding: utf-8 -*-
"""
Created on Wed Aug 13 18:48:40 2025

@author: sklat
"""

import datetime 

a='expense.txt'
b='details.txt'
c='categories.txt'

def user_details():
    start_date = input("Enter start date (DD-MM-YYYY): ")
    duration = input("Enter duration (in days): ")
    budget = input("Enter total budget: ")
    warning_percent = input("Enter warning percentage: ")
    with open(b,'w') as file:
        file.write(str(start_date)+'\n')
        file.write(str(duration)+'\n')
        file.write(str(budget)+'\n')
        file.write(str(warning_percent)+'\n')
    print('Your budget details have been stored💰')
    
    with open(b,'r') as file:
        lines=[]
        for l in file.readlines():
            new=l.strip()
            lines.append(new)
        if len(lines)==4:
            start_date= datetime.datetime.strptime(lines[0], '%d-%m-%Y') 
            duration=int(lines[1])
            budget=float(lines[2])
            warning_percent=int(lines[3])
            return start_date, duration, budget, warning_percent

def extra_category():
    category=input("Enter you category name: ")
    with open(c,'a') as file:
        file.write(category + '\n')
        print(f"Your category {category} has been added 🙌🏻 \n")
        
    with open(c,'r') as file:
        categories=[]
        for l in file.readlines():
            new2=l.strip()
            categories.append(new2)
        return categories
def user_expense():
    cat = input("Enter which category: ")
    date = input("Enter today's date (DD-MM-YYYY): ")
    amount = input("Enter amount spent: ")

    with open(a, 'a') as file:
        file.write(cat + '\n')
        file.write(date + '\n')
        file.write(amount + '\n')
    print("💸 Spending details have been logged in!")

    with open(a, 'r') as file:
        lines = [line.strip() for line in file.readlines()]
        if len(lines) % 3 == 0:
            total = 0
            for i in range(2, len(lines), 3):
                try:
                    total += float(lines[i])
                except ValueError:
                    continue  # skip bad data
            print(f"📊 Total spent so far: {total}")

def view_status():
    try:
        with open(a, 'r') as file:
            ex=[]
            for j in file.readlines():
                new3=j.strip()
                ex.append(new3)

    except FileNotFoundError:
            print("No spendings registered yet!")
            return
    details=None
    try:   
        with open(b, 'r') as file:
            lines = [l.strip() for l in file.readlines()]
            if len(lines) == 4:
                start_date = datetime.datetime.strptime(lines[0], '%d-%m-%Y')  
                duration = int(lines[1])  
                budget = float(lines[2])  
                warning_percent = int(lines[3])  
                details = (start_date, duration, budget, warning_percent)  
    except FileNotFoundError:
        print("No budget details found ❌")  
        return  
    if not details:
        print("Budget details are missing or incomplete ❌")  
        return  
        
    start_date, duration, budget, warning_percent = details  #tuple spliting 
    today = datetime.date.today()
    days_passed = (today - start_date.date()).days #.days = extracts the number of days
    Sum=0
    for i in range(2,len(ex),3):
        Sum+=float(ex[i])
    remain=budget-Sum 
    percent_used= (Sum/budget)*100
    GREEN   = "\033[38;2;80;200;120m"       
    RED     = "\033[38;2;220;20;60m"  
    YELLOW  = "\033[38;2;255;215;0m" 
    BOLD = "\033[1m"
    RESET = "\033[0m"
                
    print(f'\n      📊 {BOLD}Expense/Budget status:{RESET}     \n')
    print(f'Budget:{budget}')
    print(f'Duration:{duration}')
    print(f'Remaining Days:{duration-days_passed}')
    print(f'Amount spent={RED}{Sum:.2f}{RESET}')
    print(f'Remaining:{GREEN}{remain:.2f}{RESET}')
    
    if percent_used>=warning_percent:
        print(f'Percentage used:{YELLOW}{percent_used}{RESET}')
        print('\n')
        print(f'🚨 Warning! You’re at {BOLD}{RED}{percent_used:.2f}% {RESET}of your budget.')
    else:
        print(f'Percent used: {percent_used:.2f}%')
    
            
def main():
    while True:
        YELLOW = "\033[38;2;255;215;0m" 
        RESET = "\033[0m"
        ROSE= "\033[38;2;183;110;121m"
        CHAM= "\033[38;2;247;231;206m"
        print(f"\n       {ROSE}▷ {CHAM}Main Menu {ROSE}◁{RESET}      \n")
        print(f"{ROSE}1. {CHAM}Make a Budget")
        print(f"{ROSE}2. {CHAM}Add Category")
        print(f"{ROSE}3. {CHAM}Add Expense")
        print(f"{ROSE}4. {CHAM}Expense/Budget status")
        print(f"{ROSE}5. {CHAM}Exit{RESET}")   
        choose=input("Enter which submenu to open: ")
        
    
        if choose=='1':
            user_details()
        elif choose=='2':
            extra_category()
        elif choose=='3':
            user_expense()
        elif choose=='4':
            view_status()
        elif choose=='5':
            print(f'Farewell, {YELLOW}brave budget warrior!{RESET}')
            break
        else:
            print("enter a valid choice (1, 2, 3, 4 or 5)")
            
