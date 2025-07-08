import tkinter as tk
from tkinter import messagebox
import threading
import json
import os
import datetime
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

# Define Allowed Subjects
ALLOWED_SUBJECTS = {
    "Business": ["Accounting", "Advertising", "Biotechnology", "Broadcasting", "Business", "Business Law", "Business Plans", "Communications", "Data Analytics", "Entrepreneurship", "Excel", "Facebook Marketing", "Hospitality", "International Trade", "Internet Marketing", "Journalism", "Management", "Marketing", "News Media", "Powerpoint", "Print Media", "Publishing", "Real Estate", "Retail Management", "Risk Management", "Sales", "Sports Management", "Supply Chain", "Tourism"],
    "Economics": ["Developmental Economics", "Economics", "Finance", "Game Theory", "Growth Theory", "Information Economics", "Macro Economics", "Micro Economics"],
    "Writing": ["Accounting", "Application Writing", "Art", "Article Writing", "Biology", "Blog Post", "Business", "Case Studies", "Chemistry", "Communications", "Computer Science", "Creative Writing", "Economics", "Editing", "Email Copy", "Engineering", "English", "Environmental Science", "Film", "Foreign Languages", "Geography", "Geology", "Grammar", "Health & Medical", "History", "Humanities", "Law", "Literature", "Management", "Marketing", "Mathematics", "Nursing", "Philosophy", "Physics", "Poetry", "Political Science", "Powerpoint", "Product Descriptions", "Programming", "Proofreading", "Psychology", "Research & Summaries", "Resume Writing", "SAT", "Science", "Scriptwriting", "Shakespeare", "Social Science", "Songwriting", "Transcription", "Translation & Languages", "White Papers", "Writing"],
    "Humanities": ["African Studies", "American Studies", "Animation", "Anthropology", "Architecture", "Art", "Asian Studies", "Cooking & Baking", "Cultural Studies", "Dance", "Design", "Education & Teaching", "English", "Ethnic Studies", "Fashion Design", "Film", "Gender Studies", "Geography", "Global Studies", "Graphic Design", "History", "Humanities", "Interior Design", "Jewish Studies", "Landscape Architecture", "Latin American Studies", "Linguistics", "Literature", "Middle Eastern Studies", "Music", "Music Theory", "Philosophy", "Political Science", "Psychology", "Religion", "Social Science", "Sociology", "Theater", "Urban Planning", "Women's Studies"],
    "Law": ["Criminal Justice", "International Law", "Law", "Policy", "Public Service", "Social Justice"],
    "Mathematics":["Algebra", "Applied Mathematics", "Arithmetic", "Calculus", "Cryptography", "Differential Equations", "Discrete Math", "Geometry", "Graphs", "Linear Algebra", "Mathematics", "Number Theory", "Numerical Analysis", "Probability", "Set Theory", "Statistics", "Trigonometry"],
    "Science":["Agriculture", "Anatomy", "Applied Physics", "Astrobiology", "Astronomy", "Astrophysics", "Biochemistry", "Biology", "Botany", "Chemistry", "Earth and Space Exploration", "Ecology", "Environmental Science", "Genetics", "Geographic Information", "Geology", "Microbiology", "Physics", "Rocket Science", "Science", "Sustainability", "Zoology"],
    "Health & Medical": ["Chiropractics", "Dentistry", "Dietetics", "Fitness", "Global Health", "Health & Medical", "Immunology", "Kinesiology", "Music Therapy", "Neuroscience", "Nursing", "Nutrition", "Nutritional Sciences", "Pharmacology", "Population Health", "Public Health", "Social Work", "Speech Therapy", "Toxicology", "Wellness"],
    "Computer Science":["Algorithms & Data Structures", "Artificial Intelligence", "Assembly Language", "Computer Science", "Cyber Security", "Databases", "Machine Learning", "Networking", "Operating Systems", "Website Development"],
    "Programming":[".NET", "App Development", "Bash", "C Programming", "C#", "C++", "Clojure", "CoffeeScript", "Erlang", "F#", "Go", "Haskell", "Html / CSS", "Java", "Javascript", "jQuery / Prototype", "Linux", "Lisp", "MathLab", "MySQL", "OCaml", "Pascal", "Perl", "PHP", "Pinterest", "Programming", "Python", "Q#", "R", "Ruby", "Rust", "Software Development", "Swift", "Twitter", "Typescript", "Website Design", "Wordpress"],
    "Engineering":["Aeronautical Management", "Aerospace Engineering", "Biomedical Engineering", "Chemical Engineering", "Civil Engineering", "Computer Systems", "Construction", "Data Engineering", "Electrical Engineering", "Engineering", "Environmental Engineering", "Industrial Design", "Informatics", "Information Technology", "Mechanical Engineering", "Product Design", "Software Engineering"],
    "Foreign Languages":["Arabic", "Chinese", "ESL", "Foreign Languages", "French", "Hindi", "Italian", "Japanese", "Latin", "Russian", "Spanish"],
    "Others":["Autocad", "Brand Identity", "College Applications", "Convert Files", "Data Entry", "Editing", "Email Copy", "Illustrations", "Internet Research", "Internship", "Job", "Job Applications", "Leads", "Link Building", "Logo Design", "Market Research", "Marketing Strategies", "Other", "Photoshop", "Premiere Pro", "Product Descriptions", "Proofreading", "Relationship Advice", "Research & Summaries", "SAT", "Scholarship", "Scriptwriting", "SEO", "Songwriting", "Spokesperson Videos", "Surveys", "Tech Support", "User Interface / IA", "Video Animation", "Video Editing", "Web Analytics", "Web Scraping", "White Papers", "Windows Desktop"]
}

