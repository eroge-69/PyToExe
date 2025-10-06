# (PROGRAM):   CALORIE NINJA V1.0 BETA | FUNCTIONS: ADD/REMOVE/CHANGE CALORIE GOALS + CALORIC DATA, DELETE/CREATE USER ACCOUNTS, LOGIN/OUT OF USER ACCOUNTS
# (ALGORITHM): BASED OFF THE "NICEGUI" PYTHON LIBRARY/FRAMEWORK, PYCHARM PYTHON IDE, WINDOWS 11 PRO OS,
# (CREDITS):   NICEGUI WEB FUNCTIONS - Zauberzeug GmbH | MAIN PROGRAMMING - Ryan Veenstra | DATA PATCHES/HOTFIXES - Chatgpt.com, Ryan Veenstra | LOGO - Rushil vjaykumar | FEEDBACK/BETA TESTERS - Tayem kassaby, Ronal Weresakera, Jackson Chandra

# data types used: integers for decisive and efficient equations + calculations,
#                  strings for inputs and validation,
#                  dictionaries for key user session data and authentication status,
#                  rows to organize the user interface elements visually,
#                  columns/data fields to stack elements vertically,

# begin imports from python libraries, ensure all are loading first before any other code
import asyncio
import os
import csv
import random
import pandas as pd
import re
from fastapi import Request
from fastapi.responses import RedirectResponse
from starlette.middleware.base import BaseHTTPMiddleware
from nicegui import app, ui
import datetime
from argon2.exceptions import VerifyMismatchError

# find the current day of the week and set it to the variable current_day
current_day = datetime.datetime.now().strftime('%A')

# auto set the users gender to None, until changed upon account creation
user_gender = None

# Define the swedish calorie database used to search food items
cal_database = "Calorie_database.xlsx"

# read the Excel file
food_df = pd.read_excel(cal_database, header=2)
food_df.columns = food_df.columns.str.strip()

# search the database based on name of food and calories per 100g
food_df = food_df[['Name', 'Energy, kilocalories (kcal)']]
food_df.dropna(inplace=True)

# check for case-sensitive searches with food search inputs
food_df['Name_lower'] = food_df['Name'].str.lower()

# define the user data csv path
CSV_PATH = "users.csv"

# define the landing url's that don't need an authenticated session to access
unrestricted_page_routes = {'/login', '/CreateAccount', '/about'}

# set "passwords" as a dictionary loaded from the users csv file, use a dictionary to store and manage passwords allowing the ability for easy look-ups, adding, removing and updating
passwords = {}  # Loaded from CSV

# generate random numbers for human verification, use integers for easier math equations
num1 = random.randint(1, 10)
num2 = random.randint(1, 10)
math = (num1 + num2)
ans = math

# define the set resolution size for background ui elements and pictures
res_y = "1920px"
rex_x = "1080px"

# auto set dark mode to false upon login or account creation
dark_mode = False


# define the function set_background to change the ui elements background more efficiently
def set_background(color: str):
    ui.query('body').style(f'background-color: {color}')


# define the function get_calories_for_food to retrieve calorie data from the swedish calorie database
def get_calories_for_food(query: str) -> int | None:
    if not query:
        return None

    match = food_df[food_df['Name_lower'].str.contains(query.lower())]

    if not match.empty:
        return int(match.iloc[0]['Energy, kilocalories (kcal)'])
        # check that the matched item is not empty, return the matched items energy and calorie data

    return None
    # if not found, return None


# define the function save_bmi_and_caloric_intake_to_csv to save changed bmi and calorie data to the specified user
def save_bmi_and_caloric_intake_to_csv(username, bmi, caloric_intake):
    if not os.path.exists(CSV_PATH):
        # validate that the csv path "users.csv" exists, if not found return None
        return

    # if the "users.csv" file is found, open the file and search for the username of the user, receive the bmi and caloric data
    updated_rows = []
    with open(CSV_PATH, mode='r', newline='') as file:
        reader = csv.DictReader(file)
        for row in reader:

            if row.get('username') == username:
                # search the rows inside the specified user for the bmi and caloric intake data, use a row to iterate through the data one record at a time
                row['bmi'] = str(bmi)
                row['caloric_intake'] = str(caloric_intake)
            updated_rows.append(row)

    with open(CSV_PATH, mode='w', newline='') as file:

        fieldnames = updated_rows[0].keys()
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(updated_rows)


