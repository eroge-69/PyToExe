
import time
import random
import webbrowser
import pyautogui
import pandas as pd

# List of comment templates
COMMENT_TEMPLATES = [
    "Boosteroid delivers super smooth gameplay—no lag at all, just seamless performance every time!",
    "I love how Boosteroid runs flawlessly on any device I use, no matter where I am!",
    "Cloud gaming has never been this easy—Boosteroid makes everything smooth and effortless!",
    "Tried Boosteroid and was blown away by how great the performance is—totally worth it!",
    "With Boosteroid, I can finally play all my favorite games without needing a powerful PC!",
    "Gaming on Boosteroid feels just like console quality—super fast, responsive, and stable!",
    "The reliability of Boosteroid takes the stress out of gaming—no crashes, no worries!",
    "Boosteroid makes every game feel ultra-smooth—it honestly feels unreal sometimes!",
    "I can take my gaming anywhere now thanks to Boosteroid—no more being stuck at my desk!",
    "With Boosteroid, I’m free to play anytime and anywhere without worrying about lag or drops!",
    "Getting started with Boosteroid is incredibly easy—just log in and start playing instantly!",
    "Boosteroid gives me high-end gaming performance without the need to upgrade my hardware!",
    "I love how Boosteroid lets me enjoy AAA games even on my old laptop or tablet!",
    "Boosteroid is the perfect choice for gamers who want great performance without the hassle!",
    "Even the biggest, most demanding games run smoothly on small devices with Boosteroid!",
    "I tested Boosteroid on a budget setup and didn’t need to upgrade anything—ran perfectly!",
    "Boosteroid makes high-quality gaming accessible for everyone, no matter what gear you have!",
    "It’s my go-to service when I want to play demanding games without spending thousands on a rig!",
    "Cloud gaming with Boosteroid is on another level—it’s fast, stable, and super fun to use!"
]

# Ask user for hashtag and number of videos
hashtag = input("Enter hashtag (without #): ").strip()
max_comments = int(input("How many videos to comment on? ").strip())

# Open TikTok hashtag page
url = f"https://www.tiktok.com/tag/{hashtag}"
webbrowser.open(url)
print("Opening TikTok... You have 15 seconds to make sure it's loaded and logged in.")
time.sleep(15)

commented_links = []

for i in range(max_comments):
    print(f"Commenting on video {i+1}/{max_comments}...")

    # Scroll a bit to load new videos
    pyautogui.scroll(-300)
    time.sleep(2)

    # Open the video (user must make sure videos are visible on screen)
    pyautogui.moveRel(0, 200, duration=1)
    pyautogui.click()
    time.sleep(5)

    # Copy the URL using keyboard shortcut
    pyautogui.hotkey("ctrl", "l")
    pyautogui.hotkey("ctrl", "c")
    time.sleep(1)
    url = pyautogui.paste()
    commented_links.append([url])

    # Comment box click & type
    pyautogui.press("tab", presses=10, interval=0.1)  # Tab through to the comment field
    time.sleep(1)
    comment = random.choice(COMMENT_TEMPLATES)
    pyautogui.write(comment, interval=0.05)
    pyautogui.press("enter")
    print(f"Commented: {comment}")

    # Close the video tab using 'Escape'
    pyautogui.press("esc")
    time.sleep(random.uniform(5, 10))

# Save links to CSV
df = pd.DataFrame(commented_links, columns=["Video URL"])
df.to_csv("commented_videos_humanlike.csv", index=False)
print("All done! Comments saved to commented_videos_humanlike.csv")
