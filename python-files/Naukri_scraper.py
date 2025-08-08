import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import pandas as pd
import time
import os
import threading

# ---------- CONFIG ----------
CHROMEDRIVER_NAME = "chromedriver.exe"   # Must be in same folder as exe
MAX_RESULTS = 10
OUTPUT_FILE = "candidates.xlsx"
# ----------------------------

class NaukriScraperGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Naukri Resdex Scraper - OneClick GUI")
        self.root.geometry("700x380")
        self.driver = None
        self.chromedriver_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), CHROMEDRIVER_NAME)

        # UI Elements
        frm = ttk.Frame(root, padding=12)
        frm.pack(fill="both", expand=True)

        ttk.Label(frm, text="Naukri Resdex Scraper", font=("Segoe UI", 14, "bold")).grid(row=0, column=0, columnspan=3, pady=(0,10))

        ttk.Label(frm, text="1) ChromeDriver:").grid(row=1, column=0, sticky="w")
        self.chromedriver_lbl = ttk.Label(frm, text=CHROMEDRIVER_NAME)
        self.chromedriver_lbl.grid(row=1, column=1, sticky="w")
        ttk.Button(frm, text="Change", command=self.change_chromedriver).grid(row=1, column=2, sticky="e")

        ttk.Separator(frm).grid(row=2, column=0, columnspan=3, sticky="ew", pady=8)

        ttk.Label(frm, text="2) Paste Resdex Search URL:").grid(row=3, column=0, sticky="w")
        self.url_entry = ttk.Entry(frm, width=80)
        self.url_entry.grid(row=4, column=0, columnspan=3, pady=(0,8), sticky="w")

        ttk.Label(frm, text="(Best: paste the exact Resdex search results URL)").grid(row=5, column=0, columnspan=3, sticky="w")

        # Buttons for login and scraping
        btn_frame = ttk.Frame(frm)
        btn_frame.grid(row=6, column=0, columnspan=3, pady=12)

        self.btn_open = ttk.Button(btn_frame, text="Open Chrome (Login to Naukri)", command=self.open_browser)
        self.btn_open.grid(row=0, column=0, padx=6)

        self.btn_continue = ttk.Button(btn_frame, text="Start Scrape (after login)", command=self.start_scrape_thread)
        self.btn_continue.grid(row=0, column=1, padx=6)

        self.btn_saveas = ttk.Button(btn_frame, text="Save Results As...", command=self.save_as)
        self.btn_saveas.grid(row=0, column=2, padx=6)

        # Status and results
        ttk.Label(frm, text="Status:").grid(row=7, column=0, sticky="w", pady=(6,0))
        self.status_var = tk.StringVar(value="Idle")
        self.status_lbl = ttk.Label(frm, textvariable=self.status_var, foreground="blue")
        self.status_lbl.grid(row=7, column=1, columnspan=2, sticky="w", pady=(6,0))

        self.results_text = tk.Text(frm, width=85, height=10, state="disabled")
        self.results_text.grid(row=8, column=0, columnspan=3, pady=(10,0))

        # Internal
        self.last_saved_file = OUTPUT_FILE

    def change_chromedriver(self):
        path = filedialog.askopenfilename(title="Select chromedriver.exe", filetypes=[("exe files", "*.exe")])
        if path:
            self.chromedriver_path = path
            self.chromedriver_lbl.config(text=os.path.basename(path))
            messagebox.showinfo("Chromedriver set", f"Chromedriver set to:\n{path}")

    def open_browser(self):
        if not os.path.exists(self.chromedriver_path):
            messagebox.showerror("Chromedriver missing", f"Chromedriver not found:\n{self.chromedriver_path}\n\nPlease download matching chromedriver and place it here.")
            return

        try:
            self.status_var.set("Opening Chrome for manual login...")
            options = webdriver.ChromeOptions()
            # Keep browser open and visible so user can login and solve CAPTCHA
            options.add_experimental_option("detach", True)
            # Use local chromedriver path via Service
            service = Service(self.chromedriver_path)
            self.driver = webdriver.Chrome(service=service, options=options)
            # open the login page
            self.driver.get("https://www.naukri.com/nlogin/login")
            self.status_var.set("Chrome opened. Login manually then click 'Start Scrape (after login)'.")
        except Exception as e:
            messagebox.showerror("Browser error", f"Failed to launch Chrome: {e}")
            self.status_var.set("Idle")
            self.driver = None

    def start_scrape_thread(self):
        # Run scraping in a background thread to keep GUI responsive
        thread = threading.Thread(target=self.start_scrape, daemon=True)
        thread.start()

    def start_scrape(self):
        if not self.driver:
            messagebox.showerror("Not logged in", "Please click 'Open Chrome (Login to Naukri)' and login manually first.")
            return

        url = self.url_entry.get().strip()
        if not url:
            messagebox.showerror("Missing URL", "Please paste your Resdex search URL into the field.")
            return

        # Navigate to the Resdex results URL
        try:
            self.status_var.set("Loading Resdex URL...")
            self.driver.get(url)
            time.sleep(4)  # allow page to load
        except Exception as e:
            messagebox.showerror("Navigation Error", f"Failed to open URL: {e}")
            self.status_var.set("Idle")
            return

        self.status_var.set("Scraping top candidates (max 10)...")
        self.append_results("Starting scrape...\n")
        candidates = []

        try:
            # Try primary selector for profile cards (Resdex often uses 'article' tags or 'div' cards)
            cards = self.driver.find_elements(By.CSS_SELECTOR, "article, div.cnt, div.card, div.resumeCard, div.candidateCard, div.searchResultItem")
            if not cards:
                # fallback to generic list of elements
                cards = self.driver.find_elements(By.XPATH, "//div[contains(@class,'row') or contains(@class,'profile')]")

            # iterate through found cards and extract fields
            for card in cards:
                if len(candidates) >= MAX_RESULTS:
                    break

                try:
                    # Name and profile link
                    name = ""
                    profile_link = ""
                    try:
                        a = card.find_element(By.XPATH, ".//a[contains(@href,'/resdex/') or contains(@href,'/profile/') or contains(@class,'title') or contains(@class,'candidate-name') or contains(@class,'candName')]")
                        name = a.text.strip()
                        profile_link = a.get_attribute("href")
                    except:
                        # try other patterns
                        try:
                            a2 = card.find_element(By.CSS_SELECTOR, "a")
                            name = a2.text.strip()
                            profile_link = a2.get_attribute("href")
                        except:
                            pass

                    # Experience
                    exp = ""
                    try:
                        exp = card.find_element(By.XPATH, ".//span[contains(text(),'Yrs') or contains(text(),'Yr') or contains(@class,'exp')]").text.strip()
                    except:
                        # sometimes inside simple spans
                        try:
                            exp = card.find_element(By.CSS_SELECTOR, ".experience, .exp").text.strip()
                        except:
                            exp = ""

                    # Current role / company
                    role = ""
                    company = ""
                    try:
                        role = card.find_element(By.XPATH, ".//div[contains(@class,'designation') or contains(@class,'role')]/span | .//span[contains(@class,'designation')]").text.strip()
                    except:
                        role = ""
                    try:
                        company = card.find_element(By.XPATH, ".//div[contains(@class,'company') or contains(@class,'org')]/span | .//span[contains(@class,'company')]").text.strip()
                    except:
                        company = ""

                    # Location
                    location = ""
                    try:
                        location = card.find_element(By.XPATH, ".//span[contains(@class,'location') or contains(@class,'loc') or contains(text(),'Location')]").text.strip()
                    except:
                        location = ""

                    # Education
                    education = ""
                    try:
                        education = card.find_element(By.XPATH, ".//span[contains(@class,'education') or contains(@class,'edu')]").text.strip()
                    except:
                        education = ""

                    # CTC
                    ctc = ""
                    try:
                        ctc = card.find_element(By.XPATH, ".//span[contains(text(),'LPA') or contains(text(),'lpa') or contains(text(),'CTC')]").text.strip()
                    except:
                        ctc = ""

                    # Notice Period
                    notice = ""
                    try:
                        notice = card.find_element(By.XPATH, ".//span[contains(text(),'Notice') or contains(text(),'notice')]").text.strip()
                    except:
                        notice = ""

                    # Last Active
                    last_active = ""
                    try:
                        last_active = card.find_element(By.XPATH, ".//span[contains(text(),'Last Active') or contains(text(),'Active')]").text.strip()
                    except:
                        last_active = ""

                    # Build dict
                    candidate = {
                        "Name": name,
                        "Role": role,
                        "Company": company,
                        "Experience": exp,
                        "Location": location,
                        "Education": education,
                        "CTC": ctc,
                        "Notice Period": notice,
                        "Last Active": last_active,
                        "Profile Link": profile_link
                    }

                    # Only add meaningful entries (name or link)
                    if name or profile_link:
                        candidates.append(candidate)
                        self.append_results(f"{name} | {role} @ {company}\n{location}\n{last_active}\n{profile_link}\n\n")
                except Exception as inner_e:
                    # skip this card on any unexpected error
                    continue

            # If we couldn't collect enough from initial cards, try paginating or scrolling (best-effort)
            if len(candidates) < MAX_RESULTS:
                self.append_results("Less than 10 results found on first view — attempting to scroll or paginate...\n")
                try:
                    # scroll down a bit, wait, and re-collect
                    self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
                    time.sleep(2)
                    more_cards = self.driver.find_elements(By.CSS_SELECTOR, "article, div.cnt, div.card, div.resumeCard, div.candidateCard")
                    for card in more_cards:
                        if len(candidates) >= MAX_RESULTS:
                            break
                        # same extraction as above (lightweight)
                        try:
                            name = card.find_element(By.XPATH, ".//a").text.strip()
                            link = card.find_element(By.XPATH, ".//a").get_attribute("href")
                        except:
                            continue
                        if not any(c.get("Profile Link")==link for c in candidates):
                            candidates.append({"Name": name, "Profile Link": link})
                except:
                    pass

            # Trim to MAX_RESULTS
            if len(candidates) > MAX_RESULTS:
                candidates = candidates[:MAX_RESULTS]

            # Save to Excel
            if candidates:
                df = pd.DataFrame(candidates)
                save_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), OUTPUT_FILE)
                df.to_excel(save_path, index=False)
                self.last_saved_file = save_path
                self.status_var.set(f"Scraped {len(candidates)} candidates. Saved to {save_path}")
                self.append_results(f"\nSaved {len(candidates)} candidates to {save_path}\n")
                # Auto-open Excel file (Windows only)
                try:
                    os.startfile(save_path)
                except Exception:
                    pass
            else:
                self.status_var.set("No candidates found.")
                self.append_results("No candidates scraped.\n")

        except Exception as e:
            self.status_var.set("Error during scraping")
            messagebox.showerror("Scrape Error", f"An error occurred during scraping:\n{e}")

    def save_as(self):
        path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files","*.xlsx")])
        if path:
            # If a saved file exists, rename or move current saved file
            if os.path.exists(getattr(self, "last_saved_file", "")):
                try:
                    os.replace(self.last_saved_file, path)
                    self.last_saved_file = path
                    messagebox.showinfo("Saved", f"Results saved to {path}")
                except Exception as e:
                    messagebox.showerror("Save failed", str(e))
            else:
                messagebox.showerror("No results", "No results to save yet. Run a scrape first.")

    def append_results(self, text):
        self.results_text.configure(state="normal")
        self.results_text.insert("end", text)
        self.results_text.see("end")
        self.results_text.configure(state="disabled")


def main():
    root = tk.Tk()
    app = NaukriScraperGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()