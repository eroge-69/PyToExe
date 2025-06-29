import cloudscraper
from time import sleep
from colorama import Fore, Style, init
from pytoniq import LiteBalancer, WalletV4R2
from tonutils.client import ToncenterV3Client
from tonutils.wallet import WalletV4R2
import gradio as gr
import requests
from urllib.parse import urlparse, parse_qs
import hashlib
import platform
import subprocess
import uuid

init(autoreset=True)
scraper = cloudscraper.create_scraper()


def settings_web_app():
    def show_notification():
        gr.Success("Бот запущен, вся работа будет отображаться в консольном приложении")

    css = """
    .green-button {
      /* Основные стили кнопки */
      background-color: #4CAF50; /* Зелёный цвет */
      border: none; /* Убираем стандартную границу */
      color: white; /* Цвет текста */
      padding: 12px 24px; /* Внутренние отступы */
      text-align: center; /* Выравнивание текста */
      text-decoration: none; /* Убираем подчёркивание */
      display: inline-block;
      letter-spacing: 4px;
      width: 230px !important;
      height: 230px !important;
      font-size: 18px !important;
      margin: 0 auto !important;  /* Центрирование */
      cursor: pointer; /* Курсор в виде указателя */
      border-radius: 12px; /* Закруглённые края */
      transition: all 0.3s ease; /* Плавные переходы для анимации */
      box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); /* Тень для объёма */
    }

    /* Стили при наведении */
    .green-button:hover{
      background-color: #07bb13;
      color: #050801;
      border-radius: 20px;
      box-shadow: 0px 0px 5px #07bb13, 0px 0px 25px #03e9f4, 0px 0px 50px #07bb13, 0px 0px 100px #07bb13;

    }

    /* Стили при нажатии (активное состояние) */
    .green-button:active {
      border-radius: 12px;
      transform: scale(0.95); /* Уменьшение размера */
      box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1); /* Уменьшение тени */
      background-color: #3d8b40; /* Ещё темнее зелёный */
    }
    """
    with gr.Blocks(css=css) as app:
        gr.HTML("<div style='height: 150px;'></div>")
        gr.Markdown("# 🛠 Настройка и запуск программы")

        with gr.Row():
            collection = gr.Number(
                label="Введите номер коллекции",
                scale=1,  # Размер (меньше = компактнее)
                step=1,  # Шаг изменения (опционально)
                minimum=1,  # Минимальное значение (опционально)
            )
            character = gr.Number(
                label="Введите номер стикера",
                scale=1,  # Размер (меньше = компактнее)
                step=1,  # Шаг изменения (опционально)
                minimum=1,  # Минимальное значение (опционально)
            )
            delay = gr.Slider(
                minimum=1,
                maximum=300,
                step=1,
                label="Задержка между запросами",
                value=60
            )

        with gr.layouts.Column():
            mnemonics = gr.Textbox(
                label="mnemonics from TON-space",
                placeholder="car wall coin...",
                container=True,
            )
            bearer_token = gr.Textbox(
                label="Bearer token from StickerBot",
                placeholder="eyJhbGciadOi...",
                container=True,
            )
        run_btn = gr.Button(
            value="Запуск",
            variant="primary",
            scale=3,
            elem_classes='green-button'
        )

        run_btn.click(
            fn=main,
            inputs=[collection, character, delay, mnemonics, bearer_token],
        ).then(
            show_notification,
        )
    return app


def get_google_doc_content():
    """
    Получает текстовое содержимое Google Docs файла по публичной ссылке

    Аргументы:
        shareable_link (str): Публичная ссылка на Google Docs файл

    Возвращает:
        str: Текстовое содержимое документа или None в случае ошибки
    """
    try:
        # Извлекаем ID документа из ссылки
        parsed = urlparse("https://docs.google.com/document/d/1laPsA1svhmVgn9P98mrrbGmr1ENudEXBC0n_oKCmYog")
        if 'docs.google.com' not in parsed.netloc:
            raise ValueError("Неверная ссылка Google Docs")

        # Варианты форматов ссылок:
        # https://docs.google.com/document/d/DOC_ID/edit
        # https://docs.google.com/document/d/DOC_ID/
        path_parts = parsed.path.split('/')
        if 'd' in path_parts:
            doc_id = path_parts[path_parts.index('d') + 1]
        else:
            # Альтернативный формат ссылки
            doc_id = parse_qs(parsed.query).get('id', [None])[0]
            if not doc_id:
                raise ValueError("Не удалось извлечь ID документа из ссылки")

        # Формируем URL для экспорта в текстовом формате
        export_url = f"https://docs.google.com/document/d/{doc_id}/export?format=txt"

        # Отправляем запрос
        response = requests.get(export_url)
        response.raise_for_status()  # Проверяем на ошибки

        return response.text

    except requests.exceptions.RequestException as e:
        print(f"Ошибка при запросе: {e}")
    except ValueError as e:
        print(f"Ошибка в ссылке: {e}")
    except Exception as e:
        print(f"Неожиданная ошибка: {e}")
    return None


