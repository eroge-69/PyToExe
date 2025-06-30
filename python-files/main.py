from scraper.chrome_driver import open_browser
from scraper.site_navigator import visit_and_collect
from scraper.email_finder import extract_emails

urls = [
    "https://adrianleeds.com/subscribe-to-our-publications/parler-paris-nouvellettres/pp-archives/yes-to-europe-with-a-heart-in-france/"
]

driver = open_browser()

for url in urls:
    html = visit_and_collect(driver, url)
    emails = extract_emails(html)
    print(f"Emails trouvés sur {url} : {emails}")

driver.quit()
