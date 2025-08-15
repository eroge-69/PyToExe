from playwright.sync_api import sync_playwright

def fetch_wordle_word():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://tomsguide.com.co", timeout=60000)

        # Klik op de knop om het woord te onthullen
        page.click("button.reveal-button")

        # Wacht tot de letter-boxen verschijnen
        page.wait_for_selector("div.letter-box.revealed", timeout=10000)

        # Haal de letters op
        elements = page.query_selector_all("div.letter-box.revealed")
        letters = [el.get_attribute("data-char") for el in elements]

        wordle_word = ''.join(letters)
        print(wordle_word)

        browser.close()

fetch_wordle_word()
