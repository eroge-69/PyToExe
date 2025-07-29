import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import sqlite3
import os

# === Veritabanı Başlat ===
# Veritabanı dosyası yoksa oluşturulur
db = sqlite3.connect("terminalsoft.db")
cursor = db.cursor()

# Sales tablosunu oluştur (mevcutsa atla)
cursor.execute("""CREATE TABLE IF NOT EXISTS sales (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_name TEXT,
    price_at_sale REAL,
    quantity INTEGER,
    timestamp TEXT,
    is_complimentary INTEGER,
    table_id TEXT
)""")

# Products tablosunu oluştur (ürün adı benzersiz olmalı)
cursor.execute("""CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE,
    price REAL,
    stock INTEGER
)""")

# Settings tablosunu oluştur (anahtar-değer çiftleri için)
cursor.execute("""CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT
)""")

# Örnek ürünleri ekle (tablo boşsa)
# Bu kısım sadece ilk çalıştırmada ürün eklemek içindir.
# Yönetici paneli eklendiğinde buradan ürün eklemeye gerek kalmayacak.
# Ürünlerin zaten ekli olup olmadığını kontrol edelim
cursor.execute("SELECT COUNT(*) FROM products")
if cursor.fetchone()[0] == 0:
    cursor.execute("INSERT INTO products (name, price, stock) VALUES (?, ?, ?)", ("Kahve", 25.0, 50))
    cursor.execute("INSERT INTO products (name, price, stock) VALUES (?, ?, ?)", ("Çay", 15.0, 70))
    cursor.execute("INSERT INTO products (name, price, stock) VALUES (?, ?, ?)", ("Sandviç", 40.0, 30))
    cursor.execute("INSERT INTO products (name, price, stock) VALUES (?, ?, ?)", ("Kek", 20.0, 25))
    cursor.execute("INSERT INTO products (name, price, stock) VALUES (?, ?, ?)", ("Su", 10.0, 100))
    db.commit()

# === Tema Ayarları ===
reklam_renk = "#FFD700"  # Altın sarısı
reklam_bg = "#2C3E50"    # Koyu gri/mavi
reklam_font = ("Arial", 14, "bold")
ana_bg = "gray15"
panel_bg = "gray25"
text_fg = "white"
button_bg = "#34495E" # Daha koyu gri/mavi
button_fg = "white"
entry_bg = "#4A607C" # Açık gri/mavi
entry_fg = "white"

# === Global Değişkenler ===
current_cart = [] # Sepetteki ürünler: [{"product_id": id, "name": "...", "price": ..., "quantity": ..., "is_complimentary": False}]
current_table = "Masa 1" # Varsayılan masa
tables_data = {} # Açık masaların sepetlerini tutacak: {"Masa 1": [], "Masa 2": []}
customer_display_window = None # Müşteri ekranı penceresi

# Ayarları veritabanından yükle veya varsayılan değerleri kullan
def load_settings():
    global business_name, customer_display_idle_text
    cursor.execute("SELECT value FROM settings WHERE key = 'business_name'")
    business_name_data = cursor.fetchone()
    business_name = business_name_data[0] if business_name_data else "TerminalSoft POS"

    cursor.execute("SELECT value FROM settings WHERE key = 'customer_display_idle_text'")
    customer_display_idle_text_data = cursor.fetchone()
    customer_display_idle_text = customer_display_idle_text_data[0] if customer_display_idle_text_data else "Hoş Geldiniz!"

load_settings()

# === Arayüz ===
win = tk.Tk()
win.title(f"{business_name} - {current_table}") # Başlığı işletme adıyla güncelle
win.geometry("900x700")
win.configure(bg=ana_bg)

# === Reklam Paneli ===
reklam_var = tk.StringVar()
reklam_lbl = tk.Label(win, textvariable=reklam_var, font=reklam_font, fg=reklam_renk, bg=reklam_bg)
reklam_lbl.pack(fill="x", pady=(0, 5))

def reklam_guncelle():
    cursor.execute("SELECT name, stock FROM products WHERE stock <= 5 AND stock > 0") # Stok 0'dan büyük ve 5'ten az olanları göster
    az_stoklu_urunler = cursor.fetchall()
    
    aktif = []
    for urun, adet in az_stoklu_urunler:
        aktif.append(f"{urun} son {adet} adet!")
    
    # "Stok durumu iyi." yazısını kaldırdık, sadece az stoklu ürünler varsa göster
    reklam_var.set(" | ".join(aktif) if aktif else "") 

