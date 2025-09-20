import pyautogui
import pygetwindow as gw
from PIL import Image
import time
import requests
import base64

def capture_quotex_tab():
    browser_window = None
    for window in gw.getWindowsWithTitle("trading"):
        if window.visible:
            browser_window = window
            break

    if not browser_window:
        print("Quotex tab not found in any open browser.")
        return
    browser_window.activate()
    time.sleep(2)
    screenshot = pyautogui.screenshot()
    screenshot = screenshot.convert("RGB")
    screenshot.save("ss.png", "PNG")

    print("Screenshot of Quotex tab saved as ss.png")
capture_quotex_tab()
url = "https://text.pollinations.ai/openai"
headers = {"Content-Type": "application/json"}

def encode_image_base64(image_path):
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    except FileNotFoundError:
        print(f"Error: Image file not found at {image_path}")
        return None

def analyze_local_image(image_path, question=""):
    base64_image = encode_image_base64(image_path)
    if not base64_image:
        return None
    
    image_format = image_path.split('.')[-1].lower()
    if image_format not in ['jpeg', 'jpg', 'png', 'gif', 'webp']:
        print(f"Warning: Potentially unsupported image format '{image_format}'. Assuming jpeg.")
        image_format = 'jpeg'

    payload = {
        "model": "gpt-4-vision-preview",
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": question},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/{image_format};base64,{base64_image}"
                        }
                    }
                ]
            }
        ],
        "max_tokens": 300
    }
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error analyzing local image: {e}")
        return None

question_text = """PAIR: [Asset]  
TREND: [UP/DOWN/SIDEWAYS] [🟢/🔴/⚫️]  
CONFIDENCE: [High/Medium/Low]  
SUPPORT_RESISTANCE: [List key SR levels]  
ROUND_NUMBER: [Important round numbers visible]  
PATTERN: [Key candlestick pattern]  
TRADE_REASON: [One concise professional reason for this trade idea]  

Focus on clear, structured professional output with no extra words."""

result_local = analyze_local_image('ss.png', question=question_text)
if result_local:
    print("Chart Analysis:\n", result_local['choices'][0]['message']['content'])