async def buy_sticker(amount, comment, address, mnemonics) -> None:
    client = ToncenterV3Client(is_testnet=False, rps=1, max_retries=1)
    wallet, public_key, private_key, mnemonic = WalletV4R2.from_mnemonic(client, mnemonics.split(' '))

    tx_hash = await wallet.transfer(
        destination=address,
        amount=amount / 10 ** 9,
        body=comment,
    )

    print('\n============================================')
    print(f"Successfully payed {amount / 10 ** 9} TON!")
    print(f"Transaction hash: {tx_hash}")
    print('============================================\n')


def get_sticker(collection, character, bearer_token):
    buy_url = f"https://api.stickerdom.store/api/v1/shop/buy/crypto?collection={collection}&character={character}&currency=TON&count=1"
    headers = {
        "Authorization": f"Bearer {bearer_token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0",
        "Origin": "https://stickerdom.store",
        "Referer": "https://stickerdom.store/",
    }

    response = scraper.post(buy_url, headers=headers)
    if response.status_code == 200:
        response_json = response.json()
        try:
            if response_json["errorCode"] == 'collection_not_found' or response_json[
                "errorCode"] == 'character_not_found':
                print(Fore.YELLOW + "Waiting for sticker", "collection" + str(collection), "character" + str(character))
                return False
            if response_json["errorCode"]:
                print(Fore.RED + "Error in request:", response_json["errorCode"])
                return False
        except:
            print(Fore.GREEN + "Успешный заказ:")
            print(Fore.GREEN + "Order ID:", Style.BRIGHT + response_json["data"]["order_id"])
            print(Fore.GREEN + "Wallet:", response_json["data"]["wallet"])
            print(Fore.GREEN + "Currency:", response_json["data"]["currency"])
            print(Fore.GREEN + "Сумма:", response_json["data"]["total_amount"] / 10 ** 9)
            sticker = {
                "wallet": response_json["data"]["wallet"],
                "comment": response_json["data"]["order_id"],
                "amount": response_json["data"]["total_amount"]
            }
            return sticker
    else:
        print(Fore.RED + "Ошибка:", response.status_code)
        print(Fore.RED + response.text)
        return False


async def main(collection_number, character_number, delay_secconds, mnemonics_wors, bearer):
    print(Fore.GREEN + 'ПРИЛОЖЕНИЕ УСПЕШНО ЗАПУЩЕНО')
    while True:
        sticker = get_sticker(collection_number, character_number, bearer)
        if sticker:
            await buy_sticker(address=sticker["wallet"], amount=sticker['amount'], comment=sticker['comment'],
                              mnemonics=mnemonics_wors)
            break
        sleep(delay_secconds)


def hwid_web_app():
    def display_key():
        return f"""
        🔒 Пожалуйста, передайте этот ключ продавцу:  
        **{create_hwid()}**
        
        (После передачи ключа перезапустите приложение)  
        """

    # Создаем интерфейс
    with gr.Blocks() as app:
        gr.Markdown("### 🔑 Подтверждение покупки")
        gr.Markdown("Нажмите кнопку, чтобы увидеть уникальный ключ лицензии:")
        key_display = gr.Markdown()
        show_key_btn = gr.Button("Показать ключ")
        show_key_btn.click(display_key, outputs=key_display)

    # Запускаем приложение с автоматическим открытием в браузере
    return app


def create_hwid():
    # Собираем различную информацию о системе
    info = {
        "machine": platform.machine(),
        "node": platform.node(),
        "processor": platform.processor(),
        "system": platform.system(),
        "mac": ':'.join(['{:02x}'.format((uuid.getnode() >> ele) & 0xff)
                         for ele in range(0, 8 * 6, 8)][::-1]),
        "disk": subprocess.check_output("wmic diskdrive get serialnumber", shell=True).decode().split("\n")[1].strip()
        if platform.system() == "Windows" else "",
    }

    # Преобразуем информацию в строку и хэшируем
    hwid_str = "-".join([str(v) for v in info.values()])
    hwid = hashlib.sha256(hwid_str.encode()).hexdigest()

    return hwid


hwid = create_hwid()
licenses_hwids = get_google_doc_content()
if hwid in licenses_hwids:
    app = settings_web_app()
    app.launch(inbrowser=True)
else:
    app = hwid_web_app()
    app.launch(inbrowser=True)

    # made by reneget_