reklam_guncelle()

# === Ana Çerçeve (Ürünler, Sepet, Kontroller) ===
main_frame = tk.Frame(win, bg=ana_bg)
main_frame.pack(fill="both", expand=True, padx=10, pady=10)

# Sol Panel (Ürün Girişi ve Butonlar)
left_panel = tk.Frame(main_frame, bg=panel_bg, width=300)
left_panel.pack(side="left", fill="y", padx=(0, 10))

tk.Label(left_panel, text="Ürün Kodu / Adı:", bg=panel_bg, fg=text_fg, font=("Arial", 12)).pack(pady=(10, 5))
product_entry = tk.Entry(left_panel, font=("Arial", 14), bg=entry_bg, fg=entry_fg, insertbackground=text_fg, width=25)
product_entry.pack(pady=5, padx=10)
product_entry.focus_set() # Uygulama açıldığında odak bu alanda olsun

def add_product_to_cart(event=None):
    product_query = product_entry.get().strip()
    if not product_query:
        messagebox.showwarning("Uyarı", "Lütfen bir ürün kodu veya adı girin.")
        return

    # Ürünü veritabanından ara
    # Hem isme göre hem de ID'ye göre arama yapalım
    cursor.execute("SELECT id, name, price, stock FROM products WHERE name LIKE ? OR id = ?", (f"%{product_query}%", product_query))
    product_data = cursor.fetchone()

    if product_data:
        product_id, name, price, stock = product_data
        
        # Sepette aynı ürün var mı kontrol et
        found_in_cart = False
        for item in current_cart:
            if item["product_id"] == product_id and not item["is_complimentary"]: # İkram olmayan aynı ürünü bul
                if stock > item["quantity"]: # Stok yeterliyse
                    item["quantity"] += 1
                    found_in_cart = True
                    break
                else:
                    messagebox.showwarning("Stok Uyarısı", f"{name} için yeterli stok yok!")
                    return

        if not found_in_cart:
            if stock > 0:
                current_cart.append({"product_id": product_id, "name": name, "price": price, "quantity": 1, "is_complimentary": False})
            else:
                messagebox.showwarning("Stok Uyarısı", f"{name} stokta kalmadı!")
                return
        
        update_cart_display()
        product_entry.delete(0, tk.END) # Giriş alanını temizle
        reklam_guncelle() # Stok durumunu güncelle
    else:
        messagebox.showwarning("Ürün Bulunamadı", f"'{product_query}' adında bir ürün bulunamadı.")
    
    product_entry.focus_set() # Odak tekrar giriş alanına gelsin

product_entry.bind("<Return>", add_product_to_cart) # Enter tuşu ile sepete ekle

add_to_cart_btn = tk.Button(left_panel, text="Sepete Ekle", command=add_product_to_cart,
                            font=("Arial", 12, "bold"), bg=button_bg, fg=button_fg, width=20, height=2)
add_to_cart_btn.pack(pady=10, padx=10)

# === Sepet Görüntüleme Paneli ===
right_panel = tk.Frame(main_frame, bg=panel_bg)
right_panel.pack(side="right", fill="both", expand=True)

tk.Label(right_panel, text="Mevcut Sepet", bg=panel_bg, fg=text_fg, font=("Arial", 14, "bold")).pack(pady=10)

cart_tree = ttk.Treeview(right_panel, columns=("Urun", "Adet", "Fiyat", "Toplam"), show="headings")
cart_tree.heading("Urun", text="Ürün")
cart_tree.heading("Adet", text="Adet")
cart_tree.heading("Fiyat", text="Birim Fiyat")
cart_tree.heading("Toplam", text="Toplam")

cart_tree.column("Urun", width=150)
cart_tree.column("Adet", width=50, anchor="center")
cart_tree.column("Fiyat", width=80, anchor="e")
cart_tree.column("Toplam", width=80, anchor="e")

cart_tree.pack(fill="both", expand=True, padx=10, pady=5)

total_label = tk.Label(right_panel, text="Toplam: 0.00 ₺", bg=panel_bg, fg=reklam_renk, font=("Arial", 16, "bold"))
total_label.pack(pady=10)

