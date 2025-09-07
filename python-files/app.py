
import sqlite3
import pandas as pd
from datetime import datetime, date
import numpy as np
from flask import Flask, render_template_string, request, redirect, url_for, flash, jsonify # Added jsonify for API

# --- Database Setup ---

# Connect to an in-memory SQLite database
# For persistent data, replace ':memory:' with a file path, e.g., 'restaurant_inventory.db'
conn = sqlite3.connect(':memory:')
cursor = conn.cursor()

# Create tables
cursor.execute('''
CREATE TABLE IF NOT EXISTS Stoklar (
    urun_id INTEGER PRIMARY KEY AUTOINCREMENT,
    urun_adi VARCHAR(255) NOT NULL,
    miktar DECIMAL(10, 2) NOT NULL,
    birim VARCHAR(50),
    birim_maliyet DECIMAL(10, 2),
    son_guncelleme_tarihi DATETIME
)
''')
cursor.execute('''
CREATE TABLE IF NOT EXISTS Faturalar (
    fatura_id INTEGER PRIMARY KEY AUTOINCREMENT,
    fatura_numarasi VARCHAR(100) NOT NULL UNIQUE,
    tedarikci_adi VARCHAR(255) NOT NULL,
    fatura_tarihi DATE NOT NULL,
    toplam_tutar DECIMAL(10, 2) NOT NULL,
    odeme_durumu VARCHAR(50) DEFAULT 'Beklemede'
)
''')
cursor.execute('''
CREATE TABLE IF NOT EXISTS Fatura_Kalemleri (
    fatura_kalem_id INTEGER PRIMARY KEY AUTOINCREMENT,
    fatura_id INTEGER,
    urun_id INTEGER,
    miktar DECIMAL(10, 2) NOT NULL,
    birim_fiyat DECIMAL(10, 2) NOT NULL,
    toplam_fiyat DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (fatura_id) REFERENCES Faturalar(fatura_id) ON DELETE CASCADE,
    FOREIGN KEY (urun_id) REFERENCES Stoklar(urun_id) ON DELETE CASCADE
)
''')
cursor.execute('''
CREATE TABLE IF NOT EXISTS Masraflar (
    masraf_id INTEGER PRIMARY KEY AUTOINCREMENT,
    masraf_aciklamasi VARCHAR(255) NOT NULL,
    masraf_tarihi DATE NOT NULL,
    tutar DECIMAL(10, 2) NOT NULL,
    kategori VARCHAR(100)
)
''')
cursor.execute('''
CREATE TABLE IF NOT EXISTS Aylik_Maliyet_Raporlari (
    rapor_id INTEGER PRIMARY KEY AUTOINCREMENT,
    rapor_ay INT NOT NULL,
    rapor_yil INT NOT NULL,
    toplam_stok_maliyeti DECIMAL(10, 2),
    toplam_masraflar DECIMAL(10, 2),
    toplam_maliyet DECIMAL(10, 2),
    olusturma_tarihi DATETIME
)
''')
cursor.execute('''
CREATE TABLE IF NOT EXISTS Menu_Kategorileri (
    kategori_id INTEGER PRIMARY KEY AUTOINCREMENT,
    kategori_adi VARCHAR(255) NOT NULL UNIQUE
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS Menu_Urunleri (
    urun_id INTEGER PRIMARY KEY AUTOINCREMENT,
    kategori_id INTEGER,
    urun_adi VARCHAR(255) NOT NULL,
    fiyat DECIMAL(10, 2),
    FOREIGN KEY (kategori_id) REFERENCES Menu_Kategorileri(kategori_id) ON DELETE SET NULL
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS Urun_Reçeteleri (
    recete_kalem_id INTEGER PRIMARY KEY AUTOINCREMENT,
    menu_urun_id INTEGER,
    stok_urun_id INTEGER,
    kullanilan_miktar DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (menu_urun_id) REFERENCES Menu_Urunleri(urun_id) ON DELETE CASCADE,
    FOREIGN KEY (stok_urun_id) REFERENCES Stoklar(urun_id) ON DELETE CASCADE
)
''')
conn.commit()

# --- Core Functions ---

def add_inventory_item(urun_adi, miktar, birim=None, birim_maliyet=None):
    """Adds a new inventory item to the Stoklar table."""
    now_iso = datetime.now().isoformat()
    try:
        cursor.execute('''
        INSERT INTO Stoklar (urun_adi, miktar, birim, birim_maliyet, son_guncelleme_tarihi)
        VALUES (?, ?, ?, ?, ?)
        ''', (urun_adi, miktar, birim, birim_maliyet, now_iso))
        conn.commit()
        return cursor.lastrowid
    except Exception as e:
        conn.rollback()
        print(f"Error adding inventory item: {e}")
        return None


def update_inventory_item(urun_id, miktar=None, birim_maliyet=None):
    """Updates the quantity and/or unit cost of an existing inventory item."""
    now_iso = datetime.now().isoformat()
    updates = []
    params = []
    if miktar is not None:
        updates.append("miktar = ?")
        params.append(miktar)
    if birim_maliyet is not None:
        updates.append("birim_maliyet = ?")
        params.append(birim_maliyet)

    if not updates:
        return False

    updates.append("son_guncelleme_tarihi = ?")
    params.append(now_iso)
    params.append(urun_id)

    query = f'''
    UPDATE Stoklar
    SET {", ".join(updates)}
    WHERE urun_id = ?
    '''
    try:
        cursor.execute(query, params)
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        conn.rollback()
        print(f"Error updating inventory item: {e}")
        return False


