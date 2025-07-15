from playwright.sync_api import sync_playwright
import time

TWITTER_USERNAME = "tinytalesofai"
TWITTER_PASSWORD = "Tinytalesai@143"
base_tweet = "This is my automated tweet new "
tweets = [f"{base_tweet} {i}" for i in range(1, 251)]

def login_and_tweet():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        # Open Twitter
        page.goto("https://twitter.com/login")
        page.wait_for_timeout(3000)

        # Enter username
        page.locator('input[name="text"]').fill(TWITTER_USERNAME)
        page.keyboard.press("Enter")
        page.wait_for_timeout(3000)

        # Enter password
        try:
            page.locator('input[name="password"]').fill(TWITTER_PASSWORD)
            page.keyboard.press("Enter")
        except:
            print("Manual step required (e.g., phone/email check)")

        page.wait_for_timeout(5000)

        # Tweet loop
        for tweet in tweets:
            try:
                page.goto("https://twitter.com/home", timeout=60000)
                page.wait_for_selector('div[data-testid="tweetTextarea_0"]', timeout=10000)
                tweet_box = page.locator('div[data-testid="tweetTextarea_0"]')
                tweet_box.click()
                page.keyboard.type(tweet)
                print("Trying to find the Post button...")
                try:
                    post_button = page.locator('button[data-testid="tweetButtonInline"]')
                    print("Post button located.")
                    page.wait_for_timeout(1000)
                    if post_button.is_enabled():
                        post_button.click()
                        print("Post button clicked.")
                    else:
                        print("Post button is not enabled. Skipping click.")
                except Exception as e:
                    print(f"Failed to interact with Post button: {e}")
                print(f"Tweeted: {tweet}")
                time.sleep(30)
            except Exception as e:
                print(f"Error tweeting: {e}")
                continue

        print("Done tweeting all.")
        browser.close()

if __name__ == "__main__":
    login_and_tweet()