def update_cart_display():
    for i in cart_tree.get_children():
        cart_tree.delete(i)
    
    current_total = 0.0
    for item in current_cart:
        item_total = item["price"] * item["quantity"]
        if item["is_complimentary"]:
            # İkram ise toplamı etkilemez, Treeview'de 0.00 göster
            cart_tree.insert("", "end", values=(f"{item['name']} (İkram)", item["quantity"], f"{item['price']:.2f}", f"{0.00:.2f}"))
        else:
            current_total += item_total
            cart_tree.insert("", "end", values=(item["name"], item["quantity"], f"{item['price']:.2f}", f"{item_total:.2f}"))
            
    total_label.config(text=f"Toplam: {current_total:.2f} ₺")
    update_customer_display() # Müşteri ekranını da güncelle

# === Sepet Kontrol Butonları ===
cart_control_frame = tk.Frame(right_panel, bg=panel_bg)
cart_control_frame.pack(pady=10)

def remove_selected_from_cart():
    selected_items = cart_tree.selection()
    if not selected_items:
        messagebox.showwarning("Uyarı", "Lütfen sepetten kaldırmak istediğiniz bir ürün seçin.")
        return
    
    # Sadece ilk seçilen ürünü işleyelim, çoklu seçimde karmaşıklık artar
    item_id = selected_items[0]
    
    # Treeview'den seçilen öğenin değerlerini al
    item_values = cart_tree.item(item_id, 'values')
    product_name_in_tree = item_values[0].replace(" (İkram)", "") # İkram ibaresini kaldır
    
    # current_cart listesinden ürünü bul ve güncelle/kaldır
    for i, item in enumerate(current_cart):
        # Ürün adı ve ikram durumu ile eşleştirme yapalım
        if item["name"] == product_name_in_tree and (("İkram" in item_values[0]) == item["is_complimentary"]):
            if item["quantity"] > 1:
                item["quantity"] -= 1
            else:
                current_cart.pop(i)
            break
    update_cart_display()
    reklam_guncelle() # Stok durumunu güncelle

def clear_cart():
    if messagebox.askyesno("Sepeti Temizle", "Sepeti tamamen temizlemek istediğinizden emin misiniz?"):
        current_cart.clear()
        update_cart_display()
        reklam_guncelle() # Stok durumunu güncelle

def mark_as_complimentary():
    selected_items = cart_tree.selection()
    if not selected_items:
        messagebox.showwarning("Uyarı", "Lütfen ikram olarak işaretlemek istediğiniz bir ürün seçin.")
        return
    
    # Sadece ilk seçilen ürünü ikram yapalım
    item_id = selected_items[0]
    item_values = cart_tree.item(item_id, 'values')
    product_name_in_tree = item_values[0].replace(" (İkram)", "")
    
    for item in current_cart:
        if item["name"] == product_name_in_tree:
            item["is_complimentary"] = not item["is_complimentary"] # Toggle ikram durumu
            break
    update_cart_display()

remove_btn = tk.Button(cart_control_frame, text="Seçileni Kaldır", command=remove_selected_from_cart,
                       font=("Arial", 10), bg=button_bg, fg=button_fg, width=15)
remove_btn.pack(side="left", padx=5)

clear_btn = tk.Button(cart_control_frame, text="Sepeti Temizle", command=clear_cart,
                      font=("Arial", 10), bg=button_bg, fg=button_fg, width=15)
clear_btn.pack(side="left", padx=5)

complimentary_btn = tk.Button(cart_control_frame, text="İkram Yap/Geri Al", command=mark_as_complimentary,
                              font=("Arial", 10), bg=button_bg, fg=button_fg, width=15)
complimentary_btn.pack(side="left", padx=5)

# === Ödeme ve Fiş Butonları ===
checkout_frame = tk.Frame(right_panel, bg=panel_bg)
checkout_frame.pack(pady=10)

