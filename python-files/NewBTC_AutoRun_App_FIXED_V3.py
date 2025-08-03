"""
================================================================================
NewBTC Auto Run Bot - V1 (Simple Chrome-Only Version)
NewBTC_AutoRun_App_FIXED_V3.py
Simple, reliable Chrome automation for NewBTC mining
================================================================================
"""

""" Libraries """
from QI_f_0l_01_imports_basic import *
import customtkinter
import tkinter
import threading
import time
import os
import subprocess
import sys
import pyautogui
from datetime import datetime
from PIL import Image, ImageTk
import pytesseract
import shutil
import pyperclip
import webbrowser

import pdb
# pdb.set_trace()  # n (next), c (continue) q (quit) p variable (print) l (list)

import sys
# UTF-8 output support
sys.stdout.reconfigure(encoding='utf-8')

# Smart Tesseract Setup
def setup_tesseract():
	"""Smart Tesseract OCR installation and path setup"""
	try:
		# Standard installation paths to check
		possible_paths = [
			r'C:\Program Files\Tesseract-OCR\tesseract.exe',
			r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
			r'tesseract\tesseract.exe',  # Local folder
			r'bin\tesseract\tesseract.exe',  # Relative path
			os.path.join(os.getcwd(), 'tesseract', 'tesseract.exe'),  # Current dir
		]
		
		# Check if Tesseract exists in any standard location
		for path in possible_paths:
			if os.path.exists(path):
				pytesseract.pytesseract.tesseract_cmd = path
				#print(f"✅ Tesseract found: {path}")
				return True
		
		# If not found, try to use system PATH
		try:
			result = subprocess.run(['tesseract', '--version'], 
								  capture_output=True, text=True, timeout=5)
			if result.returncode == 0:
				pytesseract.pytesseract.tesseract_cmd = 'tesseract'  # Use system PATH
				#print("✅ Tesseract found in system PATH")
				return True
		except:
			pass
		
		# If still not found, create local tesseract folder with instructions
		#print("⚠️ Tesseract not found - creating setup instructions...")
		create_tesseract_setup_instructions()
		return False
		
	except Exception as e:
		print(f"⚠️ Tesseract setup failed: {str(e)}")
		return False

def create_tesseract_setup_instructions():
	"""Create setup instructions for Tesseract OCR"""
	try:
		os.makedirs('tesseract', exist_ok=True)
		
		instructions = """
════════════════════════════════════════════════════════════════════════════════
🔧 TESSERACT OCR SETUP REQUIRED
════════════════════════════════════════════════════════════════════════════════

The NewBTC AutoRun Bot requires Tesseract OCR for text recognition.

📥 OPTION 1: Download and install Tesseract OCR
   1. Visit: https://github.com/UB-Mannheim/tesseract/wiki
   2. Download: tesseract-ocr-w64-setup-v5.3.0.20221214.exe (or latest)
   3. Install to: C:\\Program Files\\Tesseract-OCR\\
   4. Restart the bot

📁 OPTION 2: Portable version (for EXE distribution)
   1. Copy tesseract.exe to: ./tesseract/tesseract.exe
   2. Copy tessdata folder to: ./tesseract/tessdata/
   3. Restart the bot

🚀 The bot will automatically detect Tesseract once installed.

════════════════════════════════════════════════════════════════════════════════
"""
		
		with open('tesseract/SETUP_INSTRUCTIONS.txt', 'w') as f:
			f.write(instructions)
		
		print("📄 Setup instructions created: tesseract/SETUP_INSTRUCTIONS.txt")
		
	except Exception as e:
		print(f"⚠️ Could not create setup instructions: {str(e)}")

# Initialize Tesseract setup
setup_tesseract()

# Import professional append_text function if available
try:
	from NewBTC_f_3_utils import append_text
	STYLED_TEXT_AVAILABLE = True
except ImportError:
	STYLED_TEXT_AVAILABLE = False

# Import EasyOCR loader if available
try:
	from NewBTC_f_2_easyocr_loader import get_easyocr_reader, is_easyocr_ready
	EASYOCR_AVAILABLE = True
except ImportError:
	EASYOCR_AVAILABLE = False
	
""" Libraries """

