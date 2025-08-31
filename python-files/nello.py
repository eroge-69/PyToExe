import sys
import time
import pygame
import requests
from playwright.sync_api import sync_playwright


def fetch_all_items(search="малина", max_count=50, page_size=50):
    url = "https://pub.fsa.gov.ru/api/v1/rds/common/declarations/get"
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Authorization": "Bearer eyJhbGciOiJFZERTQSJ9.eyJpc3MiOiJGQVUgTklBIiwic3ViIjoiYW5vbnltb3VzIiwiZXhwIjoxNzU2NTk4MjMzLCJpYXQiOjE3NTY1Njk0MzN9.IwxFkrgR1rsaLT1BtBHt53cTXzyjTAcI0iQxWzb9TUXeN73gNCuxRQDU1KJUs65-vuLply0hchpoD2IqxFJUAA",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0",
        "X-Ajax-Token": "526103de8f4082d77bd2bac0c4d4f4b2c44276a91d39b5f1f74a439f4cf6b5b3",
        "X-Requested-With": "XMLHttpRequest",
        "Referer": "https://pub.fsa.gov.ru/rds/declaration",
        "Origin": "https://pub.fsa.gov.ru"
    }

    all_items = []
    page_num = 0

    # Используем requests для более быстрых запросов
    while len(all_items) < max_count:
        payload = {
            "size": min(page_size, max_count - len(all_items)),
            "page": page_num,
            "columnsSort": [{"column": "id", "sort": "DESC"}],
            "filter": {"columnsSearch": [{"name": "productFullName", "search": search, "type": 0}]}
        }

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=10)
            if response.status_code != 200:
                print(f"Ошибка запроса: {response.status_code}")
                break

            data = response.json()
            items = data.get("items", [])
            if not items:
                break

            all_items.extend(items)
            page_num += 1

            if len(all_items) >= max_count:
                break

        except Exception as e:
            print(f"Ошибка при выполнении запроса: {e}")
            break

    return all_items[:max_count]


def parse_items(items):
    parsed_data = []

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        for i, item in enumerate(items):
            try:
                print(f"Обрабатывается элемент {i + 1}/{len(items)}: {item.get('number', 'N/A')}")

                decl_url = f"https://pub.fsa.gov.ru/rds/declaration/view/{item['id']}/product"

                # Переходим на страницу
                page.goto(decl_url, wait_until="domcontentloaded", timeout=30000)

                # Ждем загрузки контента
                page.wait_for_selector("fgis-card-info-row", timeout=10000)

                # Ищем элементы
                tn_text = "—"
                sto_text = "—"

                # Более быстрый способ поиска элементов
                card_rows = page.query_selector_all("fgis-card-info-row")
                for row in card_rows:
                    text = row.inner_text()
                    if "ТН ВЭД" in text:
                        tn_elem = row.query_selector("div:nth-child(2) >> div")
                        if tn_elem:
                            tn_text = tn_elem.inner_text().strip()
                    if "ТУ" in text or "СТО" in text or "ГОСТ" in text or "ОСТ" in text:
                        sto_text = row.query_selector("div:nth-child(2) >> span").inner_text()

                parsed_data.extend([
                    f"Название предприятия: {item.get('applicantName', '—')}",
                    f"Номер декларации: {item.get('number', '—')}",
                    f"ТН ВЭД: {tn_text}",
                    f"СТО: {sto_text}",
                    f"Дата регистрации: {item.get('declDate', '—')}",
                    f"Полное название: {item.get('productFullName', '—')}",
                    f"Идентификация: {item.get('productIdentificationName', '—')}",
                    "-" * 50
                ])

            except Exception as e:
                print(f"Ошибка при обработке элемента {item.get('number', 'N/A')}: {e}")
                continue

        browser.close()

    return parsed_data


