import datetime

users = {}
services = [
    "Rent an electric motorcycle for a trip within the city",
    "Renting electric cars for a trip between governorates",
    "Buy a bike",
    "Buy a skate",
    "Rent a bike",
    "Rent a skate"
]

subscription_plans = {
    
    "Bronze": {"price": 500, "features": 
     ["Less ads",
      "12/5 Dedicated Support",
      "5 monthly trips on an electric motorcycle free",
      "15 km per month using a bike or skate for free"]
               },
    
    "Silver": {"price": 1000, "features": 
     ["No ads",
      "24/5 Dedicated Support",
      "10 monthly trips on an electric motorcycle free",
      "40 km per month using a bike or skate for free"]
               },
    
    "Gold": {"price": 2000, "features": 
     ["No ads",
      "24/7 Dedicated Support",
      "20 monthly trips on an electric motorcycle free",
      "100 km per month using a bike or skate for free",
      "1 free electric car trip between governorates"]
             },
    
    "Platinum": {"price": 3500, "features": 
     ["No ads",
      "24/7 Dedicated Support",
      "40 monthly trips on an electric motorcycle free",
      "150 km per month using a bike or skate for free",
      "7 free electric car trip between governorates"]
                 },
    
    "Diamond": {"price": 5000, "features": 
     ["No ads",
      "24/7 Dedicated Support",
      "60 monthly trips on an electric motorcycle free",
      "150 km per month using a bike or skate for free",
      "15 free electric car trip between governorates"]
                }
    
}

def is_strong_password(password):
    if len(password) < 8:
        return False
    
    has_upper = any(char.isupper() for char in password)
    has_lower = any(char.islower() for char in password)
    has_digit = any(char.isdigit() for char in password)
    has_symbol = any(not char.isalnum() for char in password)
    
    return has_upper and has_lower and has_digit and has_symbol

def display_services():
    print("\n" + "="*50)
    print("Our services:".center(50))
    print("="*50)
    for i, service in enumerate(services, 1):
        print(f"{i}. {service}")

def display_days():
    today = datetime.datetime.now()
    print("\n" + "="*50)
    print("Available booking days:".center(50))
    print("="*50)
    for i in range(7):
        day = today + datetime.timedelta(days=i)
        print(f"{i+1}. {day.strftime('%A')} ({day.strftime('%d-%m-%Y')})")

def display_subscription_plans():
    print("\n" + "="*50)
    print("Subscription Plans:".center(50))
    print("="*50)
    for plan, details in subscription_plans.items():
        print(f"\n{plan} Plan:")
        print(f"Price: ${details['price']}/Year")
        print("Features:")
        for feature in details['features']:
            print(f"  - {feature}")
    print("="*50)

def book_service(username):
    display_services()
    service_choice = int(input("\nChoose the service number (1-6): ")) - 1
    while service_choice < 0 or service_choice > 5:
        print("Invalid choice! Please select between 1-6.")
        service_choice = int(input("Choose the service number (1-6): ")) - 1
    
    display_days()
    day_choice = int(input("\nChoose the day number (1-7): ")) - 1
    while day_choice < 0 or day_choice > 6:
        print("Invalid choice! Please select between 1-7.")
        day_choice = int(input("Choose the day number (1-7): ")) - 1
    
    today = datetime.datetime.now()
    selected_day = today + datetime.timedelta(days=day_choice)
    date_str = selected_day.strftime('%d-%m-%Y')
    day_name = selected_day.strftime('%A')
    
    print("\nAvailable time periods:")
    periods = [
               "12:00 AM",
               "1:00 AM",
               "2:00 AM",
               "3:00 AM",
               "4:00 AM",
               "5:00 AM",
               "6:00 AM",
               "7:00 AM",
               "8:00 AM",
               "9:00 AM",
               "10:00 AM",
               "11:00 AM",
               "12:00 PM",
               "1:00 PM",
               "2:00 PM",
               "3:00 PM",
               "4:00 PM",
               "5:00 PM",
               "6:00 PM",
               "7:00 PM",
               "8:00 PM",
               "9:00 PM",
               "10:00 PM",
               "11:00 PM"
               ]
    for i, period in enumerate(periods, 1):
        print(f"{i}. {period}")
    
    period_choice = int(input("\nSelect the period number: ")) - 1
    while period_choice < 0 or period_choice >= len(periods):
        print("Invalid choice! Please select a valid period.")
        period_choice = int(input("Select the period number: ")) - 1
    
    print("\n" + "="*50)
    print("Personal data".center(50))
    print("="*50)
    full_name = input("Full name: ")
    id_number = input("ID number: ")
    the_address = input("The address: ")
    
    print("\n" + "="*50)
    print("Your request has been successful!".center(50))
    print("="*50)
    print(f"Username: {username}")
    print(f"Full name: {full_name}")
    print(f"ID number: {id_number}")
    print(f"The address: {the_address}")
    print(f"Service: {services[service_choice]}")
    print(f"Date: {date_str} ({day_name})")
    print(f"Period: {periods[period_choice]}")
    print("="*50)
    print("Thank you for using our services!"
          "    "
          "    "
          "Save this information with you.".center(50))
    print("="*50)

