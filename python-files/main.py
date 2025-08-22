import math

def calculate_battery_packs():
    """
    Calculates the possible battery pack capacities based on a user-entered system voltage.
    """
    
    # Define module specifications
    VM = 12.8  # Voltage of one module (V)
    AH = 105   # Ah capacity of one module (Ah)
    EM = 1344  # Energy of one module (Wh)

    print("Welcome to the Battery Pack Calculator! 🔋")
    print("This program helps you find the possible capacities of battery packs.")
    print("-" * 50)
    
    try:
        # Get system voltage from the user
        VS_str = input("Please enter the desired system voltage (VS) in Volts: ")
        VS = float(VS_str)
        
        if VS <= 0:
            print("System voltage must be a positive number. Please try again.")
            return

        # Calculate number of modules in series (NMS)
        NMS = math.ceil(VS / VM)
        print(f"\nBased on your desired voltage of {VS}V, you will need {NMS} modules in series.")

        # Calculate the minimum possible capacity (MINC)
        MINC = (EM * NMS) / 1000
        print(f"The minimum possible capacity for this series configuration is {MINC:.2f} kWh.")

        # Calculate possible scaled capacities
        MINC2 = 2 * MINC
        MINC3 = 3 * MINC
        MINC4 = 4 * MINC
        MINC5 = 5 * MINC

        # Display the results
        print("\nHere are the possible capacities for your battery pack:")
        print(f"  - Option 1 (Minimum): {MINC:.2f} kWh")
        print(f"  - Option 2 (Double): {MINC2:.2f} kWh")
        print(f"  - Option 3 (Triple): {MINC3:.2f} kWh")
        print(f"  - Option 4 (Quadruple): {MINC4:.2f} kWh")
        print(f"  - Option 5 (Quintuple): {MINC5:.2f} kWh")
        
        print("-" * 50)
        print("Note: These values assume you're adding parallel strings of the series-connected modules to increase capacity.")
        
    except ValueError:
        print("Invalid input. Please enter a valid number for the system voltage.")

# Run the program
if __name__ == "__main__":
    calculate_battery_packs()