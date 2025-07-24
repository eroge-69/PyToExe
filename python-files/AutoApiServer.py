import threading

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException
from selenium.webdriver.chrome.options import Options
import shutil
import os
import time
from urllib.parse import urlparse, parse_qs
import requests
from google_auth_oauthlib.flow import InstalledAppFlow
import http.server
import random
import socketserver
import json

# API_BASE = 'http://bot-server-rahim.ap-south-1.elasticbeanstalk.com/api/'
API_BASE = "http://email-soft-env.eba-3hfcwptp.us-east-1.elasticbeanstalk.com/api/"
API_TOKEN = '1|lYOHjRFxuayByevmBLDt6R9QyU8gt9eSA7hAkHna7f478c7d'

scopes = [
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.readonly'
]


def fetch_data_from_server():
    # return {
    #     "accounts": [
    #         {
    #             "email": "hvu87628@gmail.com",
    #             "password": "igevwaronu858",
    #             "recovery": "ggaoavgskavs@gmail.com",
    #             "id": "baler_matha",
    #         }
    #     ],
    #     "batch":{
    #         "name": "Bal",
    #         "id": "Bal"
    #     }
    # }

    url = f"{API_BASE}automation/token-process"
    headers = {
        'Authorization': f'Bearer {API_TOKEN}',
        'Accept': 'application/json'
    }

    try:
        response = requests.get(url, headers=headers)

        if response.status_code == 200:

            return {
                "accounts": response.json()['accounts'],
                "batch": response.json()['batch']
            }
        else:
            print(f"❌ Failed to fetch accounts. Status: {response.status_code}, Response: {response.text}")
            return {
                "accounts": [],
                "batch": None
            }
    except requests.exceptions.RequestException as e:
        print(f"⚠️ Error connecting to server: {e}")
        return {
            "accounts": [],
            "batch": None
        }