def process_checkout():
    if not current_cart:
        messagebox.showwarning("Uyarı", "Sepet boş. Satış yapılamaz.")
        return
    
    # Toplam tutarı doğru hesapla
    current_total_for_checkout = sum(item["price"] * item["quantity"] for item in current_cart if not item["is_complimentary"])

    if messagebox.askyesno("Ödeme Onayı", f"Toplam {current_total_for_checkout:.2f} ₺ tutarındaki siparişi tamamlamak istiyor musunuz?"):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Fişi göstermeden önce sepetin bir kopyasını al, çünkü satış sonrası sepet temizlenecek
        receipt_cart_copy = list(current_cart) 

        for item in current_cart:
            # Stoktan düş (ikram olsa bile stoktan düşer)
            cursor.execute("UPDATE products SET stock = stock - ? WHERE id = ?", (item["quantity"], item["product_id"]))
            
            # Satış kaydını ekle
            price_for_sale = item["price"] if not item["is_complimentary"] else 0.0 # İkramsa fiyat 0 olarak kaydedilir
            cursor.execute("INSERT INTO sales (product_name, price_at_sale, quantity, timestamp, is_complimentary, table_id) VALUES (?, ?, ?, ?, ?, ?)",
                           (item["name"], price_for_sale, item["quantity"], timestamp, 1 if item["is_complimentary"] else 0, current_table))
            
        db.commit()
        show_receipt(current_total_for_checkout, receipt_cart_copy) # Fişe sepet kopyasını gönder
        current_cart.clear()
        update_cart_display()
        reklam_guncelle() # Stok durumunu güncelle
        messagebox.showinfo("Satış Tamamlandı", "Satış başarıyla kaydedildi.")

checkout_btn = tk.Button(checkout_frame, text="Ödeme Al / Satışı Tamamla", command=process_checkout,
                         font=("Arial", 14, "bold"), bg="#27AE60", fg="white", width=25, height=2) # Yeşil
checkout_btn.pack(padx=5)

