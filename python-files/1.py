import customtkinter as ctk
import tkinter as tk
from PIL import Image
from seleniumbase import Driver
import json
import os
import sys
from base64 import b64encode
from multiprocessing import Process, Queue
import time
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import random
from urllib.parse import urlparse, urlunparse, parse_qs, urlencode

# اسم ملف قاعدة البيانات
DATABASE_FILE = "saved_users.json"
# أسماء ملفات الأيقونات المتاحة (قم بتغييرها لتناسب ملفاتك)
AVAILABLE_ICONS = ["1.png", "2.png", "3.ico", "4.png", "5.png", "6.png", "7.png", "8.png", "9.png", "10.png"]

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# إعدادات المظهر العام
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

def start_browser_process(username, email, password, month, log_queue, choice_queue):
    """
    This function runs as a separate process to manage a single browser instance.
    It communicates with the main process via a Queue.
    """
    new_driver = None
    try:
        log_queue.put(f"Checking availability for user: {username}...")
        
        new_driver = Driver(browser="chrome", uc=True)
        new_driver.uc_open("https://visas-de.tlscontact.com/en-us/country/eg/vac/egHAC2de")
        new_driver.maximize_window()
        
        log_queue.put("Please solve the CAPTCHA now. The script will wait for the next element to appear.")
        
        # Wait for the next element to appear after CAPTCHA is solved
        new_driver.wait_for_element("#application-menu > a:nth-child(8) > span")
        new_driver.click("#application-menu > a:nth-child(8) > span")
        
        new_driver.wait_for_element("#email-input-field")
        new_driver.type("#email-input-field", email)
        
        new_driver.wait_for_element("#password-input-field")
        new_driver.type("#password-input-field", password)
        
        new_driver.wait_for_element("#btn-login")
        new_driver.click("#btn-login")

        log_queue.put("New browser instance opened and credentials entered successfully.")
        
        # --- الجزء المسؤول عن البحث عن زر "Select" ---
        log_queue.put("Starting aggressive scroll and search for 'Select' button...")
        
        selector = "button.TlsButton_tls-button__syUS5"
        
        button_clicked = False
        while not button_clicked:
            try:
                all_buttons = new_driver.find_elements(By.CSS_SELECTOR, selector)
                select_buttons = [btn for btn in all_buttons if btn.text == "Select"]
                
                if len(select_buttons) == 1:
                    log_queue.put("✅ 'Select' button found! Clicking now...")
                    select_buttons[0].click()
                    time.sleep(3)  # Wait for 3 seconds after clicking
                    button_clicked = True
                
                elif len(select_buttons) >= 2:
                    log_queue.put({"action": "choice_needed", "count": 2})
                    log_queue.put("Multiple 'Select' buttons found. Waiting for user choice...")
                    
                    chosen_index = choice_queue.get()
                    
                    all_buttons_rechecked = new_driver.find_elements(By.CSS_SELECTOR, selector)
                    select_buttons_rechecked = [btn for btn in all_buttons_rechecked if btn.text == "Select"]

                    if 0 <= chosen_index < len(select_buttons_rechecked):
                        log_queue.put(f"✅ User chose button {chosen_index + 1}. Clicking now!")
                        select_buttons_rechecked[chosen_index].click()
                        time.sleep(3)  # Wait for 3 seconds after clicking
                        button_clicked = True
                    else:
                        log_queue.put("Error: Invalid choice received. Exiting search loop.")
                        break

                else:
                    log_queue.put("Scrolling down to search for the 'Select' button...")
                    new_driver.execute_script("window.scrollBy(0, 5000);")
                    time.sleep(0.5)

            except Exception as e:
                log_queue.put(f"An unexpected error occurred while searching for the button: {e}")
                break

        if button_clicked:
            log_queue.put("Attempting to navigate to the appointment booking page...")
            
            month_map = {
                "January": "01", "February": "02", "March": "03", "April": "04",
                "May": "05", "June": "06", "July": "07", "August": "08",
                "September": "09", "October": "10", "November": "11", "December": "12"
            }
            
            current_year = time.strftime("%Y")
            
            parsed_url = urlparse(new_driver.current_url)
            
            # This flag will stop the code at the first found appointment
            stop_search = False
            
            # Phase 1: Check the user's selected month (priority check)
            initial_month_number_str = month_map.get(month)
            if initial_month_number_str:
                month_str = str(initial_month_number_str).zfill(2)
                
                log_queue.put(f"Searching for appointments in your preferred month ({month_str}) using URL: {parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}?month={month_str}-{current_year}")
                new_driver.get(f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}?month={month_str}-{current_year}")
                
                try:
                    no_appointments_element = new_driver.find_element(By.CSS_SELECTOR, "#main > div.relative.flex-1 > div > div.container.mx-auto.px-4.py-6.md\\:py-8.print\\:py-0 > div.gap.flex.flex-col.items-stretch.gap-4.lg\\:mb-20.lg\\:gap-8 > div > div.relative.col-span-2.mx-auto.w-full.max-w-screen-sm.p-4.lg\\:col-span-1.lg\\:pb-12 > div > p")
                    if "No appointments" in no_appointments_element.text:
                        log_queue.put(f"❌ No appointments found in preferred month {month_str}. Starting full search...")
                    else:
                        log_queue.put(f"✅ Potential appointments found in preferred month {month_str}. Starting search...")
                except NoSuchElementException:
                    log_queue.put(f"✅ Potential appointments found in preferred month {month_str}. Starting search...")
                
                try:
                    for day_number in range(1, 32):
                        day_selector = f"#main > div.relative.flex-1 > div > div.container.mx-auto.px-4.py-6.md\\:py-8.print\\:py-0 > div.gap.flex.flex-col.items-stretch.gap-4.lg\\:mb-20.lg\\:gap-8 > div > div:nth-child(3) > div.snap-x.scroll-ps-4.overflow-auto.whitespace-nowrap.px-4.pb-4.pt-1 > div:nth-child({day_number})"
                        
                        try:
                            day_container = new_driver.wait_for_element(day_selector, timeout=2)
                            available_buttons = day_container.find_elements(By.CSS_SELECTOR, "button")
                            
                            if available_buttons:
                                log_queue.put(f"✅ Found {len(available_buttons)} appointment buttons for day {day_number}.")
                                
                                for button in available_buttons:
                                    if button.is_enabled():
                                        log_queue.put("✅ Found an enabled appointment button! Attempting to click...")
                                        try:
                                            button.click()
                                            log_queue.put("✅ Successfully clicked the enabled button.")
                                        except ElementClickInterceptedException:
                                            log_queue.put("Element click intercepted. Retrying with JavaScript...")
                                            new_driver.execute_script("arguments[0].click();", button)
                                            log_queue.put("✅ Successfully clicked the enabled button via JavaScript.")
                                        
                                        stop_search = True
                                        break
                                
                                if stop_search:
                                    break
                        
                        except (TimeoutException, NoSuchElementException):
                            continue
                    
                    if stop_search:
                        try:
                            # New step: click the final button
                            final_button_selector = "#main > div.relative.flex-1 > div > div.container.mx-auto.px-4.py-6.md\\:py-8.print\\:py-0 > div.gap.flex.flex-col.items-stretch.gap-4.lg\\:mb-20.lg\\:gap-8 > form > button"
                            new_driver.wait_for_element(final_button_selector, timeout=10)
                            new_driver.click(final_button_selector)
                            log_queue.put("✅ Successfully clicked the final form button.")
                        except Exception as e:
                            log_queue.put(f"❌ An error occurred while clicking the final button: {e}")
                        
                        log_queue.put("Search finished. Browser will remain open. Please close it manually when done.")
                        while True:
                            time.sleep(1)

                except Exception as e:
                    log_queue.put(f"An unexpected error occurred while searching for appointments: {e}")
                    pass

            # Phase 2: Loop through all months from 1 to 12
            if not stop_search:
                while not stop_search:
                    month_numbers = list(range(1, 13))
                    for month_num in month_numbers:
                        if stop_search:
                            break

                        month_str = str(month_num).zfill(2)
                        
                        next_url_path = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}?month={month_str}-{current_year}"
                        
                        log_queue.put(f"Searching for appointments in month {month_str} using URL: {next_url_path}")
                        
                        new_driver.get(next_url_path)
                        
                        try:
                            no_appointments_element = new_driver.find_element(By.CSS_SELECTOR, "#main > div.relative.flex-1 > div > div.container.mx-auto.px-4.py-6.md\\:py-8.print\\:py-0 > div.gap.flex.flex-col.items-stretch.gap-4.lg\\:mb-20.lg\\:gap-8 > div > div.relative.col-span-2.mx-auto.w-full.max-w-screen-sm.p-4.lg\\:col-span-1.lg\\:pb-12 > div > p")
                            if "No appointments" in no_appointments_element.text:
                                log_queue.put(f"❌ No appointments found in month {month_str}. Trying next month...")
                                continue
                        except NoSuchElementException:
                            log_queue.put(f"✅ Potential appointments found in month {month_str}. Starting search...")
                        except Exception as e:
                            log_queue.put(f"An error occurred while checking for 'no appointments' message: {e}")
                            pass

                        day_base_selector = "#main > div.relative.flex-1 > div > div.container.mx-auto.px-4.py-6.md\\:py-8.print\\:py-0 > div.gap.flex.flex-col.items-stretch.gap-4.lg\\:mb-20.lg\\:gap-8 > div > div:nth-child(3) > div.snap-x.scroll-ps-4.overflow-auto.whitespace-nowrap.px-4.pb-4.pt-1 > div:nth-child({})"
                        
                        try:
                            for day_number in range(1, 32):
                                day_selector = day_base_selector.format(day_number)
                                
                                try:
                                    day_container = new_driver.wait_for_element(day_selector, timeout=2)
                                    available_buttons = day_container.find_elements(By.CSS_SELECTOR, "button")
                                    
                                    if available_buttons:
                                        log_queue.put(f"✅ Found {len(available_buttons)} appointment buttons for day {day_number}.")
                                        
                                        for button in available_buttons:
                                            if button.is_enabled():
                                                log_queue.put("✅ Found an enabled appointment button! Attempting to click...")
                                                
                                                try:
                                                    button.click()
                                                    log_queue.put("✅ Successfully clicked the enabled button.")
                                                except ElementClickInterceptedException:
                                                    log_queue.put("Element click intercepted. Retrying with JavaScript...")
                                                    new_driver.execute_script("arguments[0].click();", button)
                                                    log_queue.put("✅ Successfully clicked the enabled button via JavaScript.")
                                                except Exception as e:
                                                    log_queue.put(f"An unexpected error occurred during click attempt: {e}. Skipping to the next one.")
                                                    continue
                                                
                                                stop_search = True
                                                break
                                            else:
                                                log_queue.put("❌ This button is not enabled. Skipping to the next one.")
                                        
                                        if stop_search:
                                            break
                                
                                except (TimeoutException, NoSuchElementException):
                                    continue

                            if stop_search:
                                break
                        
                        except Exception as e:
                            log_queue.put(f"An unexpected error occurred while searching for appointments: {e}")
                            continue
                    
                    if not stop_search:
                        log_queue.put(f"❌ No appointments found across all months. The search will restart in 60 seconds.")
                        time.sleep(60)

            # Keep the browser open after finding and clicking the button
            if stop_search:
                try:
                    # New step: click the final button
                    final_button_selector = "#main > div.relative.flex-1 > div > div.container.mx-auto.px-4.py-6.md\\:py-8.print\\:py-0 > div.gap.flex.flex-col.items-stretch.gap-4.lg\\:mb-20.lg\\:gap-8 > form > button"
                    new_driver.wait_for_element(final_button_selector, timeout=10)
                    new_driver.click(final_button_selector)
                    log_queue.put("✅ Successfully clicked the final form button.")
                except Exception as e:
                    log_queue.put(f"❌ An error occurred while clicking the final button: {e}")
                
                log_queue.put("Search finished. Browser will remain open. Please close it manually when done.")
                while True:
                    time.sleep(1)

    except Exception as e:
        log_queue.put(f"An error occurred for user {username}: {e}")
    finally:
        if new_driver:
            try:
                new_driver.quit()
            except:
                pass


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        # إعدادات النافذة
        self.title("Germany Visa Booking System")
        self.geometry("1000x700")
        self.configure(fg_color="#121212")

        # اعتراض زر الإغلاق (X) في النافذة الرئيسية
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        # متغيرات المتصفح
        self.MAX_BROWSERS = 2
        self.active_processes = []
        self.current_frame = None
        self.icon_images = {}

        # إنشاء Queues للتواصل بين العمليات
        self.log_queue = Queue()
        self.choice_queue = Queue()

        # تحميل صور الأيقونات
        self.load_icons()

        # إنشاء الواجهات
        self.main_frame = self.create_main_frame()
        self.list_frame = self.create_list_frame()
        
        # عرض الواجهة الرئيسية عند بدء التشغيل
        self.show_frame(self.main_frame)
        self.check_queue_for_messages()

    def load_icons(self):
        try:
            # تحميل الصور الرئيسية
            self.flag_image = ctk.CTkImage(Image.open(resource_path("flag-3d-round-250.png")), size=(40, 40))
            self.username_icon = ctk.CTkImage(Image.open(resource_path("user.png")), size=(18, 18))
            self.email_icon = ctk.CTkImage(Image.open(resource_path("gmail.png")), size=(18, 18))
            self.password_icon = ctk.CTkImage(Image.open(resource_path("Password.png")), size=(18, 18))
            self.month_icon = ctk.CTkImage(Image.open(resource_path("Month.png")), size=(18, 18))
            self.actions_icon = ctk.CTkImage(Image.open(resource_path("settings.png")), size=(18, 18))
            self.number_list_icon = ctk.CTkImage(Image.open(resource_path("123-cubes.png")), size=(18, 18))
            self.saved_users_icon = ctk.CTkImage(Image.open(resource_path("verified-account.png")), size=(24, 24))
            self.error_icon = ctk.CTkImage(Image.open(resource_path("cross.png")), size=(30, 30))
            self.delete_icon = ctk.CTkImage(Image.open(resource_path("delete.png")), size=(18, 18))
        except Exception as e:
            print(f"Error loading core icon images: {e}")
    
    # --- دالة القائمة المنبثقة ---
    def show_context_menu(self, event, entry_widget):
        menu = tk.Menu(entry_widget, tearoff=0, bg="#121212", fg="white")
        menu.add_command(label="Copy", command=lambda: self.copy_text(entry_widget), activebackground="#333333", activeforeground="white")
        menu.add_command(label="Paste", command=lambda: self.paste_text(entry_widget), activebackground="#333333", activeforeground="white")
        menu.add_command(label="Cut", command=lambda: self.cut_text(entry_widget), activebackground="#333333", activeforeground="white")
        menu.add_command(label="Select All", command=lambda: self.select_all(entry_widget), activebackground="#333333", activeforeground="white")
        menu.tk_popup(event.x_root, event.y_root)
    
    # --- وظائف النسخ واللصق والتحديد والقص ---
    def copy_text(self, widget):
        try:
            if isinstance(widget, ctk.CTkEntry):
                selected_text = widget.selection_get()
                self.clipboard_clear()
                self.clipboard_append(selected_text)
            elif isinstance(widget, ctk.CTkTextbox):
                if widget.tag_ranges("sel"):
                    selected_text = widget.get("sel.first", "sel.last")
                    self.clipboard_clear()
                    self.clipboard_append(selected_text)
                else:
                    self.clipboard_clear()
                    self.clipboard_append(widget.get("1.0", "end-1c"))
        except tk.TclError:
            pass
        except Exception as e:
            print(f"Error copying text: {e}")
    
    def paste_text(self, widget):
        try:
            clipboard_text = self.clipboard_get()
            if isinstance(widget, ctk.CTkEntry):
                try:
                    widget.delete("sel.first", "sel.last")
                except tk.TclError:
                    pass
                current_cursor = widget.index(tk.INSERT)
                widget.insert(current_cursor, clipboard_text)
            elif isinstance(widget, ctk.CTkTextbox):
                if widget.tag_ranges("sel"):
                    widget.delete("sel.first", "sel.last")
                widget.insert(tk.INSERT, clipboard_text)
        except Exception as e:
            print(f"Error pasting text: {e}")

    def cut_text(self, widget):
        try:
            self.copy_text(widget)
            if isinstance(widget, ctk.CTkEntry):
                try:
                    widget.delete("sel.first", "sel.last")
                except tk.TclError:
                    pass
            elif isinstance(widget, ctk.CTkTextbox) and widget.tag_ranges("sel"):
                widget.delete("sel.first", "sel.last")
        except Exception as e:
            print(f"Error cutting text: {e}")
    
    def select_all(self, widget):
        try:
            if isinstance(widget, ctk.CTkEntry):
                widget.select_range(0, tk.END)
                widget.icursor(tk.END)
            elif isinstance(widget, ctk.CTkTextbox):
                widget.tag_add("sel", "1.0", "end")
                widget.mark_set("insert", "end")
        except Exception as e:
            print(f"Error selecting all text: {e}")
    
    # --- دالة جديدة للتعامل مع الاختصارات بشكل موحد ---
    def on_keypress(self, event):
        widget = event.widget
        # التحقق من نوع عنصر الواجهة
        if not (isinstance(widget, (ctk.CTkEntry, ctk.CTkTextbox))):
            return

        char = event.char.lower()
        
        # التحقق من ضغط زر Ctrl
        if event.state & 0x4:  # حالة زر Ctrl
            if char == 'c' or event.keycode == 67:  # Ctrl + C
                self.copy_text(widget)
                return "break"
            elif char == 'x' or event.keycode == 88:  # Ctrl + X
                self.cut_text(widget)
                return "break"
            elif char == 'v' or event.keycode == 86:  # Ctrl + V
                self.paste_text(widget)
                return "break"
            elif char == 'a' or event.keycode == 65:  # Ctrl + A
                self.select_all(widget)
                return "break"
        
        # اختصارات بديلة
        elif event.keysym == "Insert" and event.state & 0x1:  # Shift + Insert
            self.paste_text(widget)
            return "break"
        elif event.keysym == "Insert" and event.state & 0x4:  # Ctrl + Insert
            self.copy_text(widget)
            return "break"
    
    # --- ربط اختصارات لوحة المفاتيح (تم التعديل هنا) ---
    def bind_keyboard_shortcuts(self, widget):
        # ربط حدث الضغط على المفاتيح
        widget.bind("<KeyPress>", self.on_keypress)


    # --- دالة الإغلاق المخصصة ---
    def on_closing(self):
        self.exit_dialog = ctk.CTkToplevel(self)
        self.exit_dialog.title("Exit Confirmation")
        self.exit_dialog.resizable(False, False)
        self.exit_dialog.grab_set()

        # حساب موضع النافذة المنبثقة في منتصف الشاشة
        dialog_width = 350
        dialog_height = 200
        main_x = self.winfo_x()
        main_y = self.winfo_y()
        main_width = self.winfo_width()
        main_height = self.winfo_height()
        
        x_pos = main_x + (main_width // 2) - (dialog_width // 2)
        y_pos = main_y + (main_height // 2) - (dialog_height // 2)
        
        self.exit_dialog.geometry(f"{dialog_width}x{dialog_height}+{x_pos}+{y_pos}")

        dialog_frame = ctk.CTkFrame(self.exit_dialog, fg_color="#121212")
        dialog_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # إضافة العلم
        if self.flag_image:
            flag_label = ctk.CTkLabel(dialog_frame, image=self.flag_image, text="")
            flag_label.pack(pady=(10, 5))
            
        # إضافة رسالة الوداع
        message_label = ctk.CTkLabel(dialog_frame, text="Thank you for using the system. Goodbye!", font=ctk.CTkFont(size=14, weight="bold"))
        message_label.pack(pady=(5, 10))

        # زر موافق فقط
        ok_button = ctk.CTkButton(dialog_frame, text="OK", command=self.exit_app, fg_color="#008000", hover_color="#006400", width=80)
        ok_button.pack(pady=10)
        
    def exit_app(self):
        # اغلق المتصفحات في الخلفية أولاً
        for p in self.active_processes:
            p.terminate()
            p.join()
        self.active_processes.clear()

        # اغلق النافذة المنبثقة
        self.exit_dialog.destroy()
        
        # اغلق النافذة الرئيسية فوراً
        self.destroy()

    def show_frame(self, frame):
        if self.current_frame:
            self.current_frame.pack_forget()
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        self.current_frame = frame
    
    def log_message(self, message):
        self.log_textbox.configure(state="normal")
        self.log_textbox.insert("end", message + "\n")
        self.log_textbox.configure(state="disabled")
        self.log_textbox.see("end")

    def create_choice_popup(self, count):
        """Creates a professional popup window to let the user choose a button."""
        choice_dialog = ctk.CTkToplevel(self)
        choice_dialog.title("Select an Option")
        choice_dialog.resizable(False, False)
        choice_dialog.grab_set()

        dialog_width = 400
        dialog_height = 150
        main_x = self.winfo_x()
        main_y = self.winfo_y()
        main_width = self.winfo_width()
        main_height = self.winfo_height()
        
        x_pos = main_x + (main_width // 2) - (dialog_width // 2)
        y_pos = main_y + (main_height // 2) - (dialog_height // 2)
        
        choice_dialog.geometry(f"{dialog_width}x{dialog_height}+{x_pos}+{y_pos}")

        dialog_frame = ctk.CTkFrame(choice_dialog, fg_color="#121212")
        dialog_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        message_label = ctk.CTkLabel(dialog_frame, text="Please select the button you want to click:", font=ctk.CTkFont(size=14, weight="bold"), wraplength=350)
        message_label.pack(pady=(10, 20))
        
        buttons_frame = ctk.CTkFrame(dialog_frame, fg_color="transparent")
        buttons_frame.pack()

        # Button 1 (Red)
        choice_button_1 = ctk.CTkButton(buttons_frame, text=f"First Option", command=lambda idx=0: self.make_choice(idx, choice_dialog), fg_color="#D10000", hover_color="#B00000", width=120)
        choice_button_1.pack(side="left", padx=10)

        # Button 2 (Blue)
        choice_button_2 = ctk.CTkButton(buttons_frame, text=f"Second Option", command=lambda idx=1: self.make_choice(idx, choice_dialog), fg_color="#00A3C9", hover_color="#00839F", width=120)
        choice_button_2.pack(side="left", padx=10)

    def make_choice(self, choice_index, dialog):
        """Sends the user's choice to the browser process and closes the popup."""
        self.choice_queue.put(choice_index)
        dialog.destroy()


    def check_queue_for_messages(self):
        while not self.log_queue.empty():
            message = self.log_queue.get()
            
            if isinstance(message, dict) and message.get("action") == "choice_needed":
                self.create_choice_popup(message.get("count"))
                self.status_label.configure(text="Status: User Choice Needed")
                break
            elif isinstance(message, str):
                self.log_message(message)
                if "error" in message.lower():
                    self.status_label.configure(text="Status: Error")
                else:
                    self.status_label.configure(text="Status: Browser Open")
        
        # Keep checking the queue periodically
        self.after(500, self.check_queue_for_messages)


    def show_error_popup(self, message):
        error_dialog = ctk.CTkToplevel(self)
        error_dialog.title("Input Error")
        error_dialog.resizable(False, False)
        error_dialog.grab_set()
        
        dialog_width = 500
        dialog_height = 200
        main_x = self.winfo_x()
        main_y = self.winfo_y()
        main_width = self.winfo_width()
        main_height = self.winfo_height()
        
        x_pos = main_x + (main_width // 2) - (dialog_width // 2)
        y_pos = main_y + (main_height // 2) - (dialog_height // 2)
        
        error_dialog.geometry(f"{dialog_width}x{dialog_height}+{x_pos}+{y_pos}")

        error_frame = ctk.CTkFrame(error_dialog, fg_color="#121212")
        error_frame.pack(fill="both", expand=True, padx=20, pady=20)

        content_frame = ctk.CTkFrame(error_frame, fg_color="transparent")
        content_frame.pack(pady=(10, 0))
        
        if self.error_icon:
            icon_label = ctk.CTkLabel(content_frame, image=self.error_icon, text="")
            icon_label.pack(side="left", padx=(0, 10))
            
        message_label = ctk.CTkLabel(content_frame, text=message, font=ctk.CTkFont(size=14, weight="bold"), text_color="#FF6347", wraplength=400)
        message_label.pack(side="left")
        
        ok_button = ctk.CTkButton(error_frame, text="OK", command=error_dialog.destroy, fg_color="#FF4500", hover_color="#CD3700")
        ok_button.pack(pady=(15, 0))

    # --- إنشاء واجهة الإدخال الرئيسية ---
    def create_main_frame(self):
        frame = ctk.CTkFrame(self, fg_color="#121212")
        frame.grid_columnconfigure(0, weight=1)
        
        # Widgets
        title_frame = ctk.CTkFrame(frame, fg_color="transparent")
        title_frame.grid(row=0, column=0, pady=(20, 10), sticky="n")
        title_frame.grid_columnconfigure(0, weight=1)

        if self.flag_image:
            flag_label = ctk.CTkLabel(title_frame, image=self.flag_image, text="")
            flag_label.grid(row=0, column=0, padx=(0, 5))

        title_label = ctk.CTkLabel(title_frame, text="Germany Visa Booking System", font=ctk.CTkFont(size=28, weight="bold"))
        title_label.grid(row=0, column=1)

        # Labels and Entries with grid
        self.username_label = ctk.CTkLabel(frame, text="Username:", font=ctk.CTkFont(size=14))
        self.username_label.grid(row=1, column=0, pady=(10, 0), padx=10, sticky="w")
        self.username_entry = ctk.CTkEntry(frame, placeholder_text="", width=500, fg_color="#2A2A2A", border_color="#555555")
        self.username_entry.grid(row=2, column=0, pady=5, padx=10, sticky="ew")
        self.username_entry.bind("<Button-3>", lambda event: self.show_context_menu(event, self.username_entry))
        self.bind_keyboard_shortcuts(self.username_entry)

        self.email_label = ctk.CTkLabel(frame, text="Email:", font=ctk.CTkFont(size=14))
        self.email_label.grid(row=3, column=0, pady=(10, 0), padx=10, sticky="w")
        self.email_entry = ctk.CTkEntry(frame, placeholder_text="", width=500, fg_color="#2A2A2A", border_color="#555555")
        self.email_entry.grid(row=4, column=0, pady=5, padx=10, sticky="ew")
        self.email_entry.bind("<Button-3>", lambda event: self.show_context_menu(event, self.email_entry))
        self.bind_keyboard_shortcuts(self.email_entry)

        self.password_label = ctk.CTkLabel(frame, text="Password:", font=ctk.CTkFont(size=14))
        self.password_label.grid(row=5, column=0, pady=(10, 0), padx=10, sticky="w")
        self.password_entry = ctk.CTkEntry(frame, placeholder_text="", width=500, fg_color="#2A2A2A", border_color="#555555")
        self.password_entry.grid(row=6, column=0, pady=5, padx=10, sticky="ew")
        self.password_entry.bind("<Button-3>", lambda event: self.show_context_menu(event, self.password_entry))
        self.bind_keyboard_shortcuts(self.password_entry)
        
        self.month_label = ctk.CTkLabel(frame, text="Month:", font=ctk.CTkFont(size=14))
        self.month_label.grid(row=7, column=0, pady=(10, 0), padx=10, sticky="w")
        months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
        self.month_optionmenu = ctk.CTkOptionMenu(frame, values=months, width=500, fg_color="#2A2A2A", button_color="#3A3A3A", button_hover_color="#555555")
        self.month_optionmenu.grid(row=8, column=0, pady=5, padx=10, sticky="ew")
        
        self.status_label = ctk.CTkLabel(frame, text="Status: Ready", font=ctk.CTkFont(size=18, weight="bold"), text_color="#A9A9A9")
        self.status_label.grid(row=9, column=0, pady=(20, 5), padx=10, sticky="w")
        
        self.buttons_frame = ctk.CTkFrame(frame, fg_color="transparent")
        self.buttons_frame.grid(row=10, column=0, pady=10, sticky="ew")
        self.buttons_frame.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)
        
        self.check_button = ctk.CTkButton(self.buttons_frame, text="Check", fg_color="#D10000", hover_color="#B00000", command=lambda: self.check_action(self.username_entry.get(), self.email_entry.get(), self.password_entry.get(), self.month_optionmenu.get()))
        self.check_button.grid(row=0, column=0, padx=5, pady=10)
        
        self.clear_log_button = ctk.CTkButton(self.buttons_frame, text="Clear Log", fg_color="#E67E22", hover_color="#D35400", command=self.clear_log_action)
        self.clear_log_button.grid(row=0, column=1, padx=5, pady=10)
        
        self.save_button = ctk.CTkButton(self.buttons_frame, text="Save", fg_color="#008000", hover_color="#006400", command=self.save_action)
        self.save_button.grid(row=0, column=2, padx=5, pady=10)
        
        self.list_button = ctk.CTkButton(self.buttons_frame, text="List", fg_color="#00A3C9", hover_color="#00839F", command=self.list_action)
        self.list_button.grid(row=0, column=3, padx=5, pady=10)
        
        self.exit_button = ctk.CTkButton(self.buttons_frame, text="Exit", fg_color="#4B0082", hover_color="#3F006D", command=self.on_closing)
        self.exit_button.grid(row=0, column=4, padx=5, pady=10)
        
        self.log_textbox = ctk.CTkTextbox(frame, wrap="word", width=500, height=100, fg_color="#2A2A2A", border_color="#555555")
        self.log_textbox.grid(row=11, column=0, pady=(20, 10), padx=10, sticky="nsew")
        self.log_message("System initialized. Click 'Check' to start.")
        self.log_textbox.configure(state="disabled")
        self.log_textbox.bind("<Button-3>", lambda event: self.show_context_menu(event, self.log_textbox))
        self.bind_keyboard_shortcuts(self.log_textbox)

        return frame

    # --- إنشاء واجهة قائمة المستخدمين ---
    def create_list_frame(self):
        frame = ctk.CTkFrame(self, fg_color="#121212")
        frame.grid_columnconfigure(0, weight=1)
        
        header_frame = ctk.CTkFrame(frame, fg_color="transparent")
        header_frame.pack(fill="x", pady=(10, 0), padx=10)
        
        # Position the back button to the left
        back_button = ctk.CTkButton(header_frame, text="Back", command=lambda: self.show_frame(self.main_frame), width=80)
        back_button.pack(side="left", padx=(10, 0), pady=10)

        # Container for the centered title and icon
        title_container = ctk.CTkFrame(header_frame, fg_color="transparent")
        title_container.pack(side="left", expand=True)
        
        if self.saved_users_icon:
            icon_label = ctk.CTkLabel(title_container, image=self.saved_users_icon, text="")
            icon_label.pack(side="left", padx=(0, 5))
            
        title_label = ctk.CTkLabel(title_container, text="Saved Users", font=ctk.CTkFont(size=24, weight="bold"), text_color="#1E90FF")
        title_label.pack(side="left")
        
        self.table_frame = ctk.CTkScrollableFrame(frame, fg_color="#1F1F1F")
        self.table_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        return frame

    def load_and_display_users(self):
        for widget in self.table_frame.winfo_children():
            widget.destroy()
        
        # Headers for the table with image icons
        headers = [
            ("Username", self.username_icon),
            ("Email", self.email_icon),
            ("Password", self.password_icon),
            ("Month", self.month_icon),
            ("Actions", self.actions_icon)
        ]
        
        # Configure columns
        self.table_frame.grid_columnconfigure(0, weight=1)
        self.table_frame.grid_columnconfigure(1, weight=1)
        self.table_frame.grid_columnconfigure(2, weight=1)
        self.table_frame.grid_columnconfigure(3, weight=1)
        self.table_frame.grid_columnconfigure(4, weight=0)
        
        for i, (col_name, icon_image) in enumerate(headers):
            header_container = ctk.CTkFrame(self.table_frame, fg_color="transparent")
            header_container.grid(row=0, column=i, padx=5, pady=5, sticky="ew")
            
            header_container.grid_columnconfigure(0, weight=1)
            
            inner_frame = ctk.CTkFrame(header_container, fg_color="transparent")
            inner_frame.pack(expand=True)
            
            if icon_image:
                icon_label = ctk.CTkLabel(inner_frame, image=icon_image, text="")
                icon_label.pack(side="left", padx=(0, 5))
            
            name_label = ctk.CTkLabel(inner_frame, text=col_name, font=ctk.CTkFont(weight="bold", size=16), text_color="#A9A9A9")
            name_label.pack(side="left")
            
        saved_users = self.load_saved_users()
        
        row = 1
        if not saved_users:
            no_users_label = ctk.CTkLabel(self.table_frame, text="No saved users found.", font=ctk.CTkFont(size=14), text_color="#A9A9A9")
            no_users_label.grid(row=1, column=0, columnspan=7, pady=20)
        else:
            for user in saved_users:
                # حقول المستخدم
                username_entry = ctk.CTkEntry(self.table_frame, fg_color="#2A2A2A", border_color="#555555", text_color="white")
                username_entry.insert(0, user.get("username", ""))
                username_entry.grid(row=row, column=0, padx=5, pady=5, sticky="ew")
                username_entry.bind("<Button-3>", lambda event, entry=username_entry: self.show_context_menu(event, entry))
                self.bind_keyboard_shortcuts(username_entry)

                email_entry = ctk.CTkEntry(self.table_frame, fg_color="#2A2A2A", border_color="#555555", text_color="white")
                email_entry.insert(0, user.get("email", ""))
                email_entry.grid(row=row, column=1, padx=5, pady=5, sticky="ew")
                email_entry.bind("<Button-3>", lambda event, entry=email_entry: self.show_context_menu(event, entry))
                self.bind_keyboard_shortcuts(email_entry)

                password_entry = ctk.CTkEntry(self.table_frame, fg_color="#2A2A2A", border_color="#555555", text_color="white")
                password_entry.insert(0, user.get("password", ""))
                password_entry.grid(row=row, column=2, padx=5, pady=5, sticky="ew")
                password_entry.bind("<Button-3>", lambda event, entry=password_entry: self.show_context_menu(event, entry))
                self.bind_keyboard_shortcuts(password_entry)
                
                months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
                month_optionmenu = ctk.CTkOptionMenu(self.table_frame, values=months, width=100, fg_color="#2A2A2A", button_color="#3A3A3A", button_hover_color="#555555")
                month_optionmenu.set(user.get("month", "January"))
                month_optionmenu.grid(row=row, column=3, padx=5, pady=5, sticky="ew")

                actions_frame = ctk.CTkFrame(self.table_frame, fg_color="transparent")
                actions_frame.grid(row=row, column=4, padx=5, pady=5, sticky="ew")
                
                # أزرار الإجراءات
                save_button = ctk.CTkButton(actions_frame, text="Save", fg_color="#008000", hover_color="#006400", width=60, command=lambda original_user=user, username_entry=username_entry, email_entry=email_entry, password_entry=password_entry, month_optionmenu=month_optionmenu: self.save_edit_action(original_user, username_entry.get(), email_entry.get(), password_entry.get(), month_optionmenu.get()))
                save_button.pack(side="left", padx=2)

                check_button = ctk.CTkButton(actions_frame, text="Check", fg_color="#D10000", hover_color="#B00000", width=60, command=lambda u=user: self.check_action(u['username'], u['email'], u['password'], u.get('month')))
                check_button.pack(side="left", padx=2)
                
                if self.delete_icon:
                    delete_button = ctk.CTkButton(actions_frame, text="", image=self.delete_icon, fg_color="#8B0000", hover_color="#6B0000", width=40, command=lambda u=user: self.delete_user(u))
                    delete_button.pack(side="left", padx=2)
                
                row += 1

    # --- الدوال المربوطة بالأزرار ---
    def check_action(self, username, email, password, month):
        self.show_frame(self.main_frame)
        
        # Clean up any terminated processes first
        self.active_processes = [p for p in self.active_processes if p.is_alive()]

        # Check if max browsers limit is reached
        if len(self.active_processes) >= self.MAX_BROWSERS:
            self.show_error_popup(f"You have reached the maximum limit of {self.MAX_BROWSERS} open browser windows. Please close one to open a new one.")
            return

        # Start a new process for the browser session
        process = Process(target=start_browser_process, args=(username, email, password, month, self.log_queue, self.choice_queue))
        process.start()
        self.active_processes.append(process)

    def clear_log_action(self):
        # أغلق جميع المتصفحات
        for p in self.active_processes:
            self.log_message(f"Closing browser instance with PID {p.pid}...")
            try:
                # محاولة إنهاء العملية بلطف أولاً
                p.terminate()
            except Exception as e:
                self.log_message(f"Error while terminating process {p.pid}: {e}")
            p.join() # انتظر حتى يتم إنهاء العملية بشكل كامل
        
        self.active_processes.clear()

        # امسح محتوى Log و أعد الحقول إلى وضعها الأصلي
        self.username_entry.delete(0, "end")
        self.email_entry.delete(0, "end")
        self.password_entry.delete(0, "end")
        self.month_optionmenu.set("January")
        
        self.log_textbox.configure(state="normal")
        self.log_textbox.delete("1.0", "end")
        self.log_textbox.configure(state="disabled")
        
        self.log_message("All data and browser sessions cleared. Restarting the application...")
        self.status_label.configure(text="Status: Restarting...")

        # --- الحل الجديد والأكثر موثوقية لإعادة التشغيل ---
        self.destroy() # اغلق النافذة الحالية
        python = sys.executable
        os.execl(python, python, *sys.argv)


    def load_saved_users(self):
        saved_users = []
        if os.path.exists(DATABASE_FILE) and os.stat(DATABASE_FILE).st_size > 0:
            try:
                with open(DATABASE_FILE, "r") as f:
                    saved_users = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                pass
        return saved_users
    
    def save_action(self):
        username = self.username_entry.get()
        email = self.email_entry.get()
        password = self.password_entry.get()
        month = self.month_optionmenu.get()

        if not email or not password:
            self.show_error_popup("Error: Email and password fields cannot be empty. Please provide the required information.")
            return

        user_data = {
            "username": username,
            "email": email,
            "password": password,
            "month": month,
        }
        
        saved_users = self.load_saved_users()
        saved_users.append(user_data)
        
        with open(DATABASE_FILE, "w") as f:
            json.dump(saved_users, f, indent=4)
        
        self.log_message(f"User '{username if username else email}' saved successfully.")

    def save_edit_action(self, original_user, new_username, new_email, new_password, new_month):
        """Saves edited user data from the list view."""
        if not new_email or not new_password:
            self.show_error_popup("Error: Email and password fields cannot be empty. Please provide the required information.")
            return

        saved_users = self.load_saved_users()
        
        for i, user in enumerate(saved_users):
            if user['email'] == original_user['email']:
                saved_users[i]['username'] = new_username
                saved_users[i]['email'] = new_email
                saved_users[i]['password'] = new_password
                saved_users[i]['month'] = new_month
                break
        
        with open(DATABASE_FILE, "w") as f:
            json.dump(saved_users, f, indent=4)
        
        self.log_message(f"User '{new_username if new_username else new_email}' updated successfully.")
        self.load_and_display_users()
        
    def list_action(self):
        self.show_frame(self.list_frame)
        self.load_and_display_users()
        
    def delete_user(self, user_to_delete):
        saved_users = self.load_saved_users()
        
        saved_users = [user for user in saved_users if not (user['email'] == user_to_delete['email'])]
        
        with open(DATABASE_FILE, "w") as f:
            json.dump(saved_users, f, indent=4)
            
        self.load_and_display_users()
        self.log_message(f"User '{user_to_delete['username'] if user_to_delete['username'] else user_to_delete['email']}' deleted.")

    def exit_action(self):
        self.on_closing()

if __name__ == "__main__":
    app = App()
    app.mainloop()