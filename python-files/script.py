import pyautogui
import time
import datetime
import subprocess
import pygetwindow as gw


# --- Configuration (replace with your values) ---
app_path = "C:\\Program Files (x86)\\NetRom MealApp\\Meal.exe"
# Coordinates for key UI elements
# Get these by running the coordinate-finder script
# It's a good practice to store them in variables for clarity.
alege_meniul_coords = (100, 550)
luni_tab_coords = (250, 300)
marti_tab_coords = (350, 300)
# ... and so on for all days
ghiveci_radio_coords = (500, 400)
piept_pui_radio_coords = (750, 400)
fructe_radio_coords = (750, 800)
save_button_coords = (600, 950)
editeaza_meniul = (133, 299)
saptamana = [(665, 272), (905, 272), (1145, 272), (1385, 272), (1625, 272)]
fel1 = (880,539)
fel2 = (880,729)
fel3 = (880,919)
save = (1095,1001)
close = (1901,11)

# --- The Bot Logic ---
def order_food():
    print(app_path)
    # 1. Open the application
    subprocess.Popen(app_path) # uncomment if needed
    time.sleep(3) # Wait for the app to load

    try:
        window_title = "Meal"
        app_window = gw.getWindowsWithTitle(window_title)[0]
        print(app_window)
        app_window.maximize()
        time.sleep(2) # Give it a moment to resize
    except IndexError:
        print(f"Error: Could not find a window with the title '{window_title}'.")
        return # Stop the script if the window isn't found

    # 2. Navigate to "Alege meniul"
    pyautogui.click(editeaza_meniul)
    time.sleep(2)

    for day_coords in saptamana:
    # Use pyautogui to click on the current coordinates in the loop
        pyautogui.click(day_coords)
        time.sleep(1)
        pyautogui.click(fel1)
        pyautogui.click(fel2)
        pyautogui.click(fel3)
    pyautogui.click(save)
    time.sleep(1)
    pyautogui.click(close)
    print("Food order for the week has been placed!")

# --- Scheduling the Bot ---
# Check if today is Wednesday (weekday() returns 0 for Monday, 2 for Wednesday)
# You could also use an external scheduler like Windows Task Scheduler
if datetime.datetime.now().weekday() == 2:
    print("It's Wednesday, starting the food order bot.")
    order_food()
else:
    print("Not Wednesday. The bot will not run.")
    order_food()