def delete_inventory_item(urun_id):
    """Deletes an inventory item from the Stoklar table."""
    try:
        cursor.execute('DELETE FROM Stoklar WHERE urun_id = ?', (urun_id,))
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        conn.rollback()
        print(f"Error deleting inventory item: {e}")
        return False


def view_inventory():
    """Retrieves and returns the current inventory status as a pandas DataFrame."""
    cursor.execute('SELECT * FROM Stoklar')
    rows = cursor.fetchall()
    if not rows:
        return None
    columns = [description[0] for description in cursor.description]
    df = pd.DataFrame(rows, columns=columns)
    return df

def add_invoice(fatura_numarasi, tedarikci_adi, fatura_tarihi, toplam_tutar, odeme_durumu='Beklemede'):
    """Adds a new invoice to the Faturalar table."""
    try:
        cursor.execute('''
        INSERT INTO Faturalar (fatura_numarasi, tedarikci_adi, fatura_tarihi, toplam_tutar, odeme_durumu)
        VALUES (?, ?, ?, ?, ?)
        ''', (fatura_numarasi, tedarikci_adi, fatura_tarihi, toplam_tutar, odeme_durumu))
        conn.commit()
        return cursor.lastrowid
    except sqlite3.IntegrityError:
        conn.rollback()
        print(f"Error adding invoice: Duplicate invoice number '{fatura_numarasi}'")
        return None
    except Exception as e:
        conn.rollback()
        print(f"Error adding invoice: {e}")
        return None


def add_invoice_item(fatura_id, urun_id, miktar, birim_fiyat):
    """
    Adds an invoice item to the Fatura_Kalemleri table and updates the inventory quantity.
    Calculates and updates the birim_maliyet (unit cost) using a weighted average method.
    """
    toplam_fiyat = float(miktar) * float(birim_fiyat)
    try:
        cursor.execute('SELECT miktar, birim_maliyet FROM Stoklar WHERE urun_id = ?', (urun_id,))
        stok_info = cursor.fetchone()

        if not stok_info:
            print(f"Error adding invoice item: Product (ID: {urun_id}) not found in inventory.")
            return False

        current_miktar, current_birim_maliyet = stok_info

        cursor.execute('''
        INSERT INTO Fatura_Kalemleri (fatura_id, urun_id, miktar, birim_fiyat, toplam_fiyat)
        VALUES (?, ?, ?, ?, ?)
        ''', (fatura_id, urun_id, miktar, birim_fiyat, toplam_fiyat))

        if current_miktar is None or float(current_miktar) == 0.0:
             new_birim_maliyet = birim_fiyat
        else:
            current_miktar_dec = float(current_miktar)
            current_birim_maliyet_dec = float(current_birim_maliyet) if current_birim_maliyet is not None else 0.0
            miktar_dec = float(miktar)
            birim_fiyat_dec = float(birim_fiyat)

            total_value = (current_miktar_dec * current_birim_maliyet_dec) + (miktar_dec * birim_fiyat_dec)
            new_total_quantity = current_miktar_dec + miktar_dec
            new_birim_maliyet = total_value / new_total_quantity if new_total_quantity > 0 else 0.0

        new_miktar = float(current_miktar) + float(miktar)
        now_iso = datetime.now().isoformat()
        cursor.execute('''
        UPDATE Stoklar
        SET miktar = ?, birim_maliyet = ?, son_guncelleme_tarihi = ?
        WHERE urun_id = ?
        ''', (new_miktar, new_birim_maliyet, now_iso, urun_id))
        conn.commit()
        return True

    except sqlite3.IntegrityError as e:
        conn.rollback()
        print(f"Error adding invoice item (Integrity Error): {e}")
        return False
    except Exception as e:
        conn.rollback()
        print(f"Error adding invoice item: {e}")
        return False


def calculate_inventory_cost(urun_id, quantity):
    """Calculates the cost of a specific quantity of an inventory item."""
    cursor.execute('SELECT birim_maliyet FROM Stoklar WHERE urun_id = ?', (urun_id,))
    result = cursor.fetchone()
    if result and result[0] is not None:
        birim_maliyet = float(result[0])
        return birim_maliyet * float(quantity)
    else:
        return None

def get_invoice_details(fatura_id):
    """Retrieves a specific invoice and its items from the database."""
    cursor.execute('SELECT * FROM Faturalar WHERE fatura_id = ?', (fatura_id,))
    invoice = cursor.fetchone()

    if not invoice:
        return None, None

    invoice_columns = [description[0] for description in cursor.description]
    invoice_df = pd.DataFrame([invoice], columns=invoice_columns)

    cursor.execute('''
    SELECT fi.*, s.urun_adi
    FROM Fatura_Kalemleri fi
    JOIN Stoklar s ON fi.urun_id = s.urun_id
    WHERE fi.fatura_id = ?
    ''', (fatura_id,))
    items = cursor.fetchall()

    if not items:
        items_df = pd.DataFrame()
    else:
        item_columns = [description[0] for description in cursor.description]
        items_df = pd.DataFrame(items, columns=item_columns)

    return invoice_df, items_df

