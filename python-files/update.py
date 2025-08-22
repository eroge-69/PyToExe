import csv
import requests
import time
from tqdm import tqdm
from datetime import datetime

# читаем вебхук и убираем лишние слеши
with open("web.txt", "r") as f:
    WEBHOOK = f.read().strip().rstrip('/')

# базовые URL
CATALOG_LIST_URL = f"{WEBHOOK}/catalog.catalog.list"
PRODUCT_LIST_URL = f"{WEBHOOK}/catalog.product.list"
OFFER_UPDATE_URL = f"{WEBHOOK}/catalog.product.offer.update"

# имя файла для логов
log_filename = f"log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

def log(message):
    with open(log_filename, "a", encoding="utf-8") as f:
        f.write(message + "\n")
    print(message)

def make_api_request(url, payload, method_name):
    """Универсальная функция для API запросов"""
    try:
        log(f"📡 {method_name} запрос: {payload}")
        r = requests.post(url, json=payload, timeout=30)
        log(f"📡 {method_name} статус: {r.status_code}")
        
        r.raise_for_status()
        data = r.json()
        
        # Проверяем структуру ответа Bitrix24
        if isinstance(data, dict) and "error" in data:
            error_msg = data.get("error_description", str(data))
            raise Exception(f"API ошибка: {error_msg}")
            
        return data
        
    except Exception as e:
        log(f"❌ Ошибка в {method_name}: {e}")
        raise

def get_catalog_iblock():
    """Получаем iblockId каталога для вариаций"""
    try:
        data = make_api_request(CATALOG_LIST_URL, {}, "catalog.list")
        
        # Получаем список каталогов
        catalogs = data.get("result", {}).get("catalogs", [])
        if not catalogs:
            catalogs = data.get("result", [])
        
        if not catalogs:
            raise Exception("Не найдено ни одного каталога")
            
        # Берем второй каталог (каталог предложений)
        if len(catalogs) >= 2:
            catalog_for_offers = catalogs[1]
        else:
            catalog_for_offers = catalogs[0]
            
        iblock_id = catalog_for_offers.get("iblockId") or catalog_for_offers.get("ID")
        
        if not iblock_id:
            raise Exception("Не удалось получить iblockId из ответа")
            
        log(f"✅ Найден iblockId = {iblock_id} (каталог: {catalog_for_offers.get('name')})")
        return iblock_id
        
    except Exception as e:
        log(f"❌ Ошибка при получении iblockId: {e}")
        raise

def get_product_variations(product_id, iblock_id):
    """Получаем список вариаций товара по parentId"""
    payload = {
        "select": ["id", "xmlId", "name", "parentId", "iblockId"],
        "filter": {
            "parentId": int(product_id),
            "iblockId": int(iblock_id)
        }
    }
    
    try:
        data = make_api_request(PRODUCT_LIST_URL, payload, "product.list")
        
        # Получаем список продуктов из ответа
        products = data.get("result", {}).get("products", [])
        if not isinstance(products, list):
            products = []
            
        log(f"Найдено вариаций для товара {product_id}: {len(products)}")
        
        # Извлекаем xmlId вариаций
        xml_ids = []
        for product in products:
            if isinstance(product, dict):
                xml_id = product.get("xmlId")
                if xml_id:
                    xml_ids.append(xml_id)
                    log(f"  - Вариация XML_ID: {xml_id}, Название: {product.get('name')}")
        
        return xml_ids
        
    except Exception as e:
        log(f"Ошибка при получении вариаций: {e}")
        return []

def update_offer_purchasing_price(xml_id, new_price):
    """Обновляем закупочную цену вариации"""
    payload = {
        "id": xml_id,
        "fields": {"purchasingPrice": float(new_price)}
    }
    
    try:
        data = make_api_request(OFFER_UPDATE_URL, payload, "offer.update")
        
        # Проверяем успешность обновления
        result = data.get("result", {})
        if result:
            log(f"✅ Закупочная цена вариации {xml_id} успешно обновлена")
            return True
        else:
            raise Exception("Не удалось обновить закупочную цену")
            
    except Exception as e:
        raise Exception(f"Ошибка обновления: {e}")

def process_product(product_id, new_price, iblock_id):
    """Обрабатываем один товар"""
    try:
        # Получаем вариации товара
        xml_ids = get_product_variations(product_id, iblock_id)
        
        if not xml_ids:
            log(f"⚠️ У товара {product_id} нет вариаций")
            return False
        
        # Обновляем цены для каждой вариации
        success_count = 0
        for xml_id in xml_ids:
            try:
                update_offer_purchasing_price(xml_id, new_price)
                log(f"✅ Закупочная стоимость вариации {xml_id} товара {product_id} успешно изменена")
                success_count += 1
            except Exception as e:
                log(f"❌ Ошибка при обновлении вариации {xml_id}: {e}")
            
            time.sleep(0.3)
        
        log(f"📊 Обновлено вариаций: {success_count}/{len(xml_ids)}")
        return success_count > 0
        
    except Exception as e:
        log(f"❌ Ошибка при обработке товара {product_id}: {e}")
        return False

# --- Основной скрипт ---
try:
    log("🔄 Получение iblockId...")
    IBLOCK_ID = get_catalog_iblock()
except Exception as e:
    log(f"❌ Критическая ошибка: {e}")
    exit(1)

# Читаем CSV файл
try:
    with open("products.csv", newline="", encoding="utf-8") as csvfile:
        reader = list(csv.DictReader(csvfile))
        log(f"📊 Загружено {len(reader)} товаров для обработки")
        
        total_items = len(reader)
        success_count = 0
        error_count = 0
        
        for i, row in enumerate(tqdm(reader, desc="Обработка товаров", unit="товар")):
            product_id = row.get("id", "").strip()
            new_price = row.get("price", "").strip()
            
            if not product_id or not new_price:
                log(f"⚠️ Пропуск строки {i+1}: отсутствует ID или цена")
                error_count += 1
                continue
            
            log(f"\n🔧 Обрабатываем товар {product_id} → цена {new_price}")
            
            # Обрабатываем товар
            if process_product(product_id, new_price, IBLOCK_ID):
                success_count += 1
            else:
                error_count += 1
            
            time.sleep(0.5)
        
        # Итоговая статистика
        log(f"\n📊 ИТОГ:")
        log(f"✅ Успешно обработано: {success_count}")
        log(f"❌ С ошибками: {error_count}")
        log(f"📋 Всего: {total_items}")
            
except FileNotFoundError:
    log("❌ Файл products.csv не найден")
except Exception as e:
    log(f"❌ Ошибка при чтении CSV: {e}")

log("✅ Обработка завершена")

# Создаем файлы с логами ошибок и успехов
try:
    with open(log_filename, "r", encoding="utf-8") as f:
        all_logs = f.readlines()
    
    # Логи с ошибками
    error_logs = [line for line in all_logs if "❌" in line or "⚠️" in line or "Ошибка" in line]
    if error_logs:
        with open(f"error_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt", "w", encoding="utf-8") as f:
            f.writelines(error_logs)
    
    # Логи успехов
    success_logs = [line for line in all_logs if "✅" in line and "❌" not in line and "Ошибка" not in line]
    if success_logs:
        with open(f"success_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt", "w", encoding="utf-8") as f:
            f.writelines(success_logs)

except Exception as e:
    log(f"❌ Ошибка при создании файлов логов: {e}")