# show_receipt fonksiyonunu güncelleyelim, sepet kopyasını alacak şekilde
def show_receipt(total_amount, cart_items_for_receipt):
    receipt_window = tk.Toplevel(win)
    receipt_window.title("Fiş")
    receipt_window.geometry("350x450") # Boyutu biraz büyüttük
    receipt_window.configure(bg="white")
    
    tk.Label(receipt_window, text=f"--- {business_name} FİŞ ---", font=("Consolas", 14, "bold"), bg="white").pack(pady=10)
    
    receipt_text = tk.Text(receipt_window, height=15, width=40, font=("Consolas", 10), bg="white")
    receipt_text.pack(padx=10, pady=5)
    
    receipt_text.insert(tk.END, f"Masa: {current_table}\n")
    receipt_text.insert(tk.END, f"Tarih: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    receipt_text.insert(tk.END, "="*38 + "\n")
    receipt_text.insert(tk.END, f"{'Ürün':<20} {'Adet':>5} {'Tutar':>10}\n")
    receipt_text.insert(tk.END, "-"*38 + "\n")
    
    for item in cart_items_for_receipt: # Satış anındaki sepet kopyasını kullan
        item_total = item["price"] * item["quantity"]
        if item["is_complimentary"]:
            receipt_text.insert(tk.END, f"{item['name']} (İkram):{item['quantity']:>5} {0.00:>10.2f}\n")
        else:
            receipt_text.insert(tk.END, f"{item['name']:<20} {item['quantity']:>5} {item_total:>10.2f}\n")
            
    receipt_text.insert(tk.END, "="*38 + "\n")
    receipt_text.insert(tk.END, f"Toplam: {total_amount:>28.2f} ₺\n")
    receipt_text.insert(tk.END, "="*38 + "\n")
    receipt_text.insert(tk.END, "Bizi tercih ettiğiniz için teşekkürler!\n")
    
    receipt_text.config(state=tk.DISABLED) # Sadece okunabilir yap

    tk.Button(receipt_window, text="Kapat", command=receipt_window.destroy,
              font=("Arial", 10), bg=button_bg, fg=button_fg).pack(pady=10)

# === Müşteri Ekranı Fonksiyonları ===
def create_customer_display():
    global customer_display_window
    if customer_display_window and customer_display_window.winfo_exists():
        customer_display_window.lift() # Zaten açıksa öne getir
        return
    
    customer_display_window = tk.Toplevel(win)
    customer_display_window.title("Müşteri Ekranı")
    customer_display_window.geometry("800x600") # Büyük bir boyut verelim
    customer_display_window.configure(bg="black")
    
    # Müşteri ekranı için etiketler
    customer_display_window.lbl_business_name = tk.Label(customer_display_window, text=business_name, font=("Arial", 24, "bold"), fg=reklam_renk, bg="black")
    customer_display_window.lbl_business_name.pack(pady=(10, 5))

    customer_display_window.lbl_cart_items = tk.Label(customer_display_window, text="", font=("Arial", 20), fg="white", bg="black", justify="left", anchor="nw")
    customer_display_window.lbl_cart_items.pack(fill="both", expand=True, padx=20, pady=20)
    
    customer_display_window.lbl_total = tk.Label(customer_display_window, text="Toplam: 0.00 ₺", font=("Arial", 36, "bold"), fg=reklam_renk, bg="black")
    customer_display_window.lbl_total.pack(pady=20)

    # Pencere kapatıldığında global değişkeni sıfırla
    customer_display_window.protocol("WM_DELETE_WINDOW", close_customer_display)
    
    update_customer_display()

def close_customer_display():
    global customer_display_window
    if customer_display_window:
        customer_display_window.destroy()
        customer_display_window = None

def update_customer_display():
    if customer_display_window and customer_display_window.winfo_exists():
        customer_display_window.lbl_business_name.config(text=business_name) # İşletme adını güncelle
        if not current_cart:
            # Sepet boşsa reklam metni ve görseli göster
            # Eğer ayarlar metni boşsa varsayılan metni kullan
            display_text = customer_display_idle_text if customer_display_idle_text else "Hoş Geldiniz!" 
            customer_display_window.lbl_cart_items.config(text=display_text, font=("Arial", 30), fg="white", image="", compound="none") # image ve compound temizlendi
            customer_display_window.lbl_total.config(text="", image="", compound="none") # image ve compound temizlendi
        else:
            cart_text = ""
            current_total = 0.0
            for item in current_cart:
                item_total = item["price"] * item["quantity"]
                if item["is_complimentary"]:
                    cart_text += f"{item['name']} (İkram) x{item['quantity']} = 0.00 ₺\n"
                else:
                    current_total += item_total
                    cart_text += f"{item['name']} x{item['quantity']} = {item_total:.2f} ₺\n"
            
            customer_display_window.lbl_cart_items.config(text=cart_text, font=("Arial", 20), fg="white", image="", compound="none") # image ve compound temizlendi
            customer_display_window.lbl_total.config(text=f"Toplam: {current_total:.2f} ₺", font=("Arial", 36, "bold"), fg=reklam_renk, image="", compound="none") # image ve compound temizlendi

# Müşteri Ekranı Butonu
customer_display_btn = tk.Button(left_panel, text="Müşteri Ekranını Aç", command=create_customer_display,
                                 font=("Arial", 12), bg=button_bg, fg=button_fg, width=20, height=2)
customer_display_btn.pack(pady=10, padx=10)

# === Ayarlar Paneli ===
def open_settings_window():
    settings_window = tk.Toplevel(win)
    settings_window.title("Ayarlar")
    settings_window.geometry("400x300")
    settings_window.configure(bg=panel_bg)

    # İşletme Adı Ayarı
    tk.Label(settings_window, text="İşletme Adı:", bg=panel_bg, fg=text_fg, font=("Arial", 12)).pack(pady=(10, 5))
    business_name_entry = tk.Entry(settings_window, font=("Arial", 12), bg=entry_bg, fg=entry_fg, insertbackground=text_fg, width=30)
    business_name_entry.insert(0, business_name) # Mevcut değeri göster
    business_name_entry.pack(pady=5)

    # Müşteri Ekranı Boşta Metni Ayarı
    tk.Label(settings_window, text="Müşteri Ekranı Boşta Metni:", bg=panel_bg, fg=text_fg, font=("Arial", 12)).pack(pady=(10, 5))
    idle_text_entry = tk.Entry(settings_window, font=("Arial", 12), bg=entry_bg, fg=entry_fg, insertbackground=text_fg, width=30)
    idle_text_entry.insert(0, customer_display_idle_text) # Mevcut değeri göster
    idle_text_entry.pack(pady=5)

    def save_settings():
        global business_name, customer_display_idle_text
        new_business_name = business_name_entry.get().strip()
        new_idle_text = idle_text_entry.get().strip()

        if new_business_name:
            business_name = new_business_name
            cursor.execute("REPLACE INTO settings (key, value) VALUES (?, ?)", ('business_name', business_name))
        
        customer_display_idle_text = new_idle_text
        cursor.execute("REPLACE INTO settings (key, value) VALUES (?, ?)", ('customer_display_idle_text', customer_display_idle_text))
        
        db.commit()
        
        # Ana pencere ve müşteri ekranı başlığını/içeriğini güncelle
        win.title(f"{business_name} - {current_table}")
        if customer_display_window and customer_display_window.winfo_exists():
            update_customer_display() # Müşteri ekranını güncelle
            customer_display_window.lbl_business_name.config(text=business_name) # İşletme adını güncelle
            
        messagebox.showinfo("Ayarlar", "Ayarlar başarıyla kaydedildi.")
        settings_window.destroy()

    save_btn = tk.Button(settings_window, text="Ayarları Kaydet", command=save_settings,
                         font=("Arial", 12, "bold"), bg="#27AE60", fg="white", width=20, height=2)
    save_btn.pack(pady=20)

# Ayarlar Butonu
settings_btn = tk.Button(left_panel, text="Ayarlar", command=open_settings_window,
                         font=("Arial", 12), bg=button_bg, fg=button_fg, width=20, height=2)
settings_btn.pack(pady=10, padx=10)

# === Stok Yönetimi Paneli ===
def open_stock_management_window():
    stock_window = tk.Toplevel(win)
    stock_window.title("Stok Yönetimi")
    stock_window.geometry("700x500")
    stock_window.configure(bg=panel_bg)

    # Ürün Listesi Treeview
    stock_tree = ttk.Treeview(stock_window, columns=("ID", "Ürün Adı", "Fiyat", "Stok"), show="headings")
    stock_tree.heading("ID", text="ID")
    stock_tree.heading("Ürün Adı", text="Ürün Adı")
    stock_tree.heading("Fiyat", text="Fiyat")
    stock_tree.heading("Stok", text="Stok")

    stock_tree.column("ID", width=50, anchor="center")
    stock_tree.column("Ürün Adı", width=200)
    stock_tree.column("Fiyat", width=100, anchor="e")
    stock_tree.column("Stok", width=100, anchor="center")
    stock_tree.pack(fill="both", expand=True, padx=10, pady=10)

    def load_products_to_stock_tree():
        for i in stock_tree.get_children():
            stock_tree.delete(i)
        cursor.execute("SELECT id, name, price, stock FROM products ORDER BY name")
        products = cursor.fetchall()
        for product in products:
            stock_tree.insert("", "end", values=product)
    
    load_products_to_stock_tree()

    # Ürün Bilgileri Giriş Alanları
    input_frame = tk.Frame(stock_window, bg=panel_bg)
    input_frame.pack(pady=10)

    tk.Label(input_frame, text="Ürün Adı:", bg=panel_bg, fg=text_fg).grid(row=0, column=0, padx=5, pady=2, sticky="w")
    product_name_entry = tk.Entry(input_frame, bg=entry_bg, fg=entry_fg, insertbackground=text_fg)
    product_name_entry.grid(row=0, column=1, padx=5, pady=2)

    tk.Label(input_frame, text="Fiyat:", bg=panel_bg, fg=text_fg).grid(row=1, column=0, padx=5, pady=2, sticky="w")
    product_price_entry = tk.Entry(input_frame, bg=entry_bg, fg=entry_fg, insertbackground=text_fg)
    product_price_entry.grid(row=1, column=1, padx=5, pady=2)

    tk.Label(input_frame, text="Stok:", bg=panel_bg, fg=text_fg).grid(row=2, column=0, padx=5, pady=2, sticky="w")
    product_stock_entry = tk.Entry(input_frame, bg=entry_bg, fg=entry_fg, insertbackground=text_fg)
    product_stock_entry.grid(row=2, column=1, padx=5, pady=2)

    def select_product_from_tree(event):
        selected_item = stock_tree.focus()
        if selected_item:
            values = stock_tree.item(selected_item, 'values')
            product_name_entry.delete(0, tk.END)
            product_name_entry.insert(0, values[1]) # Ürün Adı
            product_price_entry.delete(0, tk.END)
            product_price_entry.insert(0, values[2]) # Fiyat
            product_stock_entry.delete(0, tk.END)
            product_stock_entry.insert(0, values[3]) # Stok
    
    stock_tree.bind("<<TreeviewSelect>>", select_product_from_tree)

    # İşlem Butonları
    action_frame = tk.Frame(stock_window, bg=panel_bg)
    action_frame.pack(pady=10)

    def add_product():
        name = product_name_entry.get().strip()
        price_str = product_price_entry.get().strip()
        stock_str = product_stock_entry.get().strip()

        if not name or not price_str or not stock_str:
            messagebox.showwarning("Uyarı", "Lütfen tüm alanları doldurun.")
            return
        
        try:
            price = float(price_str)
            stock = int(stock_str)
            if price < 0 or stock < 0:
                raise ValueError("Fiyat ve stok negatif olamaz.")
        except ValueError:
            messagebox.showwarning("Hata", "Fiyat ve stok geçerli sayı olmalıdır.")
            return

        try:
            cursor.execute("INSERT INTO products (name, price, stock) VALUES (?, ?, ?)", (name, price, stock))
            db.commit()
            messagebox.showinfo("Başarılı", f"'{name}' ürünü eklendi.")
            load_products_to_stock_tree()
            reklam_guncelle() # Reklam panelini güncelle
            product_name_entry.delete(0, tk.END)
            product_price_entry.delete(0, tk.END)
            product_stock_entry.delete(0, tk.END)
        except sqlite3.IntegrityError:
            messagebox.showwarning("Hata", f"'{name}' adında bir ürün zaten mevcut.")
        
    def update_product():
        selected_item = stock_tree.focus()
        if not selected_item:
            messagebox.showwarning("Uyarı", "Lütfen güncellemek için bir ürün seçin.")
            return
        
        product_id = stock_tree.item(selected_item, 'values')[0] # ID'yi al
        name = product_name_entry.get().strip()
        price_str = product_price_entry.get().strip()
        stock_str = product_stock_entry.get().strip()

        if not name or not price_str or not stock_str:
            messagebox.showwarning("Uyarı", "Lütfen tüm alanları doldurun.")
            return
        
        try:
            price = float(price_str)
            stock = int(stock_str)
            if price < 0 or stock < 0:
                raise ValueError("Fiyat ve stok negatif olamaz.")
        except ValueError:
            messagebox.showwarning("Hata", "Fiyat ve stok geçerli sayı olmalıdır.")
            return
        
        try:
            cursor.execute("UPDATE products SET name = ?, price = ?, stock = ? WHERE id = ?", (name, price, stock, product_id))
            db.commit()
            messagebox.showinfo("Başarılı", f"'{name}' ürünü güncellendi.")
            load_products_to_stock_tree()
            reklam_guncelle() # Reklam panelini güncelle
        except sqlite3.IntegrityError:
            messagebox.showwarning("Hata", f"'{name}' adında başka bir ürün zaten mevcut. Lütfen farklı bir ad kullanın.")

    def delete_product():
        selected_item = stock_tree.focus()
        if not selected_item:
            messagebox.showwarning("Uyarı", "Lütfen silmek için bir ürün seçin.")
            return
        
        product_id = stock_tree.item(selected_item, 'values')[0]
        product_name = stock_tree.item(selected_item, 'values')[1]

        if messagebox.askyesno("Silme Onayı", f"'{product_name}' ürününü silmek istediğinizden emin misiniz?"):
            cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
            db.commit()
            messagebox.showinfo("Başarılı", f"'{product_name}' ürünü silindi.")
            load_products_to_stock_tree()
            reklam_guncelle() # Reklam panelini güncelle
            product_name_entry.delete(0, tk.END)
            product_price_entry.delete(0, tk.END)
            product_stock_entry.delete(0, tk.END)

    add_btn = tk.Button(action_frame, text="Ürün Ekle", command=add_product,
                        font=("Arial", 10), bg="#27AE60", fg="white", width=15)
    add_btn.pack(side="left", padx=5)

    update_btn = tk.Button(action_frame, text="Ürünü Güncelle", command=update_product,
                           font=("Arial", 10), bg="#F39C12", fg="white", width=15) # Turuncu
    update_btn.pack(side="left", padx=5)

    delete_btn = tk.Button(action_frame, text="Ürünü Sil", command=delete_product,
                           font=("Arial", 10), bg="#E74C3C", fg="white", width=15) # Kırmızı
    delete_btn.pack(side="left", padx=5)

# Stok Yönetimi Butonu
stock_management_btn = tk.Button(left_panel, text="Stok Yönetimi", command=open_stock_management_window,
                                 font=("Arial", 12), bg=button_bg, fg=button_fg, width=20, height=2)
stock_management_btn.pack(pady=10, padx=10)


win.mainloop()

# Uygulama kapanırken veritabanı bağlantısını kapat
db.close()
