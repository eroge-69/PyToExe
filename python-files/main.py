import asyncio
import json
import time
import base64
import webbrowser
import customtkinter as ctk
from playwright.async_api import async_playwright

# === Global Status Updater ===
def update_status(msg, success=False, error=False):
    status_label.configure(
        text=msg,
        text_color="green" if success else "red" if error else "white"
    )
    app.update_idletasks()

# === Extract final link from page ===
async def extract_link_from_page(page):
    await page.wait_for_timeout(2000)
    update_status("⏳ Waiting for JavaScript execution...")
    current_time = int(time.time())

    for frame in page.frames:
        try:
            raw = await frame.evaluate("window.localStorage.getItem('soralinklite')")
            if not raw:
                continue
            obj = json.loads(raw)
            for value in obj.values():
                if value.get("new") and current_time - value.get("time", 0) < 600:
                    b64_link = value.get("link")
                    if b64_link:
                        decoded = base64.b64decode(b64_link).decode()
                        return decoded
        except Exception:
            continue
    return None

# === Core Logic to Resolve Ozolink ===
async def resolve_ozolink_once(ozolink_url):
    update_status("🚀 Launching browser...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        update_status("🌐 Navigating to the URL...")
        await page.goto(ozolink_url, wait_until="domcontentloaded")

        update_status("🔁 Waiting for redirect...")
        for _ in range(15):
            await page.wait_for_timeout(1000)
            if "ozolinks.art" not in page.url:
                update_status(f"🔀 Redirected to: {page.url}")
                break
        else:
            update_status("⚠️ No redirect detected. Proceeding anyway...")

        update_status("🔍 Extracting final link...")
        final_url = await extract_link_from_page(page)

        await browser.close()
        return final_url

# === Multi-Attempt Resolver ===
async def resolve_with_retries(ozolink_url, max_retries=2):
    for attempt in range(1, max_retries + 1):
        update_status(f"🔄 Attempt {attempt} of {max_retries}...")
        try:
            final_link = await resolve_ozolink_once(ozolink_url)
            if final_link:
                return final_link
        except Exception as e:
            update_status(f"⚠️ Error on attempt {attempt}: {str(e)}")
        await asyncio.sleep(2)
    return None

# === Button Action: Start resolving ===
def start_resolving():
    ozolink_url = url_entry.get().strip()
    if not ozolink_url:
        update_status("❗ Please enter a valid Ozolink URL.", error=True)
        return

    resolve_button.configure(state="disabled")
    clear_button.configure(state="disabled")
    update_status("🔧 Processing...")

    async def run():
        try:
            final_link = await resolve_with_retries(ozolink_url)
            if final_link:
                update_status(f"✅ Final Link:\n{final_link}", success=True)
                webbrowser.open(final_link)
            else:
                update_status("❌ Could not extract final link after retries.", error=True)
        finally:
            resolve_button.configure(state="normal")
            clear_button.configure(state="normal")

    asyncio.create_task(run())

# === Button Action: Clear ===
def clear_all():
    url_entry.delete(0, ctk.END)
    update_status("")

# === Setup GUI ===
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.title("🔓 Ozolink Decoder")
app.geometry("620x320")
app.resizable(False, False)

# === Layout ===
title_label = ctk.CTkLabel(app, text="Ozolink URL Decoder", font=ctk.CTkFont(size=22, weight="bold"))
title_label.pack(pady=(20, 10))

url_entry = ctk.CTkEntry(app, width=500, height=35, placeholder_text="Paste Ozolink URL here")
url_entry.pack(pady=(0, 15))

button_frame = ctk.CTkFrame(app, fg_color="transparent")
button_frame.pack()

resolve_button = ctk.CTkButton(button_frame, text="Decode & Open Link", command=start_resolving, height=35, width=180)
resolve_button.grid(row=0, column=0, padx=10)

clear_button = ctk.CTkButton(button_frame, text="Clear", command=clear_all, height=35, width=100)
clear_button.grid(row=0, column=1, padx=10)

status_label = ctk.CTkLabel(app, text="", wraplength=560, justify="left", font=ctk.CTkFont(size=15))
status_label.pack(pady=(20, 10))

# === Async Main Loop ===
async def async_mainloop():
    while True:
        app.update()
        await asyncio.sleep(0.01)

asyncio.run(async_mainloop())