class CREATOR:
    def __init__(self, index, account):
        super().__init__()
        self.index = index
        self.account = account  # Store account data for further use
        self.driver = None
        self.project_id = None
        self.download_path = None
        self.step = "STARTED"
        self.login_result = None
        self.port = random.randint(1024, 65535)
        self.server = None
        self.auth_code = None
        self.creds = None

    def create(self):

        email = self.account['email']
        username = email.split("@")[0]
        self.download_path = os.path.join(os.path.abspath("api"), username)
        os.makedirs(self.download_path, exist_ok=True)

        chrome_options = Options()
        prefs = {
            "download.default_directory": self.download_path,  # Set custom download directory
            "download.prompt_for_download": False,  # Don't ask for download prompt
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True  # Allow all files to download
        }

        chrome_options.add_experimental_option("prefs", prefs)
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument("--lang=en-US")

        # Additional tweaks to further mask automation (optional)
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")

        width = 700
        height = 800

        row = self.index // 3
        col = self.index % 6
        x = col * (400 + 20)
        y = row * (400 + 50)

        chrome_options.add_argument(f"--window-size={width},{height}")
        # chrome_options.add_argument(f"--window-position={x},{y}")

        self.driver = webdriver.Chrome(options=chrome_options)

        self.login()

    def login(self):
        email_bot = GmailAutomation(self.driver)
        self.login_result = email_bot.login(self.account['email'], self.account['password'], self.account['recovery'])
        print('login_result', self.login_result)
        if self.login_result == 'success':
            self.step = "LOGGED_IN"
            self.accept_tos()
        elif self.login_result == "disabled_email":
            self.step = "LOGIN_FAILED"
            self.finish()
        elif self.login_result == "invalid_password":
            self.step = "LOGIN_FAILED"
            self.finish()
        elif self.login_result == "invalid_has_two_factor":
            self.step = "LOGIN_FAILED"
            self.finish()
        elif self.login_result == "login_rejected":
            self.step = "LOGIN_FAILED"
            self.finish()
        else:
            self.step = "LOGIN_PAUSED"
            print('Something went wrong that we could not catch')
            self.finish()

    def change_lang_to_en(self, lang):
        self.driver.get("https://myaccount.google.com/u/1/language")

        base_lang = lang.split('-')[0]

        print('base_lang', base_lang)

        try:
            wait = WebDriverWait(self.driver, 10)

            li_element = wait.until(EC.presence_of_element_located(
                (By.XPATH, f"//li[starts-with(@data-id, '{base_lang}')]")
            ))
            button = li_element.find_element(By.TAG_NAME, 'button')
            button.click()
            print("Clicked current language setting.")

            time.sleep(3)

            if base_lang == "ar":

                try:
                    input_xpath = '//div[@role="dialog" and @aria-modal="true"]//input[@role="combobox"]'

                    # STEP 2: Click the outer container (usually 4 levels above input)
                    wrapper_xpath = input_xpath + '/ancestor::span[1]'

                    print('wrapper_xpath', wrapper_xpath)

                    clickable_wrapper = wait.until(EC.element_to_be_clickable((By.XPATH, wrapper_xpath)))
                    clickable_wrapper.click()

                    english_li = wait.until(EC.element_to_be_clickable(
                        (By.XPATH, "//li[@data-language-code='en']")
                    ))
                    english_li.click()

                except Exception as e:
                    print('Failed clicking the input combo box: ', e)

            else:
                try:
                    english_li = wait.until(EC.element_to_be_clickable(
                        (By.XPATH, "//li[@data-language-code='en']")
                    ))
                    english_li.click()
                except:
                    print('Maybe the language combobox is not opened yet, try to manually click it')
                    try:
                        input_xpath = '//div[@role="dialog" and @aria-modal="true"]//input[@role="combobox"]'

                        # STEP 2: Click the outer container (usually 4 levels above input)
                        wrapper_xpath = input_xpath + '/ancestor::span[1]'

                        print('wrapper_xpath', wrapper_xpath)

                        clickable_wrapper = wait.until(EC.element_to_be_clickable((By.XPATH, wrapper_xpath)))
                        clickable_wrapper.click()

                        english_li = wait.until(EC.element_to_be_clickable(
                            (By.XPATH, "//li[@data-language-code='en']")
                        ))
                        english_li.click()

                    except Exception as e:
                        print('Failed clicking the input combo box: ', e)

            time.sleep(3)

            submit_button = wait.until(EC.presence_of_element_located(
                (By.XPATH, "//button[@disabled]")
            ))
            print("Found the disabled submit button.")

            # Step 2: Find and click <li> with aria-label="United States"
            us_li = wait.until(EC.element_to_be_clickable(
                (By.XPATH, "//li[@aria-label='United States']")
            ))
            us_li.click()
            print("Clicked on 'United States' option.")
            time.sleep(2)

            submit_button.click()
            print("Switched to English successfully.")

            # Wait and select English (may require additional steps if a dialog appears)
            # Optional: Select English from the list (click logic may depend on how Google renders it)
        except Exception as e:
            print(f"Error during language change: {e}")

    def accept_tos(self):

        html_tag = self.driver.find_element(By.TAG_NAME, 'html')
        page_lang = html_tag.get_attribute('lang')

        print('page_lang', page_lang)

        if not page_lang.startswith('en'):
            print("Warning: The page language is not English. Consider using localized labels or translation.")
            # You could switch your scraping logic here based on the language
            self.change_lang_to_en(page_lang)
            time.sleep(10)
        else:
            print("Page is in English. Proceeding with normal scraping.")

        self.driver.get('https://console.cloud.google.com/welcome/new?pli=1')

        time.sleep(5)

        try:
            wait = WebDriverWait(self.driver, 30)
            dialog = wait.until(EC.presence_of_element_located((By.TAG_NAME, "mat-dialog-container")))
            time.sleep(5)

            try:
                select_box = WebDriverWait(self.driver, 60).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "[formcontrolname='optInCountry']"))
                )
                select_box.click()
                print("Dropdown clicked.")
            except Exception as e:
                print("Dropdown not found or not clickable:", e)

            time.sleep(2)

            # Step 2: Wait for and select "Desktop App" from the options
            desktop_option = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'United States')]"))
            )
            desktop_option.click()

            print('United State clicked')

            while True:
                checkboxes = dialog.find_elements(By.CSS_SELECTOR, "input[type='checkbox']")

                if len(checkboxes) > 0:
                    print('Found checkboxes:', len(checkboxes))
                    break
                else:
                    print('Looking for the checkbox...')
                    time.sleep(5)

            print('waited for checkbox', len(checkboxes))

            for checkbox in checkboxes:
                try:
                    if not checkbox.is_selected():
                        checkbox.click()
                except Exception as e:
                    print(f"Failed to click checkbox: {e}")
                    self.step = "TOS_FAILED"
                    self.finish()
                    return

            time.sleep(2)
            buttons = dialog.find_elements(By.TAG_NAME, "button")
            for button in buttons:
                try:
                    if "agree and continue" in button.text.lower():
                        button.click()
                        print("Clicked the 'Agree and continue' button.")
                        break  # stop after clicking
                except Exception as e:
                    print(f"Error clicking button: {e}")
                    self.step = "TOS_FAILED"
                    self.finish()
                    return

            time.sleep(5)

            self.step = "TOS_ACCEPTED"
            self.enable_api()

        except Exception as e:
            print("No Popup Found, Already Handled")
            self.step = "TOS_ACCEPTED"
            self.enable_api()

    def pass_two_step(self):
        wait = WebDriverWait(self.driver, 20)
        buttons = wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, "button")))

        for btn in buttons:
            try:
                if "Remind me later" in btn.text:
                    btn.click()
                    print("Clicked 'Remind me later' button.")
                    break
            except Exception as e:
                print(f"Skipping a button due to: {e}")

    def create_project(self):
        self.driver.get(
            'https://console.cloud.google.com/projectcreate?previousPage=%2Fwelcome%2Fnew%3Fpli%3D1&organizationId=0')

        time.sleep(5)

        # click remind me later if the button and modal is appeared
        self.pass_two_step()

        time.sleep(3)

        try:
            # Wait until the Create button is clickable
            create_button = WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable((
                    By.XPATH,
                    "//button[.//span[contains(text(), 'Create')]]"
                ))
            )

            create_button.click()
            print("Clicked on 'Create' button to create the project.")

            time.sleep(10)

            self.step = "PROJECT_CREATED"

            self.select_project()

        except Exception as e:
            self.step = "PROJECT_CREATION_FAILED"
            self.finish()

    def find_projects(self):
        projects_inner = []

        try:
            # Wait for either "Select a project" or"You're currently working in" button
            project_button = WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable((
                    By.XPATH,
                    "//button[contains(@aria-label, 'select a project') or contains(@aria-label, \"You're currently working in\")]"
                ))
            )

            project_button.click()
            print("Clicked on 'Select a project' button.")

        except Exception as e:
            print("Could not click 'Select a project':", e)
            return projects_inner

        try:
            # Wait for the dialog with project list to appear
            dialog = WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "mat-dialog-container.mat-mdc-dialog-container"))
            )

            time.sleep(5)

            rows = dialog.find_elements(By.CSS_SELECTOR, 'tr[role="row"]')

            for row in rows:
                try:
                    name_elem = row.find_element(By.CSS_SELECTOR,
                                                 'a[data-prober="cloud-console-core-functions-project-name"]')
                    id_elem = row.find_element(By.CSS_SELECTOR,
                                               'span[data-prober="cloud-console-core-functions-project-id"]')

                    project_name = name_elem.text.strip()
                    project_id = id_elem.text.strip()

                    projects_inner.append(project_id)

                    print(f"Project Name: {project_name} | Project ID: {project_id}")

                except Exception as e:
                    print('No Project yet')

            return projects_inner
        except Exception as e:
            return projects_inner

    def select_project(self):
        self.driver.get('https://console.cloud.google.com/welcome/new?pli=1')
        global projects
        projects = self.find_projects()

        print('projects', len(projects))

        if len(projects) == 0:
            time.sleep(10)
            projects = self.find_projects()

        self.project_id = projects[0]
        self.enable_api()

    def enable_api(self):

        # self.driver.get(f"https://console.cloud.google.com/apis/library/gmail.googleapis.com?project={self.project_id}")
        self.driver.get(f"https://console.cloud.google.com/apis/library/gmail.googleapis.com")

        time.sleep(5)

        try:
            wait = WebDriverWait(self.driver, 60)
            target_div = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'div.cfc-product-header-content')))
        except Exception as e:
            print('Not able to enable project: ', e)
            self.step = "PROJECT_ENABLING_FAILED"
            self.finish()
            return

        try:
            # Find all button elements
            buttons = target_div.find_elements(By.TAG_NAME, "button")

            print('enable buttons', len(buttons))

            for button in buttons:
                aria_label = button.get_attribute("aria-label")
                if aria_label and aria_label.strip().lower() == "enable this api":
                    try:
                        # Wait until this specific button is clickable
                        WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(button))
                        button.click()
                        time.sleep(15)
                        self.step = "PROJECT_API_ENABLED"
                        self.complete_auth_screen()
                        break
                    except ElementClickInterceptedException:
                        print("⚠️ Element was found but could not be clicked due to interception.")
                    except TimeoutException:
                        print("⏳ Button found but never became clickable.")
                elif aria_label and aria_label.strip().lower() == "manage this api":
                    print('already enabled and find the project to set the project id')

                    current_url = self.driver.current_url
                    parsed_url = urlparse(current_url)
                    query_params = parse_qs(parsed_url.query)
                    project_value = query_params.get("project", [None])[0]

                    if project_value:
                        print('I am all good ', project_value)
                        self.project_id = project_value
                        self.step = "PROJECT_API_ENABLED"
                        self.complete_auth_screen()
                        break

                    else:
                        self.step = "PROJECT_ENABLING_FAILED"
                        print('Something went wrong here at project finding')
                        self.finish()


        except Exception as e:
            print(f"❌ Unexpected error at PROJECT_ENABLING: {e}")
            self.step = "PROJECT_ENABLING_FAILED"
            self.finish()

    def complete_auth_screen(self):

        if not self.project_id:
            try:
                expected_substring = "https://console.cloud.google.com/apis/api/gmail.googleapis.com/metrics?project"
                WebDriverWait(self.driver, 90).until(
                    lambda d: d.current_url.startswith(expected_substring)
                )

                current_url = self.driver.current_url
                parsed_url = urlparse(current_url)
                query_params = parse_qs(parsed_url.query)
                project_value = query_params.get("project", [None])[0]
                self.project_id = project_value

                if project_value:
                    self.step = "PROJECT_API_ENABLED"
                else:
                    self.step = "PROJECT_ENABLING_FAILED"
                    self.finish()

            except Exception as e:
                print('URL did not matched')
                print(f"❌ Unexpected error as complete_auth_screen: {e}")
                self.step = "PROJECT_ENABLING_FAILED"
                self.finish()
        else:
            print('From Here No Project')

        self.driver.get(f"https://console.cloud.google.com/auth/overview/create")
        time.sleep(10)

        def click_section_next(section_title, btn_text="next"):
            section = self.driver.find_element(By.XPATH,
                                               f'//cfc-stepper-step[@headertitle="{section_title}"]')

            print('app_information_section', section)

            buttons = section.find_elements(By.TAG_NAME, "button")

            print(f"Found {len(buttons)} buttons in {section_title}.")

            for btn in buttons:
                print(btn.text)
                if btn.text.strip().lower() == "next":
                    btn.click()
                    break

        try:
            input_element = self.driver.find_element(By.CSS_SELECTOR, 'input[formcontrolname="displayName"]')

            input_element.clear()
            input_element.send_keys(self.account['email'])

            select_element = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'cfc-select[formcontrolname="userSupportEmail"]'))
            )

            # Click the dropdown to open options
            select_element.click()

            time.sleep(1)

            # Wait for the dropdown options to be visible
            email = self.account['email'].lower()
            gmail_option = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located(
                    (By.XPATH,
                     f'//span[contains(translate(text(), "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz"), "{email}")]')
                )
            )

            # Click the Gmail option
            gmail_option.click()

            time.sleep(3)

            click_section_next("App Information")

            time.sleep(3)

            audience_section = self.driver.find_element(By.XPATH,
                                                        f'//cfc-stepper-step[@headertitle="Audience"]')

            print('audience_section', audience_section)

            audience_section_radio_buttons = audience_section.find_elements(By.XPATH, ".//input[@type='radio']")

            for radio in audience_section_radio_buttons:
                value = radio.get_attribute("value")
                print('value', value)
                if value and value.lower() == "external":
                    radio.click()
                    break

            time.sleep(2)

            click_section_next("Audience")

            time.sleep(3)
            email_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//input[@aria-label="Text field for emails"]'))
            )

            # Insert the email address
            email_input.clear()
            email_input.send_keys(self.account['email'])

            time.sleep(1)

            click_section_next("Contact Information")

            finish_section = self.driver.find_element(By.XPATH, '//cfc-stepper-step[@headertitle="Finish"]')

            print('finish_section', finish_section)

            checkboxes = finish_section.find_elements(By.CSS_SELECTOR, 'input[type="checkbox"]')

            print(f"Found {len(checkboxes)} checkboxes.")

            for checkbox in checkboxes:
                checkbox.click()

            submit_section = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "cfc-stepper-submit-button.cm-button-wrapper"))
            )

            # Find all buttons inside this section
            buttons = submit_section.find_elements(By.TAG_NAME, "button")

            print('buttons founded in submit section', len(buttons))

            # You can iterate or interact with the buttons as needed
            for btn in buttons:
                print(btn.text)
                if btn.text.strip().lower() == "create":
                    print("Create button pressed")
                    btn.click()
                    break

            time.sleep(8)

            self.step = "AUTH_COMPLETED"
            self.create_auth_client()

        except Exception as e:
            print(f"❌ Unexpected error AUTH_COMPLETION_FAILED")
            self.step = "AUTH_COMPLETION_FAILED"
            self.create_auth_client()

    def create_auth_client(self):

        try:
            expected_substring = "https://console.cloud.google.com/auth/overview"
            WebDriverWait(self.driver, 90).until(
                lambda d: d.current_url.startswith(expected_substring)
            )
        except Exception as e:
            print('URL did not matched for auth overview')
            print(f"❌ Unexpected error: {e}")
            self.step = "CLIENT_CREATION_FAILED"
            self.finish()

        self.driver.get(f"https://console.cloud.google.com/auth/clients")

        try:
            # Wait up to 30 seconds for the link with "Create client" text inside it
            create_client_link = WebDriverWait(self.driver, 30).until(
                EC.element_to_be_clickable((
                    By.XPATH,
                    "//a[.//span[contains(text(), 'Create client')]]"
                ))
            )
            create_client_link.click()
            print("Clicked on 'Create client' link.")
        except Exception as e:
            print("Could not find or click 'Create client':", e)

        try:
            # Step 1: Click to open the dropdown
            dropdown = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, 'cfc-select[formcontrolname="typeControl"] .cfc-select-trigger'))
            )
            dropdown.click()

            time.sleep(1)

            # Step 2: Wait for and select "Desktop App" from the options
            desktop_option = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Desktop app')]"))
            )
            desktop_option.click()

            time.sleep(2)

            input_field = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.XPATH, '//input[@formcontrolname="displayName"]'))
            )

            input_field.clear()  # Clears the field
            input_field.send_keys(self.account["email"])

            time.sleep(1)

            submit_section = self.driver.find_element(By.CSS_SELECTOR, "cfc-progress-button.cm-button-wrapper")
            # Find all buttons inside this section
            buttons = submit_section.find_elements(By.TAG_NAME, "button")

            # You can iterate or interact with the buttons as needed
            for btn in buttons:
                print(btn.text)
                if btn.text.strip().lower() == "create":
                    print("Create button pressed")
                    btn.click()
                    break

            time.sleep(5)
            self.step = "AUTH_CREATED"
            # self.download_json()

            try:
                # Wait up to 90 seconds for the <created-client-dialog> element to appear
                element = WebDriverWait(self.driver, 90).until(
                    EC.presence_of_element_located((By.TAG_NAME, "created-client-dialog"))
                )
                print("Modal Element found:", element)

                try:
                    # Wait up to 90 seconds for the div that contains a known part of the message
                    warning_div = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((
                            By.XPATH,
                            "//div[contains(@class, 'cfc-message-text-wrapper') and contains(text(), 'Starting in June 2025')]"
                        ))
                    )
                    print("Warning div found:", warning_div.text)

                    try:
                        # Wait up to 90 seconds for the button containing "Download JSON"
                        download_button = WebDriverWait(self.driver, 90).until(
                            EC.presence_of_element_located(
                                (By.XPATH, "//button[.//span[contains(text(), 'Download JSON')]]")
                            )
                        )
                        print("Button found at warning:", download_button)

                        # Optional: Click the button
                        download_button.click()

                        time.sleep(5)

                        self.publish_app()

                    except Exception as e:
                        self.download_json()
                        print("Download JSON button not found:", e)

                except Exception as e:
                    print("Warning div not found:", e)
                    self.download_json()

            except:
                print("Element->Download JSON not found within 90 seconds")
                self.download_json()

        except TimeoutException:
            self.step = "CLIENT_CREATION_FAILED"
            self.finish()

    def download_json(self):

        self.driver.get(f"https://console.cloud.google.com/auth/clients?project={self.project_id}")

        time.sleep(5)

        wait = WebDriverWait(self.driver, 30)

        # Wait for the table to be visible (optional but safer)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "table")))

        rows = self.driver.find_elements(By.CSS_SELECTOR, 'table[role="grid"] tbody tr')

        if len(rows) == 0:
            time.sleep(10)
            self.driver.get(f"https://console.cloud.google.com/auth/clients?project={self.project_id}")

        rows = self.driver.find_elements(By.CSS_SELECTOR, 'table[role="grid"] tbody tr')

        if len(rows) == 0:
            print('Sorry something went wrong creating the auth client id')
            self.step = "FAILED_TO_DOWNLOAD_NO_CLIENT"
            self.finish()
            return

        buttons = self.driver.find_elements(By.XPATH, "//table//button")

        is_downloaded = False

        for button in buttons:
            try:
                tooltip = button.get_attribute("cfctooltip")
                if tooltip and "Download OAuth client" in tooltip:
                    wait.until(EC.element_to_be_clickable(button)).click()
                    print("✅ Clicked the download button.")

                    time.sleep(3)
                    download_json_button = wait.until(EC.element_to_be_clickable((
                        By.XPATH,
                        "//button[span[contains(., 'Download JSON')]]"
                    )))
                    print('download_json_button', download_json_button)
                    download_json_button.click()
                    is_downloaded = True
                    break
            except Exception as e:
                print(f"⚠️ Skipped a button due to error: {e}")

        if is_downloaded:
            self.step = "DOWNLOADED"
            self.get_auth_token()
        else:
            self.step = "FAILED_TO_DOWNLOAD"
            self.finish()

    def publish_app(self):
        self.driver.get(f"https://console.cloud.google.com/auth/audience?project={self.project_id}")
        time.sleep(5)
        try:
            publish_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[.//span[contains(text(), 'Publish app')]]"))
            )
            publish_button.click()
            print("Clicked the 'Publish app' button.")

            time.sleep(3)
            try:
                confirm_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[.//span[contains(text(), 'Confirm')]]"))
                )
                confirm_button.click()
                print("Clicked the 'Confirm' button.")

                time.sleep(5)

                self.step = "APP_PUBLISHED"
                self.get_auth_token()
            except Exception as e:
                print(f"Failed to click the 'Confirm' button: {e}")
                self.step = "APP_PUBLISHING_FAILED"
                self.get_auth_token()

        except Exception as e:
            print(f"Failed to click the publish button")

            try:
                WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[.//span[contains(text(), 'Back to testing')]]"))
                )
                self.step = "APP_PUBLISHED"
                self.get_auth_token()
            except Exception as e:
                self.step = "APP_PUBLISHING_FAILED"
                print('Failed checking if already published')
                self.get_auth_token()

    def start_auth_server(self):
        bot_instance = self  # needed for the handler to access instance variables

        class AuthHandler(http.server.SimpleHTTPRequestHandler):
            def do_GET(self):
                try:
                    if "code=" in self.path:
                        bot_instance.auth_code = self.path
                        self.send_response(200)
                        self.end_headers()
                        self.wfile.write(b'Authorization successful. You can close this window.')
                    else:
                        self.send_error(400)
                except ConnectionResetError:
                    print("[AuthHandler] Client closed the connection before completion.")
                except Exception as e:
                    print(f"[AuthHandler] Unexpected error: {e}")

        self.server = socketserver.TCPServer(("localhost", self.port), AuthHandler)
        threading.Thread(target=self.server.serve_forever, daemon=True).start()
        print(f"[+] Auth server running on http://localhost:{self.port}")

    def stop_auth_server(self):
        try:
            if self.server:
                self.server.shutdown()
                self.server.server_close()
                print("[+] Auth server stopped.")
        except:
            print('Error stopping the auth server')

    def get_auth_token(self):
        download_path = self.download_path

        files = os.listdir(download_path)
        json_files = [f for f in files if f.endswith('.json')]

        if not json_files:
            print('You did not download the JSON file')
            self.step = "FAILED_AUTH_TOKEN"
            self.finish()
        else:
            json_file = json_files[0]
            old_path = os.path.join(download_path, json_file)

            creds_path = old_path

            if os.path.isfile(creds_path):
                print(f"✅ File exists: {creds_path}")
            else:
                print(f"❌ File does not exist: {creds_path}")
                self.step = "FAILED_AUTH_TOKEN"
                self.finish()
                return

            self.start_auth_server()

            flow = InstalledAppFlow.from_client_secrets_file(creds_path, scopes,
                                                             redirect_uri=f'http://localhost:{self.port}/')
            auth_url, _ = flow.authorization_url(prompt='consent')

            self.driver.get(auth_url)

            time.sleep(5)

            try:
                email_div = WebDriverWait(self.driver, 20).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, f'div[data-email="{self.account["email"].lower()}"]'))
                )
                email_div.click()
            except Exception as e:
                print("Error: Could not find or click on the email selection element:", e)
                self.step = "FAILED_AUTH_TOKEN"
                self.finish()
                return

            email_type = self.account["email"].split("@")[1]

            try:

                if "gmail" in email_type:
                    print("Email type is gmail: ", email_type)
                    expected_substring = "https://accounts.google.com/signin/oauth/danger"
                    WebDriverWait(self.driver, 60).until(
                        lambda d: d.current_url.startswith(expected_substring)
                    )
                else:
                    print(
                        'Not gmail, Domain mail so dont need to wait for https://accounts.google.com/signin/oauth/danger: ',
                        email_type)

                time.sleep(5)

                print('Checking language')
                html_tag = self.driver.find_element(By.TAG_NAME, 'html')
                page_lang = html_tag.get_attribute('lang')

                if not page_lang.startswith('en'):
                    print("Warning: The page language is not English. Consider using localized labels or translation.")
                    # You could switch your scraping logic here based on the language
                    self.change_lang_to_en(page_lang)
                    time.sleep(10)

                    self.driver.get(auth_url)

                    time.sleep(5)

                    try:
                        email_div = WebDriverWait(self.driver, 20).until(
                            EC.element_to_be_clickable(
                                (By.CSS_SELECTOR, f'div[data-email="{self.account["email"].lower()}"]'))
                        )
                        email_div.click()
                    except Exception as e:
                        print("Error: Could not find or click on the email selection element:", e)
                        self.step = "FAILED_AUTH_TOKEN"
                        self.finish()
                        return

                else:
                    print("Page is in English. Proceeding with normal scraping.")

            except Exception as e:
                print('URL did not matched', 'https://accounts.google.com/signin/oauth/danger')
                print(f"❌ Unexpected error: {e}")
                self.step = "FAILED_AUTH_TOKEN"
                self.finish()
                return

            wait = WebDriverWait(self.driver, 20)

            if "gmail" in email_type:
                try:
                    advanced_link = wait.until(
                        EC.element_to_be_clickable((By.XPATH, '//a[contains(text(), "Advanced")]'))
                    )
                    advanced_link.click()
                    print("Clicked the 'Advanced' link.")
                except Exception as e:
                    print("Failed to click 'Advanced':", e)
                    self.step = "FAILED_AUTH_TOKEN"
                    self.finish()

                time.sleep(2)

                try:
                    go_to_link = wait.until(
                        EC.element_to_be_clickable((By.XPATH, '//a[starts-with(text(), "Go to")]'))
                    )
                    go_to_link.click()
                    print("Clicked the 'Go to ... (unsafe)' link.")

                    try:
                        expected_substring = "https://accounts.google.com/signin/oauth/v2/consentsummary"
                        WebDriverWait(self.driver, 60).until(
                            lambda d: d.current_url.startswith(expected_substring)
                        )
                    except Exception as e:
                        print('URL did not matched', 'https://accounts.google.com/signin/oauth/v2/consentsummary')
                        print(f"❌ Unexpected error: {e}")
                        self.step = "FAILED_AUTH_TOKEN"
                        self.finish()

                    try:
                        label = WebDriverWait(self.driver, 20).until(
                            EC.element_to_be_clickable((
                                By.XPATH,
                                '//label[translate(normalize-space(text()), "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz")="select all"]'
                            ))
                        )

                        label.click()
                    except:
                        print('Already access given')

                except Exception as e:
                    print("Failed to click 'Go to ... (unsafe)':", e)
                    self.step = "FAILED_AUTH_TOKEN"
                    self.finish()

            try:
                approve_btn = WebDriverWait(self.driver, 20).until(
                    EC.element_to_be_clickable((By.ID, "submit_approve_access"))
                )
                approve_btn.click()
                print("Clicked the 'Approve Access' button.")
            except Exception as e:
                print("Failed to click the 'Approve Access' button:", e)
                self.step = "FAILED_AUTH"
                self.finish()
                return

            # Wait for the auth code to be set by the local server
            while self.auth_code is None:
                pass  # busy wait — you could also use a condition or event

            # Extract just the code
            code = parse_qs(urlparse(self.auth_code).query)["code"][0]

            # Fetch token using the auth code
            flow.fetch_token(code=code)
            creds = flow.credentials
            self.creds = {
                "token": creds.token,
                "refresh_token": creds.refresh_token,
                "token_uri": creds.token_uri,
                "client_id": creds.client_id,
                "client_secret": creds.client_secret,
                "scopes": creds.scopes
            }
            print("[+] Authentication complete. Access token obtained.")
            self.finish()

    def finish(self):
        try:
            download_path = self.download_path  # e.g., os.path.abspath("api/username")
            username = self.account['email']
            main_api_path = os.path.abspath("api")

            files = os.listdir(download_path)
            json_files = [f for f in files if f.endswith('.json')]

            json_file_path = None

            if not json_files:
                print('You did not download the JSON file')
            else:
                json_file = json_files[0]
                old_path = os.path.join(download_path, json_file)
                new_filename = f"{username}.json"
                new_path = os.path.join(main_api_path, new_filename)

                # Rename and move to main api folder
                shutil.move(old_path, new_path)
                json_file_path = new_path  # store path for upload

            # Delete the username folder
            shutil.rmtree(download_path)

            # Determine validity_status based on step
            if self.step == "APP_PUBLISHED":
                validity_status = "good"
            elif self.step == "LOGIN_FAILED":
                validity_status = "invalid_password" if self.login_result == "invalid_password" else "disabled"
            else:
                validity_status = "manual_try"

            # Prepare payload and file

            payload = {
                "email": self.account['email'],
                "status": "valid",
                "validity_status": validity_status,
                'account_id': self.account['id'],
                "creds": json.dumps(self.creds)
            }

            headers = {
                'Authorization': f'Bearer {API_TOKEN}'
            }

            files = {}
            if json_file_path and os.path.exists(json_file_path):
                files['json'] = open(json_file_path, 'rb')

            # Send update to API
            response = requests.post(
                f"{API_BASE}automation/updateToken",
                data=payload,
                files=files,
                headers=headers
            )

            if response.status_code == 200:
                print(f"✅ Status updated for {self.account['email']}")
            else:
                print(f"❌ Failed to update {self.account['email']}. Response: {response.text}")

            # Close the browser
            self.driver.quit()
            self.start_auth_server()

        except Exception as e:
            print("Error", f"Something went wrong:\n{e}")