CONFIG_FILE = "user_config.json"

def save_user_config(data):
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f)

def load_user_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {}

class LoginWindow:
    def __init__(self, root, on_login):
        self.root = root
        self.root.title("StudyPool Login")
        self.root.geometry("400x400")
        self.root.configure(bg="green")

        self.user_config = load_user_config()

        tk.Label(root, font=("Arial", 14, "bold"), bg="green", fg="white").pack(pady=20)
        tk.Label(root, text="Username:", bg="green").pack(pady=5)
        self.username_entry = tk.Entry(root)
        self.username_entry.pack(pady=5)

        tk.Label(root, text="Password:", bg="green").pack(pady=5)
        self.password_entry = tk.Entry(root, show="*")
        self.password_entry.pack(pady=5)

        if "username" in self.user_config:
            self.username_entry.insert(0, self.user_config["username"])
        if "password" in self.user_config:
            self.password_entry.insert(0, self.user_config["password"])

        self.login_button = tk.Button(root, text="Login", command=self.attempt_login, bg="blue", fg="white", padx=10, pady=5)
        self.login_button.pack(pady=20)

        self.on_login = on_login

    def attempt_login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if username and password:
            self.user_config["username"] = username
            self.user_config["password"] = password
            save_user_config(self.user_config)

            self.root.destroy()
            self.on_login(username, password)
        else:
            messagebox.showwarning("Input Error", "Please enter both username and password.")

