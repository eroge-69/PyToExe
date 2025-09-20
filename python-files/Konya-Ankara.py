import asyncio, re, time, sys
from playwright.async_api import async_playwright, TimeoutError as PWTimeout

FROM = "KONYA , KONYA"
TO   = "ANKARA GAR , ANKARA"
CHECK_EVERY_SECONDS = 60  # 1 minute
PAREN_RE = re.compile(r"\((\d+)\)")

async def quick_choose(page, selector, text):
    await page.click(selector)
    await page.fill(selector, text)
    await page.keyboard.press("ArrowDown")
    await page.keyboard.press("Enter")

async def get_seat_numbers(page):
    # Read (N) from <span class="emptySeat">(97)</span>
    try:
        await page.wait_for_selector("span.emptySeat", timeout=8000)
    except PWTimeout:
        return []
    texts = await page.locator("span.emptySeat").all_text_contents()
    nums = []
    for t in texts:
        m = PAREN_RE.search(t.strip())
        if m:
            nums.append(int(m.group(1)))
    return nums

async def bring_to_front_and_flash_title(page, seats):
    # Try to bring the tab to front
    try:
        await page.bring_to_front()
    except:
        pass
    # Flash the tab title for 60 seconds (no overlays, no sounds)
    msg = f"★ SEATS: {sorted(set(seats))} ★"
    js = f"""
      (() => {{
        const base = document.__origTitle || document.title || "TCDD";
        document.__origTitle = base;
        let on = false;
        if (window.__flashTimer__) clearInterval(window.__flashTimer__);
        window.__flashTimer__ = setInterval(() => {{
          document.title = on ? base : "{msg}";
          on = !on;
        }}, 400);
        if (window.__flashStop__) clearTimeout(window.__flashStop__);
        window.__flashStop__ = setTimeout(() => {{
          clearInterval(window.__flashTimer__);
          document.title = document.__origTitle;
        }}, 60000);
      }})();
    """
    try:
        await page.evaluate(js)
    except:
        pass

async def run():
    print(">>> Kapatmak için Ctrl+C'ye basınız. program çalışıyor <<<")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=0)
        page = await browser.new_page()

        # Open site and search once
        await page.goto("https://ebilet.tcddtasimacilik.gov.tr/")
        await quick_choose(page, "#fromTrainInput", FROM)
        await quick_choose(page, "#toTrainInput", TO)
        await page.get_by_text("Yarın").click()
        await page.get_by_role("button", name="Ara").click()
        await page.wait_for_url("**/sefer-listesi*", timeout=20000)
        print("[ok] Results page loaded")

        # Loop: check seats, flash if >2, then reload after 60s
        while True:
            try:
                await page.wait_for_selector("text=Bilet Ücreti", timeout=15000)
            except PWTimeout:
                print("[warn] No results visible yet")

            seats = await get_seat_numbers(page)
            ts = time.strftime("%H:%M:%S")
            if seats:
                print(f"[{ts}] Seats seen: {seats}")
                good = [n for n in seats if n not in (0, 1, 2)]
                if good:
                    print(f"[{ts}] ✅ Seats available >2: {sorted(set(good))}")
                    await bring_to_front_and_flash_title(page, good)
                else:
                    print(f"[{ts}] No suitable seats (only 0/1/2).")
            else:
                print(f"[{ts}] No seat numbers detected.")

            await asyncio.sleep(CHECK_EVERY_SECONDS)
            await page.reload(wait_until="domcontentloaded")
            print("[info] Page reloaded; checking again...")

if __name__ == "__main__":
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        print("\n>>> Stopped by user.")
        sys.exit(0)