def add_expense(masraf_aciklamasi, masraf_tarihi, tutar, kategori=None):
    """Adds a new expense to the Masraflar table."""
    try:
        date.fromisoformat(masraf_tarihi)
        cursor.execute('''
        INSERT INTO Masraflar (masraf_aciklamasi, masraf_tarihi, tutar, kategori)
        VALUES (?, ?, ?, ?)
        ''', (masraf_aciklamasi, masraf_tarihi, tutar, kategori))
        conn.commit()
        return cursor.lastrowid
    except ValueError:
        conn.rollback()
        print(f"Error adding expense: Invalid date format '{masraf_tarihi}'. Expected YYYY-MM-DD.")
        return None
    except Exception as e:
        conn.rollback()
        print(f"Error adding expense: {e}")
        return None

def view_expenses():
    """Retrieves and returns all expenses from the Masraflar table as a pandas DataFrame."""
    cursor.execute('SELECT * FROM Masraflar')
    rows = cursor.fetchall()
    if not rows:
        return None
    columns = [description[0] for description in cursor.description]
    df = pd.DataFrame(rows, columns=columns)
    return df

def get_expenses_by_date_range(start_date, end_date):
    """Retrieves expenses within a specified date range and returns them as a pandas DataFrame."""
    try:
        date.fromisoformat(start_date)
        date.fromisoformat(end_date)

        cursor.execute('''
        SELECT * FROM Masraflar
        WHERE masraf_tarihi BETWEEN ? AND ?
        ORDER BY masraf_tarihi
        ''', (start_date, end_date))
        rows = cursor.fetchall()

        if not rows:
            return None

        columns = [description[0] for description in cursor.description]
        df = pd.DataFrame(rows, columns=columns)
        return df
    except ValueError:
        print("Error getting expenses by date range: Invalid date format. Expected YYYY-MM-DD.")
        return None


