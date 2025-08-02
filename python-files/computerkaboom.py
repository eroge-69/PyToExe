import os
import webbrowser
import time

# List of programs to open
programs = [
    "notepad", "mspaint", "calc", "wordpad", "write", "snippingtool",
    "mspaint", "calc", "notepad", "mspaint", "calc", "notepad"
]

# List of URLs to open in new browser tabs
urls = [
    "https://www.google.com", "https://www.youtube.com", "https://www.facebook.com",
    "https://www.twitter.com", "https://www.instagram.com", "https://www.reddit.com",
    "https://www.amazon.com", "https://www.netflix.com", "https://www.wikipedia.org",
    "https://www.github.com"
]

def open_programs():
    for program in programs:
        os.system(f"start {program}")

def open_tabs():
    for url in urls * 50:  # Multiply the list to open more tabs
        webbrowser.open_new_tab(url)
        time.sleep(0.1)  # Small delay to avoid overwhelming the browser

if __name__ == "__main__":
    # Open programs in the background
    open_programs()

    # Open browser tabs
    open_tabs()