class SubjectSelectionApp:
    def __init__(self, root, start_selenium_callback):
        self.root = root
        self.root.title("Subject Selection")
        self.root.geometry("900x600")
        self.root.configure(bg="green")
        self.root.resizable(False, False)

        self.user_config = load_user_config()

        self.main_frame = tk.Frame(self.root, bg="green")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.subject_frame = tk.Frame(self.main_frame, bg="green")
        self.subject_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.canvas = tk.Canvas(self.subject_frame, bg="green")
        self.scrollbar = tk.Scrollbar(self.subject_frame, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.scrollable_frame = tk.Frame(self.canvas, bg="green")
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        self.checkbuttons = {}
        self.create_checkboxes()

        self.scrollable_frame.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox("all"))

        self.input_frame = tk.Frame(self.root, bg="green")
        self.input_frame.pack(pady=10)

        self.min_price_label = tk.Label(self.input_frame, text="Min Price ($):", bg="green")
        self.min_price_label.grid(row=0, column=0, padx=2, pady=5)

        self.min_price_entry = tk.Entry(self.input_frame)
        self.min_price_entry.grid(row=0, column=1, padx=2, pady=5)

        self.min_time_label = tk.Label(self.input_frame, text="Min Time (hours):", bg="green")
        self.min_time_label.grid(row=0, column=2, padx=2, pady=5)

        self.min_time_entry = tk.Entry(self.input_frame)
        self.min_time_entry.grid(row=0, column=3, padx=2, pady=5)

        if "min_price" in self.user_config:
            self.min_price_entry.insert(0, str(self.user_config["min_price"]))
        if "min_time" in self.user_config:
            self.min_time_entry.insert(0, str(self.user_config["min_time"]))

        self.save_button = tk.Button(self.root, text="Save and Continue", command=self.save_and_continue, bg="blue", fg="white", padx=10, pady=5)
        self.save_button.pack(side="bottom", pady=10)

        self.start_selenium_callback = start_selenium_callback

    def create_checkboxes(self):
        row = 0
        max_columns = 6
        selected_subjects = self.user_config.get("selected_subjects", [])
        for category, subjects in ALLOWED_SUBJECTS.items():
            category_label = tk.Label(self.scrollable_frame, text=category, font=("Arial", 12, "bold"), bg="green")
            category_label.grid(row=row, column=0, padx=10, pady=5, sticky="w", columnspan=max_columns)
            row += 1

            column = 0
            for subject in subjects:
                var = tk.BooleanVar()
                if subject in selected_subjects:
                    var.set(True)
                checkbox = tk.Checkbutton(self.scrollable_frame, text=subject, variable=var, bg="green")
                checkbox.grid(row=row, column=column, padx=5, pady=5, sticky="w")
                self.checkbuttons[subject] = var
                column += 1
                if column >= max_columns:
                    column = 0
                    row += 1

            row += 1

    def save_and_continue(self):
        selected_subjects = [subject for subject, var in self.checkbuttons.items() if var.get()]
        if not selected_subjects:
            messagebox.showwarning("No Subjects Selected", "Please select at least one subject.")
            return

        min_price = self.min_price_entry.get()
        min_time = self.min_time_entry.get()

        try:
            min_price = float(min_price) if min_price else 0
            min_time = float(min_time) if min_time else 0
        except ValueError:
            messagebox.showwarning("Invalid Input", "Please enter valid numbers for price and time.")
            return

        self.user_config["selected_subjects"] = selected_subjects
        self.user_config["min_price"] = min_price
        self.user_config["min_time"] = min_time
        save_user_config(self.user_config)

        self.root.destroy()
        self.start_selenium_callback(selected_subjects, min_price, min_time)

def login(driver, username, password, max_retries=3):
    attempt = 0
    while attempt < max_retries:
        try:
            driver.get("https://www.studypool.com/")
            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//a[@onclick='open_login(); return false;']"))
            ).click()
            
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "UserLogin_username"))
            ).send_keys(username)
            
            driver.find_element(By.ID, "UserLogin_password").send_keys(password)
            driver.find_element(By.ID, "login-button").click()

            # Wait for login to complete (you may need to adjust the condition)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "dashboard"))  # Adjust based on successful login indicator
            )

            print(f"✅ Logged in successfully on attempt {attempt + 1}!")
            return True  # Success
        except (TimeoutException, NoSuchElementException) as e:
            print(f"⚠️ Login attempt {attempt + 1} failed: {e}")
            attempt += 1
            time.sleep(5)  # Wait before retrying
    
    print("❌ All login attempts failed. Please check your credentials or internet connection.")
    return False  # Failure


