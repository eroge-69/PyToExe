
# ✅ STEP 1: Install necessary packages
# Run this in your terminal before executing this script:
# pip install pytesseract opencv-python-headless
# sudo apt-get install -y tesseract-ocr

# ✅ STEP 2: Import libraries
import cv2
import pytesseract
import re
import tkinter as tk
from tkinter import filedialog

# ✅ STEP 3: Upload the image using file picker
print("📤 Please select the image containing the duty schedule.")
root = tk.Tk()
root.withdraw()
file_path = filedialog.askopenfilename(title="Select Image", filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp")])

if not file_path:
    print("❌ No file selected.")
    exit()

# ✅ STEP 4: Process and extract text
image = cv2.imread(file_path)

if image is None:
    print("❌ Failed to load image.")
else:
    print(f"✅ Image '{file_path}' loaded successfully.")

    # Convert to grayscale for better OCR
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Run Tesseract OCR
    text = pytesseract.image_to_string(gray)

    print("\n📝 Extracted Text:\n")
    print(text)

    # ✅ STEP 5: Try to find the roster date
    date_match = re.search(r"Saturday.*\d{4}", text)
    roster_date = date_match.group(0) if date_match else "Not Found"

    # ✅ STEP 6: Try to detect duty times from the header
    time_match = re.findall(r"\((.*?)\)", text)
    day_shift = time_match[0] if len(time_match) > 0 else "Not Found"
    night_shift = time_match[1] if len(time_match) > 1 else "Not Found"

    # ✅ STEP 7: Find Dr. Shahariar’s row and station
    pattern = r"(.*?)\s+Dr\.?\s*Shahariar\s*19611"
    match = re.search(pattern, text, re.IGNORECASE)

    if match:
        # Try to get the station name
        line = match.group(1).strip()
        station = line if line else "Unknown"

        # Guess shift based on position
        line_number = text[:match.start()].count("\n")
        if "Night" in text.split("\n")[line_number]:
            shift = "Night"
            duty_time = night_shift
        else:
            shift = "Day"
            duty_time = day_shift

        # ✅ Nicely formatted output
        print("\n✅ Duty Details Found:\n")
        print(f"📅 Date: {roster_date}")
        print(f"👨‍⚕️ Name: Dr. Shahariar")
        print(f"🆔 ID: 19611")
        print(f"📍 Station: {station}")
        print(f"⏰ Duty Time: {shift} ({duty_time})")

    else:
        print("\n❗Could not find Dr. Shahariar 19611 in the roster.")
