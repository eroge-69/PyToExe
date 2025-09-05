import os
import json
import requests
import time
import threading
import logging
import hashlib
import base58
import ecdsa
import asyncio
import aiohttp
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from mnemonic import Mnemonic
from web3 import Web3, AsyncWeb3
from web3.middleware import async_geth_poa_middleware
import telebot
from dotenv import load_dotenv
from eth_account import Account
import binascii
import csv
from pathlib import Path

# Загрузка переменных окружения
load_dotenv()

# Создание директорий для хранения данных
Path("logs").mkdir(exist_ok=True)
Path("seeds").mkdir(exist_ok=True)
Path("results").mkdir(exist_ok=True)

# Настройка логирования
log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(
    level=logging.INFO,
    format=log_format,
    handlers=[
        logging.FileHandler(f"logs/crypto_checker_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Конфигурация
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
CHECK_INTERVAL = int(os.getenv('CHECK_INTERVAL', 60))
MAX_WORKERS = int(os.getenv('MAX_WORKERS', 10))
SEEDS_PER_BATCH = int(os.getenv('SEEDS_PER_BATCH', 100))
SAVE_INTERVAL = int(os.getenv('SAVE_INTERVAL', 300))

# Подключение к узлам блокчейна
ETHEREUM_RPC = os.getenv('ETHEREUM_RPC', 'https://mainnet.infura.io/v3/your_project_id')
BITCOIN_API = os.getenv('BITCOIN_API', 'https://blockstream.info/api/')
BSC_RPC = os.getenv('BSC_RPC', 'https://bsc-dataseed.binance.org/')
POLYGON_RPC = os.getenv('POLYGON_RPC', 'https://polygon-rpc.com/')

# Инициализация Telegram бота
if TELEGRAM_BOT_TOKEN:
    bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)
else:
    bot = None

# Инициализация генератора мнемоник
mnemo = Mnemonic("english")

# Глобальные переменные для статистики
stats = {
    "total_generated": 0,
    "total_checked": 0,
    "start_time": time.time(),
    "wallets_with_balance": 0
}

async def init_web3_providers():
    """Инициализация асинхронных Web3 провайдеров"""
    try:
        session = aiohttp.ClientSession()
        
w3_bsc_sync = Web3(Web3.HTTPProvider(BSC_RPC)) if BSC_RPC else None
w3_poly_sync = Web3(Web3.HTTPProvider(POLYGON_RPC)) if POLYGON_RPC else None

if w3_bsc_sync:
    w3_bsc_sync.middleware_onion.inject(sync_geth_poa_middleware, layer=0)
if w3_poly_sync:
    w3_poly_sync.middleware_onion.inject(sync_geth_poa_middleware, layer=0)
        
        logger.info("Web3 провайдеры успешно инициализированы")
        return session, w3_eth, w3_bsc, w3_poly
        
    except Exception as e:
        logger.error(f"Ошибка инициализации Web3 провайдеров: {e}")
        return None, None, None, None

def generate_btc_address(private_key_bytes):
    """Генерация Bitcoin адреса из приватного ключа"""
    try:
        # Получаем публичный ключ
        sk = ecdsa.SigningKey.from_string(private_key_bytes, curve=ecdsa.SECP256k1)
        vk = sk.get_verifying_key()
        public_key = b'\x04' + vk.to_string()
        
        # Хешируем публичный ключ (SHA-256 + RIPEMD-160)
        sha256_hash = hashlib.sha256(public_key).digest()
        ripemd160_hash = hashlib.new('ripemd160', sha256_hash).digest()
        
        # Добавляем сетевой префикс (0x00 для mainnet)
        network_byte = b'\x00'
        extended_ripemd160 = network_byte + ripemd160_hash
        
        # Вычисляем checksum
        checksum = hashlib.sha256(hashlib.sha256(extended_ripemd160).digest()).digest()[:4]
        
        # Формируем финальный адрес
        binary_address = extended_ripemd160 + checksum
        btc_address = base58.b58encode(binary_address).decode('utf-8')
        
        return btc_address
        
    except Exception as e:
        logger.error(f"Ошибка генерации BTC адреса: {e}")
        return None

class CryptoWallet:
    def __init__(self, mnemonic):
        self.mnemonic = mnemonic
        self.addresses = {}
        self.balances = {}
        self.private_keys = {}
        
    def generate_addresses(self):
        """Генерация адресов для разных блокчейнов из сид-фразы"""
        try:
            # Генерируем seed из мнемонической фразы
            seed = mnemo.to_seed(self.mnemonic)
            
            # Генерируем приватный ключ из seed (первые 32 байта)
            private_key_bytes = seed[:32]
            private_key_hex = binascii.hexlify(private_key_bytes).decode('utf-8')
            
            # Bitcoin
            btc_address = generate_btc_address(private_key_bytes)
            if btc_address:
                self.addresses['bitcoin'] = btc_address
                self.private_keys['bitcoin'] = private_key_hex
            
            # Ethereum
            acct = Account.from_key(private_key_hex)
            self.addresses['ethereum'] = acct.address
            self.private_keys['ethereum'] = private_key_hex
            
            # BSC (тот же адрес что и Ethereum)
            self.addresses['bsc'] = self.addresses['ethereum']
            self.private_keys['bsc'] = private_key_hex
            
            # Polygon (тот же адрес что и Ethereum)
            self.addresses['polygon'] = self.addresses['ethereum']
            self.private_keys['polygon'] = private_key_hex
            
            logger.debug(f"Сгенерированы адреса для сид-фразы: {self.mnemonic}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка генерации адресов: {e}")
            return False

    async def check_balance_async(self, blockchain, address, session, w3_eth, w3_bsc, w3_poly):
        """Асинхронная проверка баланса для конкретного блокчейна"""
        try:
            if blockchain == 'bitcoin':
                # Используем Blockstream API для проверки баланса Bitcoin
                async with session.get(f"{BITCOIN_API}/address/{address}", timeout=30) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get('chain_stats', {}).get('funded_txo_sum', 0) - data.get('chain_stats', {}).get('spent_txo_sum', 0)
                    else:
                        return 0
            
            elif blockchain == 'ethereum' and w3_eth:
                try:
                    balance = await w3_eth.eth.get_balance(Web3.to_checksum_address(address))
                    return balance
                except:
                    return 0
            
            elif blockchain == 'bsc' and w3_bsc:
                try:
                    balance = await w3_bsc.eth.get_balance(Web3.to_checksum_address(address))
                    return balance
                except:
                    return 0
            
            elif blockchain == 'polygon' and w3_poly:
                try:
                    balance = await w3_poly.eth.get_balance(Web3.to_checksum_address(address))
                    return balance
                except:
                    return 0
            
            return 0
            
        except Exception as e:
            logger.debug(f"Ошибка проверки баланса {blockchain}: {e}")
            return 0
    
    async def check_all_balances_async(self, session, w3_eth, w3_bsc, w3_poly):
        """Асинхронная проверка балансов по всем блокчейнам"""
        try:
            self.balances = {}
            tasks = []
            
            for blockchain, address in self.addresses.items():
                tasks.append(self.check_balance_async(blockchain, address, session, w3_eth, w3_bsc, w3_poly))
            
            # Запускаем все задачи параллельно
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Обрабатываем результаты
            for i, (blockchain, _) in enumerate(self.addresses.items()):
                if not isinstance(results[i], Exception) and results[i] > 0:
                    self.balances[blockchain] = results[i]
            
            return len(self.balances) > 0
            
        except Exception as e:
            logger.error(f"Ошибка проверки балансов: {e}")
            return False

def save_seed_to_file(mnemonic, filename=None):
    """Сохранение сид-фразы в файл"""
    try:
        if filename is None:
            filename = f"seeds/seeds_{datetime.now().strftime('%Y%m%d')}.txt"
        
        with open(filename, 'a', encoding='utf-8') as f:
            f.write(f"{mnemonic}\n")
        
        logger.debug(f"Сид-фраза сохранена в файл: {filename}")
        return filename
    except Exception as e:
        logger.error(f"Ошибка сохранения сид-фразы в файл: {e}")
        return None

def save_results_to_csv(mnemonic, balances, addresses, private_keys):
    """Сохранение результатов в CSV файл"""
    try:
        filename = f"results/found_wallets_{datetime.now().strftime('%Y%m%d')}.csv"
        file_exists = os.path.isfile(filename)
        
        with open(filename, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            if not file_exists:
                # Записываем заголовок, если файл не существует
                writer.writerow(['Timestamp', 'Mnemonic', 'Blockchain', 'Address', 'Balance', 'Private Key'])
            
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            for blockchain, balance in balances.items():
                writer.writerow([timestamp, mnemonic, blockchain, addresses.get(blockchain, ''), balance, private_keys.get(blockchain, '')])
        
        logger.info(f"Результаты сохранены в CSV файл: {filename}")
        return filename
    except Exception as e:
        logger.error(f"Ошибка сохранения результатов в CSV: {e}")
        return None

def generate_mnemonic(words_num=12):
    """Генерация сид-фразы"""
    try:
        if words_num == 12:
            strength = 128
        elif words_num == 24:
            strength = 256
        else:
            strength = 128
            
        mnemonic = mnemo.generate(strength=strength)
        stats["total_generated"] += 1
        return mnemonic
    except Exception as e:
        logger.error(f"Ошибка генерации сид-фразы: {e}")
        return None

async def send_telegram_notification(mnemonic, balances, addresses, private_keys):
    """Отправка уведомления в Telegram"""
    if not bot or not TELEGRAM_CHAT_ID:
        logger.warning("Telegram бот не настроен")
        return False
    
    try:
        message = "💰 Найден кошелек с балансом!\n\n"
        message += f"Сид-фраза: `{mnemonic}`\n\n"
        
        for blockchain, balance in balances.items():
            if blockchain == 'bitcoin':
                btc_balance = balance / 100000000
                message += f"Bitcoin: {btc_balance:.8f} BTC\n"
                message += f"Адрес BTC: `{addresses['bitcoin']}`\n"
            elif blockchain == 'ethereum':
                eth_balance = Web3.from_wei(balance, 'ether')
                message += f"Ethereum: {eth_balance:.6f} ETH\n"
                message += f"Адрес ETH: `{addresses['ethereum']}`\n"
            elif blockchain == 'bsc':
                bnb_balance = Web3.from_wei(balance, 'ether')
                message += f"BSC: {bnb_balance:.6f} BNB\n"
                message += f"Адрес BSC: `{addresses['bsc']}`\n"
            elif blockchain == 'polygon':
                matic_balance = Web3.from_wei(balance, 'ether')
                message += f"Polygon: {matic_balance:.6f} MATIC\n"
                message += f"Адрес Polygon: `{addresses['polygon']}`\n"
        
        message += f"\nВремя обнаружения: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        bot.send_message(TELEGRAM_CHAT_ID, message, parse_mode="Markdown")
        logger.info("Уведомление отправлено в Telegram")
        return True
        
    except Exception as e:
        logger.error(f"Ошибка отправки уведомления в Telegram: {e}")
        return False

def print_stats():
    """Вывод статистики"""
    elapsed = time.time() - stats["start_time"]
    hours = int(elapsed // 3600)
    minutes = int((elapsed % 3600) // 60)
    seconds = int(elapsed % 60)
    
    speed = stats["total_checked"] / elapsed if elapsed > 0 else 0
    
    logger.info(
        f"Статистика: Генерация: {stats['total_generated']}, "
        f"Проверка: {stats['total_checked']}, "
        f"Найдено: {stats['wallets_with_balance']}, "
        f"Скорость: {speed:.2f} seeds/сек, "
        f"Время: {hours:02d}:{minutes:02d}:{seconds:02d}"
    )

async def process_seed_batch(seeds_batch, session, w3_eth, w3_bsc, w3_poly):
    """Обработка пакета сид-фраз"""
    results = []
    
    for mnemonic in seeds_batch:
        try:
            # Создаем кошелек
            wallet = CryptoWallet(mnemonic)
            if not wallet.generate_addresses():
                continue
            
            # Сохраняем сид-фразу в файл
            save_seed_to_file(mnemonic)
            
            # Проверяем балансы
            has_balance = await wallet.check_all_balances_async(session, w3_eth, w3_bsc, w3_poly)
            stats["total_checked"] += 1
            
            if has_balance:
                stats["wallets_with_balance"] += 1
                logger.info(f"Найден кошелек с балансом: {mnemonic}")
                
                # Сохраняем результаты в CSV
                save_results_to_csv(mnemonic, wallet.balances, wallet.addresses, wallet.private_keys)
                
                # Отправляем уведомление в Telegram
                await send_telegram_notification(mnemonic, wallet.balances, wallet.addresses, wallet.private_keys)
                
                results.append((mnemonic, wallet.balances))
            
            # Выводим статистику каждые 100 проверенных сид-фраз
            if stats["total_checked"] % 100 == 0:
                print_stats()
                
        except Exception as e:
            logger.error(f"Ошибка обработки сид-фразы: {e}")
    
    return results

async def main_worker():
    """Основной рабочий процесс"""
    logger.info("Запуск генератора и проверщика сид-фраз...")
    
    # Проверяем конфигурацию
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        logger.warning("Telegram бот не настроен. Уведомления отправляться не будут.")
    
    # Инициализируем Web3 провайдеры
    session, w3_eth, w3_bsc, w3_poly = await init_web3_providers()
    if not session:
        logger.error("Не удалось инициализировать Web3 провайдеры")
        return
    
    last_save_time = time.time()
    batch_counter = 0
    
    try:
        while True:
            batch_counter += 1
            logger.info(f"Обработка батча #{batch_counter}")
            
            # Генерируем пакет сид-фраз
            seeds_batch = [generate_mnemonic() for _ in range(SEEDS_PER_BATCH)]
            seeds_batch = [seed for seed in seeds_batch if seed is not None]
            
            if not seeds_batch:
                logger.warning("Не удалось сгенерировать сид-фразы")
                await asyncio.sleep(CHECK_INTERVAL)
                continue
            
            # Обрабатываем пакет
            await process_seed_batch(seeds_batch, session, w3_eth, w3_bsc, w3_poly)
            
            # Периодически сохраняем статистику
            current_time = time.time()
            if current_time - last_save_time >= SAVE_INTERVAL:
                print_stats()
                last_save_time = current_time
            
            # Задержка между пакетами
            await asyncio.sleep(CHECK_INTERVAL)
            
    except Exception as e:
        logger.error(f"Ошибка в рабочем процессе: {e}")
    finally:
        # Закрываем сессию при завершении
        await session.close()
        logger.info("Сессия закрыта")

def main():
    """Основная функция"""
    try:
        # Запускаем асинхронный рабочий процесс
        asyncio.run(main_worker())
    except KeyboardInterrupt:
        logger.info("Остановка приложения по запросу пользователя...")
        print_stats()
    except Exception as e:
        logger.error(f"Неожиданная ошибка: {e}")
    finally:
        logger.info("Приложение завершено")

if __name__ == "__main__":
    main()