class NewBTCMiningWindow(ctk.CTk):
	def __init__(self):
		super().__init__()	
		
		"""Initialize the simple NewBTC Auto Run Bot V1"""
		
		# Initialize CustomTkinter
		customtkinter.set_appearance_mode("dark")
		customtkinter.set_default_color_theme("blue")
		
		# Create main window
		#self = customtkinter.CTk()
		self.title("🚀 NewBTC Auto Run Bot - V1 PRODUCTION")
		self.geometry("600x500")
		
		# Professional styling
		self.my_font = customtkinter.CTkFont(family="Verdana", size=12, weight="bold")
		self.option_add('*Font', ('Verdana', 9, 'bold'))
		
		self.resizable(width=False, height=False)
		self.attributes('-topmost', True)
		
		# UI state
		self.is_running = False
		self.current_view = "main"
		self.wallet_monitor_running = False
		self.wallet_connected = False  # Track if wallet is successfully connected
		self.testing_mode = False  # PRODUCTION MODE: Real clicks enabled
		
		# Stage completion tracking
		self.stage_3_claim_done = False
		self.stage_4_staking_done = False  
		self.stage_5_mining_done = False
		self.cycle_complete = False
		
		# Create UI
		self.setup_ui()
		
		# Display startup messages
		self.display_startup_info()
		
		# DON'T start wallet monitor until GO button is pressed
	
	def auto_setup_mining_pools(self):
		"""Automatically setup mining pools with available FNBTC"""
		try:
			self.log("⛏️ Auto-setting up mining pools...", "info")
			time.sleep(2)  # Let page settle
			
			# FIRST: Scroll down halfway to see mining pools section
			self.log("📜 Scrolling down to reveal mining pools section...", "info")
			pyautogui.scroll(-5)  # Scroll down halfway
			time.sleep(1)
			
			# Get available FNBTC balance  
			available_fnbtc = self.get_available_fnbtc_balance()
			if not available_fnbtc or available_fnbtc <= 0.1:
				self.log(f"⏭️ Insufficient FNBTC balance: {available_fnbtc} - need > 0.1", "info")
				return
			
			# Calculate mining amount (reserve 0.1 for next round as specified)
			mining_amount = available_fnbtc - 0.1
			self.log(f"💰 Available: {available_fnbtc} FNBTC, Mining: {mining_amount} FNBTC (reserve 0.1)", "info")
			
			# Step 1: Click Split Fuel (not Fixed Fuel)
			self.log("1️⃣ STEP 1: Clicking Split Fuel button...", "info")
			if not self.click_split_fuel():
				self.log("❌ Failed to click Split Fuel", "error")
				return
			
			# Step 2: Enter fuel amount (Available - 0.1 reserve)
			self.log(f"2️⃣ STEP 2: Entering fuel amount ({mining_amount} FNBTC)...", "info")
			if not self.enter_fuel_amount(mining_amount):
				self.log("❌ Failed to enter fuel amount", "error")
				return
			
			# Step 3: Select all 10 pools (Pool 0 through Pool 9)
			self.log("3️⃣ STEP 3: Selecting all 10 mining pools...", "info")
			if not self.select_all_mining_pools():
				self.log("❌ Failed to select mining pools", "error")
				return
			
			# Step 4: Execute mining with retry logic (the buggy end)
			self.log("4️⃣ STEP 4: Approve & Mine (with retry for buggy behavior)...", "info")
			if not self.execute_mining():
				self.log("❌ Failed to execute mining after retries", "error")
				return
			
			self.log("🎉 ALL 4 STEPS COMPLETED - Mining pools setup successfully!", "success")
			
		except Exception as e:
			self.log(f"⚠️ Mining pool setup failed: {str(e)}", "warning")
	
	def get_available_fnbtc_balance(self):
		"""Extract available FNBTC balance from mining page"""
		try:
			# Take screenshot to read balance
			filepath = self.take_screenshot("fnbtc_balance_check.png")
			if not filepath:
				return None
			
			ocr_result = self.ocr_screenshot(filepath)
			if not ocr_result:
				return None
			
			ocr_method, raw_result = ocr_result
			
			# Look for "Available FNBTC Balance: X.XXX"
			for i, item in enumerate(raw_result):
				text = item[1].strip().upper()
				if "AVAILABLE FNBTC BALANCE" in text or ("AVAILABLE" in text and "FNBTC" in text):
					# Look for number in this or nearby text
					for j in range(max(0, i-2), min(len(raw_result), i+3)):
						balance_text = raw_result[j][1].strip()
						if any(c.isdigit() for c in balance_text) and '.' in balance_text:
							import re
							numbers = re.findall(r'\d+\.?\d*', balance_text)
							for num in numbers:
								try:
									balance = float(num)
									if balance > 0:
										self.log(f"💰 Found FNBTC balance: {balance}", "info")
										return balance
								except:
									continue
			
			self.log("⚠️ Could not find FNBTC balance", "warning")
			return None
			
		except Exception as e:
			self.log(f"⚠️ FNBTC balance reading failed: {str(e)}", "warning")
			return None
	
	def click_split_fuel(self):
		"""Click the Split Fuel button"""
		try:
			self.log("🎯 Clicking Split Fuel button...", "info")
			
			filepath = self.take_screenshot("split_fuel_click.png")
			if not filepath:
				return False
			
			ocr_result = self.ocr_screenshot(filepath)
			if not ocr_result:
				return False
			
			ocr_method, raw_result = ocr_result
			
			# Look for "Split Fuel" button
			for item in raw_result:
				text = item[1].strip().upper()
				if "SPLIT FUEL" in text:
					if ocr_method == "easyocr" and len(item) > 0:
						try:
							bbox = item[0]
							if bbox:
								x = sum([point[0] for point in bbox]) / 4
								y = sum([point[1] for point in bbox]) / 4
								
								self.smart_click(x, y, "Split Fuel button")
								if not self.testing_mode:
									time.sleep(2)  # Wait for UI update only in production
								return True
						except:
							pass
			
			self.log("⚠️ Split Fuel button not found", "warning")
			return False
			
		except Exception as e:
			self.log(f"⚠️ Split Fuel click failed: {str(e)}", "warning")
			return False
	
	def enter_fuel_amount(self, amount):
		"""Enter fuel amount in the input field"""
		try:
			self.log(f"💰 Entering fuel amount: {amount}", "info")
			
			filepath = self.take_screenshot("fuel_amount_input.png")
			if not filepath:
				return False
			
			ocr_result = self.ocr_screenshot(filepath)
			if not ocr_result:
				return False
			
			ocr_method, raw_result = ocr_result
			
			# Look for "Total Fuel Amount" or input field
			for item in raw_result:
				text = item[1].strip().upper()
				if "TOTAL FUEL AMOUNT" in text:
					if ocr_method == "easyocr" and len(item) > 0:
						try:
							bbox = item[0]
							if bbox:
								# Look for input field below this text
								field_y = sum([point[1] for point in bbox]) / 4 + 50  # 50px below text
								field_x = sum([point[0] for point in bbox]) / 4
								
								# Click input field
								self.smart_click(field_x, field_y, "Fuel amount input field")
								
								if not self.testing_mode:
									time.sleep(1)
									# Clear field and enter amount (only in production)
									pyautogui.hotkey('ctrl', 'a')
									time.sleep(0.5)
									pyautogui.typewrite(str(amount))
									time.sleep(1)
								
								self.log(f"✅ Fuel amount {'detected' if self.testing_mode else 'entered'}: {amount}", "success")
								return True
						except:
							pass
			
			self.log("⚠️ Fuel amount input field not found", "warning")
			return False
			
		except Exception as e:
			self.log(f"⚠️ Fuel amount entry failed: {str(e)}", "warning")
			return False
	
	def select_all_mining_pools(self):
		"""Select all 10 mining pools (with scrolling to make them visible)"""
		try:
			self.log("🎱 Selecting all 10 mining pools...", "info")
			
			# First scroll down to make pools visible
			self.log("📜 Scrolling down to reveal mining pools...", "info")
			self.scroll_to_pools()
			
			filepath = self.take_screenshot("pool_selection.png")
			if not filepath:
				return False
			
			ocr_result = self.ocr_screenshot(filepath)
			if not ocr_result:
				return False
			
			ocr_method, raw_result = ocr_result
			pools_selected = 0
			
			# Look for Pool 0, Pool 1, etc.
			for pool_num in range(10):  # Pool 0-9
				pool_text = f"POOL {pool_num}"
				
				for item in raw_result:
					text = item[1].strip().upper()
					if pool_text in text:
						if ocr_method == "easyocr" and len(item) > 0:
							try:
								bbox = item[0]
								if bbox:
									x = sum([point[0] for point in bbox]) / 4
									y = sum([point[1] for point in bbox]) / 4
									
									# Click the pool
									self.smart_click(x, y, f"Pool {pool_num}")
									if not self.testing_mode:
										time.sleep(0.5)  # Brief pause between clicks only in production
									pools_selected += 1
									self.log(f"✅ {'Detected' if self.testing_mode else 'Selected'} Pool {pool_num}", "info")
									break
							except:
								pass
			
			if pools_selected >= 8:  # Allow some OCR misses
				self.log(f"✅ Successfully selected {pools_selected} pools", "success")
				return True
			else:
				self.log(f"⚠️ Only selected {pools_selected} pools", "warning")
				return False
			
		except Exception as e:
			self.log(f"⚠️ Pool selection failed: {str(e)}", "warning")
			return False
	
	def execute_mining(self):
		"""Click Approve & Mine with retry logic for the 'buggy end'"""
		try:
			self.log("🚀 Executing mining (with retry logic for buggy behavior)...", "info")
			
			max_retries = 3  # Try up to 3 times
			
			for attempt in range(1, max_retries + 1):
				self.log(f"🎯 Mining attempt {attempt}/{max_retries}...", "info")
				
				# Scroll down to ensure Approve & Mine button is visible
				self.log("📜 Scrolling to reveal Approve & Mine button...", "info")
				self.scroll_to_approve_button()
				
				filepath = self.take_screenshot(f"approve_mine_attempt_{attempt}.png")
				if not filepath:
					continue
				
				ocr_result = self.ocr_screenshot(filepath)
				if not ocr_result:
					continue
				
				ocr_method, raw_result = ocr_result
				
				# Look for "Approve & Mine" button
				approve_clicked = False
				for item in raw_result:
					text = item[1].strip().upper()
					if "APPROVE" in text and "MINE" in text:
						if ocr_method == "easyocr" and len(item) > 0:
							try:
								bbox = item[0]
								if bbox:
									x = sum([point[0] for point in bbox]) / 4
									y = sum([point[1] for point in bbox]) / 4
									
									self.smart_click(x, y, f"Approve & Mine button (attempt {attempt})")
									approve_clicked = True
									
									if not self.testing_mode:
										# Wait for SafePal popup and handle it (production only)
										time.sleep(3)
										self.click_safepal_continue()
									
									break
							except:
								pass
				
				if not approve_clicked:
					self.log(f"⚠️ Approve & Mine button not found (attempt {attempt})", "warning")
					continue
				
				# Wait and check if mining was actually processed
				self.log("⏳ Waiting to check if mining was processed...", "info")
				time.sleep(5)  # Wait for processing
				
				# Check for success or need to retry
				if self.check_mining_success():
					self.log("✅ Mining successfully processed!", "success")
					return True
				else:
					if attempt < max_retries:
						self.log(f"⚠️ Mining didn't take effect - retrying (attempt {attempt + 1})...", "warning")
						time.sleep(2)  # Wait before retry
					else:
						self.log("❌ Mining failed after all retry attempts", "error")
			
			return False
			
		except Exception as e:
			self.log(f"⚠️ Mining execution failed: {str(e)}", "warning")
			return False
	
	def check_mining_success(self):
		"""Check if mining was successfully processed by looking for success indicators"""
		try:
			self.log("🔍 Checking mining success status...", "info")
			
			# Take screenshot to check for success messages
			filepath = self.take_screenshot("mining_success_check.png")
			if not filepath:
				return False
			
			ocr_result = self.ocr_screenshot(filepath)
			if not ocr_result:
				return False
			
			ocr_method, raw_result = ocr_result
			
			# Look for success indicators
			for item in raw_result:
				text = item[1].strip().upper()
				
				# Look for green success messages or "already done" indicators
				if any(keyword in text for keyword in [
					"SUCCESS", "COMPLETED", "CONFIRMED", "DONE", "ALREADY", 
					"APPROVED", "MINED", "TRANSACTION", "PROCESSED"
				]):
					self.log(f"✅ Success indicator found: {item[1].strip()}", "success")
					return True
			
			self.log("⚠️ No success indicators found - may need retry", "warning")
			return False
			
		except Exception as e:
			self.log(f"⚠️ Mining success check failed: {str(e)}", "warning")
			return False
	
	def scroll_to_pools(self):
		"""Scroll down to make mining pools visible"""
		try:
			# Get screen center for scrolling
			screen_width, screen_height = pyautogui.size()
			center_x = screen_width // 2
			center_y = screen_height // 2
			
			# Click on the main content area to ensure it's focused
			pyautogui.click(center_x, center_y)
			time.sleep(0.5)
			
			# Scroll down to reveal pools (multiple scrolls to ensure visibility)
			for i in range(5):  # 5 scroll wheel downs
				pyautogui.scroll(-3)  # Negative = scroll down
				time.sleep(0.3)
			
			self.log("📜 Scrolled down to reveal pools", "success")
			time.sleep(1)  # Let page settle after scrolling
			
		except Exception as e:
			self.log(f"⚠️ Scrolling failed: {str(e)}", "warning")
	
	def scroll_to_approve_button(self):
		"""Scroll down to make Approve & Mine button visible"""
		try:
			# Get screen center for scrolling
			screen_width, screen_height = pyautogui.size()
			center_x = screen_width // 2
			center_y = screen_height // 2
			
			# Click on the main content area to ensure it's focused
			pyautogui.click(center_x, center_y)
			time.sleep(0.5)
			
			# Scroll down more to reveal Approve & Mine button
			for i in range(3):  # Additional scrolling for button
				pyautogui.scroll(-2)  # Negative = scroll down
				time.sleep(0.3)
			
			self.log("📜 Scrolled to reveal Approve & Mine button", "success")
			time.sleep(1)  # Let page settle after scrolling
			
		except Exception as e:
			self.log(f"⚠️ Button scroll failed: {str(e)}", "warning")
	
	def smart_click(self, x, y, element_name="element"):
		"""Smart click that either clicks or just moves mouse based on testing mode"""
		try:
			if self.testing_mode:
				# Testing mode: just move mouse to position
				pyautogui.moveTo(x, y, duration=0.5)
				self.log(f"🖱️ TESTING: Mouse moved to {element_name} at ({int(x)}, {int(y)})", "info")
				time.sleep(2)  # Hold position so user can see it
			else:
				# Production mode: actually click
				pyautogui.click(x, y)
				self.log(f"🖱️ Clicked {element_name} at ({int(x)}, {int(y)})", "success")
		except Exception as e:
			self.log(f"⚠️ Smart click failed: {str(e)}", "warning")
	
	def start_countdown_timer(self, time_remaining_text):
		"""Start countdown timer based on mining time remaining"""
		try:
			if not time_remaining_text:
				return
			
			# Parse time format like "03 H : 46 M : 12 S"
			parts = time_remaining_text.split()
			hours = 0
			minutes = 0
			
			for i, part in enumerate(parts):
				if part == "H" and i > 0:
					hours = int(parts[i-1])
				elif part == "M" and i > 0:
					minutes = int(parts[i-1])
			
			# Calculate total minutes until block ends
			total_minutes = (hours * 60) + minutes
			
			# Calculate end time
			import datetime
			now = datetime.datetime.now()
			self.current_block_end_time = now + datetime.timedelta(minutes=total_minutes)
			
			self.log(f"⏰ Block ends in {hours}h {minutes}m - Starting real-time countdown (updates every 1min)", "info")
			
			# Start timer update loop if not already running
			if not self.timer_update_running:
				self.timer_update_running = True
				self.log("🔄 Starting countdown update loop (every 1 minute)", "info")
				self.update_countdown_display()
			else:
				self.log("🔄 Timer already running - updated end time", "info")
			
		except Exception as e:
			self.log(f"⚠️ Timer setup failed: {str(e)}", "warning")
	
	def update_countdown_display(self):
		"""Update the countdown timer display every 1 minute"""
		try:
			if not self.current_block_end_time:
				self.update_timer_field("⏰ No timer data yet", "#ffaa00")
				self.timer_update_running = False
				return
			
			import datetime
			now = datetime.datetime.now()
			time_left = self.current_block_end_time - now
			
			if time_left.total_seconds() <= 0:
				# Block has ended
				self.update_timer_field("🎯 SHOWTIME! Block ended - ready for next cycle", "#ff4400")
				self.timer_update_running = False
				return
			
			# Calculate hours, minutes, and seconds remaining
			total_seconds = int(time_left.total_seconds())
			hours = total_seconds // 3600
			minutes = (total_seconds % 3600) // 60
			seconds = total_seconds % 60
			
			# Update display with real-time precision
			if hours > 0:
				timer_text = f"⏰ {hours}h {minutes}m {seconds}s till SHOWTIME"
			elif minutes > 0:
				timer_text = f"⏰ {minutes}m {seconds}s till SHOWTIME"
			else:
				timer_text = f"⏰ {seconds}s till SHOWTIME"
			
			# Change color based on time remaining
			if total_seconds <= 3600:  # Less than 1 hour (3600 seconds)
				text_color = "#ff4400"  # Red
				border_color = "#ff4400"
			elif total_seconds <= 7200:  # Less than 2 hours (7200 seconds)
				text_color = "#ffaa00"  # Orange
				border_color = "#ffaa00"
			else:
				text_color = "#44aa44"  # Green
				border_color = "#44aa44"
			
			self.update_timer_field(timer_text, text_color, border_color)
			
			# Schedule next update (configurable interval)
			if self.timer_update_running:
				self.after(self.timer_update_interval, self.update_countdown_display)
			
		except Exception as e:
			self.log(f"⚠️ Timer update failed: {str(e)}", "warning")
			self.timer_update_running = False
	
	def update_timer_field(self, text, text_color="#ffaa00", border_color="#ffaa00"):
		"""Safely update timer field without UI issues"""
		try:
			# Temporarily enable the field to update content
			self.timer_field.configure(state="normal")
			
			# Clear and insert new text
			self.timer_field.delete(0, "end")
			self.timer_field.insert(0, text)
			
			# Update colors
			self.timer_field.configure(
				text_color=text_color,
				border_color=border_color,
				state="readonly"  # Set back to readonly
			)
			
		except Exception as e:
			self.log(f"⚠️ Timer field update failed: {str(e)}", "warning")
	
	def check_wallet_connection(self):
		"""Check if Connect Wallet button is visible"""
		try:
			# Take a quick screenshot
			screenshot = pyautogui.screenshot()
			
			# Save temp screenshot
			temp_path = "temp_wallet_check.png"
			screenshot.save(temp_path)
			
			# Use OCR to check for "Connect Wallet" text
			ocr_result = self.ocr_screenshot(temp_path)
			
			if ocr_result:
				ocr_method, raw_result = ocr_result
				
				# Check if "Connect Wallet" text is found
				for item in raw_result:
					text = item[1].strip().upper()
					if "CONNECT WALLET" in text or "CONNECT" in text:
						# Clean up temp file
						try:
							os.remove(temp_path)
						except:
							pass
						return True
			
			# Clean up temp file
			try:
				os.remove(temp_path)
			except:
				pass
			
			return False
			
		except Exception as e:
			return False
	
	def connect_wallet(self):
		"""Attempt to connect SafePal wallet automatically
		
		Note: This function ALWAYS uses real clicks (even in testing mode)
		to verify the complete wallet connection flow works properly.
		"""
		try:
			self.log("🔗 Step 1: Clicking Connect Wallet button...", "info")
			
			# STEP 1: Click the Connect Wallet button first
			screenshot = pyautogui.screenshot()
			temp_path = "temp_connect_button.png"
			screenshot.save(temp_path)
			
			# Find and click Connect Wallet button
			ocr_result = self.ocr_screenshot(temp_path)
			connect_clicked = False
			
			if ocr_result:
				ocr_method, raw_result = ocr_result
				
				for item in raw_result:
					text = item[1].strip().upper()
					if "CONNECT WALLET" in text:
						if ocr_method == "easyocr" and len(item) > 0:
							try:
								bbox = item[0]
								if bbox:
									x = sum([point[0] for point in bbox]) / 4
									y = sum([point[1] for point in bbox]) / 4
									
									# Always REALLY click Connect Wallet (even in test mode)
									pyautogui.click(x, y)
									self.log("✅ REAL CLICK: Connect Wallet button (needed for popup)", "success")
									connect_clicked = True
									time.sleep(2)  # Wait for popup to open
									break
							except:
								pass
			
			# Clean up temp file
			try:
				os.remove(temp_path)
			except:
				pass
			
			if not connect_clicked:
				self.log("⚠️ Could not find Connect Wallet button", "warning")
				return
			
			# STEP 2: Now click SafePal in the popup
			self.log("🔗 Step 2: Looking for SafePal option...", "info")
			
			screenshot = pyautogui.screenshot()
			temp_path = "temp_safepal.png"
			screenshot.save(temp_path)
			
			ocr_result = self.ocr_screenshot(temp_path)
			
			if ocr_result:
				ocr_method, raw_result = ocr_result
				
				for item in raw_result:
					text = item[1].strip().upper()
					if "SAFEPAL" in text:
						if ocr_method == "easyocr" and len(item) > 0:
							try:
								bbox = item[0]
								if bbox:
									x = sum([point[0] for point in bbox]) / 4
									y = sum([point[1] for point in bbox]) / 4
									
									# Always REALLY click SafePal (even in test mode)
									pyautogui.click(x, y)
								self.log("✅ REAL CLICK: SafePal wallet (needed for popup)", "success")
								time.sleep(3)
								
								# Close SafePal popup after connection
								self.close_safepal_popup()
								
								# Mark as connected and restore window
								self.wallet_connected = True
								self.log("📈 Connection complete - restoring window...", "info")
								try:
									self.deiconify()
								except:
									pass
								break
							except:
								pass
			
			# Clean up temp file
			try:
				os.remove(temp_path)
			except:
				pass
			
		except Exception as e:
			self.log(f"⚠️ Wallet connection failed: {str(e)}", "warning")
	
	def close_safepal_popup(self):
		"""Close SafePal popup after successful connection - ALWAYS uses real clicks
		
		Note: This function ignores testing mode to properly test popup closing functionality.
		"""
		try:
			time.sleep(2)  # Give popup time to settle
			
			# Take screenshot to check for popup
			screenshot = pyautogui.screenshot()
			temp_path = "temp_popup_check.png"
			screenshot.save(temp_path)
			
			# Use OCR to detect if SafePal popup is still open
			ocr_result = self.ocr_screenshot(temp_path)
			popup_found = False
			close_button_found = False
			
			if ocr_result:
				ocr_method, raw_result = ocr_result
				
				# First check if SafePal popup is visible
				for item in raw_result:
					text = item[1].strip().upper()
					if "SAFEPAL" in text or "CONTINUE" in text:
						popup_found = True
						self.log("🔲 SafePal popup detected - closing...", "info")
						break
				
				# WALLET CONNECTION: Always use real clicks to test full functionality
				if popup_found:
					self.log("🔲 Attempting to close SafePal popup with REAL CLICKS", "info")
					# Look for X button or close elements
					for item in raw_result:
						text = item[1].strip().upper()
						if text in ["X", "×", "CLOSE"] or len(text) == 1 and ord(text) > 8000:  # Unicode X symbols
							if ocr_method == "easyocr" and len(item) > 0:
								try:
									bbox = item[0]
									if bbox:
										x = sum([point[0] for point in bbox]) / 4
										y = sum([point[1] for point in bbox]) / 4
										
										# Always REAL CLICK for wallet connection testing
										pyautogui.click(x, y)
										self.log("✅ REAL CLICK: SafePal popup X button", "success")
										time.sleep(1)
										close_button_found = True
										break
								except:
									pass
					
					# If popup exists but no X found, try fallback position
					if not close_button_found:
						screen_width, screen_height = pyautogui.size()
						close_x = screen_width // 2 + 300  # Right side of popup area
						close_y = screen_height // 2 - 150  # Top of popup area
						
						try:
							# Always REAL CLICK for wallet connection testing
							pyautogui.click(close_x, close_y)
							self.log("✅ REAL CLICK: Close button (fallback position)", "info")
						except:
							pass
				else:
					self.log("ℹ️ No SafePal popup detected - already closed", "info")
			
			# Clean up temp file
			try:
				os.remove(temp_path)
			except:
				pass
			
		except Exception as e:
			self.log(f"⚠️ Popup close check failed: {str(e)}", "warning")
	
	def goto_claim_page(self):
		"""Navigate to the claim page using typewrite (focus browser first)"""
		try:
			self.log("💰 Navigating to claim page...", "info")
			
			claim_url = "https://beta.newbitcoin.pro/claim"
			
			# Click on browser window to ensure focus (center-right of screen)
			screen_width, screen_height = pyautogui.size()
			browser_x = screen_width // 2 + 200  # Right side of center
			browser_y = screen_height // 2        # Middle height
			
			pyautogui.click(browser_x, browser_y)
			time.sleep(0.5)
			
			# Select address bar
			pyautogui.hotkey('ctrl', 'l')
			time.sleep(0.7)  # Longer wait for address bar selection
			
			# Type URL (your original working method)
			pyautogui.typewrite(claim_url)
			time.sleep(0.5)
			
			# Press Enter to navigate
			pyautogui.press('enter')
			time.sleep(2)
			
			self.log("✅ Navigated to claim page (typewrite method)", "success")
			self.log("🔍 Check browser for claim page", "info")
			
		except Exception as e:
			self.log(f"⚠️ Navigation failed: {str(e)}", "warning")
	
	def goto_staking_page(self):
		"""Navigate to the staking page using typewrite (focus browser first)"""
		try:
			self.log("💎 Navigating to staking page...", "info")
			
			staking_url = "https://beta.newbitcoin.pro/staking"
			
			# Click on browser window to ensure focus (center-right of screen)
			screen_width, screen_height = pyautogui.size()
			browser_x = screen_width // 2 + 200  # Right side of center
			browser_y = screen_height // 2        # Middle height
			
			pyautogui.click(browser_x, browser_y)
			time.sleep(0.5)
			
			# Select address bar
			pyautogui.hotkey('ctrl', 'l')
			time.sleep(0.7)  # Longer wait for address bar selection
			
			# Type URL (your original working method)
			pyautogui.typewrite(staking_url)
			time.sleep(0.5)
			
			# Press Enter to navigate
			pyautogui.press('enter')
			time.sleep(2)
			
			self.log("✅ Navigated to staking page (typewrite method)", "success")
			self.log("🔍 Check browser for staking page", "info")
			
		except Exception as e:
			self.log(f"⚠️ Staking navigation failed: {str(e)}", "warning")
	
	def goto_main_page(self):
		"""Navigate back to the main mining page using typewrite (focus browser first)"""
		try:
			self.log("⛏️ Navigating back to main mining page...", "info")
			
			main_url = "https://beta.newbitcoin.pro/"
			
			# Click on browser window to ensure focus (center-right of screen)
			screen_width, screen_height = pyautogui.size()
			browser_x = screen_width // 2 + 200  # Right side of center
			browser_y = screen_height // 2        # Middle height
			
			pyautogui.click(browser_x, browser_y)
			time.sleep(0.5)
			
			# Select address bar
			pyautogui.hotkey('ctrl', 'l')
			time.sleep(0.7)  # Longer wait for address bar selection
			
			# Type URL (your original working method)
			pyautogui.typewrite(main_url)
			time.sleep(0.5)
			
			# Press Enter to navigate
			pyautogui.press('enter')
			time.sleep(2)
			
			self.log("✅ Navigated to main mining page (typewrite method)", "success")
			self.log("🔍 Check browser for main mining page", "info")
			
		except Exception as e:
			self.log(f"⚠️ Main page navigation failed: {str(e)}", "warning")
	
	def run_completion_based_stages(self):
		"""Run stages with completion tracking - only proceed when each stage is actually done"""
		try:
			self.log("🎯 Starting completion-based stage system...", "info")
			
			# STAGE 3: Claims (only if not done)
			if not self.stage_3_claim_done:
				if self.run_stage_3_claims():
					self.stage_3_claim_done = True
					self.log("✅ STAGE 3 COMPLETE - Claims processed", "success")
				else:
					self.log("❌ STAGE 3 FAILED - Stopping automation", "error")
					self.reset_automation()
					return
			else:
				self.log("⏭️ STAGE 3 already complete - skipping claims", "info")
			
			# STAGE 4: Staking (only if Stage 3 done and Stage 4 not done)
			if self.stage_3_claim_done and not self.stage_4_staking_done:
				if self.run_stage_4_staking():
					self.stage_4_staking_done = True
					self.log("✅ STAGE 4 COMPLETE - Staking processed", "success")
				else:
					self.log("❌ STAGE 4 FAILED - Stopping automation", "error")
					self.reset_automation()
					return
			else:
				self.log("⏭️ STAGE 4 already complete - skipping staking", "info")
			
			# STAGE 5: Mining (only if Stages 3&4 done and Stage 5 not done)
			if self.stage_3_claim_done and self.stage_4_staking_done and not self.stage_5_mining_done:
				if self.run_stage_5_mining():
					self.stage_5_mining_done = True
					self.log("✅ STAGE 5 COMPLETE - Mining processed", "success")
					
					# Verify stats updated and prepare for next cycle
					if self.verify_mining_stats_updated():
						self.cycle_complete = True
						self.log("🎉 FULL CYCLE COMPLETE - Stats updated successfully!", "success")
						self.prepare_next_cycle()
					else:
						self.log("⚠️ Mining stats not updated - may need manual check", "warning")
				else:
					self.log("❌ STAGE 5 FAILED - Stopping automation", "error")
					self.reset_automation()
					return
			else:
				self.log("⏭️ STAGE 5 already complete - skipping mining", "info")
			
			# All stages complete
			if self.stage_3_claim_done and self.stage_4_staking_done and self.stage_5_mining_done:
				self.log("🏆 ALL STAGES COMPLETE - Ready for next 4-hour cycle!", "success")
				self.show_completion_message()
				self.start_hourly_cycle_management()
			
		except Exception as e:
			self.log(f"⚠️ Completion-based stages failed: {str(e)}", "warning")
			self.reset_automation()
	
	def run_stage_3_claims(self):
		"""Execute Stage 3: Claims with verification"""
		try:
			self.log("💰 STAGE 3: Testing claim page navigation + functionality", "info")
			self.log("🔗 Will test: URL typing → Login check → Data extraction → Button hover", "info")
			
			time.sleep(3)
			
			# Navigate to claim page
			self.goto_claim_page()
			
			# Verify we're actually on claim page
			if not self.verify_on_claim_page():
				self.log("❌ Not on claim page - navigation failed", "error")
				return False
			
			# Check if still logged in
			self.check_login_after_navigation()
			
			# Process claims
			self.read_claim_data()
			self.auto_claim_buttons()
			
			return True  # Stage 3 complete
			
		except Exception as e:
			self.log(f"⚠️ Stage 3 failed: {str(e)}", "warning")
			return False
	
	def run_stage_4_staking(self):
		"""Execute Stage 4: Staking with verification"""
		try:
			self.log("💎 STAGE 4: Testing staking page navigation + functionality", "info")  
			self.log("🔗 Will test: URL typing → Login check → Staking data → Claim & Stake hover", "info")
			
			time.sleep(3)
			
			# Navigate to staking page
			self.goto_staking_page()
			
			# Verify we're actually on staking page
			if not self.verify_on_staking_page():
				self.log("❌ Not on staking page - navigation failed", "error")
				return False
			
			# Check if still logged in
			self.check_login_after_navigation()
			
			# Process staking
			self.read_staking_data()
			self.auto_stake_rewards()
			
			return True  # Stage 4 complete
			
		except Exception as e:
			self.log(f"⚠️ Stage 4 failed: {str(e)}", "warning")
			return False
	
	def run_stage_5_mining(self):
		"""Execute Stage 5: Mining with verification"""
		try:
			self.log("⛏️ STAGE 5: THE HOME STRETCH - Mining Pool Automation!", "info")
			self.log("🔗 Will test: Main page return → FNBTC detection → Split Fuel → Pool selection → Approve & Mine", "info")
			
			time.sleep(3)
			
			# Navigate back to main page
			self.goto_main_page()
			
			# Verify we're actually on main page
			if not self.verify_on_main_page():
				self.log("❌ Not on main page - navigation failed", "error")
				return False
			
			# Check if still logged in
			self.check_login_after_navigation()
			
			# Read main page data
			main_screenshot = self.take_screenshot("main_final.png")
			if main_screenshot:
				mining_data = self.read_mining_data(main_screenshot)
				if mining_data:
					self.display_mining_data(mining_data)
			
			# Execute mining automation
			self.auto_setup_mining_pools()
			
			return True  # Stage 5 complete
			
		except Exception as e:
			self.log(f"⚠️ Stage 5 failed: {str(e)}", "warning")
			return False
	
	def verify_on_claim_page(self):
		"""Verify we're actually on the claim page"""
		try:
			time.sleep(2)  # Let page load
			filepath = self.take_screenshot("verify_claim_page.png")
			if not filepath:
				return False
				
			ocr_result = self.ocr_screenshot(filepath)
			if not ocr_result:
				return False
				
			ocr_method, raw_result = ocr_result
			
			# Look for claim page indicators
			claim_indicators = ["CLAIM FUEL REFUND", "CLAIM BONUS", "REFUND & BONUS DASHBOARD"]
			
			for item in raw_result:
				text = item[1].strip().upper()
				if any(indicator in text for indicator in claim_indicators):
					self.log("✅ Verified: On claim page", "success")
					return True
			
			self.log("❌ Verification failed: Not on claim page", "error")
			return False
			
		except Exception as e:
			self.log(f"⚠️ Claim page verification failed: {str(e)}", "warning")
			return False
	
	def verify_on_staking_page(self):
		"""Verify we're actually on the staking page"""
		try:
			time.sleep(2)  # Let page load
			filepath = self.take_screenshot("verify_staking_page.png")
			if not filepath:
				return False
				
			ocr_result = self.ocr_screenshot(filepath)
			if not ocr_result:
				return False
				
			ocr_method, raw_result = ocr_result
			
			# Look for staking page indicators
			staking_indicators = ["STAKING DASHBOARD", "CLAIMABLE REWARDS", "CLAIM & STAKE", "TOTAL STAKED"]
			
			for item in raw_result:
				text = item[1].strip().upper()
				if any(indicator in text for indicator in staking_indicators):
					self.log("✅ Verified: On staking page", "success")
					return True
			
			self.log("❌ Verification failed: Not on staking page", "error")
			return False
			
		except Exception as e:
			self.log(f"⚠️ Staking page verification failed: {str(e)}", "warning")
			return False
	
	def verify_on_main_page(self):
		"""Verify we're actually on the main mining page"""
		try:
			time.sleep(2)  # Let page load
			filepath = self.take_screenshot("verify_main_page.png")
			if not filepath:
				return False
				
			ocr_result = self.ocr_screenshot(filepath)
			if not ocr_result:
				return False
				
			ocr_method, raw_result = ocr_result
			
			# Look for main page indicators
			main_indicators = ["SELECT MINING POOLS", "AVAILABLE FNBTC BALANCE", "SPLIT FUEL", "NEWBTC MINING"]
			
			for item in raw_result:
				text = item[1].strip().upper()
				if any(indicator in text for indicator in main_indicators):
					self.log("✅ Verified: On main mining page", "success")
					return True
			
			self.log("❌ Verification failed: Not on main mining page", "error")
			return False
			
		except Exception as e:
			self.log(f"⚠️ Main page verification failed: {str(e)}", "warning")
			return False
	
	def verify_mining_stats_updated(self):
		"""Verify mining stats have been updated after mining setup"""
		try:
			self.log("🔄 Refreshing page to check updated stats...", "info")
			
			# Refresh the page
			pyautogui.press('f5')
			time.sleep(5)  # Wait for page reload
			
			# Take screenshot and check for updated stats
			filepath = self.take_screenshot("stats_verification.png")
			if not filepath:
				return False
				
			ocr_result = self.ocr_screenshot(filepath)
			if not ocr_result:
				return False
				
			ocr_method, raw_result = ocr_result
			
			# Look for indicators that mining was processed
			success_indicators = [
				"SELECTED POOLS:", "TOTAL FUEL:", "MINING IN PROGRESS", 
				"POOLS SELECTED", "FUEL ALLOCATED"
			]
			
			for item in raw_result:
				text = item[1].strip().upper()
				if any(indicator in text for indicator in success_indicators):
					# Check if it shows actual values (not zeros)
					if "0.0000" not in text or "NONE" not in text:
						self.log(f"✅ Stats updated: {item[1].strip()}", "success")
						return True
			
			# Alternative check: Look for reduced FNBTC balance
			available_fnbtc = self.get_available_fnbtc_balance()
			if available_fnbtc and available_fnbtc < 0.1:  # Should be reduced after mining
				self.log(f"✅ Stats updated: FNBTC balance reduced to {available_fnbtc}", "success")
				return True
			
			self.log("⚠️ Stats verification: No clear update indicators found", "warning")
			return False
			
		except Exception as e:
			self.log(f"⚠️ Stats verification failed: {str(e)}", "warning")
			return False
	
	def prepare_next_cycle(self):
		"""Prepare for the next 4-hour cycle (deprecated - now uses hourly management)"""
		try:
			self.log("🕐 Preparing for next 4-hour cycle...", "info")
			
			# Reset stage flags for next cycle
			self.stage_3_claim_done = False
			self.stage_4_staking_done = False
			self.stage_5_mining_done = False
			self.cycle_complete = False
			
			# This method is now mainly for fallback/legacy support
			# The new hourly cycle management handles production mode
			self.log("🧪 Legacy cycle preparation - ready for next manual run", "info")
			self.reset_automation()
			
		except Exception as e:
			self.log(f"⚠️ Next cycle preparation failed: {str(e)}", "warning")
			self.reset_automation()
	
	def reset_automation(self):
		"""Reset automation state and UI"""
		try:
			self.is_running = False
			button_text = "🧪 TEST MODE - HOVER ONLY" if self.testing_mode else "🚀 GO - DO EVERYTHING"
			self.go_button.configure(state="normal", text=button_text)
			self.log("🔄 Automation reset - ready for next run", "info")
			
		except Exception as e:
			self.log(f"⚠️ Reset failed: {str(e)}", "warning")
	
	def show_completion_message(self):
		"""Show completion message when all stages are done"""
		try:
			self.log("🎉 ═══════════════════════════════════════", "success")
			self.log("🎉 WELL DONE! The bot has completed its task for you this session.", "success") 
			self.log("🎉 Ready for the next 4-hour roustabout!", "success")
			self.log("🎉 ═══════════════════════════════════════", "success")
			self.log("🕐 Starting hourly timer checks - will update countdown every hour", "info")
			self.log("🔍 Monitoring for any changes or updates", "info")
			
		except Exception as e:
			self.log(f"⚠️ Completion message failed: {str(e)}", "warning")
	
	def start_hourly_cycle_management(self):
		"""Start 4-hour cycle with hourly timer updates"""
		try:
			if self.testing_mode:
				self.log("🧪 TESTING MODE: Hourly checks disabled - ready for next manual run", "info")
				self.reset_automation()
				return
			
			# Production mode: Start hourly monitoring
			self.log("🚀 PRODUCTION MODE: Starting 4-hour cycle with hourly updates", "info")
			
			# Start hourly check cycle in background thread
			threading.Thread(target=self._hourly_cycle_thread, daemon=True).start()
			
		except Exception as e:
			self.log(f"⚠️ Hourly cycle management failed: {str(e)}", "warning")
			self.reset_automation()
	
	def _hourly_cycle_thread(self):
		"""Background thread that handles hourly checks for 4 hours"""
		try:
			# 4 cycles of 1 hour each (3600 seconds) + 15 min buffer at end
			for hour in range(1, 5):  # Hours 1, 2, 3, 4
				self.log(f"💤 Sleeping for 1 hour... (Hour {hour}/4)", "info")
				time.sleep(3600)  # Sleep for 1 hour
				
				# Perform hourly check
				self.perform_hourly_check(hour)
			
			# Final 15-minute buffer
			self.log("💤 Final 15-minute buffer before next cycle...", "info")
			time.sleep(900)  # 15 minutes
			
			# Start next full cycle
			self.log("⏰ 4-hour cycle complete! Starting next full automation cycle...", "success")
			self.clear_readout_for_new_cycle()
			self.run_automation()
			
		except Exception as e:
			self.log(f"⚠️ Hourly cycle thread failed: {str(e)}", "warning")
			self.reset_automation()
	
	def perform_hourly_check(self, hour_number):
		"""Perform hourly check: grab timer and check for changes"""
		try:
			self.log(f"🕐 HOUR {hour_number} CHECK - Updating timer and checking for changes", "info")
			
			# Navigate to main page to grab current timer
			self.goto_main_page()
			time.sleep(3)  # Let page load
			
			# Take screenshot and read current mining data
			filepath = self.take_screenshot(f"hourly_check_hour_{hour_number}.png")
			if filepath:
				mining_data = self.read_mining_data(filepath)
				if mining_data:
					# Update timer display
					if 'time_remaining' in mining_data:
						self.start_countdown_timer(mining_data['time_remaining'])
						self.log(f"🕐 Hour {hour_number}: Timer updated - {mining_data['time_remaining']}", "success")
					
					# Check for significant changes
					self.check_for_changes(mining_data, hour_number)
				else:
					self.log(f"⚠️ Hour {hour_number}: Could not read mining data", "warning")
			else:
				self.log(f"⚠️ Hour {hour_number}: Could not take screenshot", "warning")
			
			remaining_hours = 4 - hour_number
			if remaining_hours > 0:
				self.log(f"✅ Hour {hour_number} check complete - {remaining_hours} hour(s) remaining", "success")
			else:
				self.log("✅ Final hourly check complete - preparing for next cycle!", "success")
				
		except Exception as e:
			self.log(f"⚠️ Hour {hour_number} check failed: {str(e)}", "warning")
	
	def check_for_changes(self, mining_data, hour_number):
		"""Check for any significant changes in mining data"""
		try:
			changes_found = []
			
			# Check block number change
			if 'block_no' in mining_data:
				changes_found.append(f"Block: {mining_data['block_no']}")
			
			# Check price changes (simplified - just log current prices)
			if 'newbtc_price' in mining_data:
				changes_found.append(f"NEWBTC: {mining_data['newbtc_price']}")
			
			if 'fnbtc_price' in mining_data:
				changes_found.append(f"FNBTC: {mining_data['fnbtc_price']}")
			
			# Check user activity
			if 'users_joined' in mining_data:
				changes_found.append(f"Users Joined: {mining_data['users_joined']}")
			
			if 'users_left' in mining_data:
				changes_found.append(f"Users Left: {mining_data['users_left']}")
			
			if changes_found:
				self.log(f"📊 Hour {hour_number} Status: {' | '.join(changes_found)}", "info")
			else:
				self.log(f"📊 Hour {hour_number}: No significant changes detected", "info")
				
		except Exception as e:
			self.log(f"⚠️ Change detection failed: {str(e)}", "warning")
	
	def clear_readout_for_new_cycle(self):
		"""Clear the activity log readout before starting new full cycle"""
		try:
			self.log("🧹 ═══════════════════════════════════════", "info")
			self.log("🧹 CLEARING READOUT FOR NEW CYCLE", "info")
			self.log("🧹 ═══════════════════════════════════════", "info")
			
			# Clear the log text widget
			if hasattr(self, 'log_text'):
				self.log_text.delete('1.0', 'end')
			
			# Show fresh startup message for new cycle
			self.log("🚀 ═══════════════════════════════════════", "header")
			self.log("🚀 STARTING NEW 4-HOUR AUTOMATION CYCLE", "header")
			self.log("🚀 ═══════════════════════════════════════", "header")
			
		except Exception as e:
			self.log(f"⚠️ Readout clearing failed: {str(e)}", "warning")
	
	def check_login_after_navigation(self):
		"""Check if still logged in after page navigation"""
		try:
			self.log("🔍 Checking login status...", "info")
			time.sleep(2)  # Give page time to fully load
			
			# Take quick screenshot to check login status
			screenshot = pyautogui.screenshot()
			temp_path = "temp_login_check.png"
			screenshot.save(temp_path)
			
			# Use OCR to check for "Connect Wallet" button
			ocr_result = self.ocr_screenshot(temp_path)
			
			if ocr_result:
				ocr_method, raw_result = ocr_result
				
				# Check if "Connect Wallet" text is found
				for item in raw_result:
					text = item[1].strip().upper()
					if "CONNECT WALLET" in text:
						self.log("⚠️ Not logged in - reconnecting wallet...", "warning")
						# Clean up temp file
						try:
							os.remove(temp_path)
						except:
							pass
						# Trigger wallet connection
						self.connect_wallet()
						return
			
			# Clean up temp file
			try:
				os.remove(temp_path)
			except:
				pass
			
			self.log("✅ Still logged in", "success")
			
		except Exception as e:
			self.log(f"⚠️ Login check failed: {str(e)}", "warning")
	
	def display_claim_data(self, claim_data):
		"""Display extracted claim data"""
		self.log("💰 Claim Data Found:", "mining")
		
		# Display FNBTC amounts
		fnbtc_count = 0
		for key, value in claim_data.items():
			if "fnbtc_amount" in key:
				fnbtc_count += 1
				self.log(f"   💎 FNBTC Amount {fnbtc_count}: {value}", "info")
		
		# Display specific claim buttons
		if "claim_fuel_refund" in claim_data:
			self.log(f"   🔘 Claim Fuel Refund Button: Available", "success")
		
		if "claim_bonus" in claim_data:
			self.log(f"   🔘 Claim Bonus Button: Available", "success")
		
		# Show total buttons found
		button_count = len([k for k in claim_data.keys() if "claim_" in k])
		if button_count > 0:
			self.log(f"   📊 Total claim buttons found: {button_count}", "info")
	
	def ocr_screenshot(self, image_path=None):
		"""OCR function using EasyOCR first, then Tesseract as backup"""
		if not image_path:
			return None
		
		# Try EasyOCR first
		if EASYOCR_AVAILABLE and is_easyocr_ready():
			try:
				reader = get_easyocr_reader()
				if reader:
					result = reader.readtext(image_path)
					return ("easyocr", result)
			except Exception as e:
				pass
		
		# Try Tesseract as backup
		try:
			image = Image.open(image_path)
			text = pytesseract.image_to_string(image)
			# Convert Tesseract result to similar format as EasyOCR
			lines = [line.strip() for line in text.split('\n') if line.strip()]
			result = [(None, line, None) for line in lines]  # Similar to EasyOCR format
			return ("tesseract", result)
		except Exception as e:
			pass
		
		return None

	def click_stake_button(self, item, ocr_method):
		"""Click the Claim & Stake button"""
		try:
			if ocr_method == "easyocr" and len(item) > 0:
				bbox = item[0]
				if bbox:
					x = sum([point[0] for point in bbox]) / 4
					y = sum([point[1] for point in bbox]) / 4
					
					self.log("🖱️ Clicking Claim & Stake button...", "info")
					self.smart_click(x, y, "Claim & Stake button")
					
					# Wait and check for SafePal popup, then click Continue
					time.sleep(3)
					self.click_safepal_continue()
					
					return True
			return False
		except Exception as e:
			self.log(f"⚠️ Stake button click failed: {str(e)}", "warning")
			return False
	
	def check_stake_success(self):
		"""Check for staking success notifications"""
		try:
			# Take screenshot to check for success messages
			filepath = self.take_screenshot("stake_success_check.png")
			if not filepath:
				return
			
			ocr_result = self.ocr_screenshot(filepath)
			if ocr_result:
				ocr_method, raw_result = ocr_result
				
				for item in raw_result:
					text = item[1].strip().upper()
					if "STAKED SUCCESSFULLY" in text or "SUCCESS" in text:
						self.log("🎉 Staking success detected!", "success")
						break
					elif "VIEW ON BSCSCAN" in text:
						self.log("🔗 Staking transaction confirmed on BSC", "success")
						break
		except Exception as e:
			self.log(f"⚠️ Stake success check failed: {str(e)}", "warning")
	
	def display_staking_data(self, staking_data):
		"""Display extracted staking data"""
		self.log("💎 Staking Data Found:", "mining")
		
		if "claimable_rewards" in staking_data:
			self.log(f"   💰 Claimable Rewards: {staking_data['claimable_rewards']}", "info")
		
		if "total_staked" in staking_data:
			self.log(f"   📊 Total Staked: {staking_data['total_staked']}", "info")
		
		if "claim_stake_button" in staking_data:
			self.log(f"   🔘 Claim & Stake Button: Available", "success")
	
	def click_safepal_continue(self):
		"""Click Continue button in SafePal popup after claim"""
		try:
			self.log("🔄 Looking for SafePal Continue button...", "info")
			time.sleep(2)  # Give popup time to appear
			
			# Take screenshot to find Continue button
			screenshot = pyautogui.screenshot()
			temp_path = "temp_continue_check.png"
			screenshot.save(temp_path)
			
			# Use OCR to find Continue button
			ocr_result = self.ocr_screenshot(temp_path)
			
			if ocr_result:
				ocr_method, raw_result = ocr_result
				
				# Look for Continue button
				for item in raw_result:
					text = item[1].strip().upper()
					if "CONTINUE" in text:
						if ocr_method == "easyocr" and len(item) > 0:
							try:
								bbox = item[0]
								if bbox:
									x = sum([point[0] for point in bbox]) / 4
									y = sum([point[1] for point in bbox]) / 4
									
									self.log("🔄 Clicking SafePal Continue button...", "info")
									self.smart_click(x, y, "SafePal Continue button")
									time.sleep(2)
									self.log("✅ SafePal Continue clicked!", "success")
									break
							except:
								pass
			
			# Clean up temp file
			try:
				os.remove(temp_path)
			except:
				pass
				
		except Exception as e:
			self.log(f"⚠️ SafePal Continue failed: {str(e)}", "warning")
	
	def has_claimable_amount(self, raw_result, button_index):
		"""Check if there's a claimable FNBTC amount near the button"""
		try:
			# Look at nearby text items for amounts > 0.0000
			search_range = 8  # Check 8 items before and after
			start_idx = max(0, button_index - search_range)
			end_idx = min(len(raw_result), button_index + search_range)
			
			found_amounts = []
			
			for i in range(start_idx, end_idx):
				text = raw_result[i][1].strip()
				if "FNBTC" in text and any(c.isdigit() for c in text):
					# Extract number and check if > 0
					import re
					numbers = re.findall(r'\d+\.?\d*', text)
					for num in numbers:
						try:
							amount = float(num)
							found_amounts.append(amount)
							if amount > 0.0000:
								self.log(f"💰 Found claimable amount: {num} FNBTC", "info")
								return True
							else:
								self.log(f"⏭️ Skipping zero amount: {num} FNBTC", "info")
						except:
							continue
			
			if not found_amounts:
				self.log("⏭️ No FNBTC amounts found near button", "info")
			
			return False
		except:
			return False
	
	def click_claim_button(self, item, ocr_method, button_name):
		"""Click a specific claim button"""
		try:
			if ocr_method == "easyocr" and len(item) > 0:
				bbox = item[0]
				if bbox:
					x = sum([point[0] for point in bbox]) / 4
					y = sum([point[1] for point in bbox]) / 4
					
					self.log(f"🖱️ Clicking {button_name} button...", "info")
					self.smart_click(x, y, f"{button_name} button")
					
					# Wait and check for SafePal popup, then click Continue
					time.sleep(3)
					self.click_safepal_continue()
					
					return True
			return False
		except Exception as e:
			self.log(f"⚠️ Button click failed: {str(e)}", "warning")
			return False
	
	def should_check_claims(self, mining_data):
		"""Check if it's time to check claims (around 3H:40M mark)"""
		if not mining_data or "time_remaining" not in mining_data:
			return False
		
		time_text = mining_data["time_remaining"]
		
		try:
			# Parse time format like "03 H : 52 M : 18 S"
			if "H" in time_text and "M" in time_text:
				# Extract hours and minutes
				parts = time_text.split()
				hours = 0
				minutes = 0
				
				for i, part in enumerate(parts):
					if part == "H" and i > 0:
						hours = int(parts[i-1])
					elif part == "M" and i > 0:
						minutes = int(parts[i-1])
				
				# Convert to total minutes
				total_minutes = (hours * 60) + minutes
				
				# Check if <= 4H:00M (240 minutes) - once blocks start moving
				claim_threshold = 4 * 60  # 240 minutes
				
				if total_minutes <= claim_threshold:
					self.log(f"⏰ Time check: {time_text} - Claims available!", "success")
					return True
				else:
					self.log(f"⏰ Time check: {time_text} - Too early for claims", "info")
					return False
		
		except Exception as e:
			self.log(f"⚠️ Time parsing failed: {str(e)}", "warning")
			return False
		
		return False
	
	def is_mining_time(self, text):
		"""Check if text looks like mining time format"""
		text = text.strip()
		
		# Look for mining time patterns: "00 H : 37 M : 56 S"
		if "H :" in text and "M :" in text and "S" in text:
			return True
		
		# Look for other mining time patterns with hours/minutes
		if ("H" in text and "M" in text and len(text) > 8):
			# Must have numbers and not be system time (AM/PM)
			if any(c.isdigit() for c in text) and "AM" not in text and "PM" not in text:
				return True
		
		# Avoid system time formats
		if "AM" in text or "PM" in text or text.count(":") == 1:
			return False
		
		return False
	
	def read_mining_data(self, screenshot_path):
		"""Read mining data from screenshot using OCR"""
		if not os.path.exists(screenshot_path):
			return None
		
		try:
			# Use OCR to read screenshot (EasyOCR first, then Tesseract)
			ocr_result = self.ocr_screenshot(screenshot_path)
			
			if not ocr_result:
				return None
			
			ocr_method, raw_result = ocr_result
			self.log(f"🔍 Using {ocr_method.upper()}", "info")
			
			# Extract text from OCR result
			text_data = []
			for item in raw_result:
				text_data.append(item[1])  # item[1] contains the text
			
			# Look for mining data - vertical layout (label above value)
			mining_data = {}
			
			for i, text in enumerate(text_data):
				text = text.strip()
				
				# Block No - look for #1710 pattern
				if text.startswith("#") and text[1:].isdigit():
					mining_data["block_no"] = text
				
				# Time Remaining - SMART filtering for mining time vs system time
				elif self.is_mining_time(text):
					mining_data["time_remaining"] = text
				
				# NEWBTC Price - look for big numbers (price format)
				elif text.replace(".", "").isdigit() and len(text) > 6:
					mining_data["newbtc_price"] = f"${text}"
				
				# FNBTC Price - look for S followed by numbers (OCR mistake)
				elif text.startswith("S") and text[1:].replace(".", "").isdigit():
					clean_price = text.replace("S", "$")
					mining_data["fnbtc_price"] = clean_price
				
				# Available FNBTC Balance
				elif "Available FNBTC Balance:" in text:
					# Next item should be the balance
					if i + 1 < len(text_data):
						balance = text_data[i + 1].strip()
						mining_data["fnbtc_balance"] = balance
				
				# Available NEWBTC Balance  
				elif "Available NEWBTC Balance:" in text:
					if i + 1 < len(text_data):
						balance = text_data[i + 1].strip()
						mining_data["newbtc_balance"] = balance
				
				# Users Joined This Block
				elif "Users Joined This Block:" in text:
					if i + 1 < len(text_data):
						users = text_data[i + 1].strip()
						mining_data["users_joined"] = users
				
				# Users Left This Block
				elif "Users Left This Block:" in text:
					if i + 1 < len(text_data):
						users = text_data[i + 1].strip()
						mining_data["users_left"] = users
			
			return mining_data if mining_data else None
			
		except Exception as e:
			self.log(f"❌ OCR reading failed: {str(e)}", "error")
			return None
	
	def auto_stake_rewards(self):
		"""Automatically stake available rewards if > 0"""
		try:
			self.log("💎 Auto-staking available rewards...", "info")
			time.sleep(2)  # Let page settle
			
			# Take screenshot for staking button detection
			filepath = self.take_screenshot("staking_buttons.png")
			if not filepath:
				return
			
			# Use OCR to find staking elements
			ocr_result = self.ocr_screenshot(filepath)
			if not ocr_result:
				self.log("⚠️ Could not read staking buttons", "warning")
				return
			
			ocr_method, raw_result = ocr_result
			stakes_made = 0
			
			# Look for claimable rewards and stake button
			claimable_amount = 0
			stake_button_item = None
			
			for i, item in enumerate(raw_result):
				text = item[1].strip().upper()
				
				# Check for claimable rewards amount
				if "NEWBTC" in text and any(c.isdigit() for c in text):
					# Check if this is claimable rewards (not total staked)
					nearby_text = " ".join([raw_result[j][1].upper() for j in range(max(0, i-3), min(len(raw_result), i+3))])
					if "CLAIMABLE" in nearby_text and "REWARDS" in nearby_text:
						import re
						numbers = re.findall(r'\d+\.?\d*', text)
						for num in numbers:
							try:
								amount = float(num)
								claimable_amount = amount  # Always set the amount found
								if amount > 0:
									self.log(f"💰 Found claimable rewards: {num} NEWBTC", "info")
								else:
									self.log(f"💰 Found claimable rewards: {num} NEWBTC (zero amount)", "info")
								break  # Take the first valid amount found
							except:
								continue
				
				# Check for claim & stake button
				elif "CLAIM" in text and "STAKE" in text:
					stake_button_item = item
			
			# Click stake button if there are claimable rewards >= 0.01 NEWBTC
			minimum_stake_threshold = 0.01  # Only stake if >= 0.01 NEWBTC
			
			if claimable_amount >= minimum_stake_threshold and stake_button_item:
				self.log(f"💎 Amount {claimable_amount} >= {minimum_stake_threshold} NEWBTC - staking...", "info")
				if self.click_stake_button(stake_button_item, ocr_method):
					stakes_made += 1
					time.sleep(3)  # Wait for transaction
			elif claimable_amount > 0 and claimable_amount < minimum_stake_threshold:
				self.log(f"⏭️ Amount {claimable_amount} < {minimum_stake_threshold} NEWBTC - too small to stake", "info")
			elif claimable_amount <= 0:
				self.log(f"ℹ️ No stakeable rewards: {claimable_amount} NEWBTC (below {minimum_stake_threshold} threshold)", "info")
			else:
				self.log(f"⚠️ Claim & Stake button not found (rewards: {claimable_amount} NEWBTC)", "warning")
			
			# Summary of staking decision
			self.log(f"📊 Staking Summary: {claimable_amount} NEWBTC detected, threshold: {minimum_stake_threshold} NEWBTC", "info")
			
			if stakes_made > 0:
				self.log(f"✅ Successfully staked {stakes_made} reward(s)!", "success")
				# Wait and check for success notifications
				time.sleep(2)
				self.check_stake_success()
			else:
				self.log("⏸️ No staking performed this round", "info")
			
		except Exception as e:
			self.log(f"⚠️ Auto-stake failed: {str(e)}", "warning")
	
	def take_screenshot(self, custom_name=None):
		"""Take screenshot with page-specific naming"""
		try:
			# Create images folder if it doesn't exist
			images_folder = "images"
			if not os.path.exists(images_folder):
				os.makedirs(images_folder)
			
			# Detect current page and generate appropriate filename
			if custom_name:
				filename = custom_name
			else:
				page_type = self.detect_current_page()
				timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
				filename = f"{page_type}_{timestamp}.png"
			
			filepath = os.path.join(images_folder, filename)
			
			# Take screenshot
			screenshot = pyautogui.screenshot()
			screenshot.save(filepath)
			
			self.log(f"📸 Screenshot saved: {filename}", "success")
			return filepath
			
		except Exception as e:
			self.log(f"❌ Screenshot failed: {str(e)}", "error")
			return None
	
	def read_staking_data(self):
		"""Read staking page data using OCR"""
		try:
			self.log("💎 Reading staking page data...", "info")
			time.sleep(2)  # Give page time to fully load
			
			# Take screenshot with staking page naming
			filepath = self.take_screenshot("staking.png")
			if not filepath:
				return
			
			# Use OCR to read staking data
			ocr_result = self.ocr_screenshot(filepath)
			
			if ocr_result:
				ocr_method, raw_result = ocr_result
				self.log(f"🔍 Using {ocr_method.upper()} for staking data", "info")
				
				# Extract staking data
				staking_data = {}
				
				for i, item in enumerate(raw_result):
					text = item[1].strip()
					text_upper = text.upper()
					
					# Look for claimable rewards
					if "NEWBTC" in text and any(c.isdigit() for c in text):
						if "CLAIMABLE" in " ".join([raw_result[j][1].upper() for j in range(max(0, i-3), min(len(raw_result), i+3))]):
							staking_data["claimable_rewards"] = text
					
					# Look for total staked
					elif "STAKED" in " ".join([raw_result[j][1].upper() for j in range(max(0, i-2), min(len(raw_result), i+3))]) and "NEWBTC" in text:
						staking_data["total_staked"] = text
					
					# Look for claim & stake button
					elif "CLAIM" in text_upper and "STAKE" in text_upper:
						staking_data["claim_stake_button"] = text
				
				# Display staking data
				if staking_data:
					self.display_staking_data(staking_data)
				else:
					self.log("⚠️ No staking data found", "warning")
			
		except Exception as e:
			self.log(f"⚠️ Staking data reading failed: {str(e)}", "warning")
	
	def check_claim_success(self):
		"""Check for claim success notifications"""
		try:
			# Take screenshot to check for success messages
			filepath = self.take_screenshot("claim_success_check.png")
			if not filepath:
				return
			
			ocr_result = self.ocr_screenshot(filepath)
			if ocr_result:
				ocr_method, raw_result = ocr_result
				
				for item in raw_result:
					text = item[1].strip().upper()
					if "CLAIMED SUCCESSFULLY" in text or "SUCCESS" in text:
						self.log("🎉 Claim success detected!", "success")
						break
					elif "VIEW ON BSCSCAN" in text:
						self.log("🔗 Transaction confirmed on BSC", "success")
						break
		except Exception as e:
			self.log(f"⚠️ Success check failed: {str(e)}", "warning")
	
	def auto_claim_buttons(self):
		"""Automatically click available claim buttons"""
		try:
			self.log("🎯 Auto-claiming available rewards...", "info")
			time.sleep(2)  # Let page settle
			
			# Take screenshot for claim button detection
			filepath = self.take_screenshot("claim_buttons.png")
			if not filepath:
				return
			
			# Use OCR to find claim buttons
			ocr_result = self.ocr_screenshot(filepath)
			if not ocr_result:
				self.log("⚠️ Could not read claim buttons", "warning")
				return
			
			ocr_method, raw_result = ocr_result
			claims_made = 0
			
			# Look for claimable amounts and buttons
			for i, item in enumerate(raw_result):
				text = item[1].strip().upper()
				
				# Check for claim buttons with available amounts
				if "CLAIM FUEL REFUND" in text:
					# Check if there's a claimable amount nearby
					if self.has_claimable_amount(raw_result, i):
						self.log("💰 Found claimable Fuel Refund", "info")
						if self.click_claim_button(item, ocr_method, "CLAIM FUEL REFUND"):
							claims_made += 1
							time.sleep(3)  # Wait for transaction
				
				elif "CLAIM BONUS" in text:
					# Check if there's a claimable amount nearby
					if self.has_claimable_amount(raw_result, i):
						self.log("💰 Found claimable Bonus", "info")
						if self.click_claim_button(item, ocr_method, "CLAIM BONUS"):
							claims_made += 1
							time.sleep(3)  # Wait for transaction
			
			if claims_made > 0:
				self.log(f"✅ Successfully claimed {claims_made} reward(s)!", "success")
				# Wait and check for success notifications
				time.sleep(2)
				self.check_claim_success()
			else:
				self.log("ℹ️ No claimable rewards found", "info")
			
		except Exception as e:
			self.log(f"⚠️ Auto-claim failed: {str(e)}", "warning")
	
	def read_claim_data(self):
		"""Read claim page data using OCR"""
		try:
			self.log("💰 Reading claim page data...", "info")
			time.sleep(2)  # Give page time to fully load
			
			# Take screenshot with claim page naming
			filepath = self.take_screenshot("claim.png")
			
			# Use OCR to read claim data
			ocr_result = self.ocr_screenshot(filepath)
			
			if ocr_result:
				ocr_method, raw_result = ocr_result
				self.log(f"🔍 Using {ocr_method.upper()} for claim data", "info")
				
				# Extract text from OCR result
				text_data = []
				for item in raw_result:
					text_data.append(item[1])
				
				# Parse claim data
				claim_data = {}
				
				for i, text in enumerate(text_data):
					text = text.strip()
					text_upper = text.upper()
					
					# Look for FNBTC amounts (refunded fuel, bonus, etc.)
					if "FNBTC" in text and any(c.isdigit() for c in text):
						# Clean up the amount
						if "." in text:
							claim_data[f"fnbtc_amount_{len(claim_data)}"] = text
					
					# Look for specific claim buttons
					elif "CLAIM FUEL REFUND" in text_upper:
						claim_data["claim_fuel_refund"] = text
					elif "CLAIM BONUS" in text_upper:
						claim_data["claim_bonus"] = text
					elif "CLAIM" in text_upper and "FUEL" in text_upper:
						claim_data["claim_fuel_refund"] = text
					elif "CLAIM" in text_upper and "BONUS" in text_upper:
						claim_data["claim_bonus"] = text
				
				# Display claim data
				if claim_data:
					self.display_claim_data(claim_data)
				else:
					self.log("⚠️ No claim data found", "warning")
			
		except Exception as e:
			self.log(f"⚠️ Claim data reading failed: {str(e)}", "warning")
	
	def detect_current_page(self):
		"""Detect which NewBTC page we're currently on"""
		try:
			# Take a quick screenshot to analyze
			temp_screenshot = pyautogui.screenshot()
			temp_path = "temp_page_detect.png"
			temp_screenshot.save(temp_path)
			
			# Use OCR to detect page content
			ocr_result = self.ocr_screenshot(temp_path)
			page_type = "main"  # Default
			pdb.set_trace()
			if ocr_result:
				ocr_method, raw_result = ocr_result
				text_content = " ".join([item[1].strip().upper() for item in raw_result])
				
				# Check for main mining page indicators FIRST (most specific)
				if any(keyword in text_content for keyword in ["SELECT MINING POOLS", "AVAILABLE FNBTC BALANCE", "SPLIT FUEL"]):
					page_type = "main"
					self.log("🔍 Detected: Main mining page", "info")
				# Check for claim page indicators (specific claim page only)
				elif any(keyword in text_content for keyword in ["REFUND & BONUS DASHBOARD", "CLAIM FUEL REFUND", "PARTICIPATION BONUS"]):
					page_type = "claim"
					self.log("🔍 Detected: Claim page", "info")
				# Check for staking page indicators
				elif any(keyword in text_content for keyword in ["STAKING DASHBOARD", "CLAIMABLE REWARDS", "CLAIM & STAKE"]):
					page_type = "staking"
					self.log("🔍 Detected: Staking page", "info")
				# Fallback: check less specific mining indicators
				elif any(keyword in text_content for keyword in ["NEWBTC MINING", "CURRENT BLOCK STATUS"]):
					page_type = "main"
					self.log("🔍 Detected: Main mining page (fallback)", "info")
			
			# Clean up temp file
			try:
				os.remove(temp_path)
			except:
				pass
			
			return page_type
			
		except Exception as e:
			self.log(f"⚠️ Page detection failed: {str(e)}", "warning")
			return "main"  # Default fallback
	
	def display_mining_data(self, mining_data):
		"""Display extracted mining data"""
		self.log("📊 Mining Data Found:", "mining")
		
		if "block_no" in mining_data:
			self.log(f"   Block No: {mining_data['block_no']}", "info")
		
		if "time_remaining" in mining_data:
			self.log(f"   Time Remaining: {mining_data['time_remaining']}", "info")
			# Start countdown timer with this data
			self.start_countdown_timer(mining_data['time_remaining'])
		
		if "newbtc_price" in mining_data:
			self.log(f"   NEWBTC Price: {mining_data['newbtc_price']}", "info")
		
		if "fnbtc_price" in mining_data:
			self.log(f"   FNBTC Price: {mining_data['fnbtc_price']}", "info")
		
		# Mining Pool Data
		if "fnbtc_balance" in mining_data:
			self.log(f"   💰 Available FNBTC: {mining_data['fnbtc_balance']}", "info")
		
		if "newbtc_balance" in mining_data:
			self.log(f"   💰 Available NEWBTC: {mining_data['newbtc_balance']}", "info")
		
		if "users_joined" in mining_data:
			self.log(f"   👥 Users Joined: {mining_data['users_joined']}", "info")
		
		if "users_left" in mining_data:
			self.log(f"   👥 Users Left: {mining_data['users_left']}", "info")
	
	def _automation_thread(self):
		"""Main automation thread - Screenshot + OCR only"""
		self.log("🚀 Taking screenshot...", "info")
		
		# Move app to top left corner, down 100px to avoid address bar
		self.geometry("600x500+0+100")
		
		# Minimize app
		self.iconify()
		time.sleep(1)
		
		# Take screenshot
		screenshot_path = self.take_screenshot()
		
		# Un-minimize app
		self.deiconify()
		self.lift()
		self.attributes('-topmost', True)
		self.attributes('-topmost', False)
		
		# Read screenshot with OCR
		if screenshot_path:
			mining_data = self.read_mining_data(screenshot_path)
			if mining_data:
				self.display_mining_data(mining_data)
		
		# Check if we're already on claim page or should navigate to it
		current_page = self.detect_current_page()
		
		if current_page == "claim":
			self.log("🎯 Already on claim page - processing claims...", "info")
			# Read claim page data and auto-claim
			self.read_claim_data()
			# Automatically click available claim buttons
			self.auto_claim_buttons()
		elif current_page == "staking":
			self.log("💎 Already on staking page - processing staking...", "info")
			# Read staking page data and auto-stake
			self.read_staking_data()
			# Automatically click stake buttons if rewards available
			self.auto_stake_rewards()
		elif current_page == "main":
			self.log("📍 Already on main mining page - extracting data...", "info")
			# Read mining data 
			mining_data = self.read_mining_data(screenshot_path)
			if mining_data:
				self.display_mining_data(mining_data)
			
			# Start the completion-based stage system
			if self.testing_mode:
				self.log("🧪 STAGE 1 COMPLETE - Data extracted, timer started", "success")
				self.log("🔌 STAGE 2: Wallet monitor will auto-stop when connected + deiconify", "info")
				self.run_completion_based_stages()
				return  # Stop here - All stages complete
			else:
				# Production: Continue with mining automation
				self.auto_setup_mining_pools()
		else:
			# Check if we should go to claim page (only at 4H:00M mark)
			should_check_claims = self.should_check_claims(mining_data)
			
			if should_check_claims:
				# Small pause before going to claim page
				self.log("⏱️ Pausing before claim page...", "info")
				time.sleep(3)
				
				# Automatically navigate to claim page
				self.goto_claim_page()
				
				# Check if still logged in after navigation
				self.check_login_after_navigation()
				
				# Read claim page data and auto-claim
				self.read_claim_data()
				
				# Automatically click available claim buttons
				self.auto_claim_buttons()
			else:
				self.log("⏱️ Too early for claims - skipping claim page", "info")
		
		self.log("⏸️ Automation cycle complete - awaiting next trigger", "info")
		
		# Reset button
		self.is_running = False
		button_text = "🧪 TEST MODE - HOVER ONLY" if self.testing_mode else "🚀 GO - DO EVERYTHING"
		self.go_button.configure(state="normal", text=button_text)
	
	def wallet_monitor_thread(self):
		"""Background thread to monitor wallet connection"""
		while self.wallet_monitor_running:
			try:
				time.sleep(10)  # Check every 10 seconds
				
				if not self.wallet_monitor_running:
					break
				
				# Stop monitoring if already connected
				if self.wallet_connected:
					self.log("😴 Wallet already connected - monitor going to sleep", "info")
					self.wallet_monitor_running = False
					break
				
				# Check if wallet connection is needed
				needs_connection = self.check_wallet_connection()
				
				if needs_connection:
					self.log("🔗 Connect Wallet button detected", "warning")
					self.connect_wallet()
				else:
					# Successfully connected! Stop monitoring and restore window
					self.log("✅ Wallet connected successfully - stopping monitor", "success")
					self.log("📈 Restoring app window...", "info")
					
					# Mark as connected and restore window
					self.wallet_connected = True
					try:
						self.deiconify()
					except:
						pass
					
					# Stop the wallet monitor loop
					self.wallet_monitor_running = False
					break
				
			except Exception as e:
				pass  # Silent fail for background thread
		
		self.log("🔍 Wallet monitor stopped", "info")
	
	def start_wallet_monitor(self):
		"""Start wallet connection monitor in background"""
		if not self.wallet_monitor_running:
			self.wallet_monitor_running = True
			threading.Thread(target=self.wallet_monitor_thread, daemon=True).start()
			self.log("🔍 Wallet monitor started", "info")
			
	def run_automation(self):
		""" Start the automation process """
		if self.is_running:
			self.log("⚠️ Automation already running", "warning")
			return
			
		self.is_running = True
		self.go_button.configure(state="disabled", text="🔄 Running Full Automation...")
		self.status_label.configure(text="Full automation in progress...", text_color="#ffaa00")
		
		""" STAGE 2: Enable wallet monitor for Connect Wallet testing """
		self.wallet_connected = False  # Reset connection status for new run
		
		# Reset stage completion flags for new run
		self.stage_3_claim_done = False
		self.stage_4_staking_done = False
		self.stage_5_mining_done = False
		self.cycle_complete = False
		
		self.start_wallet_monitor()
		self.log("🔌 STAGE 2: Wallet monitor ENABLED (auto-stops when connected)", "info")
		# Start automation in separate thread
		threading.Thread(target=self._automation_thread, daemon=True).start()
		
	def enable_go_button(self):
		"""Enable the GO button when EasyOCR is ready"""
		button_text = "🧪 TEST MODE - HOVER ONLY" if self.testing_mode else "🚀 GO - DO EVERYTHING"
		status_text = "Ready for testing (mouse hover only)" if self.testing_mode else "Ready for full automation"
		button_color = "#ff8800" if self.testing_mode else "#00aa00"
		hover_color = "#ffaa00" if self.testing_mode else "#00cc00"
		
		self.go_button.configure(
			text=button_text,
			state="normal",
			fg_color=button_color,
			hover_color=hover_color
		)
		self.status_label.configure(
			text=status_text,
			text_color="#888888"
		)
	
	def check_easyocr_status(self):
		"""Check EasyOCR status periodically"""
		if EASYOCR_AVAILABLE and is_easyocr_ready():
			self.log("🔍 EasyOCR ready!", "success")
			self.enable_go_button()
		else:
			# Check again in 2 seconds
			self.after(2000, self.check_easyocr_status)
			
	def display_startup_info(self):
		"""Display startup information"""
		self.log("🚀 Ready to go!", "success")
		
		# Testing mode notification
		if self.testing_mode:
			self.log("🧪 TESTING MODE ENABLED - Mouse hover only, no actual clicks", "warning")
			self.log("👀 Watch mouse movements to verify element detection", "info")
		
		# Check EasyOCR status
		if EASYOCR_AVAILABLE:
			if is_easyocr_ready():
				self.log("🔍 EasyOCR ready", "success")
				self.enable_go_button()
			else:
				self.log("🔍 EasyOCR loading...", "info")
				self.check_easyocr_status()
				
	def log(self, message, msg_type="info"):
		"""Add styled message to activity log - tkinter.Text with emoji support"""
		try:
			if hasattr(self, 'log_text'):
				if STYLED_TEXT_AVAILABLE:
					# Use professional styled append_text function (handles colors + emojis)
					timestamp = time.strftime("[%H:%M:%S]")
					full_message = f"{timestamp} {message}"
					append_text(self.log_text, full_message, msg_type)
				else:
					# Fallback with emoji icons
					timestamp = time.strftime("[%H:%M:%S]")
					
					# Color coding icons for different message types
					if msg_type == "success":
						icon = "✅"
					elif msg_type == "error": 
						icon = "❌"
					elif msg_type == "warning":
						icon = "⚠️"
					elif msg_type == "ai":
						icon = "🤖"
					elif msg_type == "mining":
						icon = "⛏️"
					elif msg_type == "info":
						icon = "ℹ️"
					elif msg_type == "header":
						icon = "🚀"
					else:
						icon = "📝"
					
					formatted_message = f"{timestamp} {icon} {message}\n"
					self.log_text.insert(tkinter.END, formatted_message)
				
				# Auto-scroll to bottom
				self.log_text.see(tkinter.END)
				self.update()
		except Exception as e:
			pass
			
	def setup_activity_log(self):
		"""Create activity log (only in main frame)"""
		if self.current_view != "main":
			return
			
		log_frame = customtkinter.CTkFrame(self.content_frame)
		log_frame.pack(pady=10, fill="both", expand=True)
		
		log_label = customtkinter.CTkLabel(
			log_frame,
			text="📊 Status & Activity Log",
			font=customtkinter.CTkFont(family="Verdana", size=14, weight="bold")
		)
		log_label.pack(pady=5)
		
		# Text frame for proper scrollbar layout
		text_frame = tkinter.Frame(log_frame, bg="#212121")
		text_frame.pack(pady=5, padx=10, fill="both", expand=True)
		
		# Create tkinter Text widget (handles emojis properly)
		self.log_text = tkinter.Text(
			text_frame,
			height=12,
			width=70,
			bg="#2b2b2b",
			fg="white",
			font=("Verdana", 11, "bold"),
			wrap=tkinter.WORD,
			insertbackground="white"
		)
		
		# Create scrollbar
		scrollbar = tkinter.Scrollbar(
			text_frame,
			orient="vertical",
			command=self.log_text.yview,
			bg="#404040",
			troughcolor="#2b2b2b",
			activebackground="#666666"
		)
		
		# Configure text widget to use scrollbar
		self.log_text.configure(yscrollcommand=scrollbar.set)
		
		# Pack widgets - scrollbar first (on right), then text
		scrollbar.pack(side="right", fill="y")
		self.log_text.pack(side="left", fill="both", expand=True)
		
	def setup_main_interface(self):
		"""Setup the main interface with GO button and log"""
		
		# Buttons frame
		buttons_frame = customtkinter.CTkFrame(self.content_frame)
		buttons_frame.pack(pady=20, fill="x")
		
		# GO Button - Does everything automatically
		initial_text = "⏳ Loading EasyOCR..." if not self.testing_mode else "🧪 TESTING MODE - Loading EasyOCR..."
		self.go_button = customtkinter.CTkButton(
			buttons_frame,
			text=initial_text,
			width=300,
			height=50,
			font=customtkinter.CTkFont(size=16, weight="bold"),
			command=self.run_automation,
			fg_color="#666666",
			hover_color="#666666",
			state="disabled"
		)
		self.go_button.pack(pady=10)
		
		# Status info
		self.status_label = customtkinter.CTkLabel(
			buttons_frame,
			text="Waiting for EasyOCR to load...",
			font=customtkinter.CTkFont(size=12),
			text_color="#ffaa00"
		)
		self.status_label.pack(pady=5)
		
		# Countdown Timer Display (read-only entry field for stability)
		self.timer_field = customtkinter.CTkEntry(
			buttons_frame,
			width=350,
			height=45,
			font=customtkinter.CTkFont(size=18, weight="bold"),
			justify="center",
			state="readonly",
			fg_color="#2b2b2b",
			text_color="#ffaa00",
			border_width=3,
			border_color="#ffaa00"
		)
		self.timer_field.pack(pady=10)
		self.timer_field.insert(0, "⏰ No timer data yet")
		
		# Timer state variables
		self.current_block_end_time = None
		self.timer_update_running = False
		self.timer_update_interval = 60000  # 1 minute in milliseconds (smooth updates!)
		# Timing options: 30000 = 30sec, 60000 = 1min, 300000 = 5min, 600000 = 10min
		
		# Setup activity log
		self.setup_activity_log()
		
	def setup_ui(self):
		"""Create the simple user interface"""
		
		# Title
		self.title_label = customtkinter.CTkLabel(
			self,
			text="🚀 NewBTC Auto Run Bot - V3 Simple",
			font=customtkinter.CTkFont(family="Verdana", size=20, weight="bold")
		)
		self.title_label.pack(pady=20)	

		# Subtitle
		self.subtitle_label = customtkinter.CTkLabel(
			self,
			text="Full Automation | Mining Data + Claim Page",
			font=customtkinter.CTkFont(family="Verdana", size=12),
			text_color="#888888"
		)
		self.subtitle_label.pack(pady=5)	

		# Content frame
		self.content_frame = customtkinter.CTkFrame(self)
		self.content_frame.pack(pady=10, padx=20, fill="both", expand=True)
		
		# Setup main interface
		self.setup_main_interface()
		
if __name__ == "__main__":
	app = NewBTCMiningWindow()
	app.mainloop()
	
""" Main Window """