def generate_monthly_cost_report(report_month, report_year):
    """
    Generates a monthly cost report by calculating total inventory cost (from invoices)
    and general expenses. Inserts the report into the Aylik_Maliyet_Raporlari table.
    """
    cursor.execute('''
    SELECT SUM(fi.toplam_fiyat)
    FROM Fatura_Kalemleri fi
    JOIN Faturalar f ON fi.fatura_id = f.fatura_id
    WHERE STRFTIME('%Y', f.fatura_tarihi) = ? AND STRFTIME('%m', f.fatura_tarihi) = ?
    ''', (str(report_year), f'{report_month:02d}'))
    total_inventory_cost_row = cursor.fetchone()
    total_inventory_cost = total_inventory_cost_row[0] if total_inventory_cost_row and total_inventory_cost_row[0] is not None else 0.0

    cursor.execute('''
    SELECT SUM(tutar)
    FROM Masraflar
    WHERE STRFTIME('%Y', masraf_tarihi) = ? AND STRFTIME('%m', masraf_tarihi) = ?
    ''', (str(report_year), f'{report_month:02d}'))
    total_expenses_row = cursor.fetchone()
    total_general_expenses = total_expenses_row[0] if total_expenses_row and total_expenses_row[0] is not None else 0.0

    total_overall_cost = float(total_inventory_cost) + float(total_general_expenses)
    now_iso = datetime.now().isoformat()

    if float(total_inventory_cost) == 0.0 and float(total_general_expenses) == 0.0:
        return False

    try:
        cursor.execute('''
        INSERT INTO Aylik_Maliyet_Raporlari (rapor_ay, rapor_yil, toplam_stok_maliyeti, toplam_masraflar, toplam_maliyet, olusturma_tarihi)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (report_month, report_year, total_inventory_cost, total_general_expenses, total_overall_cost, now_iso))
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print(f"Error generating monthly cost report: {e}")
        return False


def view_monthly_cost_reports():
    """Retrieves and returns all monthly cost reports as a pandas DataFrame."""
    cursor.execute('SELECT * FROM Aylik_Maliyet_Raporlari')
    rows = cursor.fetchall()

    if not rows:
        return None

    columns = [description[0] for description in cursor.description]
    df = pd.DataFrame(rows, columns=columns)
    return df

def add_menu_category(kategori_adi):
    """Adds a new menu category to the Menu_Kategorileri table."""
    try:
        cursor.execute('''
        INSERT INTO Menu_Kategorileri (kategori_adi)
        VALUES (?)
        ''', (kategori_adi,))
        conn.commit()
        return cursor.lastrowid
    except sqlite3.IntegrityError:
        conn.rollback()
        print(f"Error adding menu category: Category '{kategori_adi}' already exists.")
        return None
    except Exception as e:
        conn.rollback()
        print(f"Error adding menu category: {e}")
        return None

def add_menu_item(kategori_id, urun_adi, fiyat=None):
    """Adds a new menu item to the Menu_Urunleri table."""
    try:
        cursor.execute('''
        INSERT INTO Menu_Urunleri (kategori_id, urun_adi, fiyat)
        VALUES (?, ?, ?)
        ''', (kategori_id, urun_adi, fiyat))
        conn.commit()
        return cursor.lastrowid
    except sqlite3.IntegrityError:
         conn.rollback()
         print(f"Error adding menu item: Item '{urun_adi}' already exists or invalid category ID {kategori_id}.")
         return None
    except Exception as e:
        conn.rollback()
        print(f"Error adding menu item: {e}")
        return None

def add_recipe_item(menu_urun_id, stok_urun_id, kullanilan_miktar):
    """Adds a recipe item (ingredient) for a menu item."""
    try:
        cursor.execute('''
        INSERT INTO Urun_Reçeteleri (menu_urun_id, stok_urun_id, kullanilan_miktar)
        VALUES (?, ?, ?)
        ''', (menu_urun_id, stok_urun_id, kullanilan_miktar))
        conn.commit()
        return cursor.lastrowid
    except sqlite3.IntegrityError as e:
        conn.rollback()
        print(f"Error adding recipe item (Integrity Error): {e}")
        return None
    except Exception as e:
        conn.rollback()
        print(f"Error adding recipe item: {e}")
        return False

def update_recipe_item(recete_kalem_id, menu_urun_id=None, stok_urun_id=None, kullanilan_miktar=None):
    """Updates a recipe item."""
    updates = []
    params = []
    if menu_urun_id is not None:
        updates.append("menu_urun_id = ?")
        params.append(menu_urun_id)
    if stok_urun_id is not None:
        updates.append("stok_urun_id = ?")
        params.append(stok_urun_id)
    if kullanilan_miktar is not None:
        updates.append("kullanilan_miktar = ?")
        params.append(kullanilan_miktar)

    if not updates:
        return False

    params.append(recete_kalem_id)

    query = f'''
    UPDATE Urun_Reçeteleri
    SET {", ".join(updates)}
    WHERE recete_kalem_id = ?
    '''
    try:
        cursor.execute(query, params)
        conn.commit()
        return cursor.rowcount > 0
    except sqlite3.IntegrityError as e:
        conn.rollback()
        print(f"Error updating recipe item (Integrity Error): {e}")
        return False
    except Exception as e:
        conn.rollback()
        print(f"Error updating recipe item: {e}")
        return False

def delete_recipe_item(recete_kalem_id):
    """Deletes a recipe item."""
    try:
        cursor.execute('DELETE FROM Urun_Reçeteleri WHERE recete_kalem_id = ?', (recete_kalem_id,))
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        conn.rollback()
        print(f"Error deleting recipe item: {e}")
        return False

def view_menu_categories():
    """Retrieves and returns all menu categories as a pandas DataFrame."""
    cursor.execute('SELECT * FROM Menu_Kategorileri')
    rows = cursor.fetchall()
    if not rows:
        return None
    columns = [description[0] for description in cursor.description]
    df = pd.DataFrame(rows, columns=columns)
    return df

def view_menu_items():
    """Retrieves and returns all menu items, including category name, as a pandas DataFrame."""
    cursor.execute('''
    SELECT mu.urun_id, mu.urun_adi, mu.fiyat, mk.kategori_adi
    FROM Menu_Urunleri mu
    LEFT JOIN Menu_Kategorileri mk ON mu.kategori_id = mk.kategori_id
    ''')
    rows = cursor.fetchall()
    if not rows:
        return None
    columns = [description[0] for description in cursor.description]
    df = pd.DataFrame(rows, columns=columns)
    return df

def view_recipe_items():
    """Retrieves and returns all recipe items as a pandas DataFrame."""
    cursor.execute('SELECT * FROM Urun_Reçeteleri')
    rows = cursor.fetchall()
    if not rows:
        return None
    columns = [description[0] for description in cursor.description]
    df = pd.DataFrame(rows, columns=columns)
    return df

def view_recipe_items_detailed():
    """Retrieves and returns all recipe items with menu item and stock item names as a pandas DataFrame."""
    cursor.execute('''
    SELECT
        ur.recete_kalem_id,
        mu.urun_adi AS menu_urun_adi,
        s.urun_adi AS stok_urun_adi,
        ur.kullanilan_miktar
    FROM Urun_Reçeteleri ur
    JOIN Menu_Urunleri mu ON ur.menu_urun_id = mu.urun_id
    JOIN Stoklar s ON ur.stok_urun_id = s.urun_id
    ''')
    rows = cursor.fetchall()
    if not rows:
        return None
    columns = [description[0] for description in cursor.description]
    df = pd.DataFrame(rows, columns=columns)
    return df


def calculate_menu_item_cost(menu_urun_id):
    """
    Calculates the cost of a single menu item based on its recipe
    and current stock item unit costs.

    Args:
        menu_urun_id (int): The ID of the menu item.

    Returns:
        float: The total cost of the menu item, or None if the menu item
               is not found or has no recipe/stock cost information.
    """
    cursor.execute('''
    SELECT stok_urun_id, kullanilan_miktar
    FROM Urun_Reçeteleri
    WHERE menu_urun_id = ?
    ''', (menu_urun_id,))
    recipe_items = cursor.fetchall()

    if not recipe_items:
        return None

    total_menu_item_cost = 0.0

    for stok_urun_id, kullanilan_miktar in recipe_items:
        cursor.execute('SELECT birim_maliyet FROM Stoklar WHERE urun_id = ?', (stok_urun_id,))
        stock_cost_info = cursor.fetchone()

        if not stock_cost_info or stock_cost_info[0] is None:
            return None # Return None if any ingredient's cost is unknown

        birim_maliyet = float(stock_cost_info[0])
        item_cost = float(kullanilan_miktar) * birim_maliyet
        total_menu_item_cost += item_cost

    return total_menu_item_cost

def calculate_all_menu_item_costs():
    """
    Calculates the cost for all defined menu items.

    Returns:
        pandas.DataFrame: A DataFrame containing menu item names, IDs,
                          and their calculated costs. Returns None if no
                          menu items are found or no costs can be calculated
                          for any item that has a recipe.
    """
    cursor.execute('SELECT urun_id, urun_adi FROM Menu_Urunleri')
    menu_items = cursor.fetchall()

    if not menu_items:
        return None

    results = []
    all_costs_are_none = True

    for menu_urun_id, urun_adi in menu_items:
        cost = calculate_menu_item_cost(menu_urun_id)
        results.append({'urun_id': menu_urun_id, 'urun_adi': urun_adi, 'maliyet': cost})
        if cost is not None:
            all_costs_are_none = False

    results_df = pd.DataFrame(results)

    if not results_df.empty and all_costs_are_none:
         return None

    return results_df


# --- Flask Application and Routes ---

app = Flask(__name__)
# Need a secret key for flashing messages and sessions
app.config['SECRET_KEY'] = 'your_secret_key_here' # !!! REPLACE WITH A REAL SECRET KEY IN PRODUCTION !!!

# HTML templates (as defined in previous UI step)
BASE_LAYOUT = """
<!doctype html>
<html>
<head><title>Restaurant Inventory Management</title></head>
<body>
    <h1>Restaurant Inventory Management</h1>
    <nav>
        <a href="/">Stok Durumu</a> |
        <a href="/add_inventory">Stok Ekle</a> |
        <a href="/view_expenses">Masrafları Görüntüle/Ekle</a> |
        <a href="/view_reports">Aylık Raporlar</a> |
        <a href="/menu">Menü Yönetimi</a>
    </nav>
    <hr>
    {% with messages = get_flashed_messages() %}
        {% if messages %}
            <ul class=flashes>
            {% for message in messages %}
              <li>{{ message }}</li>
            {% endfor %}
            </ul>
        {% endif %}
    {% endwith %}
    {% block content %}{% endblock %}
</body>
</html>
"""

INVENTORY_TEMPLATE = BASE_LAYOUT + """
{% block content %}
    <h2>Stok Durumu</h2>
    {% if inventory_table %}
        {{ inventory_table | safe }}
    {% else %}
        <p>Stokta hiç ürün bulunmamaktadır.</p>
    {% endif %}
{% endblock %}
"""

ADD_INVENTORY_TEMPLATE = BASE_LAYOUT + """
{% block content %}
    <h2>Yeni Stok Kalemi Ekle</h2>
    <form method="POST" action="{{ url_for('add_inventory_ui') }}">
        Ürün Adı: <input type="text" name="urun_adi" required><br>
        Miktar: <input type="number" step="0.01" name="miktar" required><br>
        Birim (örn: kg, adet): <input type="text" name="birim"><br>
        Birim Maliyet: <input type="number" step="0.01" name="birim_maliyet"><br>
        <input type="submit" value="Ekle">
    </form>
{% endblock %}
"""

EXPENSES_TEMPLATE = BASE_LAYOUT + """
{% block content %}
    <h2>Masraflar</h2>
    {% if expenses_table %}
        {{ expenses_table | safe }}
    {% else %}
        <p>Sistemde hiç masraf bulunmamaktadır.</p>
    {% endif %}
    <h3>Masraf Ekle</h3>
    <form method="POST" action="{{ url_for('add_expense_ui') }}">
        Açıklama: <input type="text" name="masraf_aciklamasi" required><br>
        Tarih (YYYY-MM-DD): <input type="date" name="masraf_tarihi" required><br>
        Tutar: <input type="number" step="0.01" name="tutar" required><br>
        Kategori: <input type="text" name="kategori"><br>
        <input type="submit" value="Ekle">
    </form>
{% endblock %}
"""

REPORTS_TEMPLATE = BASE_LAYOUT + """
{% block content %}
    <h2>Aylık Maliyet Raporları</h2>
    <h3>Rapor Oluştur</h3>
    <form method="POST" action="{{ url_for('generate_report_ui') }}">
        Ay (1-12): <input type="number" name="month" min="1" max="12" required><br>
        Yıl: <input type="number" name="year" min="2000" required><br> {# Adjust min year as needed #}
        <input type="submit" value="Rapor Oluştur">
    </form>
    <hr>
    <h3>Mevcut Raporlar</h3>
    {% if reports_table %}
        {{ reports_table | safe }}
    {% else %}
        <p>Sistemde hiç aylık maliyet raporu bulunmamaktadır.</p>
    {% endif %}
{% endblock %}
"""

MENU_BASE_TEMPLATE = BASE_LAYOUT + """
{% block content %}
    <h2>Menü Yönetimi</h2>
    <nav>
        <a href="{{ url_for('view_menu_categories_ui') }}">Kategoriler</a> |
        <a href="{{ url_for('view_menu_items_ui') }}">Menü Ürünleri</a> |
        <a href="{{ url_for('view_recipes_ui') }}">Reçeteler</a> |
        <a href="{{ url_for('view_menu_item_costs_ui') }}">Menü Ürünü Maliyetleri</a>
    </nav>
    <hr>
    {% block menu_content %}{% endblock %}
{% endblock %}
"""

MENU_CATEGORIES_TEMPLATE = MENU_BASE_TEMPLATE.replace("{% block menu_content %}{% endblock %}", """
{% block menu_content %}
    <h3>Menü Kategorileri</h3>
    {% if categories_table %}
        {{ categories_table | safe }}
    {% else %}
        <p>Sistemde hiç menü kategorisi bulunmamaktadır.</p>
    {% endif %}
    <h4>Yeni Kategori Ekle</h4>
    <form method="POST" action="{{ url_for('add_menu_category_ui') }}">
        Kategori Adı: <input type="text" name="kategori_adi" required><br>
        <input type="submit" value="Ekle">
    </form>
{% endblock %}
""")

MENU_ITEMS_TEMPLATE = MENU_BASE_TEMPLATE.replace("{% block menu_content %}{% endblock %}", """
{% block menu_content %}
    <h3>Menü Ürünleri</h3>
    {% if menu_items_table %}
        {{ menu_items_table | safe }}
    {% else %}
        <p>Sistemde hiç menü ürünü bulunmamaktadır.</p>
    {% endif %}
    <h4>Yeni Menü Ürünü Ekle</h4>
    <form method="POST" action="{{ url_for('add_menu_item_ui') }}">
        Ürün Adı: <input type="text" name="urun_adi" required><br>
        Kategori ID: <input type="number" name="kategori_id" required><br> {# Could use a select dropdown linked to categories #}
        Fiyat: <input type="number" step="0.01" name="fiyat"><br>
        <input type="submit" value="Ekle">
    </form>
{% endblock %}
""")

RECIPES_TEMPLATE = MENU_BASE_TEMPLATE.replace("{% block menu_content %}{% endblock %}", """
{% block menu_content %}
    <h3>Reçeteler</h3>
    {% if recipes_table %}
        {{ recipes_table | safe }}
    {% else %}
        <p>Sistemde hiç reçete kalemi bulunmamaktadır.</p>
    {% endif %}
    <h4>Yeni Reçete Kalemi Ekle</h4>
    <form method="POST" action="{{ url_for('add_recipe_item_ui') }}">
        Menü Ürün ID: <input type="number" name="menu_urun_id" required><br> {# Could use a select dropdown #}
        Stok Ürün ID: <input type="number" name="stok_urun_id" required><br> {# Could use a select dropdown #}
        Kullanılan Miktar: <input type="number" step="0.01" name="kullanilan_miktar" required><br>
        <input type="submit" value="Ekle">
    </form>
    <p>Detaylı reçete görünümü (stok isimleri ile birlikte) için 'view_recipe_items_detailed()' fonksiyonunu kullanabilirsiniz, ancak basitlik adına burada listelenmemiştir.</p>
{% endblock %}
""")

MENU_ITEM_COSTS_TEMPLATE = MENU_BASE_TEMPLATE.replace("{% block menu_content %}{% endblock %}", """
{% block menu_content %}
    <h3>Menü Ürünü Maliyetleri</h3>
    {% if menu_item_costs_table %}
        {{ menu_item_costs_table | safe }}
    {% else %}
        <p>Menü ürünleri için maliyet hesaplanamadı veya hiç menü ürünü bulunmamaktadır (reçete veya stok maliyeti eksik olabilir).</p>
    {% endif %}
{% endblock %}
""")


@app.route('/')
def index():
    """Displays the current inventory status."""
    df = view_inventory()
    inventory_table = df.to_html() if df is not None and not df.empty else None
    return render_template_string(INVENTORY_TEMPLATE, inventory_table=inventory_table)

@app.route('/add_inventory', methods=['GET', 'POST'])
def add_inventory_ui():
    """Handles adding a new inventory item."""
    if request.method == 'POST':
        try:
            urun_adi = request.form['urun_adi']
            miktar = float(request.form['miktar'])
            birim = request.form.get('birim')
            birim_maliyet = request.form.get('birim_maliyet')
            birim_maliyet = float(birim_maliyet) if birim_maliyet else None

            add_inventory_item(urun_adi, miktar, birim, birim_maliyet)
            flash(f"Ürün '{urun_adi}' başarıyla eklendi.")
        except ValueError:
            flash("Hata: Miktar veya Birim Maliyet için geçerli bir sayı girin.")
        except Exception as e:
            flash(f"Hata oluştu: {e}")
        return redirect(url_for('add_inventory_ui'))

    return render_template_string(ADD_INVENTORY_TEMPLATE)


@app.route('/view_expenses')
def view_expenses_ui():
    """Displays all expenses and a form to add new ones."""
    df = view_expenses()
    expenses_table = df.to_html() if df is not None and not df.empty else None
    return render_template_string(EXPENSES_TEMPLATE, expenses_table=expenses_table)

@app.route('/add_expense_ui', methods=['POST'])
def add_expense_ui():
    """Handles adding a new expense from the UI."""
    try:
        masraf_aciklamasi = request.form['masraf_aciklamasi']
        masraf_tarihi_str = request.form['masraf_tarihi']
        tutar = float(request.form['tutar'])
        kategori = request.form.get('kategori')

        date.fromisoformat(masraf_tarihi_str)

        add_expense(masraf_aciklamasi, masraf_tarihi_str, tutar, kategori)
        flash(f"Masraf '{masraf_aciklamasi}' başarıyla eklendi.")
    except ValueError:
        flash("Hata: Tutar için geçerli bir sayı veya Tarih için geçerli format (YYYY-MM-DD) girin.")
    except Exception as e:
        flash(f"Hata oluştu: {e}")

    return redirect(url_for('view_expenses_ui'))


@app.route('/view_reports')
def view_reports_ui():
    """Displays all monthly cost reports and a form to generate new ones."""
    df = view_monthly_cost_reports()
    reports_table = df.to_html() if df is not None and not df.empty else None
    return render_template_string(REPORTS_TEMPLATE, reports_table=reports_table)

@app.route('/generate_report_ui', methods=['POST'])
def generate_report_ui():
    """Generates a monthly cost report from UI input."""
    try:
        month = int(request.form['month'])
        year = int(request.form['year'])

        if not (1 <= month <= 12):
            flash("Hata: Geçerli bir ay (1-12) girin.")
        else:
            report_generated = generate_monthly_cost_report(month, year)
            if report_generated:
                 flash(f"{month}/{year} dönemi için rapor başarıyla oluşturuldu.")
            else:
                 flash(f"{month}/{year} dönemi için rapor oluşturulamadı (veri bulunamadı).")

    except ValueError:
        flash("Hata: Ay ve Yıl için geçerli sayılar girin.")
    except Exception as e:
        flash(f"Hata oluştu: {e}")

    return redirect(url_for('view_reports_ui'))

# --- Menu Management Routes ---

@app.route('/menu')
def menu_management_base():
    """Base page for menu management."""
    return render_template_string(MENU_BASE_TEMPLATE)


@app.route('/menu/categories')
def view_menu_categories_ui():
    """Displays all menu categories and a form to add new ones."""
    df = view_menu_categories()
    categories_table = df.to_html() if df is not None and not df.empty else None
    return render_template_string(MENU_CATEGORIES_TEMPLATE, categories_table=categories_table)

@app.route('/menu/categories/add', methods=['POST'])
def add_menu_category_ui():
    """Handles adding a new menu category from the UI."""
    try:
        kategori_adi = request.form['kategori_adi']
        cat_id = add_menu_category(kategori_adi)
        if cat_id is not None:
            flash(f"Menü kategorisi '{kategori_adi}' başarıyla eklendi (ID: {cat_id}).")
        else:
            flash(f"Hata: Menü kategorisi '{kategori_adi}' zaten mevcut veya bir hata oluştu.")
    except Exception as e:
        flash(f"Hata oluştu: {e}")
    return redirect(url_for('view_menu_categories_ui'))


@app.route('/menu/items')
def view_menu_items_ui():
    """Displays all menu items and a form to add new ones."""
    df = view_menu_items()
    menu_items_table = df.to_html() if df is not None and not df.empty else None
    return render_template_string(MENU_ITEMS_TEMPLATE, menu_items_table=menu_items_table)

@app.route('/menu/items/add', methods=['POST'])
def add_menu_item_ui():
    """Handles adding a new menu item from the UI."""
    try:
        kategori_id = int(request.form['kategori_id']) # Ensure integer
        urun_adi = request.form['urun_adi']
        fiyat_str = request.form.get('fiyat')
        fiyat = float(fiyat_str) if fiyat_str else None

        menu_item_id = add_menu_item(kategori_id, urun_adi, fiyat)
        if menu_item_id is not None:
             flash(f"Menü ürünü '{urun_adi}' başarıyla eklendi (ID: {menu_item_id}).")
        else:
             flash(f"Hata: Menü ürünü '{urun_adi}' zaten mevcut veya kategori ID {kategori_id} geçersiz.")

    except ValueError:
         flash("Hata: Kategori ID veya Fiyat için geçerli bir sayı girin.")
    except Exception as e:
        flash(f"Hata oluştu: {e}")
    return redirect(url_for('view_menu_items_ui'))


@app.route('/menu/recipes')
def view_recipes_ui():
    """Displays all recipe items and a form to add new ones."""
    df = view_recipe_items_detailed()
    recipes_table = df.to_html() if df is not None and not df.empty else None
    return render_template_string(RECIPES_TEMPLATE, recipes_table=recipes_table)

@app.route('/menu/recipes/add', methods=['POST'])
def add_recipe_item_ui():
    """Handles adding a new recipe item from the UI."""
    try:
        menu_urun_id = int(request.form['menu_urun_id'])
        stok_urun_id = int(request.form['stok_urun_id'])
        kullanilan_miktar = float(request.form['kullanilan_miktar'])

        recipe_item_id = add_recipe_item(menu_urun_id, stok_urun_id, kullanilan_miktar)
        if recipe_item_id is not None:
            flash(f"Reçete kalemi başarıyla eklendi (ID: {recipe_item_id}).")
        else:
            flash(f"Hata: Reçete kalemi eklenemedi. Menü Ürün ID {menu_urun_id} veya Stok Ürün ID {stok_urun_id} geçersiz olabilir.")

    except ValueError:
         flash("Hata: Menü Ürün ID, Stok Ürün ID veya Kullanılan Miktar için geçerli sayılar girin.")
    except Exception as e:
        flash(f"Hata oluştu: {e}")
    return redirect(url_for('view_recipes_ui'))


@app.route('/menu/item_costs')
def view_menu_item_costs_ui():
    """Displays the calculated costs for all menu items."""
    df = calculate_all_menu_item_costs()
    if df is not None:
         df['maliyet'] = df['maliyet'].apply(lambda x: f"{x:.2f}" if pd.notna(x) else "N/A")

    menu_item_costs_table = df.to_html() if df is not None and not df.empty else None
    return render_template_string(MENU_ITEM_COSTS_TEMPLATE, menu_item_costs_table=menu_item_costs_table)

# --- API Endpoint ---

@app.route('/sales', methods=['POST'])
def receive_sales_data():
    """
    Receives sales data from a POS system and updates inventory.
    Expected JSON format:
    [
        {"product_id": 1, "quantity_sold": 5.0, "timestamp": "2023-10-27T10:00:00Z"},
        ...
    ]
    Note: This API currently expects 'product_id' which should correspond to 'urun_id' in the Stoklar table.
    For integration with POS systems selling 'Menu_Urunleri', this logic would need to be updated
    to find the Menu_Urunleri by their ID or name and then use their recipes to decrement Stoklar.
    """
    if not request.is_json:
        return jsonify({"message": "Invalid input, JSON required"}), 415

    sales_data = request.get_json()

    if not isinstance(sales_data, list):
         return jsonify({"message": "Invalid input, JSON array of sales records required"}), 400

    results = []
    success_count = 0
    error_count = 0

    for sale_record in sales_data:
        product_id = sale_record.get('product_id')
        quantity_sold = sale_record.get('quantity_sold')
        timestamp_str = sale_record.get('timestamp')

        if product_id is None or quantity_sold is None:
            results.append({"record": sale_record, "status": "failure", "message": "Missing 'product_id' or 'quantity_sold'"})
            error_count += 1
            continue

        try:
            quantity_sold = float(quantity_sold)
            if quantity_sold < 0:
                 results.append({"record": sale_record, "status": "failure", "message": "Quantity sold cannot be negative"})
                 error_count += 1
                 continue

            cursor.execute('SELECT miktar FROM Stoklar WHERE urun_id = ?', (product_id,))
            row = cursor.fetchone()

            if row:
                current_quantity = row[0]
                if current_quantity >= quantity_sold:
                    new_quantity = current_quantity - quantity_sold
                    now = datetime.now().isoformat()
                    cursor.execute('''
                    UPDATE Stoklar
                    SET miktar = ?, son_guncelleme_tarihi = ?
                    WHERE urun_id = ?
                    ''', (new_quantity, now, product_id))
                    conn.commit()
                    results.append({"record": sale_record, "status": "success", "message": "Inventory updated"})
                    success_count += 1
                else:
                    conn.rollback()
                    results.append({"record": sale_record, "status": "failure", "message": f"Insufficient stock for product ID {product_id}. Available: {current_quantity}"})
                    error_count += 1
            else:
                conn.rollback()
                results.append({"record": sale_record, "status": "failure", "message": f"Product ID {product_id} not found in inventory"})
                error_count += 1

        except ValueError:
            results.append({"record": sale_record, "status": "failure", "message": "Invalid quantity_sold value"})
            error_count += 1
        except Exception as e:
            conn.rollback()
            results.append({"record": sale_record, "status": "failure", "message": f"An error occurred: {e}"})
            error_count += 1

    if error_count == 0:
        return jsonify({"message": "All sales records processed successfully", "results": results}), 200
    elif success_count > 0:
         return jsonify({"message": f"{success_count} sales records processed successfully, {error_count} failed", "results": results}), 207
    else:
        return jsonify({"message": "All sales records failed to process", "results": results}), 400


# --- How to run the Flask app (Conceptual in Notebook) ---

# To run this Flask app in a standard Python environment (e.g., your local machine):
# Save this code to a file named app.py
# Open a terminal in the same directory
# Make sure you have Flask and pandas installed: pip install Flask pandas
# Uncomment the line below to run the development server:
# if __name__ == '__main__':
    # WARNING: Do NOT use debug=True in a production environment!
    # For production, use a production-ready WSGI server like Gunicorn or uWSGI.
    # Example using Gunicorn: gunicorn app:app -w 4 (assuming this code is in app.py)
    # app.run(debug=True)