def run_viewer(text, width=800, height=600):
    pygame.init()
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Просмотр результатов поиска")
    font = pygame.font.SysFont("Arial", 16)
    scroll = 0
    lh = font.get_height() + 4
    clock = pygame.time.Clock()

    if not text:
        text = ["Нет данных для отображения"]

    running = True
    while running:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    running = False
                elif e.key == pygame.K_DOWN:
                    scroll -= lh * 3
                elif e.key == pygame.K_UP:
                    scroll += lh * 3
            if e.type == pygame.MOUSEWHEEL:
                scroll += e.y * lh * 3

        # Ограничиваем скролл
        min_scroll = min(0, height - len(text) * lh)
        max_scroll = 0
        scroll = max(min_scroll, min(scroll, max_scroll))

        screen.fill((30, 30, 40))
        y = scroll + 10

        for line in text:
            # Отображаем полный текст без переноса
            rendered = font.render(line, True, (220, 220, 220))
            screen.blit(rendered, (10, y))
            y += lh

        # Отображаем подсказки
        hints = [
            "↑/↓ или колесо мыши - прокрутка",
            "ESC - выход"
        ]
        for i, hint in enumerate(hints):
            hint_text = font.render(hint, True, (150, 150, 150))
            screen.blit(hint_text, (width - hint_text.get_width() - 10, height - (len(hints) - i) * lh - 10))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


def preview_input(width=800, height=400):
    pygame.init()
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Поиск деклараций")
    font = pygame.font.SysFont("Arial", 24)
    small_font = pygame.font.SysFont("Arial", 18)
    inp_cat, inp_cnt, active = "малина", "10", "cat"
    clock = pygame.time.Clock()

    running = True
    while running:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_TAB:
                    active = "cnt" if active == "cat" else "cat"
                elif e.key == pygame.K_RETURN and inp_cat and inp_cnt.isdigit():
                    running = False
                elif e.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                elif e.key == pygame.K_BACKSPACE:
                    if active == "cat":
                        inp_cat = inp_cat[:-1]
                    else:
                        inp_cnt = inp_cnt[:-1] if inp_cnt else ""
                elif e.unicode:
                    if active == "cat":
                        inp_cat += e.unicode
                    elif active == "cnt" and e.unicode.isdigit():
                        inp_cnt += e.unicode

        screen.fill((40, 40, 60))

        # Отображаем поля ввода
        cat_color = (255, 255, 150) if active == "cat" else (220, 220, 220)
        cnt_color = (255, 255, 150) if active == "cnt" else (220, 220, 220)

        screen.blit(font.render("Категория:", True, (200, 200, 200)), (40, 80))
        screen.blit(font.render(inp_cat + ("|" if active == "cat" else ""), True, cat_color), (240, 80))

        screen.blit(font.render("Количество:", True, (200, 200, 200)), (40, 140))
        screen.blit(font.render(inp_cnt + ("|" if active == "cnt" else ""), True, cnt_color), (240, 140))

        # Подсказки
        screen.blit(small_font.render("TAB - переключение между полями", True, (180, 180, 180)), (40, 200))
        screen.blit(small_font.render("ENTER - начать поиск", True, (180, 180, 180)), (40, 230))
        screen.blit(small_font.render("ESC - выход", True, (180, 180, 180)), (40, 260))

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()
    return inp_cat, int(inp_cnt)

class Main:
    def __init__(self):
        try:
            cat, cnt = preview_input()
            print(f"Поиск: '{cat}', количество: {cnt}")

            start_time = time.time()
            items = fetch_all_items(cat, cnt)
            fetch_time = time.time() - start_time
            print(f"Получено {len(items)} элементов за {fetch_time:.2f} секунд")

            if items:
                print("Парсинг дополнительной информации...")
                start_time = time.time()
                text = parse_items(items)
                parse_time = time.time() - start_time
                print(f"Парсинг завершен за {parse_time:.2f} секунд")
                run_viewer(text)
            else:
                print("Не удалось получить данные")

        except Exception as e:
            print(f"Произошла ошибка: {e}")
            import traceback

            traceback.print_exc()
if __name__ == "__main__":
    Main()