def navigate_to_question(driver, allowed_subjects, min_price, min_time, max_retries=3):
    """ Opens the newest questions page and clicks an available question that matches allowed subjects and meets price and time criteria. """
    
    attempt = 0
    while attempt < max_retries:
        try:
            driver.get("https://www.studypool.com/questions/newest")
            wait = WebDriverWait(driver, 10)

            try:
                wait.until(EC.presence_of_element_located((By.CLASS_NAME, "question-list-entry")))
                questions = driver.find_elements(By.CLASS_NAME, "question-list-entry")

                for question in questions:
                    try:
                        if "disabled" in question.get_attribute("class"):
                            continue

                        subject_element = question.find_element(By.CLASS_NAME, "category-name")
                        subject = subject_element.text.strip()

                        if subject not in allowed_subjects:
                            print(f"⚠️ Skipping question: '{subject}' is not in the allowed subjects list.")
                            continue

                        # Extract and handle price safely
                        
                    # ✅ Extract Budget
                        try:
                            budget_element = question.find_element(By.CSS_SELECTOR, ".budget .upper-line")
                            budget_text = budget_element.text.strip().replace("$", "").replace(",", "")
                            budget = float(budget_text) if budget_text else 0
                        except:
                            budget = 0  # Default if extraction fails

                        # ✅ Extract Time Limit
                        try:
                            time_element = question.find_element(By.CSS_SELECTOR, ".timeVal.upper-line")
                            time_text = time_element.text.strip()

                            if "D" in time_text:
                                time_limit = float(time_text.replace("D", "").strip()) * 24  # Convert days to hours
                            elif "H" in time_text:
                                time_limit = float(time_text.replace("H", "").strip())  # Hours remain unchanged
                            elif "M" in time_text:
                                time_limit = float(time_text.replace("M", "").strip()) / 60  # Convert minutes to hours
                            else:
                                time_limit = 0  # Default to 0 if time is missing
                        except:
                            time_limit = 0  # Default if extraction fails  
                        
                        try:
                            price_element = question.find_element(By.CLASS_NAME, "budget-green")
                            price_text = price_element.text.strip().replace('$', '').replace(',', '')
                            print(f"Debug: Extracted price text: '{price_text}'")  # Debugging line
                            price = float(price_text) if price_text else 0
                        except Exception as e:
                            print(f"⚠️ Skipping question due to price extraction error: {e}")
                            price = 0

                        # Check if the question meets the price and time criteria
                        if budget < min_price or time_limit < min_time:
                            print(f"⚠️ Skipping question due to price or time constraint. Price: {price}, Time: {time_limit}")
                            continue


                        bid_icon = question.find_elements(By.CLASS_NAME, "tutor-bid-made")
                        if bid_icon and bid_icon[0].is_displayed():
                            print(f"⚠️ Skipping already bidded question: {subject}")
                            continue

                        title_element = question.find_element(By.CLASS_NAME, "questionTitleCol")
                        driver.execute_script("arguments[0].click();", title_element)
                        print(f"✅ Navigating to question: {subject}")

                        time.sleep(2)
                        driver.switch_to.window(driver.window_handles[-1])

                        time.sleep(5)
                        return True
                    except Exception as e:
                        print(f"❌ Skipping question due to error: {e}")

                print("❌ No new available questions matching the allowed subjects.")
                return False

            except Exception as e:
                print(f"❌ Error navigating to question: {e}")
                return False

        except (TimeoutException, NoSuchElementException) as e:
            print(f"⚠️ Navigation attempt {attempt + 1} failed: {e}")
            attempt += 1
            time.sleep(5)  # Wait before retrying
    
    print("❌ All navigation attempts failed. Please check if the site is accessible.")
    return False  # Failure