def subscribe_service(username):
    display_subscription_plans()
    
    print("\nAvailable subscription plans:")
    plans = list(subscription_plans.keys())
    for i, plan in enumerate(plans, 1):
        print(f"{i}. {plan} (${subscription_plans[plan]['price']}/month)")
    
    plan_choice = int(input("\nChoose the plan number: ")) - 1
    while plan_choice < 0 or plan_choice >= len(plans):
        print("Invalid choice! Please select a valid plan.")
        plan_choice = int(input("Choose the plan number: ")) - 1
    
    selected_plan = plans[plan_choice]
    
    print("\n" + "="*50)
    print("Payment Information".center(50))
    print("="*50)
    card_number = input("Credit Card Number: ")
    expiry_date = input("Expiry Date (MM/YY): ")
    cvv = input("CVV: ")
    
    print("\n" + "="*50)
    print("Subscription Successful!".center(50))
    print("="*50)
    print(f"Plan: {selected_plan}")
    print(f"Price: ${subscription_plans[selected_plan]['price']}/month")
    print(f"Features:")
    for feature in subscription_plans[selected_plan]['features']:
        print(f"  - {feature}")
    print("="*50)
    print("Thank you for your subscription!"
          "    "
          "    "
          "Save this information with you.".center(50))
    print("="*50)

def main_menu(username):
    while True:
        print("\n" + "="*50)
        print(f"Welcome {username}!".center(50))
        print("="*50)
        print("\nMain Menu:")
        print("1. Book a service")
        print("2. Subscribe to a plan")
        print("3. Log out")
        
        choice = input("\nSelect option number: ")
        
        if choice == '1':
            book_service(username)
        elif choice == '2':
            subscribe_service(username)
        elif choice == '3':
            print("\nYou have been logged out successfully!")
            break
        else:
            print("Invalid choice! Please select a valid option.")

def create_account():
    print("\n" + "-" * 50)
    print("Create a new account")
    print("-" * 50)

    while True:
        username = input("Enter your username: ").strip()
        if not username:
            print("Error: Username cannot be empty!")
        elif username in users:
            print("Error: Username already exists!")
        else:
            break

    print("\n" + "=" * 50)
    print("Password requirements:")
    print("- Must be at least 8 characters")
    print("- Must contain uppercase and lowercase letters")
    print("- Must contain numbers")
    print("- Must contain special symbols")
    print("=" * 50 + "\n")

    while True:
        password = input("Enter your password: ")
        if is_strong_password(password):
            break
        else:
            print("Weak password! Please try again.")
            print("Make sure it meets all the requirements.")

    while True:
        confirm = input("Re-enter your password to confirm: ")
        if password == confirm:
            users[username] = password
            print("\n" + "*" * 50)
            print("Registration successful! You can now log in.")
            print("*" * 50)
            return username
        else:
            print("Error: Passwords do not match! Please try again.")

def main():
    current_user = None
    
    print("=" * 60)
    print("Smart City Services Management System".center(60))
    print("=" * 60)

    while True:
        if current_user:
            main_menu(current_user)
            current_user = None
        else:
            print("\nAvailable options:")
            print("1: Create new account")
            print("2: Log in")
            print("3: Exit")
        
            choice = input("\nSelect option number: ")

            if choice == '1':
                current_user = create_account()
            elif choice == '2':
                print("\n" + "-" * 50)
                print("Login")
                print("-" * 50)

                username = input("Username: ")
                password = input("Password: ")

                if username in users and users[username] == password:
                    current_user = username
                    print("\n" + "=" * 50)
                    print(f"Welcome {username}! You have successfully logged in!")
                    print("=" * 50)
                else:
                    print("Error: Incorrect username or password! Please try again.")
            elif choice == '3':
                print("\nThank you for using the system. See you soon!")
                break
            else:
                print("Error: Invalid selection! Please select 1, 2 or 3.")

if __name__ == "__main__":
    main()