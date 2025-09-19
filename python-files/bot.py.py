import asyncio
import logging
import random
from urllib.parse import unquote
from playwright.async_api import async_playwright

# Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")

# Bases
ufo_bases = ["FAST BOT", "ASYNC RENAME", "PLAYWRIGHT", "ULTRA", "NC"]
emoji_suffixes = ["🔥", "💥", "🚀", "👾", "😈"]

# Global stats
success_count = 0
fail_count = 0
lock = asyncio.Lock()

# === Utils ===
def generate_name():
    return f"{random.choice(ufo_bases)}_{random.choice(emoji_suffixes)}"

async def rename_loop(page):
    global success_count, fail_count
    change_btn = page.locator('div[aria-label="Change group name"][role="button"]')
    group_input = page.locator('input[aria-label="Group name"][name="change-group-name"]')
    save_btn = page.locator('div[role="button"]:has-text("Save")')

    while True:
        try:
            name = generate_name()
            await change_btn.click()
            await group_input.fill(name)

            if await save_btn.get_attribute("aria-disabled") == "true":
                async with lock: fail_count += 1
                continue

            await save_btn.click()
            async with lock: success_count += 1

            # tiny delay to avoid hammering too fast
            await asyncio.sleep(0.02)

        except Exception:
            async with lock: fail_count += 1
            await asyncio.sleep(0.05)

async def live_stats():
    while True:
        async with lock:
            total = success_count + fail_count
            print(f"✅ {success_count} | ❌ {fail_count} | Total: {total}", end="\r")
        await asyncio.sleep(0.3)

async def main():
    session_id = input("Session ID: ").strip() or unquote("dummy-session-id")
    dm_url = input("Group chat URL: ").strip() or "https://www.instagram.com/direct/t/xxxxx/"
    try:
        task_count = int(input("Number of async tasks: ").strip())
    except:
        task_count = 5

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-gpu", "--disable-dev-shm-usage"]
        )
        context = await browser.new_context(locale="en-US")
        await context.add_cookies([{
            "name": "sessionid",
            "value": session_id,
            "domain": ".instagram.com",
            "path": "/",
            "httpOnly": True,
            "secure": True,
            "sameSite": "None"
        }])

        page = await context.new_page()
        await page.goto(dm_url, wait_until="domcontentloaded")

        # open GC info once
        gear = page.locator('svg[aria-label="Conversation information"]')
        await gear.wait_for()
        await gear.click()

        # run rename tasks on same page
        tasks = [asyncio.create_task(rename_loop(page)) for _ in range(task_count)]
        tasks.append(asyncio.create_task(live_stats()))

        try:
            await asyncio.gather(*tasks)
        except KeyboardInterrupt:
            print("\n👋 Stopped.")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