class GmailAutomation:
    def __init__(self, driver):
        """
        Initialize with a Selenium WebDriver instance.

        Args:
        driver (webdriver): The Selenium WebDriver instance to control the browser.
        """
        self.driver = driver

    def login(self, username, password, recovery_email):
        """
        Logs into the email service.

        Args:
        username (str): The username or email address to log in.
        password (str): The password for the account.
        """
        self.driver.get("https://accounts.google.com/servicelogin?hl=en-gb")

        time.sleep(2)

        self.driver.find_element(By.ID, 'identifierId').send_keys(username)
        time.sleep(2)
        self.driver.find_element(By.ID, 'identifierNext').click()
        time.sleep(5)

        current_url_after_email = self.driver.current_url

        if "signin/identifier" in current_url_after_email:
            print("The email is invalid. URL contains 'signin/identifier'.")
            return "invalid_email"
        else:
            print("The email seems valid. URL does not contain 'signin/identifier'. Continue...")

        if "signin/challenge/recaptcha" in current_url_after_email:
            print("The email is disabled. URL contains 'signin/challenge/recaptcha'.")
            return "disabled_email"
        else:
            print("The email seems valid. URL does not contain 'signin/challenge/recaptcha'. Continue...")

        if "signin/challenge/iap" in current_url_after_email:
            print("The email is disabled. URL contains 'signin/challenge/iap'.")
            return "disabled_email"
        else:
            print("The email seems valid. URL does not contain 'signin/challenge/iap'. Continue...")

        self.driver.find_element(By.NAME, 'Passwd').send_keys(password)
        self.driver.find_element(By.ID, 'passwordNext').click()
        time.sleep(5)

        current_url_after_password = self.driver.current_url

        if "signin/challenge/pwd" in current_url_after_password:
            print("Invalid Email Password. URL contains 'signin/challenge/pwd'.")
            return "invalid_password"
        else:
            print("The password seems valid. URL does not contain 'signin/challenge/pwd'. Continue...")

        if "signin/challenge/dp" in current_url_after_password:
            print("Email has two step enabled. URL contains 'signin/challenge/dp'.")
            return "invalid_has_two_factor"
        else:
            print("Email has not two step enabled. URL does not contains 'signin/challenge/dp'. Continue...")

        if "signin/rejected" in current_url_after_password:
            print("Email is disabled or login rejected. URL contains 'signin/rejected'.")
            return "login_rejected"
        else:
            print("URL does not contains 'signin/rejected'. Continue...")

        self.decline_passkey(current_url_after_password)

        if "signin/challenge/selection" in current_url_after_password:
            print("URL contains signin/challenge/selection. Means we need to find recovery option")
            try:
                confirm_recovery_div = self.driver.find_element(By.XPATH,
                                                                "//div[contains(text(), 'Confirm your recovery email')]")
                if confirm_recovery_div:
                    confirm_recovery_div.click()
                    time.sleep(5)
                    self.driver.find_element(By.NAME, 'knowledgePreregisteredEmailResponse').send_keys(recovery_email)
                    next_button_in_recover = self.driver.find_element(By.XPATH, "//span[contains(text(), 'Next')]")

                    if next_button_in_recover:
                        next_button_in_recover.click()
                        time.sleep(5)
                    else:
                        return "invalid_has_two_factor"
                else:
                    return "invalid_has_two_factor"
            except:
                return "invalid_has_two_factor"

        self.decline_passkey(self.driver.current_url)

        return "success"

    def decline_passkey(self, current_url_after_password):
        if "signin/speedbump/passkeyenrollment" in current_url_after_password:
            print("Email is asking to setup pass key. URL contains 'signin/speedbump/passkeyenrollment'.")
            decline_passkey_button = self.driver.find_element(By.XPATH, "//span[contains(text(), 'Not now')]")
            if decline_passkey_button:
                decline_passkey_button.click()
                time.sleep(5)
        else:
            if "signin/v2/passkeyenrollment" in current_url_after_password:
                print("Email is asking to setup pass key. URL contains 'signin/v2/passkeyenrollment'.")
                decline_passkey_button = self.driver.find_element(By.XPATH, "//span[contains(text(), 'Not now')]")
                if decline_passkey_button:
                    decline_passkey_button.click()
                    time.sleep(5)


class AutoAPI:
    def __init__(self):
        super().__init__()
        self.thread_count = 0

    def start(self):

        data = fetch_data_from_server()

        if not data['batch']:
            print('You dont have any batch in the server')
            time.sleep(30)
            self.start()
            return

        if len(data['accounts']) == 0:
            print('You dont have any account in the server')
            time.sleep(30)
            self.start()
            return

        threads = []

        for i, account in enumerate(data['accounts']):
            thread = threading.Thread(target=self.worker, daemon=True, args=(i, account))
            thread.start()
            threads.append(thread)
            time.sleep(5)

        # Wait for all threads to finish
        for thread in threads:
            thread.join()

        time.sleep(10)
        self.start()

    def worker(self, index, account):
        creator = CREATOR(index, account)
        creator.create()


if __name__ == "__main__":
    bot = AutoAPI()
    bot.start()