def check_finalize_bid(driver):
    """ Locates and checks the 'Finalize Bid' checkbox. """
    try:
        wait = WebDriverWait(driver, 5)
        driver.save_screenshot("checkbox_debug.png")
        print("📸 Screenshot saved as 'checkbox_debug.png'. Check the file to see the current page state.")

        checkbox = wait.until(EC.presence_of_element_located((By.ID, "finalize-bid-checkbox")))

        label = driver.find_element(By.CSS_SELECTOR, "label[for='finalize-bid-checkbox']")
        driver.execute_script("arguments[0].scrollIntoView();", checkbox)

        driver.execute_script("arguments[0].style.display = 'block';", checkbox)

        print(f"🔹 Attempting to click checkbox with ID: {checkbox.get_attribute('id')}")
        print(f"🔹 Checkbox status - Displayed: {checkbox.is_displayed()}, Enabled: {checkbox.is_enabled()}")

        if checkbox.is_displayed() and checkbox.is_enabled():
            driver.execute_script("arguments[0].click();", checkbox)
            print("✅ Checkbox successfully checked!")
            return True
        else:
            print("⚠️ Checkbox not interactable. Clicking label instead...")
            driver.execute_script("arguments[0].click();", label)
            print("✅ Label clicked, checkbox should now be checked!")
            return True
    except Exception as e:
        print(f"❌ Error checking checkbox: {e}")
        return False

def place_bid(driver):
    """ Places a bid and handles any confirmation popups. """
    try:
        wait = WebDriverWait(driver, 5)

        checkbox = driver.find_element(By.ID, "finalize-bid-checkbox")
        if not checkbox.is_selected():
            print("⚠️ Checkbox is not checked. Attempting to check it again...")
            check_finalize_bid(driver)

        if not checkbox.is_selected():
            print("❌ Failed to check the checkbox. Cannot place bid.")
            return False

        place_bid_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(),'Place Bid')]")))
        driver.execute_script("arguments[0].click();", place_bid_button)
        print("✅ Clicked initial 'Place Bid' button.")

        try:
            warning_popup = WebDriverWait(driver, 3).until(
                EC.visibility_of_element_located((By.ID, "user-action-tutor-bid-place-warning"))
            )
            print("✅ Warning popup detected. Clicking 'Place Bid' inside the popup...")
            popup_place_bid = warning_popup.find_element(By.XPATH, ".//a[contains(text(),'Place Bid')]")
            driver.execute_script("arguments[0].click();", popup_place_bid)
            print("✅ Clicked 'Place Bid' inside warning popup.")
        except Exception:
            print("⚠️ No warning popup detected, proceeding.")

        try:
            confirmation_popup = WebDriverWait(driver, 3).until(
                EC.visibility_of_element_located((By.CLASS_NAME, "cta-resolve"))
            )
            final_bid_button = confirmation_popup.find_element(By.XPATH, ".//a[contains(text(),'Place Bid')]")
            driver.execute_script("arguments[0].click();", final_bid_button)
            print("✅ Final 'Place Bid' clicked, bid placed successfully!")
        except Exception:
            print("⚠️ No confirmation popup appeared, bid placed successfully.")
            
        if len(driver.window_handles) > 1:
                driver.close()  # Close the question tab
                driver.switch_to.window(driver.window_handles[0])  # Switch back to main tab
                print("🧹 Closed question tab and returned to main window.")

        return True

    except Exception as e:
        print(f"❌ Error placing bid: {e}")
        return False





def start_selenium(selected_subjects, min_price, min_time, username, password):
    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    options.add_argument("--user-data-dir=C:/Users/Mshinz/AppData/Local/Google/Chrome/User Data/SeleniumProfile")
    options.add_argument("--profile-directory=Profile 11")
    options.add_argument("--start-maximized")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(service=service, options=options)
    login(driver, username, password)
    while True:
        if navigate_to_question(driver, selected_subjects, min_price, min_time):
            place_bid(driver)
        time.sleep(15)

def main():
    def on_login(username, password):
        root = tk.Tk()
        SubjectSelectionApp(root, lambda subjects, min_price, min_time: start_selenium(subjects, min_price, min_time, username, password))
        root.mainloop()

    login_root = tk.Tk()
    LoginWindow(login_root, on_login)
    login_root.mainloop()

if __name__ == "__main__":
    main()