# define the function load_user_calories_from_users_csv to retrieve users calorie goals
def load_user_calories_from_users_csv(username: str) -> int:
    if not os.path.exists(CSV_PATH):
        # validate that the csv path "users.csv" exists, if not found return None
        return 0

    with open(CSV_PATH, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:

            if row.get('username') == username:
                try:
                    # return the specified total calories from the unique user account

                    return int(row.get('total_calories', 0))
                except (ValueError, TypeError):
                    return 0
    return 0


# define the function load_user_daily_calories_from_users_csv to retrieve users daily calorie goals
def load_user_daily_calories_from_users_csv(username: str) -> int:
    if not os.path.exists(CSV_PATH):
        # validate that the csv path "users.csv" exists, if not found return None
        return 0

    with open(CSV_PATH, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)

        for row in reader:
            if row.get('username') == username:
                try:

                    return int(row.get('set_daily_calories', 0))

                # check for value errors and type errors that may occur
                except (ValueError, TypeError):
                    return 0
    return 0


# define the function save_user_calories_to_users_csv to save users changed caloric data to the csv (TAKEN FROM nicegui.io demo's)
def save_user_calories_to_users_csv(username: str, total_calories: int, user_set_calories_amount: int):
    rows = []
    updated = False

    # Read existing rows from the users csv file
    if os.path.exists(CSV_PATH):
        # validate that the csv path "users.csv" exists, if not found return None
        with open(CSV_PATH, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)

    # define the field names for the stored user data/variables, visible at the top of the csv file, use a list to allow easier understanding of the csv headings and values
    fieldnames = ['username', 'password', 'age_value', 'total_calories', 'set_daily_calories', 'user_gender', 'bmi',
                  'caloric_intake']

    # add any extra unknown fieldnames
    if rows:
        for key in rows[0].keys():
            if key not in fieldnames:
                fieldnames.append(key)

    # update existing rows if needed
    for row in rows:
        if row['username'] == username:
            row['total_calories'] = str(total_calories)
            row['set_daily_calories'] = str(user_set_calories_amount)
            updated = True
            break

    # add new user rows if not found
    if not updated:
        new_row = {
            'username': username,
            'password': '',
            'age_value': '',
            'total_calories': str(total_calories),
            'set_daily_calories': str(user_set_calories_amount),
            'user_gender': '',
            'bmi': '',
            'caloric_intake': ''
        }

        # fill any extra fields with empty string
        for key in fieldnames:
            if key not in new_row:
                new_row[key] = ''
        rows.append(new_row)

    with open(CSV_PATH, 'w', newline='', encoding='utf-8') as f:

        # define the csv writer
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for row in rows:
            clean_row = {}
            for key, value in row.items():

                # clean any list/dictionary data into flat strings
                if isinstance(value, list) or isinstance(value, dict):
                    clean_row[key] = str(value)

                else:
                    clean_row[key] = str(value).strip()
            writer.writerow(clean_row)


# define the function load_users_from_csv to load users accounts + data from the users csv file
def load_users_from_csv():
    if not os.path.exists(CSV_PATH):
        # validate that the csv path "users.csv" exists, if not found return None
        return

    # Clear previous users first
    passwords.clear()

    with open(CSV_PATH, "r", newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:

            if len(row) >= 2:
                username, hashed_pass = row[0].strip(), row[1].strip()

                passwords[username] = hashed_pass


# ensure the "users.csv" file is fully read, make sure the users are properly loaded before loading the ui to combat potential errors
load_users_from_csv()


# define the function remove_user_data to wipe users data clean from the csv file
def remove_user_data(username: str, csv_path: str):
    if not os.path.exists(csv_path):
        # validate that the csv path "users.csv" exists, if not found return None
        return

    with open(csv_path, 'r', newline='') as f:
        rows = list(csv.reader(f))
        # read the rows of the csv file

    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        # define the writer to the csv file

        for row in rows:
            if row and row[0] != username:
                # remove the existing users data, wiping all saves
                writer.writerow(row)


# define the function load_bmi_from_csv to load users bmi details from the csv file
def load_bmi_from_csv(username: str):
    if not os.path.exists(CSV_PATH):
        # validate that the csv path "users.csv" exists, if not found empty strings in the place of the bmi value
        return "", ""

    with open(CSV_PATH, mode='r', newline='') as file:

        reader = csv.DictReader(file)
        for row in reader:

            if row['username'] == username:
                # find the data related to the users bmi
                return row.get('bmi', '')
    return ""


# define the function load_gender_from_csv to load users gender from the csv file
def load_gender_from_csv(username: str):
    if not os.path.exists(CSV_PATH):
        # validate that the csv path "users.csv" exists, if not found empty strings in the place of the bmi value
        return ""

    with open(CSV_PATH, mode='r', newline='', encoding='utf-8') as file:
        # read the file only in mode "R"
        reader = csv.DictReader(file)
        for row in reader:
            if row.get('username', '').strip() == username.strip():
                # find the data related to the users gender value
                return row.get('user_gender', '').strip()
    return ""


# define the function load_caloric_intake_from_csv to load users caloric intake data from the csv file
def load_caloric_intake_from_csv(username: str):
    if not os.path.exists(CSV_PATH):
        # validate that the csv path "users.csv" exists, if not found empty strings in the place of the calorie intake value
        return "", ""

    with open(CSV_PATH, mode='r', newline='') as file:
        reader = csv.DictReader(file)

        # read the file only in mode "R"
        for row in reader:
            if row['username'] == username:
                # find the data related to the users caloric_intake
                return row.get('caloric_intake', '')
    return ""


# define the function load_user_age_from_users_csv to load users account age from the csv file
def load_user_age_from_users_csv(username: str) -> int:
    if not os.path.exists(CSV_PATH):
        # validate that the csv path "users.csv" exists, if not found empty strings in the place of the calorie intake value
        return 0

    with open(CSV_PATH, mode='r', newline='') as file:
        reader = csv.DictReader(file)

        # read the file only in mode "R"
        for row in reader:
            if row.get('username') == username:
                # find the data related to the users age_value
                return int(row.get('age_value', 0))
    return 0


# GENERATED BY CHATGPT - create a class to check if the user is authenticated (through login) and redirect the user if not fully authenticated
class AuthMiddleware(BaseHTTPMiddleware):

    # create an async function
    async def dispatch(self, request: Request, call_next):
        user = getattr(app.storage, 'user', {})

        # define the authenticity check, ensuring users are properly authenticated before accessing certain domains
        authenticated = user.get('authenticated', False)
        path = request.url.path

        # redirect un-authenticated users toward the login page, do this to patch potential data related errors
        if not authenticated and not path.startswith('/_nicegui') and path not in unrestricted_page_routes:
            return RedirectResponse(f'/login?redirect_to={path}')
        return await call_next(request)


# define the password encrypter as get_hasher
def get_hasher():
    from argon2 import PasswordHasher

    # allow the function to access the password hasher library, returning the password hashing algorithm
    return PasswordHasher()


# GENERATED BY CHATGPT -
app.add_middleware(AuthMiddleware)


# create the class dashboardPage
class DashboardPage:
    def __init__(self):

        self.current_user = app.storage.user.get('username')

        # check that the user is properly logged in, if not redirect the individual to the login page
        if not self.current_user:
            ui.notify('No logged-in user found', color='negative')
            ui.navigate.to('/login')
            return

        # define user unique csv data values
        self.user_calories = load_user_calories_from_users_csv(self.current_user)
        self.age = load_user_age_from_users_csv(self.current_user)
        self.current_daily = load_user_daily_calories_from_users_csv(self.current_user)
        self.gender = load_gender_from_csv(self.current_user)
        self.progress_container = None
        self.progress = None

        # Prevent scrolling or resizing
        ui.add_head_html('<style>html, body { overflow: hidden; height: 100%; margin: 0; }</style>')

        self.build()
        self.build_ui()

    def build(self):

        # display the background image and log the loading of the page
        with ui.column().classes(
                "w-[calc(100%+20px)] shrink-0 fixed top-0 left-0 -translate-x-5 h-screen "
                "bg-[url('https://images.pexels.com/photos/349610/pexels-photo-349610.jpeg?cs=srgb&dl=pexels-goumbik-349610.jpg&fm=jpg')] "
                "bg-cover bg-center opacity-50 text-white"
        ):
            print("Loaded dashboard")

    async def logout(self):

        # clear all ui elements on screen
        app.storage.user.clear()
        self.progress_container.clear()
        self.card2.clear()
        self.card3.clear()
        self.card4.clear()
        self.card5.clear()
        self.card6.clear()
        self.name_label.clear()
        self.row.clear()

        with self.progress_container:
            # display the loading animation and redirect the user to the login page
            ui.skeleton().classes('w-[480px] h-2')
            ui.label('Logging out...').classes('text-white text-xl justify-center text-bold')

        await asyncio.sleep(2)
        ui.notify('Successfully logged out', color='positive')
        await asyncio.sleep(1)
        ui.navigate.to('/login')

    def new_day_check(self):
        # find current day
        current_day = datetime.datetime.now().strftime('%A')

        # get the stored last day (default to empty string if not found)
        last_day = app.storage.general.get('last_day', '')

        # if the stored day is different from today
        if last_day != current_day:
            # update stored day to current day
            app.storage.general['last_day'] = current_day

            # reset progress value
            self.progress.set_value(0)

    def add_calories(self, calorie_input):
        try:
            calorie_val = int(calorie_input.value)

            # check that the calorie amount entered is below 0
            if calorie_val < 0:
                remove_val = abs(calorie_val)

                # check that the removal amount is not greater than the maximum daily goal
                if remove_val > self.user_calories:
                    ui.notify("Cannot remove more than your current calories.", color='red')
                    return

                # remove the calories entered from the users calories
                self.user_calories -= remove_val
                self.user_calories = max(self.user_calories, 0)
                ui.notify(f"Removed {remove_val} calories. Total now {self.user_calories}.", color='blue')

            else:
                self.user_calories += calorie_val
                self.user_calories = min(self.user_calories, self.current_daily)
                ui.notify(f"Added {calorie_val} calories. Total now {self.user_calories}.", color='positive')

            self.progress.set_value(self.user_calories)

            # save updated calories to the csv file
            save_user_calories_to_users_csv(self.current_user, self.user_calories, self.current_daily)

        except (ValueError, TypeError):

            # validate value errors and type errors when users type inside
            ui.notify("Please enter a valid number value.", color='negative')

        finally:
            calorie_input.value = ''

    def change_daily(self, daily_input):
        try:
            new_daily = int(daily_input.value)
            if 1000 <= new_daily <= 5000:
                self.current_daily = new_daily
                if self.user_calories > self.current_daily:
                    self.user_calories = self.current_daily

                # re-render/load progress bar
                self.render_progress()

                # clear the daily goal input, allow the user to type in a new integer value
                daily_input.value = ''

                save_user_calories_to_users_csv(self.current_user, self.user_calories, self.current_daily)
                ui.notify(f'Changed daily calorie goal to {new_daily}', color='positive')
            else:
                ui.notify('Please enter a valid number value between 1000 and 5000', color='negative')

        except (ValueError, TypeError):
            # validate any datatype errors or type errors and inform the user if any
            ui.notify('Please enter a valid number value.', color='negative')

    def render_progress(self):
        # clear previous progress
        self.progress_container.clear()

        with self.progress_container:
            with ui.column().classes('items-center justify-center mt-40 ml-[117px]'):
                self.progress = ui.circular_progress(
                    value=self.user_calories,
                    min=0,
                    max=self.current_daily,
                    color='green'
                ).classes('w-[250px] h-[250px] text-black text-sm')
        return self.progress

    def search_and_add_calories(self, search_input):

        # take the value of the users input inside "search_input"
        food = search_input.value.strip()

        if not food or food.isdigit():
            # validate the input for incorrect formalities and integer values
            search_input.value = ''
            ui.notify('Please enter a valid word value', color='negative')
            return

        if len(food) <= 3:
            # validate the length of the users input, removing small errors in typing or csv searching
            search_input.value = ''
            ui.notify('Please enter a valid word value over 3 characters long', color='negative')
            return

        calories = get_calories_for_food(food)

        if calories is not None:

            # check if the entered text is valid, search the csv and add the correct calories
            self.user_calories += calories
            if self.user_calories > self.current_daily:
                self.user_calories = self.current_daily

            # update the value of the circle
            self.progress.set_value(self.user_calories)

            # clear the daily goal input, allow the user to type in a new integer value
            search_input.value = ''
            save_user_calories_to_users_csv(self.current_user, self.user_calories, self.current_daily)
            ui.notify(f'Added {calories} kcal from "{food}". Total now {self.user_calories}.', color='positive')

        else:

            # validate the entered string value and inform the user of issues
            ui.notify(f'No match found for "{food}" in calorie database.', color='negative')

    def build_ui(self):

        # build the main ui to hold the inputs and buttons for the user to interact with
        with ui.card().classes('shrink-0 w-[510px] mt-20 absolute-center border-opacity-50 shadow-none') as self.row:
            calorie_input = ui.input('Add/Remove Calories', placeholder='eg. 500 or -500').classes(
                'w-[480px] mt-[180px] text-black')
            ADD_CALORIES = ui.button('Add/Remove Calories', on_click=lambda: self.add_calories(calorie_input)).classes(
                'w-[480px] text-black').props('color=white')

            daily_input = ui.input('Set daily calorie limit', placeholder='eg. (1200-5000)').classes(
                'w-[480px] text-black')
            ui.button('Change calorie goal', on_click=lambda: self.change_daily(daily_input)).classes(
                'w-[480px] text-black').props('color=white')

            # allow the enter key on the keyboard to fire the event "add_calories" and "change_daily"
            calorie_input.on('keydown.enter', lambda e: self.add_calories(calorie_input))
            daily_input.on('keydown.enter', lambda e: self.change_daily(daily_input))

        with ui.card().classes(
                'shrink-0 w-[510px] mt-[-160px] absolute-center border-opacity-50 shadow-none') as self.card2:

            # set the parameters of the progress ui (circle)
            self.progress_container = ui.row()
            self.render_progress()

        with ui.card().classes(
                'fixed bottom-0 left-0 w-screen rounded-none justify-center mb-0 text-sm font-bold font-sans z-50'
        ) as self.card3:

            # display the bottom buttons allowing the user to switch dashboard screens
            with ui.row().classes('w-full justify-around items-center'):
                home_button = ui.button(icon='home', color='white', on_click=lambda: print("home")).classes(
                    'text-black')
                home_button.tooltip('Home').classes('bg-green')

                exercises_button = ui.button(icon='o_monitor_heart', color='white',
                                             on_click=lambda: ui.navigate.to('/dashboard/exercises_and_food')).classes(
                    'text-black')
                exercises_button.tooltip('Exercises + food').classes('bg-green')

                data_button = ui.button(icon='o_scale', color='positive',
                                        on_click=lambda: ui.navigate.to('/dashboard/data')).classes('text-black')
                data_button.tooltip('User Data').classes('bg-green')

                settings_button = ui.button(icon='o_settings', color='white',
                                            on_click=lambda: ui.navigate.to('/dashboard/settings')).classes(
                    'text-black')
                settings_button.tooltip('Settings').classes('bg-green')

        with ui.card().classes(

                # display the day of the week, use the library datetime to find the exact day
                'w-[1000px] shrink-0 mt-[150px] absolute-center top-0 border-opacity-50 shadow-none') as self.card4:
            with ui.tabs().classes('w-full') as tabs:
                monday = ui.tab('Monday')
                tuesday = ui.tab('Tuesday')
                wednesday = ui.tab('Wednesday')
                thursday = ui.tab('Thursday')
                friday = ui.tab('Friday')
                saturday = ui.tab('Saturday')
                sunday = ui.tab('Sunday')

            # define days of the week, (mon-sun)
            day_tab_map = {
                'Monday': monday,
                'Tuesday': tuesday,
                'Wednesday': wednesday,
                'Thursday': thursday,
                'Friday': friday,
                'Saturday': saturday,
                'Sunday': sunday
            }

            with ui.tab_panels(tabs, value=day_tab_map.get(current_day, monday)).classes('w-full') as today:

                # display the specified day of the week with the users goal
                if today.value == monday:
                    with ui.tab_panel(monday):
                        ui.label('MONDAY - TODAYS GOAL:')
                elif today.value == tuesday:
                    with ui.tab_panel(tuesday):
                        ui.label('TUESDAY - TODAYS GOAL:')
                elif today.value == wednesday:
                    with ui.tab_panel(wednesday):
                        ui.label('WEDNESDAY - TODAYS GOAL:')
                elif today.value == thursday:
                    with ui.tab_panel(thursday):
                        ui.label('THURSDAY - TODAYS GOAL:')
                elif today.value == friday:
                    with ui.tab_panel(friday):
                        ui.label('FRIDAY - TODAYS GOAL:')
                elif today.value == saturday:
                    with ui.tab_panel(saturday):
                        ui.label('SATURDAY - TODAYS GOAL:')
                elif today.value == sunday:
                    with ui.tab_panel(sunday):
                        ui.label('SUNDAY - TODAYS GOAL:')

        with ui.card().classes(
                'w-[510px] shrink-0 fixed left-[30px] top-1/2 -translate-y-1/2 border-opacity-50 shadow-none') as self.card5:
            ui.label("Food calorie searcher").classes('w-[480px] text-black text-sm font-bold').props(
                'color=white')

            # define search inputs and buttons for the calorie database searcher
            search_input = ui.input(label='Search food (per 100g)', placeholder='Start typing food name...').props(
                'autocomplete').classes('w-[480px] text-black text-sm font-bold')
            ui.button('Add from food database', icon='fastfood',
                      on_click=lambda: self.search_and_add_calories(search_input)).classes(
                'w-[480px] text-black').props('color=white')

            # allow the user to press the enter key to fire the search_and_add_calories function
            search_input.on('keydown.enter', lambda e: self.search_and_add_calories(search_input))

        with ui.card().classes(
                'w-[510px] shrink-0 fixed right-10 top-1/2 -translate-y-1/2 border-opacity-50 shadow-none') as self.card6:
            ui.label("User account details").classes('w-[480px] text-black text-sm font-bold').props(
                'color=white')
            ui.label(f"Your age is: {self.age}").classes('w-[480px] text-black text-sm font-bold').props(
                'color=white')
            ui.label(f"Your gender is: {self.gender}").classes('w-[480px] text-black text-sm font-bold').props(
                'color=white')

            # allow the user to logout upon clicking, redirecting the user and clearing the local storage
            ui.button("Logout", icon='logout', on_click=self.logout).props('outline square').classes(
                'w-[480px] text-black').props('color=white')

        with ui.column().classes(
                'fixed top-0 left-1/2 -translate-x-1/2 mt-5 items-center w-[600px]') as self.name_label:

            # display a welcome message at the top of the screen with the users account username
            ui.label(f"Welcome back user: {self.current_user}!").classes(
                'text-black text-4xl font-bold text-center'
            )


@ui.page('/dashboard')
def dashboard_main():
    DashboardPage().new_day_check()
    dashboard = DashboardPage()


# define the about page, giving details and tips about the CN program
class AboutPage:
    def __init__(self):
        # Main container column with background and styling
        self.container = ui.column().classes(
            "w-[calc(100%+20px)] shrink-0 fixed top-0 left-0 -translate-x-5 h-screen "
            "bg-[url('https://rare-gallery.com/uploads/posts/583221-food-4k-wallpaper.jpg')] "
            "bg-cover bg-center opacity-30 text-white"
        )
        print("loaded settings")
        set_background('white')

        # build and render the main ui elements of the page
        self.stepper = ui.stepper().props('vertical').classes('w-[510px] text-black absolute-center shadow-none')
        self.build()

        self.build_header()
        self.build_footer()

    def build(self):
        self.stepper.clear()
        with self.stepper as stepper:
            # build a stepper to allow the user to click a button to show another slide
            with ui.step('Initialization'):
                ui.label(
                    'Built from the bareness of word documents, software development diagrams and python scripts....'
                ).classes('text-black')

                with ui.stepper_navigation():
                    ui.button('Next', on_click=stepper.next)

            with ui.step('Thorough Ideation'):
                ui.label(
                    'The design of the calorie ninja came not upon single night, but with many fruit-full nights...'
                ).classes('text-black')

                with ui.stepper_navigation():
                    ui.button('Next', on_click=stepper.next)
                    ui.button('Back', on_click=stepper.previous).props('flat')

            with ui.step('Our journey.. and maybe yours'):
                ui.label(
                    'A breakthrough with the python library NICEGUI allowed the calorie ninja application to shine in its developed glory.'
                ).classes('text-black')

                with ui.stepper_navigation():
                    ui.button('Back', on_click=stepper.previous).props('flat')

                # allow the user to redirect to the create account screen
                with ui.card().classes(
                        'w-[510px] mt-[200px] text-black absolute-center shadow-none border-green-600') as card:
                    card.clear()
                    ui.button('Start your Journey now', on_click=self.loading_login).classes(
                        'w-[480px] text-black').props('color=white')

    async def loading_login(self):
        ui.navigate.to('/CreateAccount')

    def build_header(self):
        with ui.row().classes("absolute-top text-7xl mt-35 w-full justify-center font-bold font-sans"):
            ui.label("About the Calorie Ninja").classes('text-white')

    def build_footer(self):
        with ui.row().classes("fixed bottom-0 w-full justify-center mb-2 text-sm font-bold font-sans z-45"):
            ui.label("CALORIE NINJA V1.0 BETA").classes("text-white")


@ui.page('/about')
def about_page():
    if app.storage.user.get('authenticated', False):
        # check that the user is correctly authenticated, if already authenticated - redirect the user to the dashboard
        return RedirectResponse('/dashboard')
    AboutPage().build()


# define the settings page, allowing users to customise their application visuals/accounts
class SettingsPage:
    def __init__(self, username):

        # define pre-existing variables until changed
        self.dark_mode = False
        self.username_input = None
        self.pass_input = None
        self.hasher = get_hasher()

    def toggle_dark_mode(self):

        # check if dark mode is on or off and switch to the opposite
        self.dark_mode = not self.dark_mode
        color = 'black' if self.dark_mode else 'white'
        ui.query('body').style(f'background-color: {color}')

    def confirm_delete(self):
        with ui.dialog() as dialog, ui.card():

            # ensure the user enters only their accounts username to delete
            ui.label("Enter your username and password to confirm account deletion:")
            self.username_input = ui.input(placeholder="Enter account username").classes('w-full')
            self.pass_input = ui.input(placeholder="Enter account password").classes('w-full')

            def on_confirm():
                typed_username = self.username_input.value.strip()
                typed_password = self.pass_input.value.strip()

                current_username = app.storage.user.get("username", "")
                stored_hash = passwords.get(current_username)

                # check the username of the account
                if typed_username != current_username or not stored_hash:
                    ui.notify("Username or password incorrect. Account NOT deleted.", color='negative')
                    return

                # check the password with validation
                try:
                    if not self.hasher.verify(stored_hash, typed_password):
                        ui.notify("Username or password incorrect. Account NOT deleted.", color='negative')
                        return

                # check for any miss match errors between inputs - SOLUTION FROM CHAT GPT
                except VerifyMismatchError:
                    ui.notify("Username or password incorrect. Account NOT deleted.", color='negative')
                    return

                # if all validation passes, delete account users account
                remove_user_data(current_username, 'users.csv')
                app.storage.user.clear()
                load_users_from_csv()

                dialog.close()
                ui.notify("Account successfully deleted!", color='positive')

                # delay the redirect then redirect the user
                ui.timer(0.5, lambda: ui.navigate.to('/login'))

            confirm_delete = ui.button("Confirm Delete", on_click=on_confirm).classes('w-full text-black').props(
                'color=red')
            ui.button("Cancel", on_click=dialog.close).classes('w-full text-black').props('color=white')

        dialog.open()

    def build(self):
        # display the background container
        with ui.column().classes(
                "w-[calc(100%+20px)] fixed top-0 left-0 -translate-x-5 h-screen bg-[url('https://images.pexels.com/photos/1640770/pexels-photo-1640770.jpeg?cs=srgb&dl=pexels-ella-olsson-572949-1640770.jpg&fm=jpg')] bg-cover bg-center opacity-50 text-white shrink-0"
        ):
            print("loaded settings")
            set_background('white')

        # center the page title
        with ui.column().classes(
                'fixed top-0 left-1/2 -translate-x-1/2 mt-5 items-center w-[600px]'):
            ui.label("User settings").classes(
                'text-black text-4xl font-bold text-center'
            )

        # Main content container
        with ui.element().classes("absolute inset-[70px] bg-white rounded-sm shadow-lg shrink-0"):
            ui.label("").classes('text-black text-xl font-bold justify-center w-[350px] mt-[25px] -translate-y-[30px]')

            with ui.row().classes("w-full h-full px-10 gap-2 shrink-0"):
                # display Settings Column
                with ui.column().classes("flex-1 bg-gray-100 p-2 rounded shrink-0"):
                    ui.label("Display settings").classes("text-black text-md font-bold")

                    # display settings icons and switches
                    with ui.expansion('Visuals', icon='work').classes('w-full'):
                        ui.switch('Dark Mode', on_change=self.toggle_dark_mode)

                # account Settings Column
                with ui.column().classes("flex-1 bg-gray-100 p-2 rounded shrink-0"):
                    ui.label("Account settings").classes("text-black text-md font-bold")

                    # display settings icons and buttons
                    with ui.expansion('User options', icon='work').classes('w-full'):
                        ui.button('Delete user account', on_click=self.confirm_delete).classes(
                            'w-[600px] text-black').props('color=red')

        # display the bottom Navigation Bar inside a ui card
        with ui.card().classes(
                'fixed bottom-0 left-0 w-screen rounded-none justify-center mb-0 text-sm font-bold font-sans z-50 shrink-0'):
            with ui.row().classes('w-full justify-around items-center'):
                ui.button(icon='o_home', color='white', on_click=lambda: ui.navigate.to('/dashboard')).tooltip(
                    'Home').classes('bg-green')
                ui.button(icon='o_monitor_heart', color='white',
                          on_click=lambda: ui.navigate.to('/dashboard/exercises_and_food')).tooltip(
                    'Exercises + food').classes('bg-green')
                ui.button(icon='o_scale', color='white', on_click=lambda: ui.navigate.to('/dashboard/data')).tooltip(
                    'Data').classes('bg-green')
                ui.button(icon='settings', color='positive', on_click=lambda: print("settings")).tooltip(
                    'Settings').classes('text-black bg-green')

    def render(self):
        # just call build
        self.build()


@ui.page('/dashboard/settings')
def main_settings():
    current_user = app.storage.user.get('username')

    page = SettingsPage(current_user)
    page.render()


# define the dashboard data page
class DashboardDataPage:
    def __init__(self, username: str):
        # define important variables inside class, username, user calories, total calories
        self.username = username
        self.total_calories = load_user_calories_from_users_csv(username)
        self.daily_calories = load_user_daily_calories_from_users_csv(username)
        self.chart = None

    def render(self):
        with ui.column().classes(
                "w-[calc(100%+20px)] fixed top-0 left-0 -translate-x-5 h-screen "
                "bg-[url('https://images.unsplash.com/photo-1490818387583-1baba5e638af?fm=jpg&q=60&w=3000&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8Mnx8Zm9vZCUyMGJhY2tncm91bmR8ZW58MHx8MHx8fDA%3D')] "
                "bg-cover bg-center opacity-70 text-white"
        ):
            # log that the user has accessed the pashboard page
            print("loaded data page background")
            set_background("black")

        with ui.column().classes(
                'fixed top-24 left-1/2 -translate-x-1/2 items-center z-30') as name_label:
            ui.label("User data (graph)").classes('text-black text-6xl font-bold text-center')

        with ui.element().classes("absolute inset-[70px] bg-white rounded-sm shadow-lg shrink-0"):
            ui.label("").classes(
                'text-black text-xl font-bold justify-center w-[150px] mt-[50px] -translate-y-[30px]')

        with ui.card().classes(
                'fixed bottom-0 left-0 w-screen rounded-none justify-center mb-0 text-sm font-bold font-sans z-50'):
            with ui.row().classes('w-full justify-around items-center'):
                ui.button(icon='o_home', color='white', on_click=lambda: ui.navigate.to('/dashboard')).tooltip(
                    'Home').classes('bg-green')
                ui.button(icon='o_monitor_heart', color='white',
                          on_click=lambda: ui.navigate.to('/dashboard/exercises_and_food')).tooltip(
                    'Exercises + food').classes('bg-green')
                ui.button(icon='scale', color='positive').tooltip('User Data').classes('bg-green text-black')
                ui.button(icon='o_settings', color='white',
                          on_click=lambda: ui.navigate.to('/dashboard/settings')).tooltip('Settings').classes(
                    'bg-green')

        # build data for the calorie chart: show the daily goal and current total calories
        # the x axis shows the calorie amount, the y axis just shows label "Calories"

        # RECODED WITH CHAT GPT 3, NICEGUI CIRCULAR GRAPH
        chart_data = {
            'xAxis': {
                'type': 'value',
                'max': max(self.daily_calories, self.total_calories, 1000),
                'axisLabel': {
                    'color': 'black'  # X-axis numbers color
                },
                'axisLine': {
                    'lineStyle': {
                        'color': 'black'  # X-axis line color
                    }
                }
            },
            'yAxis': {
                'type': 'category',
                'data': ['Calories'],
                'inverse': True,
                'axisLabel': {
                    'color': 'black'  # Y-axis label color
                },
                'axisLine': {
                    'lineStyle': {
                        'color': 'black'  # Y-axis line color
                    }
                }
            },
            'legend': {
                'textStyle': {
                    'color': 'black'  # Legend text color
                }
            },
            'series': [
                {
                    'type': 'bar',
                    'name': 'Daily Calorie Goal',
                    'data': [self.daily_calories],
                    'label': {
                        'show': True,
                        'position': 'inside',
                        'color': 'black'  # Data label color for Daily Goal
                    }
                },
                {
                    'type': 'bar',
                    'name': 'Calories consumed',
                    'data': [self.total_calories],
                    'label': {
                        'show': True,
                        'position': 'inside',
                        'color': 'black'  # Data label color for Consumed
                    }
                },
            ],
            'color': ['#3498db', '#2ecc71'],  # blue for goal, green for consumed
            'backgroundColor': 'transparent'  # Optional: make chart background transparent
        }

        self.chart = ui.echart(chart_data).classes(
            'absolute w-[90%] shrink-0 h-[300px] top-[260px] left-1/2 -translate-x-1/2')

    # update chart data if needed
    def update_calories(self, total_calories: int, daily_calories: int):
        self.total_calories = total_calories
        self.daily_calories = daily_calories
        if self.chart:
            self.chart.options = {
                'series': [
                    {'data': [self.daily_calories]},
                    {'data': [self.total_calories]},
                ]
            }
            self.chart.update()


@ui.page('/dashboard/data')
def dashboard_data_page():
    current_user = app.storage.user.get('username')

    # check that the user is correctly authenticated, if already authenticated - redirect the user to the dashboard
    if not app.storage.user.get('authenticated', False):
        return RedirectResponse('/CreateAccount')  # or '/login'

    # otherwise, render the dashboard
    page = DashboardDataPage(current_user)
    page.render()


# define the dashboard exercises page
class DashboardExercisesPage:
    def __init__(self):

        # define important variables, bmi_label, caloric label, weight + height input
        self.bmi_label = None
        self.caloric_label = None
        self.weight_input = None
        self.height_input = None

    def calculate_and_save_health_data(self):
        try:

            # grab user variables, user weight + heigh input and users age input
            username = app.storage.user.get('username', '')
            weight = int(self.weight_input.value)
            height = int(self.height_input.value)
            age = load_user_age_from_users_csv(username)

            # validate correct int value inputs from users between 0 and 375 kg
            if weight <= 0 or weight > 375:
                ui.notify("Please enter a valid weight range value from 0 to 375kg.", color='negative')
                return

            # validate correct int value inputs from users between 0 and 200 cm
            if height <= 0 or height > 300:
                ui.notify("Please enter a valid height range value from 0 to 300cm.", color='negative')
                return

            else:
                # if the users inputs passes the validations above, allow the formula to function

                # calculate the bmi of the user
                height_m = height / 100
                bmi = round(weight / (height_m ** 2), 1)

                # caloric intake formula (Integer), for easier tracking and understanding (Harris-Benedict calorie formula)
                caloric_intake = round((12 * weight) + (10 * height) - (5 * age) + 5)

                # interpret the users bmi, and give a insight as to the health level
                if bmi < 18.5:
                    bmi_interpretation = "Underweight"

                # check between 18.5 and 25 for the users bmi
                elif 18.5 <= bmi < 25:
                    bmi_interpretation = "Normal weight"

                # check between 25 and 30 for the users bmi
                elif 25 <= bmi < 30:
                    bmi_interpretation = "Overweight"

                # if not any of the above and bigger than 30, display obese
                else:
                    bmi_interpretation = "Obese"

                # notify the user of the predictions
                ui.notify(f"BMI: {bmi} ({bmi_interpretation})", color='info')
                ui.notify(f"Estimated daily caloric intake: {caloric_intake} kcal", color='positive')

                # save the bmi and caloric data to the users csv
                save_bmi_and_caloric_intake_to_csv(username, bmi, caloric_intake)

                # update the ui text, grabbing it from the saved users csv document
                self.bmi_label.set_text(f"Your estimated BMI is: {bmi}")
                self.caloric_label.set_text(f"Your estimated caloric intake is: {caloric_intake}")
                self.weight_class.set_text(f"Your weight class is: {bmi_interpretation}")

        except (ValueError, TypeError):

            # notify the user of any errors that may occur with data types or values
            ui.notify("Please enter valid weight and height number value.", color='negative')

    def render(self):
        with ui.column().classes(
                "w-[calc(100%+20px)] fixed top-0 left-0 -translate-x-5 h-screen bg-[url('https://images.alphacoders.com/131/1311045.jpg')] bg-cover bg-center opacity-50 text-white"
        ):
            print("loaded exercises + food")

        with ui.element().classes("relative mx-[30px] my-[30px] bg-white rounded-xl opacity-70 shadow-lg p-6"):
            ui.label("")

        with ui.row().classes("absolute top-0 left-0 w-full justify-center items-center mt-6"):

            # display a label at the top of the screen for the exercises tab
            ui.label("Exercise Recommendations").classes(
                "text-black text-4xl font-bold font-sans"
            )

        with ui.element().classes("absolute inset-[70px] bg-white rounded-sm shadow-lg shrink-0"):
            ui.label("").classes(
                'text-black text-xl font-bold justify-center w-[150px] mt-[25px] -translate-y-[30px]')

            with ui.row().classes("w-full h-[1500px] px-10 gap-2 shrink-0"):

                # create a row with columns inside to set the you-tube embeds into horizontal rows
                with ui.row().classes("w-full h-[5200px] gap-5"):
                    with ui.column().classes("flex-1 bg-gray-100 p-2 rounded shrink-0"):

                        # display labels for each ui class
                        ui.label("Health Calculators").classes("text-black text-md font-bold")
                        ui.label("BMI Calculator").classes('text-black text-xl text-bold justify-center')

                        # define user bmi calculation inputs, asking for height and weight
                        self.height_input = ui.input('Your height in (cm)', placeholder="eg: 180").classes(
                            "w-[480px] text-black text-bold bg-white-800 rounded placeholder-white-500 border border-white-600").props(
                            'input-class=text-black text-sm')

                        self.weight_input = ui.input('Your weight in (kg)', placeholder="eg: 80").classes(
                            "w-[480px] text-black text-bold bg-white-800 rounded placeholder-white-500 border border-white-600").props(
                            'input-class=text-black text-sm')

                        ui.button('Find BMI', on_click=self.calculate_and_save_health_data).classes(
                            'w-[480px] text-black').props('color=white')

                        ui.label("").classes('text-black text-xl text-bold justify-center')

                    with ui.column().classes("flex-1 bg-gray-200 p-2 rounded shrink-0"):
                        ui.label("Exercise Recommendations").classes("text-black text-md font-bold")

                        # clear the labels once
                        self.bmi_label = ui.label("").classes('text-black text-xl text-bold justify-center')
                        self.caloric_label = ui.label("").classes('text-black text-xl text-bold justify-center')
                        self.weight_class = ui.label("").classes('text-black text-xl text-bold justify-center')

                        try:

                            # create a try statement to update the text of the bmi and caloric value, load this value from the userse csv
                            username = app.storage.user.get('username', '')
                            bmi_value = load_bmi_from_csv(username)
                            caloric_value = load_caloric_intake_from_csv(username)

                            self.bmi_label.set_text(f"Your estimated BMI is: {bmi_value}")
                            self.caloric_label.set_text(f"Your estimated caloric intake is: {caloric_value}")
                            self.weight_class.set_text(f'Your weight class is: ')

                        except ValueError:

                            # check for any errors that may occur
                            ui.notify('Error occurred loading user caloric data', color='negative')

                        # define the dimensions of the you-tube video embed links
                        yt_width = 280
                        yt_height = 157

                        def suggestive_exercises():
                            try:

                                # find users age from csv file and load it
                                age = load_user_age_from_users_csv(username)

                                # validate the users age between ranges to find the most optimal exercises
                                if 0 <= age <= 20:
                                    with ui.column().classes('w-full gap-4'):
                                        with ui.element().classes(
                                                "absolute left-[10px] top-[400px] bg-white rounded-xl opacity-70 shadow-lg p-4"
                                        ):
                                            with ui.column().classes('items-start p-4 gap-2'):
                                                ui.label(
                                                    f"Suggested exercises for someone that's: {age} years old!"
                                                ).classes("text-black text-md font-bold")

                                            # display youtube embeds inside a row, horizontally
                                            with ui.row().classes('w-full justify-start gap-8 flex-wrap'):
                                                for label, url in [
                                                    ("Bench Press (3 sets of 12)",
                                                     "https://www.youtube.com/embed/4Y2ZdHCOXok"),
                                                    ("Lat Pulldown (2 sets of 10)",
                                                     "https://www.youtube.com/embed/SALxEARiMkw"),
                                                    ("Weighted Squat (3 sets of 15)",
                                                     "https://www.youtube.com/embed/t2b8UdqmlFs"),
                                                    ("Deadlift (3 sets of 10)",
                                                     "https://www.youtube.com/embed/XxWcirHIwVo"),
                                                ]:
                                                    # set the length and witdth of the embeds
                                                    with ui.column().classes('items-center gap-2'):
                                                        ui.label(label).classes('text-xl font-bold')
                                                        ui.html(f'''
                                                            <iframe width="{yt_width}" height="{yt_height}"
                                                                src="{url}"
                                                                frameborder="0"
                                                                allowfullscreen>
                                                            </iframe>
                                                        ''')

                                if 21 <= age <= 40:
                                    with ui.column().classes('w-full items-center gap-4'):
                                        with ui.element().classes(
                                                "absolute left-[10px] top-[400px] bg-white rounded-xl opacity-70 shadow-lg p-4"
                                        ):
                                            with ui.column().classes('items-start p-4 gap-2'):
                                                ui.label(
                                                    f"Suggested exercises for someone that's: {age} years old!"
                                                ).classes("text-black text-md font-bold")

                                            # display youtube embeds inside a row, horizontally
                                            with ui.row().classes('w-full justify-start gap-8 flex-wrap'):
                                                for label, url in [
                                                    ("Bench Press (3 sets of 15)",
                                                     "https://www.youtube.com/embed/4Y2ZdHCOXok"),
                                                    ("Lat Pulldown (3 sets of 15)",
                                                     "https://www.youtube.com/embed/SALxEARiMkw"),
                                                    ("Weighted Squat (3 sets of 15)",
                                                     "https://www.youtube.com/embed/t2b8UdqmlFs"),
                                                    ("Deadlift (3 sets of 15)",
                                                     "https://www.youtube.com/embed/XxWcirHIwVo"),
                                                    ("Calf raises (3 sets of 12)",
                                                     "https://www.youtube.com/embed/ucHse-6l5Ho"),
                                                    ("Leg press (3 sets of 15)",
                                                     "https://www.youtube.com/embed/B6rGDcfyPto"),
                                                ]:
                                                    # set the length and witdth of the embeds
                                                    with ui.column().classes('items-center gap-2'):
                                                        ui.label(label).classes('text-xl font-bold')
                                                        ui.html(f'''
                                                            <iframe width="{yt_width}" height="{yt_height}"
                                                                src="{url}"
                                                                frameborder="0"
                                                                allowfullscreen>
                                                            </iframe>
                                                        ''')

                                if 41 <= age <= 60:
                                    with ui.column().classes('w-full items-center gap-4'):
                                        with ui.element().classes(
                                                "absolute left-[10px] top-[400px] bg-white rounded-xl opacity-70 shadow-lg p-4"
                                        ):
                                            with ui.column().classes('items-start p-4 gap-2'):
                                                ui.label(
                                                    f"Suggested exercises for someone that's: {age} years old!"
                                                ).classes("text-black text-md font-bold")

                                            # display youtube embeds inside a row, horizontally
                                            with ui.row().classes('w-full justify-start gap-8 flex-wrap'):
                                                for label, url in [
                                                    ("Bench Press (3 sets of 12)",
                                                     "https://www.youtube.com/embed/4Y2ZdHCOXok"),
                                                    ("Lat Pulldown (3 sets of 12)",
                                                     "https://www.youtube.com/embed/SALxEARiMkw"),
                                                    ("Weighted Squat (3 sets of 15)",
                                                     "https://www.youtube.com/embed/t2b8UdqmlFs"),
                                                    ("Deadlift (3 sets of 12)",
                                                     "https://www.youtube.com/embed/uJmYpr_CPBo"),
                                                    (
                                                            "Dips (2 sets of 15)",
                                                            "https://www.youtube.com/embed/2z8JmcrW-As"),
                                                    ("Shoulder press (3 sets of 10)",
                                                     "https://www.youtube.com/embed/uJmYpr_CPBo"),
                                                ]:
                                                    # set the length and witdth of the embeds
                                                    with ui.column().classes('items-center gap-2'):
                                                        ui.label(label).classes('text-xl font-bold')
                                                        ui.html(f'''
                                                            <iframe width="{yt_width}" height="{yt_height}"
                                                                src="{url}"
                                                                frameborder="0"
                                                                allowfullscreen>
                                                            </iframe>
                                                        ''')

                                if 60 <= age <= 80:
                                    with ui.element().classes(
                                            "absolute left-[10px] top-[400px] bg-white rounded-xl opacity-70 shadow-lg p-4"
                                    ):
                                        with ui.column().classes('items-start gap-4'):
                                            ui.label(
                                                f"Suggested exercises for someone that's: {age} years old!"
                                            ).classes("text-black text-md font-bold")

                                            # display youtube embeds inside a row, horizontally
                                            with ui.row().classes('w-full justify-start gap-8 flex-wrap'):
                                                for label, url in [
                                                    ("Bench Press", "https://www.youtube.com/embed/4Y2ZdHCOXok"),
                                                    ("Lat Pulldown", "https://www.youtube.com/embed/SALxEARiMkw"),
                                                    (
                                                            "Dips (2 sets of 15)",
                                                            "https://www.youtube.com/embed/2z8JmcrW-As"),
                                                    ("Shoulder press (3 sets of 10)",
                                                     "https://www.youtube.com/embed/uJmYpr_CPBo"),
                                                    ("Calf raises (3 sets of 12)",
                                                     "https://www.youtube.com/embed/ucHse-6l5Ho"),
                                                    ("Leg press (3 sets of 15)",
                                                     "https://www.youtube.com/embed/B6rGDcfyPto")
                                                ]:
                                                    # set the length and witdth of the embeds
                                                    with ui.column().classes('items-center gap-2'):
                                                        ui.label(label).classes('text-xl font-bold')
                                                        ui.html(f'''
                                                            <iframe width="{yt_width}" height="{yt_height}"
                                                                src="{url}"
                                                                frameborder="0"
                                                                allowfullscreen>
                                                            </iframe>
                                                        ''')

                            except ValueError:
                                ui.notify('An error has occurred loading suggestive exercises.', color='negative')

                        # fire the function upon the page being loaded, checking for the users age and recommended different exercises
                        suggestive_exercises()

                    with ui.column().classes("flex-1 bg-gray-100 p-2 rounded shrink-0"):

                        # create another tab on the right of the screen wallowing the user to write personal notes down
                        ui.label("Personal notes").classes("text-black text-md font-bold")
                        ui.textarea('Entry:').classes('w-full').bind_value(app.storage.user, 'note')

        with ui.card().classes(
                'fixed bottom-0 left-0 w-screen rounded-none justify-center mb-0 text-sm font-bold font-sans z-50'):
            with ui.row().classes('w-full justify-around items-center'):
                ui.button(icon='o_home', color='white', on_click=lambda: ui.navigate.to('/dashboard')).tooltip(
                    'Home').classes('bg-green')
                ui.button(icon='monitor_heart', color='white',
                          on_click=lambda: ui.navigate.to('/dashboard/exercises_and_food')).classes(
                    'text-black').tooltip('Exercises + food').classes('bg-green')
                ui.button(icon='o_scale', color='white', on_click=lambda: ui.navigate.to('/dashboard/data')).tooltip(
                    'User Data').classes('bg-green')
                ui.button(icon='o_settings', color='white',
                          on_click=lambda: ui.navigate.to('/dashboard/settings')).tooltip('Settings').classes(
                    'bg-green')


@ui.page('/dashboard/exercises_and_food')
def dashboard_exercises_page():
    current_user = app.storage.user.get('username')

    # define the exercises page, load the page then render the page
    page = DashboardExercisesPage()
    page.render()


# define the create account class
class CreateAccountPage:
    def __init__(self):

        # define the user entered inputs and assign them to None
        self.username_input = None
        self.password_input = None
        self.password_input2 = None
        self.age_input = None
        self.human_check = None
        self.gender_input = None
        self.card = None

    def render(self):
        with ui.element('div').classes(
                'transform scale-[var(--scale)] origin-top-left transition-all duration-200').style(
            f'width: {res_y}; height: {rex_x};').bind_visibility_from(ui.query('body'), 'visible'):
            ui.add_head_html('<style>body { overflow: hidden; }</style>')

        # ensure that the user is fully authenticated, used to patch data errors
        if app.storage.user.get('authenticated', False):
            return RedirectResponse('/dashboard')

        with ui.row().classes(
                "absolute-top text-7xl mt-35 w-full justify-center font-bold font-sans items-center gap-4"):
            ui.image('static/CN logo white.png').classes('w-[650px] h-[300px] object-fill').style('margin-top: -60px;')

        with ui.column().classes(
                "w-[calc(100%+20px)] fixed top-0 left-0 -translate-x-5 h-screen  bg-[url('https://images.pexels.com/photos/1640774/pexels-photo-1640774.jpeg')] bg-cover bg-center opacity-50 text-white"):
            print("Loaded account creator")

        with (ui.card().classes('w-[510px] mt-[-40px] absolute-center shadow-none border-green-600') as card):
            card.clear()
            set_background('black')
            ui.label("Create user account").classes('text-black text-xl text-bold justify-center')

            # define the user input items and text boxes that allow the user to enter data
            username_input = ui.input('Username', placeholder='eg. JackieChan2').classes(
                "w-[480px] text-black text-bold bg-white-800 rounded placeholder-white-500 border border-white-600").props(
                'input-class=text-black text-sm')

            password_input = ui.input('Password', password=True, password_toggle_button=True,
                                      placeholder='eg. #sMn2F(!').classes(
                "w-[480px] text-black text-bold bg-white-800 rounded placeholder-white-500 border border-white-600").props(
                'input-class=text-black text-sm')

            password_input2 = ui.input('Re-type Password', password=True, password_toggle_button=True).classes(
                "w-[480px] text-black text-bold bg-white-800 rounded placeholder-white-500 border border-white-600").props(
                'input-class=text-black text-sm')

            age_input = ui.input('Age', placeholder='eg. 21').classes(
                "w-[480px] text-black text-bold bg-white-800 rounded placeholder-white-500 border border-white-600").props(
                'input-class=text-black text-sm')

            human_check = ui.input(f'Enter security question: What is {num1} + {num2} ').classes(
                "w-[480px] text-black text-bold bg-white-800 rounded placeholder-white-500 border border-white-600").props(
                'input-class=text-black text-sm')

            # define the change_color_Male function, which runs when the user selects male as their gender
            def change_color_Male():
                global user_gender
                gender_input.props('color=blue')
                gender_input.set_text('Gender: Male (♂)')
                user_gender = 'Male'

            # define the change_color_Female function, which runs when the user selects female as their gender
            def change_color_Female():
                global user_gender
                gender_input.props('color=pink')
                gender_input.set_text('Gender: Female (♀)')
                user_gender = 'Female'

            with ui.dropdown_button('Gender: ', auto_close=True).classes(
                    "w-[480px] text-black text-bold bg-white-800 rounded").props('text-sm color=white') as gender_input:

                # define the male/female ui items, appearing when the gender dropdown box is selected
                male_value = ui.item('Male', on_click=lambda: change_color_Male()).classes(
                    "w-[480px] text-black text-bold bg-white-800 rounded placeholder-white-500 border border-white-600").props(
                    'input-class=text-black text-sm')

                male_value = ui.item('Female', on_click=lambda: change_color_Female()).classes(
                    "w-[480px] text-black text-bold bg-white-800 rounded placeholder-white-500 border border-white-600").props(
                    'input-class=text-black text-sm')

            # define the class "flash_Red" which allows certain class elements to change colour to red ( BASED OFF BETA TESTING FEEDBACK | JACKSON/PB)
            async def flash_red(element):
                element.classes('bg-red')

                # wait 1 second then change the colour back
                await asyncio.sleep(1)
                element.classes(remove='bg-red')
                element.classes('bg-white')

            async def try_create_account():
                # try many validation techniques against the users inputs, ensure proper and effective user login data

                # define the text inputs from the input elements as variables, saved toward the user csv
                age_input2 = age_input.value.strip()
                username = username_input.value.strip()
                password = password_input.value.strip()
                password_confirm = password_input2.value.strip()

                # check for data range errors and incorrect data types inside the password, username, age and gender inputs

                # username checks
                if not username or not password:
                    await flash_red(username_input)
                    await flash_red(password_input)
                    await flash_red(password_input2)
                    # ensure that the input fields have been filled with string data, if not fully filled inform the user and return the loop
                    ui.notify('Please fill in all type-able fields', color='negative')
                    return

                if username in passwords:
                    await flash_red(username_input)
                    # ensure that the username entered is not already inside the csv file, if found then inform the user and return the loop
                    ui.notify('Username already taken', color='negative')
                    return

                # username length check:
                if len(username) < 4:
                    await flash_red(username_input)
                    # ensure that the username entered is longer than 4 characters, if not inform the user and return the loop
                    ui.notify('Usernames must be longer than 4 characters', color='negative')
                    return

                if len(username) >= 12:
                    await flash_red(username_input)
                    # ensure that the username entered is shorter than 12 characters
                    ui.notify('Usernames cannot be longer than 11 characters', color='negative')
                    return

                # password parameters:
                if password != password_confirm:
                    await flash_red(password_input)
                    await flash_red(password_input2)
                    # ensure that the passwords entered are both the exact same
                    ui.notify('Passwords are not the same', color='negative')
                    return

                if len(password) < 8:
                    await flash_red(password_input)
                    await flash_red(password_input2)
                    # ensure that the passwords length is above 8 characters
                    ui.notify('Passwords must be at least 8 characters long', color='negative')
                    return

                if not re.search(r"[A-Z]", password):
                    await flash_red(password_input)
                    await flash_red(password_input2)
                    # ensure that the passwords include one uppercase letter
                    ui.notify('Passwords must contain at least one uppercase letter', color='negative')
                    return

                if not re.search(r"\d", password):
                    await flash_red(password_input)
                    await flash_red(password_input2)
                    # ensure that the passwords contain one number
                    ui.notify('Passwords must contain at least one number', color='negative')
                    return

                if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
                    await flash_red(password_input)
                    await flash_red(password_input2)
                    # ensure that the passwords contain one special symbol
                    password_input.classes('bg-red')
                    ui.notify('Passwords must contain at least one special character', color='negative')

                    return

                # age parameters + type check
                if not age_input2.isdigit() or int(age_input2) >= 115:
                    await flash_red(age_input)
                    # ensure that the users entered age is a valid whole number/integer value, if not inform the user and return the loop
                    ui.notify('Please enter a valid age number below 115', color='negative')
                    return

                # human CAPTCHA checks
                if not human_check.value.strip():
                    await flash_red(human_check)
                    ui.notify('Please complete the CAPTCHA question', color='negative')
                    return

                if int(human_check.value.strip()) != ans:
                    await flash_red(human_check)
                    # ensure the security question is answered correctly, if not inform the user and return the loop

                    ui.notify('CAPTCHA question incorrect', color='negative')
                    return

                # gender data existence check
                if gender_input.text == "Gender: ":
                    await flash_red(gender_input)
                    # ensure the user selects a gender, needed for later caloric calculations
                    ui.notify('Please select a gender', color='negative')
                    return

                else:
                    # if all data checks and validation pass correctly run the create account functions and redirect the user

                    # define the password hashing library
                    hasher = get_hasher()

                    try:
                        # de-crypt the users password
                        hashed_pass = await asyncio.to_thread(hasher.hash, password)

                    except Exception as ex:
                        ui.notify(f'Error hashing password: {ex}', color='negative')
                        return

                    # write a new line to the 'users.csv' file, putting inside all listed fields by the user
                    try:
                        with open(CSV_PATH, "a", newline="", encoding="utf-8") as f:
                            writer = csv.writer(f)

                            # set the entered calories to 0 and max calories to 3000 as a default for all users
                            total_calories = 0
                            set_daily_calories = 3000

                            writer.writerow([
                                username,
                                hashed_pass,
                                age_input2,
                                total_calories,
                                set_daily_calories,
                                user_gender,
                                '',
                                ''
                            ])

                    # ensure proper error checks, notify the user if there are any
                    except Exception as ex:
                        ui.notify(f'There was an error saving the account: {ex}', color='negative')
                        return

                    # update in-memory passwords immediately
                    passwords[username] = hashed_pass

                    # update app.storage.user before loading the dashboard and authenticating the user
                    app.storage.user.update({'username': username, 'authenticated': True})

                    # Load the dashboard
                    await loading_dash()

            async def loading_login():

                # define the login landing page animation, playing an animation upon changing webpages
                card.clear()

                with card.classes('bg-transparent'):
                    ui.skeleton().classes('w-[480px] h-2 bg-transparent')
                    ui.label('Redirecting to dashboard...').classes(
                        'text-white text-xl justify-center text-bold h-1')

                    with ui.row().classes('w-[480px] h-1 opacity-50'):
                        ui.button('', icon='restaurant').classes('w-[40px] animate-spin centered h-1').props(
                            'color=positive')
                    await asyncio.sleep(1.5)
                    ui.navigate.to('/Login')

            async def loading_dash():
                # define the dashboard landing page animation, playing an animation upon changing webpages
                card.clear()

                with card.classes('bg-transparent'):
                    # load the animation and redirect the user
                    ui.skeleton().classes('w-[480px] h-2 bg-transparent')
                    ui.label('Redirecting to dashboard...').classes(
                        'text-white text-xl justify-center text-bold h-1')

                    with ui.row().classes('w-[480px] h-1 opacity-50'):
                        ui.button('', icon='restaurant').classes('w-[40px] animate-spin centered h-1').props(
                            'color=positive')

                    await asyncio.sleep(4)
                    ui.navigate.to('/dashboard')

            # allow the user to press the enter key on any of the inputs to fire the try_create_account function
            username_input.on('keydown.enter', try_create_account)
            password_input.on('keydown.enter', try_create_account)
            password_input2.on('keydown.enter', try_create_account)
            age_input.on('keydown.enter', try_create_account)
            human_check.on('keydown.enter', try_create_account)

            ui.button('Create account', on_click=try_create_account).classes('w-[480px] text-black').props(
                'color=white ')

            ui.button('Return to login screen', on_click=lambda: loading_login()).classes(
                'w-[480px] text-black').props('color=white')

        # include the version type at the bottom of the screen
        with ui.row().classes("fixed bottom-0 w-full justify-center mb-2 text-sm font-bold font-sans z-45"):
            ui.label("CALORIE NINJA V1.0 BETA").classes("text-white")

        # display a "FAQ" button on the top right of the screen
        with ui.row().classes(
                "fixed top-0 w-full justify-end items-center p-4 bg-transparent z-50 font-bold font-sans"):
            info_button = ui.button("FAQs / INFO", on_click=lambda: ui.navigate.to('/about')).props(
                'outline square').classes('text-white bg-transparent')
            info_button.tooltip('About Calorie Ninja')


# define the create account landing web-link
@ui.page('/CreateAccount')
def make_account_page():
    if app.storage.user.get('authenticated', False):
        # check that the user is correctly authenticated, if already authenticated - redirect the user to the dashboard
        return RedirectResponse('/dashboard')

    page = CreateAccountPage()
    page.render()


# define the login page (main users landing page)
class LoginPage:
    def __init__(self):

        # define the users variable inputs
        self.username_input = None
        self.password_input = None
        self.card = None
        self.hasher = get_hasher()

        # build and render the page
        self.build()

    def build(self):

        # check that the user is properly authenticated, if true redirect the user to the dashboard else allow the user to stay on the page
        if app.storage.user.get('authenticated', False):
            return RedirectResponse('/dashboard')

        with ui.element('div').classes(
                'transform scale-[var(--scale)] origin-top-left transition-all duration-200').style(
            f'width: {res_y}; height: {rex_x};').bind_visibility_from(ui.query('body'), 'visible'):
            ui.add_head_html('<style>body { overflow: hidden; }</style>')

            with ui.row().classes(
                    "absolute-top text-7xl mt-35 w-full justify-center font-bold font-sans items-center gap-4"):
                ui.image('static/CN logo white.png').classes('w-[650px] h-[300px] object-fill').style(
                    'margin-top: -60px;')

            with ui.column().classes(
                    "w-[calc(100%+20px)] fixed top-0 left-0 -translate-x-5 h-screen bg-[url('https://images.pexels.com/photos/1640773/pexels-photo-1640773.jpeg?cs=srgb&dl=pexels-ella-olsson-572949-1640773.jpg&fm=jpg')] bg-cover bg-center opacity-50 text-white"):
                print("Loaded login page")

            with ui.card().classes('w-[510px] mt-[-85px] absolute-center border-opacity-50 shadow-none') as self.card:
                # define buttons and inputs inside the ui element, allow the user to type in strings inside and age in integers
                self.card.clear()
                set_background('black')
                ui.label("Enter user credentials").classes('text-black text-xl text-bold justify-center')

                self.username_input = ui.input('Username', placeholder="eg. KennyC").classes(
                    "w-[480px] text-black text-bold bg-white-800 rounded placeholder-white-500 border border-white-600").props(
                    'input-class=text-black text-sm')

                self.password_input = ui.input('Password', placeholder="eg. @N92js(d", password=True,
                                               password_toggle_button=True).classes(
                    "w-[480px] text-black text-bold bg-white-800 rounded placeholder-white-500 border border-white-600").props(
                    'input-class=text-black text-sm')

                # bind the Enter key to allow users to fire the try_login event
                self.username_input.on('keydown.enter', self.try_login)
                self.password_input.on('keydown.enter', self.try_login)

                ui.button('Log in', on_click=self.try_login).classes('w-[480px] text-black').props('color=white ')
                ui.button('Don’t have an account?', on_click=self.loading_acc_create).classes(
                    'w-[480px] text-black').props('color=white')

            # display the application version at the bottom of the screen
            with ui.row().classes(
                    "fixed bottom-0 w-full justify-center mb-2 text-sm font-bold font-sans border-transparent z-45"):
                ui.label("CALORIE NINJA V1.0 BETA").classes("text-white")

            with ui.row().classes(
                    "fixed top-0 w-full justify-end items-center p-4 bg-transparent z-50 font-bold font-sans"):
                info_button = ui.button("FAQs / INFO", on_click=lambda: ui.navigate.to('/about')).props(
                    'outline square').classes('text-white bg-transparent')
                info_button.tooltip('About Calorie Ninja')

    async def try_login(self):

        # grab the users entered password and username, strip that value
        username = self.username_input.value.strip()
        password = self.password_input.value.strip()

        if not username or not password:
            # validate that all fields have been filled out by the user
            ui.notify('Please fill in all fields', color='negative')
            return

        # define the password hasher to de-crypt the password
        stored_hash = passwords.get(username)
        if stored_hash:
            try:
                if self.hasher.verify(stored_hash, password):
                    app.storage.user.update({'username': username, 'authenticated': True})
                    # set the users authentication to True if the user successfully logs in

                    self.card.clear()
                    with self.card.classes('bg-transparent'):

                        # display the loading animation and redirect the user to the dashboard screen
                        ui.skeleton().classes('w-[480px] h-2 bg-transparent')
                        ui.label('Redirecting to dashboard...').classes(
                            'text-white text-xl justify-center text-bold h-1')

                        with ui.row().classes('w-[480px] h-1 opacity-50'):
                            ui.button('', icon='restaurant').classes('w-[40px] animate-spin centered h-1').props(
                                'color=positive')

                    # user async io sleep to pause the program for 2 seconds
                    await asyncio.sleep(2)
                    ui.notify('Successfully logged in', color='positive')
                    await asyncio.sleep(2)
                    ui.navigate.to('/dashboard')

                else:

                    # validate any other errors, notifying the user
                    ui.notify('Wrong username or password', color='negative')

            except Exception as e:

                # validate any other errors, notifying the user
                ui.notify('Wrong username or password', color='negative')
        else:

            # validate any other errors, notifying the user
            ui.notify('Wrong username or password', color='negative')

    async def loading_acc_create(self):

        # upon loading the create-account page, display the loading animation and wait, then redirect the user
        self.card.clear()
        with self.card.classes('bg-transparent'):
            # display the loading animation
            ui.skeleton().classes('w-[480px] h-2 bg-transparent')
            ui.label('Redirecting to account creation screen...').classes(
                'text-white text-xl justify-center text-bold h-1')

            with ui.row().classes('w-[480px] h-1 opacity-50'):
                ui.button('', icon='restaurant').classes('w-[40px] animate-spin centered h-1').props(
                    'color=positive')

        await asyncio.sleep(4)
        ui.navigate.to('/CreateAccount')


@ui.page('/login')
def login_page():
    if app.storage.user.get('authenticated', False):
        # check that the user is correctly authenticated, if already authenticated - redirect the user to the dashboard
        return RedirectResponse('/dashboard')

    return LoginPage()


# set the main landing page to redirect users toward the login page
@ui.page('/')
def root_page():
    # if the user lands on this domain, redirect them towards the login page
    return RedirectResponse('/login')


# define the run script for nicegui browser hosting web (NEEDED TO RUN SCRIPT)
if __name__ in {'__main__', '__mp_main__'}:
    # run the nicegui library
    ui.run(storage_secret='your_secret')
