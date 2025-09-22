import glob
import pandas as pd
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, PageBreak, Spacer, Image
)
from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape, letter, A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch, cm
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from datetime import datetime
from itertools import combinations
import locale
import threading
import math
import sys # Font hata ayıklaması için sys
import traceback # Detaylı hata izi için
import gc # Garbage collection için eklendi

# --- Yapılandırma ve Sabitler ---

# Türkçe yerel ayarları (locale) belirlemeye çalışıyoruz
try:
    locale.setlocale(locale.LC_ALL, 'tr_TR.UTF-8')
except locale.Error:
    try:
        locale.setlocale(locale.LC_ALL, 'tr_TR')
    except locale.Error:
        print("Uyarı: 'tr_TR.UTF-8' veya 'tr_TR' yerel ayarı bulunamadı. Varsayılan yerel ayar kullanılıyor.")

# Font Kayıt İşlemi
FONT_NAME = 'DejaVuSans'
program_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
FONT_PATH = os.path.join(program_dir, "DejaVuSans.ttf")
FONT_BOLD_PATH = os.path.join(program_dir, "DejaVuSans-Bold.ttf")

# Alternatif font yolu (sistem fontları veya projenin bir alt dizini)
# FONT_ALT_PATH = os.path.join(program_dir, "fonts", "DejaVuSans.ttf")
# FONT_BOLD_ALT_PATH = os.path.join(program_dir, "fonts", "DejaVuSans-Bold.ttf")
# if not os.path.exists(FONT_PATH): FONT_PATH = FONT_ALT_PATH
# if not os.path.exists(FONT_BOLD_PATH): FONT_BOLD_PATH = FONT_BOLD_ALT_PATH

if not os.path.exists(FONT_PATH): FONT_PATH = "DejaVuSans.ttf" # Çalışma dizinini dene
if not os.path.exists(FONT_BOLD_PATH): FONT_BOLD_PATH = "DejaVuSans-Bold.ttf"

registered_font_name = 'Helvetica' # Varsayılan
registered_bold_font_name = 'Helvetica-Bold'
font_registration_success = False

try:
    font_found = False
    bold_font_found = False
    if os.path.exists(FONT_PATH):
        pdfmetrics.registerFont(TTFont(FONT_NAME, FONT_PATH))
        registered_font_name = FONT_NAME
        font_found = True
        print(f"Font '{FONT_NAME}' başarıyla '{FONT_PATH}' yolundan kaydedildi.")
    else:
        print(f"Uyarı: Font dosyası bulunamadı: '{FONT_PATH}'.")

    if os.path.exists(FONT_BOLD_PATH):
        pdfmetrics.registerFont(TTFont(FONT_NAME + '-Bold', FONT_BOLD_PATH))
        registered_bold_font_name = FONT_NAME + '-Bold'
        bold_font_found = True
        print(f"Kalın Font '{FONT_NAME}-Bold' başarıyla '{FONT_BOLD_PATH}' yolundan kaydedildi.")
    else:
        print(f"Uyarı: Kalın font dosyası bulunamadı: '{FONT_BOLD_PATH}'.")

    if font_found:
        font_registration_success = True
        if not bold_font_found:
            # Kalın font bulunamadıysa, normal fontu kalın olarak da kullan (veya Helvetica-Bold kalsın)
            registered_bold_font_name = FONT_NAME # Normal fontu kalın için de kullan
            print(f"Uyarı: Kalın font bulunamadığı için '{registered_font_name}' kalın metinler için de kullanılacak.")
            # Alternatif: registered_bold_font_name = 'Helvetica-Bold' # Varsayılanı kullanmaya devam et
    else:
        print(f"Uyarı: Özel font '{FONT_NAME}' yüklenemedi. Varsayılan ReportLab fontları ('Helvetica', 'Helvetica-Bold') kullanılacak.")
        registered_font_name = 'Helvetica'
        registered_bold_font_name = 'Helvetica-Bold'
        # Varsayılan fontlar her zaman mevcut olmalı, bu yüzden başarıyı true sayabiliriz.
        font_registration_success = True # ReportLab varsayılanları kullanabiliyor

except Exception as e:
    print(f"Font kaydı sırasında kritik hata: {e}")
    print(f"Hata Detayı: {traceback.format_exc()}")
    print("Varsayılan Helvetica fontları kullanılacak.")
    registered_font_name = 'Helvetica'
    registered_bold_font_name = 'Helvetica-Bold'
    # Hata olsa bile ReportLab varsayılanlara dönebildiği için program devam edebilir.
    font_registration_success = False # Ancak özel font başarısız oldu.


# Excel'den okunacak ve birleştirme için kullanılacak sütunlar
BASE_COLUMNS = ["Birim Adı", "Dosya No", "Dosya Durumu", "Dosya Türü"]
# Raporda kullanılacak geçerli dosya türleri
VALID_DOSYA_TURU = ["Soruşturma Dosyası", "Ceza Dava Dosyası", "CBS İhbar Dosyası"]
# Kısaltma için metin değişim kuralları
REPLACEMENTS = {
    "Birim Adı": {"Cumhuriyet Başsavcılığı": "CBS"},
    "Dosya Türü": {"CBS Sorusturma Dosyası": "Soruşturma Dosyası"}
}
# Varsayılan sütun adı değiştirme haritası (GUI üzerinden değiştirilebilir)
DEFAULT_COLUMN_RENAME_MAP = {"Dosya Durumu": "Derdest"}
# Varsayılan Kenar Boşlukları (cm cinsinden)
DEFAULT_MARGIN_CM = 1.5
# Çok sayıda dosya seçimi için onay sınırı
MAX_FILES_NO_CONFIRM = 50 # 50'den fazla dosya seçilirse (kombinasyon sayısı değil) sor

# --- Stil Fonksiyonları ---

def get_base_styles():
    """Temel ReportLab stillerini alır ve kaydedilen fontu ayarlar."""
    styles = getSampleStyleSheet()
    # Kaydedilen font adlarını kullan
    styles['Title'].fontName = registered_font_name
    styles['Heading1'].fontName = registered_bold_font_name # Başlıkları kalın yapalım
    styles['Heading2'].fontName = registered_font_name
    styles['Normal'].fontName = registered_font_name
    styles['Italic'].fontName = registered_font_name # İtalik font için ayrı bir font dosyası tanımlanabilir
    styles['BodyText'].fontName = registered_font_name
    styles['BodyText'].leading = 14
    styles['Normal'].leading = 14
    styles['h1'].fontSize = 16
    styles['h1'].fontName = registered_bold_font_name # h1 için kalın font
    styles['h1'].leading = 20
    styles['h3'].fontSize = 10
    styles['h3'].leading = 12
    styles['h3'].fontName = registered_font_name

    return styles

def create_table_style(num_rows):
    """Modern görünümlü bir tablo stili oluşturur."""
    bold_font = registered_bold_font_name
    normal_font = registered_font_name

    style = TableStyle([
        # Başlık Stili
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, 0), bold_font),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('TOPPADDING', (0, 0), (-1, 0), 8),

        # Genel Gövde Stili
        ('FONTNAME', (0, 1), (-1, -1), normal_font),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.darkslategray),
        ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 1), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 4),
        ('TOPPADDING', (0, 1), (-1, -1), 4),

        # Izgara ve Alternatif Satır Renkleri
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.aliceblue, colors.whitesmoke])
    ])
    return style

def calculate_column_widths(dataframe, page_width, min_col_width=1*cm, max_col_width=8*cm, base_char_width=2.5):
    """
    İçeriğe ve sayfa genişliğine göre dinamik sütun genişlikleri hesaplar.
    Bellek kullanımı için dataframe'in tamamı yerine içeriğin uzunluk istatistiklerini kullanır.
    """
    widths = []
    total_max_len = 0
    max_lengths = []

    # Her sütun için maksimum uzunluğu hesapla (başlık + veri)
    for column in dataframe.columns:
        header_len = len(str(column))
        try:
            # Belleği daha az kullanmak için sadece maksimum uzunluğu bulalım
            # .astype(str) büyük DataFrame'lerde geçici olarak belleği artırabilir.
            # Eğer çok büyük dosyalarda sorun olursa, satır satır işleme veya örneklem düşünülebilir.
            max_data_len_series = dataframe[column].astype(str).map(len)
            max_data_len = max_data_len_series.max()
            if pd.isna(max_data_len): max_data_len = 0
            del max_data_len_series # Belleği serbest bırak
        except Exception as e:
            print(f"Uyarı: '{column}' sütunu için maksimum uzunluk hesaplanırken hata: {e}. Varsayılan uzunluk kullanılacak.")
            max_data_len = header_len # En azından başlık sığsın
        # Başlık ve veri uzunluğunun maksimumunu al, biraz boşluk ekle (+2)
        current_max = max(header_len, int(max_data_len)) + 2
        max_lengths.append(current_max)
        total_max_len += current_max

    available_width = page_width
    estimated_total_content_width = total_max_len * base_char_width
    scale_factor = available_width / estimated_total_content_width if estimated_total_content_width > 0 else 1

    for max_len in max_lengths:
        calculated_width = max_len * base_char_width * scale_factor
        final_width = max(min_col_width, min(calculated_width, max_col_width))
        widths.append(final_width)

    # Toplam hesaplanan genişliği kontrol et ve ayarla
    total_calculated_width = sum(widths)
    if total_calculated_width > 0 and page_width > 0:
        target_width = page_width # Tam genişliği kullan
        if abs(total_calculated_width - target_width) > 1.0:
            adjustment_factor = target_width / total_calculated_width
            # Genişlikleri ayarla ve min/max sınırlarını tekrar uygula
            new_widths = [max(min_col_width, min(w * adjustment_factor, max_col_width)) for w in widths]
            # Çok küçük farklar için orijinali koru, büyük farklarda ayarla
            if abs(sum(new_widths) - target_width) < abs(total_calculated_width - target_width) or sum(new_widths) <= target_width :
                 widths = new_widths

    # print(f"Sayfa Genişliği: {page_width:.2f}, Hesaplanan Toplam Genişlik: {sum(widths):.2f}")
    return widths


# --- Arka Plan/Filigran Fonksiyonu ---

def draw_background(canvas, doc, background_type, background_value):
    """Sayfada filigran metni veya arka plan resmi çizer."""
    if not background_type or background_type == "None":
        return

    canvas.saveState()
    page_width, page_height = doc.pagesize

    if background_type == "Watermark Text" and background_value:
        try:
            canvas.setFont(registered_font_name, 60) # Fontu burada ayarla
            canvas.setFillGray(0.85)
            canvas.translate(page_width / 2.0, page_height / 2.0)
            canvas.rotate(45)
            canvas.drawCentredString(0, 0, background_value)
        except Exception as e:
            print(f"Filigran metni çizilirken hata: {e}. Detay: {traceback.format_exc()}")
            # Hata durumunda basit bir uyarı çizelim
            canvas.restoreState() # Önceki state'i geri yükle
            canvas.saveState()    # Yeni state
            canvas.setFont("Helvetica", 12)
            canvas.setFillColor(colors.red)
            canvas.drawCentredString(page_width / 2.0, page_height / 2.0, "[Filigran Hatası]")

    elif background_type == "Background Image" and background_value and os.path.exists(background_value):
        try:
            img_width, img_height = page_width, page_height
            drawable_width = img_width - doc.leftMargin - doc.rightMargin
            drawable_height = img_height - doc.topMargin - doc.bottomMargin
            canvas.drawImage(
                background_value,
                doc.leftMargin, doc.bottomMargin,
                width=drawable_width, height=drawable_height,
                preserveAspectRatio=True, anchor='c'
            )
        except Exception as e:
            print(f"Arka plan resmi çizilirken hata: '{background_value}': {e}. Detay: {traceback.format_exc()}")
            canvas.setFillColor(colors.red)
            canvas.setFont("Helvetica", 12)
            canvas.drawCentredString(page_width / 2.0, page_height / 2.0, f"[Resim Yüklenemedi: {os.path.basename(background_value)}]")

    canvas.restoreState()

# --- Yardımcı Fonksiyonlar ---

def generate_unique_pdf_path(output_dir, base_name):
    """Verilen temel isme göre benzersiz bir PDF dosya yolu oluşturur."""
    pdf_name = f"{base_name}.pdf"
    output_pdf_path = os.path.join(output_dir, pdf_name)
    counter = 1
    while os.path.exists(output_pdf_path):
        pdf_name = f"{base_name}({counter}).pdf"
        output_pdf_path = os.path.join(output_dir, pdf_name)
        counter += 1
        if counter > 100: # Sonsuz döngüye karşı koruma
            print(f"Uyarı: '{base_name}' için 100'den fazla kopya bulundu. İsimlendirme sorunu olabilir.")
            # Belki rastgele bir ek ekleyebilir veya hata verebilir
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            pdf_name = f"{base_name}_{timestamp}.pdf"
            output_pdf_path = os.path.join(output_dir, pdf_name)
            if os.path.exists(output_pdf_path): # Bu bile varsa artık hata verelim
                 raise IOError(f"Benzersiz PDF dosya adı oluşturulamadı: {base_name}")
            break
    return output_pdf_path

# --- Temel Mantık Fonksiyonları ---

def process_files(file1_path, file2_path, columns_to_use, column_rename_map, log_callback):
    """İki Excel dosyasını okur, birleştirir, temizler, filtreler, sıralar ve sütun adlarını değiştirir. Belleği yönetir."""
    df1, df2, merged_df, filtered_df = None, None, None, None # Önce tanımla
    try:
        log_callback(f"{os.path.basename(file1_path)} okunuyor...", "INFO")
        # usecols ile sadece gerekli sütunları okuyarak bellek tasarrufu
        df1 = pd.read_excel(file1_path, usecols=lambda c: c in columns_to_use, engine='openpyxl') # Engine belirtmek uyumluluğu artırabilir
        log_callback(f"{os.path.basename(file2_path)} okunuyor...", "INFO")
        df2 = pd.read_excel(file2_path, usecols=lambda c: c in columns_to_use, engine='openpyxl')

        # Sütun kontrolü
        missing_cols_df1 = [col for col in columns_to_use if col not in df1.columns]
        if missing_cols_df1:
            raise KeyError(f"{os.path.basename(file1_path)} dosyasında eksik sütunlar: {', '.join(missing_cols_df1)}")
        missing_cols_df2 = [col for col in columns_to_use if col not in df2.columns]
        if missing_cols_df2:
            raise KeyError(f"{os.path.basename(file2_path)} dosyasında eksik sütunlar: {', '.join(missing_cols_df2)}")

    except FileNotFoundError as e:
        log_callback(f"Hata: Dosya bulunamadı - {e}", "ERROR")
        return None
    except KeyError as e:
        log_callback(f"Hata: Gerekli sütun bulunamadı - {e}", "ERROR")
        return None
    except pd.errors.EmptyDataError as e:
        log_callback(f"Hata: Dosya boş veya okunamıyor - {e}", "ERROR")
        return None
    except Exception as e:
        log_callback(f"Excel dosyaları okunurken kritik hata ({os.path.basename(file1_path)}, {os.path.basename(file2_path)}): {e}", "ERROR")
        log_callback(f"Detay: {traceback.format_exc()}", "DEBUG")
        return None

    try:
        log_callback("Dosyalar birleştiriliyor...", "INFO")
        # Birleştirme öncesi sütun tiplerini kontrol et, object iyidir.
        for col in columns_to_use:
             if df1[col].dtype != df2[col].dtype:
                  log_callback(f"Uyarı: '{col}' sütunu için dosyalarda farklı veri tipleri ({df1[col].dtype} vs {df2[col].dtype}). String'e çevriliyor.", "WARN")
                  # Güvenlik için string'e çevir, merge öncesi tutarlılık sağlar.
                  df1[col] = df1[col].astype(str)
                  df2[col] = df2[col].astype(str)

        # Strip whitespace from join columns before merge
        for col in columns_to_use:
             if df1[col].dtype == 'object':
                  df1[col] = df1[col].str.strip()
             if df2[col].dtype == 'object':
                  df2[col] = df2[col].str.strip()

        merged_df = pd.merge(df1, df2, on=columns_to_use, how='inner')

        # Birleştirme sonrası df1 ve df2'ye gerek kalmadı, belleği boşalt
        del df1, df2
        gc.collect()

    except KeyError as e:
        log_callback(f"Hata: Birleştirme sütunları ({', '.join(columns_to_use)}) dosyalarda eşleşmiyor veya bulunamıyor. Hata: {e}", "ERROR")
        return None
    except Exception as e:
        log_callback(f"Birleştirme sırasında beklenmedik hata: {e}", "ERROR")
        log_callback(f"Detay: {traceback.format_exc()}", "DEBUG")
        return None

    # Tekrarlananları kaldır
    merged_df = merged_df.drop_duplicates(subset=columns_to_use).reset_index(drop=True)

    if merged_df.empty:
        log_callback(f"Bilgi: {os.path.basename(file1_path)} ve {os.path.basename(file2_path)} arasında ortak kayıt bulunamadı.", "INFO")
        return pd.DataFrame() # Boş DataFrame döndür, hata değil

    log_callback(f"Ortak kayıt sayısı (birleştirme sonrası): {len(merged_df)}", "INFO")

    # Metin değişimleri ve temizlik
    log_callback("Metin değişimleri ve temizlik uygulanıyor...", "INFO")
    try:
        for col, replacements_map in REPLACEMENTS.items():
            if col in merged_df.columns:
                # apply yerine .replace kullanmak genellikle daha hızlıdır
                merged_df[col] = merged_df[col].astype(str).str.strip() # Önce temizle
                for old, new in replacements_map.items():
                    merged_df[col] = merged_df[col].str.replace(old, new, case=False, regex=False)

        # Tüm object sütunlarında baştaki/sondaki boşlukları temizle
        for col in merged_df.select_dtypes(include=['object']).columns:
             merged_df[col] = merged_df[col].str.strip()

    except Exception as e:
        log_callback(f"Metin değiştirme/temizlik sırasında hata: {e}", "WARN")
        log_callback(f"Detay: {traceback.format_exc()}", "DEBUG")
        # Hata olsa bile devam etmeyi dene

    # Filtreleme
    if "Dosya Türü" in merged_df.columns:
        log_callback(f"'Dosya Türü'ne göre filtreleme: {VALID_DOSYA_TURU}", "INFO")
        try:
             # .copy() yerine filtrelemeyi doğrudan yapıp sonucu ata
             filtered_df = merged_df[merged_df["Dosya Türü"].isin(VALID_DOSYA_TURU)]
             # merged_df'ye artık gerek yok (eğer filtreleme yapıldıysa)
             del merged_df
             gc.collect()
        except Exception as e:
             log_callback(f"Filtreleme sırasında hata: {e}", "WARN")
             log_callback(f"Detay: {traceback.format_exc()}", "DEBUG")
             filtered_df = merged_df # Filtrelemesiz devam et
    else:
        log_callback("Uyarı: 'Dosya Türü' sütunu bulunamadı, filtreleme atlanıyor.", "WARN")
        filtered_df = merged_df # merged_df'yi filtered_df olarak kullan

    if filtered_df.empty:
        log_callback(f"Bilgi: Birleştirme ve filtreleme sonrası geçerli kayıt bulunamadı.", "INFO")
        return pd.DataFrame()

    log_callback(f"Filtreleme sonrası kayıt sayısı: {len(filtered_df)}", "INFO")

    # Sıralama
    log_callback("Veriler sıralanıyor...", "INFO")
    if 'Dosya No' in filtered_df.columns:
        try:
            # Geçici sütunları .loc kullanarak oluştur
            # errors='coerce' ile sayıya dönüşmeyenler NaN olacak, sıralamada sona gider
            split_data = filtered_df['Dosya No'].astype(str).str.split('/', n=1, expand=True) # Sadece ilk /'a göre böl
            filtered_df.loc[:, '_Yil'] = pd.to_numeric(split_data[0].str.strip(), errors='coerce')
            if split_data.shape[1] > 1:
                 no_part = split_data[1].astype(str).str.replace(r'[^\d]', '', regex=True) # Sadece rakamları al
                 filtered_df.loc[:, '_No'] = pd.to_numeric(no_part, errors='coerce')
            else:
                 filtered_df.loc[:, '_No'] = pd.NA # Pandas'ın kendi NA'sı daha iyi

            sort_cols = []
            if 'Birim Adı' in filtered_df.columns:
                 filtered_df.loc[:, '_BirimAdiStr'] = filtered_df['Birim Adı'].astype(str) # NaN'ları 'nan' yapmaz, string yapar
                 sort_cols.append('_BirimAdiStr')

            sort_cols.extend(['_Yil', '_No'])

            # Sırala ve indeksi sıfırla. inplace=False (varsayılan)
            filtered_df = filtered_df.sort_values(by=sort_cols, na_position='last').reset_index(drop=True)

            # Geçici sütunları kaldır
            drop_cols = ['_Yil', '_No']
            if '_BirimAdiStr' in sort_cols: drop_cols.append('_BirimAdiStr')
            filtered_df = filtered_df.drop(columns=drop_cols, errors='ignore')
            del split_data # Belleği serbest bırak
            gc.collect()

        except Exception as e:
            log_callback(f"Uyarı: 'Dosya No'ya göre detaylı sıralama başarısız oldu: {e}.", "WARN")
            log_callback(f"Detay: {traceback.format_exc()}", "DEBUG")
            # Basit sıralama dene
            if 'Birim Adı' in filtered_df.columns:
                 try:
                      filtered_df = filtered_df.sort_values(by=['Birim Adı'], key=lambda col: col.astype(str), na_position='last').reset_index(drop=True)
                      log_callback("Alternatif olarak 'Birim Adı'na göre sıralandı.", "INFO")
                 except Exception as e_sort:
                      log_callback(f"Uyarı: 'Birim Adı'na göre sıralama da başarısız: {e_sort}", "WARN")

    elif 'Birim Adı' in filtered_df.columns:
        log_callback("Uyarı: 'Dosya No' sütunu yok. 'Birim Adı'na göre sıralanıyor.", "WARN")
        try:
            filtered_df = filtered_df.sort_values(by=['Birim Adı'], key=lambda col: col.astype(str), na_position='last').reset_index(drop=True)
        except Exception as e_sort:
             log_callback(f"Uyarı: 'Birim Adı'na göre sıralama başarısız: {e_sort}", "WARN")

    # Sütun adlarını değiştir ve Sıra No ekle
    log_callback("Sütun adları değiştiriliyor ve Sıra No ekleniyor.", "INFO")
    if column_rename_map:
        valid_rename_map = {k: v for k, v in column_rename_map.items() if k in filtered_df.columns}
        if valid_rename_map:
            filtered_df = filtered_df.rename(columns=valid_rename_map) # inplace=False (varsayılan)

    final_df = filtered_df.copy() # filtered_df'yi tekrar kullanmamak için kopyala
    del filtered_df # Belleği serbest bırak
    final_df.insert(0, 'Sıra No', range(1, len(final_df) + 1))
    gc.collect() # Son GC

    log_callback("Veri işleme tamamlandı.", "INFO")
    return final_df

def build_pdf_report(output_pdf_path, dataframe, file1_name, file2_name, page_orientation, background_info, margins_cm, log_callback):
    """İşlenmiş verilerle PDF dokümanını oluşturur. Font hatalarını kontrol eder."""
    if not font_registration_success and registered_font_name != 'Helvetica':
        log_callback(f"Uyarı: Özel fontlar yüklenemediği için PDF oluşturmada sorunlar yaşanabilir. Varsayılan fontlar kullanılacak.", "WARN")
        # Yine de devam etmeyi deneyebiliriz, ReportLab varsayılanları kullanmalı.

    styles = get_base_styles()
    page_size = landscape(A4) if page_orientation == "Landscape" else A4
    left_margin_pt = margins_cm["left"] * cm
    right_margin_pt = margins_cm["right"] * cm
    top_margin_pt = margins_cm["top"] * cm
    bottom_margin_pt = margins_cm["bottom"] * cm

    page_width_pt, page_height_pt = page_size
    if left_margin_pt + right_margin_pt >= page_width_pt or top_margin_pt + bottom_margin_pt >= page_height_pt:
        log_callback(f"Hata: Hesaplanan kenar boşlukları sayfa boyutundan büyük! PDF oluşturulamıyor: {os.path.basename(output_pdf_path)}", "ERROR")
        return False

    doc = SimpleDocTemplate(
        output_pdf_path,
        pagesize=page_size,
        leftMargin=left_margin_pt, rightMargin=right_margin_pt,
        topMargin=top_margin_pt, bottomMargin=bottom_margin_pt,
        title=f"Karşılaştırma - {file1_name} vs {file2_name}",
        author="Comparison Tool"
    )

    elements = []
    title_text = f"{datetime.now().strftime('%d/%m/%Y')} Tarihi İtibarıyla Müşterek Dosyalar"
    elements.append(Paragraph(title_text, styles['h1']))
    elements.append(Spacer(1, 0.2*cm))

    # Bellek kullanımı için DataFrame'i doğrudan listeye çevir ve DataFrame'i sil
    try:
        # NaN değerleri boş string yap
        data_list = [dataframe.columns.to_list()] + [[str(cell) if pd.notna(cell) else "" for cell in row] for row in dataframe.values.tolist()]
        available_width = doc.width
        column_widths = calculate_column_widths(dataframe, available_width)
        del dataframe # DataFrame'i bellekten sil
        gc.collect()
    except Exception as e:
        log_callback(f"Hata: PDF için veri hazırlanırken veya sütun genişliği hesaplanırken hata: {e}", "ERROR")
        log_callback(f"Detay: {traceback.format_exc()}", "DEBUG")
        del dataframe # Hata durumunda da silmeyi dene
        gc.collect()
        return False # PDF oluşturma başarısız

    # Tabloyu oluştur
    try:
        table = Table(data_list, colWidths=column_widths, repeatRows=1)
        table.setStyle(create_table_style(len(data_list)))
        elements.append(table)
        del data_list # data_list'i de sil
        gc.collect()
    except Exception as e:
        log_callback(f"Hata: ReportLab tablosu oluşturulurken hata: {e}", "ERROR")
        log_callback(f"Detay: {traceback.format_exc()}", "DEBUG")
        return False


    elements.append(Spacer(1, 0.5*cm))
    note_text = f"<b>Not:</b> Bu tablo, <u>{os.path.basename(file1_name)}.xlsx</u> ve <u>{os.path.basename(file2_name)}.xlsx</u> dosyalarında bulunan ortak kayıtları göstermektedir. Karşılaştırma <i>{', '.join(BASE_COLUMNS)}</i> sütunlarına göre yapılmıştır."
    elements.append(Paragraph(note_text, styles['Normal']))

    # PDF Oluştur
    log_callback(f"PDF oluşturuluyor: {os.path.basename(output_pdf_path)}", "INFO")
    try:
        background_func = None
        if background_info and background_info["type"] != "None":
            def page_background(canvas, current_doc): # Argüman ismi 'doc' olunca çakışabiliyor
                draw_background(canvas, current_doc, background_info["type"], background_info["value"])
            background_func = page_background

        if background_func:
            doc.build(elements, onFirstPage=background_func, onLaterPages=background_func)
        else:
            doc.build(elements)

        log_callback(f"BAŞARILI: PDF oluşturuldu -> {output_pdf_path}", "SUCCESS") # Yeni seviye
        return True

    except Exception as e:
        log_callback(f"KRİTİK HATA: PDF oluşturulamadı ({os.path.basename(output_pdf_path)}): {e}", "ERROR")
        log_callback(f"Detay: {traceback.format_exc()}", "DEBUG")
        # Hata mesajı GUI'de zaten gösteriliyor olacak (run_comparison'dan)
        return False
    finally:
         # Elementler listesini temizleyerek belleği boşaltmaya yardımcı ol
         del elements
         gc.collect()

# --- Ana Uygulama Sınıfı (GUI) ---

class ComparisonApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Excel Dosya Karşılaştırma ve PDF Oluşturma Aracı")
        self.root.geometry("750x750") # Log alanı için biraz daha yükseklik

        # Uygulama kapatılırken temizlik için
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.processing_thread = None
        self.is_processing = False

        self.style = ttk.Style(self.root)
        self.style.theme_use('clam') # veya 'alt', 'default', 'classic'

        # Değişkenler
        self.output_folder = tk.StringVar(value=os.getcwd())
        self.page_orientation = tk.StringVar(value="Landscape")
        self.background_type = tk.StringVar(value="None")
        self.background_value = tk.StringVar()
        self.column_rename_map = DEFAULT_COLUMN_RENAME_MAP.copy()

        self.left_margin = tk.DoubleVar(value=DEFAULT_MARGIN_CM)
        self.right_margin = tk.DoubleVar(value=DEFAULT_MARGIN_CM)
        self.top_margin = tk.DoubleVar(value=DEFAULT_MARGIN_CM)
        self.bottom_margin = tk.DoubleVar(value=DEFAULT_MARGIN_CM)

        # --- Arayüz ---
        options_frame = ttk.LabelFrame(self.root, text="Ayarlar", padding="10")
        options_frame.pack(fill=tk.X, padx=10, pady=5)

        control_frame = ttk.Frame(self.root, padding="10")
        control_frame.pack(fill=tk.X, padx=10, pady=5)

        status_frame = ttk.LabelFrame(self.root, text="Durum ve Log", padding="10") # Çerçeve başlığı
        status_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # -- Options Frame --
        # Sayfa Yönü
        orient_frame = ttk.Frame(options_frame)
        orient_frame.pack(fill=tk.X, pady=5)
        ttk.Label(orient_frame, text="Sayfa Yönü:").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(orient_frame, text="Yatay", variable=self.page_orientation, value="Landscape").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(orient_frame, text="Dikey", variable=self.page_orientation, value="Portrait").pack(side=tk.LEFT, padx=5)

        # Kenar Boşlukları
        margin_frame = ttk.LabelFrame(options_frame, text="Kenar Boşlukları (cm)", padding="10")
        margin_frame.pack(fill=tk.X, pady=5)
        margin_frame.columnconfigure((1, 3), weight=1) # Giriş alanları genişlesin
        ttk.Label(margin_frame, text="Sol:").grid(row=0, column=0, sticky=tk.W, padx=2, pady=2)
        ttk.Entry(margin_frame, textvariable=self.left_margin, width=7).grid(row=0, column=1, sticky=tk.EW, padx=2, pady=2)
        ttk.Label(margin_frame, text="Sağ:").grid(row=0, column=2, sticky=tk.W, padx=(10, 2), pady=2)
        ttk.Entry(margin_frame, textvariable=self.right_margin, width=7).grid(row=0, column=3, sticky=tk.EW, padx=2, pady=2)
        ttk.Label(margin_frame, text="Üst:").grid(row=1, column=0, sticky=tk.W, padx=2, pady=2)
        ttk.Entry(margin_frame, textvariable=self.top_margin, width=7).grid(row=1, column=1, sticky=tk.EW, padx=2, pady=2)
        ttk.Label(margin_frame, text="Alt:").grid(row=1, column=2, sticky=tk.W, padx=(10, 2), pady=2)
        ttk.Entry(margin_frame, textvariable=self.bottom_margin, width=7).grid(row=1, column=3, sticky=tk.EW, padx=2, pady=2)

        # Arka Plan/Filigran
        bg_frame = ttk.Frame(options_frame)
        bg_frame.pack(fill=tk.X, pady=5)
        bg_frame.columnconfigure(4, weight=1) # Entry genişlesin
        ttk.Label(bg_frame, text="Arka Plan:").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(bg_frame, text="Yok", variable=self.background_type, value="None", command=self.update_bg_input_state).pack(side=tk.LEFT, padx=2)
        ttk.Radiobutton(bg_frame, text="Yazı", variable=self.background_type, value="Watermark Text", command=self.update_bg_input_state).pack(side=tk.LEFT, padx=2)
        ttk.Radiobutton(bg_frame, text="Resim", variable=self.background_type, value="Background Image", command=self.update_bg_input_state).pack(side=tk.LEFT, padx=2)
        self.bg_entry = ttk.Entry(bg_frame, textvariable=self.background_value, width=30, state=tk.DISABLED)
        self.bg_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        self.bg_button = ttk.Button(bg_frame, text="Seç...", command=self.select_bg_image, state=tk.DISABLED, width=5)
        self.bg_button.pack(side=tk.LEFT, padx=5)

        # Sütun Adı Değiştirme
        rename_frame = ttk.Frame(options_frame)
        rename_frame.pack(fill=tk.X, pady=5)
        ttk.Label(rename_frame, text="Sütun Adı Değiştirme:").pack(side=tk.LEFT, padx=5)
        ttk.Button(rename_frame, text="Düzenle", command=self.edit_renames, width=8).pack(side=tk.LEFT, padx=5)
        self.rename_label = ttk.Label(rename_frame, text=f"Aktif: {self.column_rename_map}", foreground="blue", wraplength=450) # Sığmazsa alt satıra geç
        self.rename_label.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        # -- Control Frame --
        control_frame.columnconfigure(1, weight=1)
        ttk.Label(control_frame, text="PDF Kayıt Klasörü:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(control_frame, textvariable=self.output_folder, width=60).grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5)
        ttk.Button(control_frame, text="Gözat...", command=self.select_output_folder, width=8).grid(row=0, column=2, padx=5, pady=5)

        self.run_button = ttk.Button(control_frame, text="Excel Dosyalarını Seç ve Karşılaştırmayı Başlat", command=self.select_files_and_start)
        self.run_button.grid(row=1, column=0, columnspan=3, pady=15)

        # -- Status Frame --
        info_frame = ttk.Frame(status_frame)
        info_frame.pack(fill=tk.X, expand=False, pady=(0, 10))
        self.current_pair_label = ttk.Label(info_frame, text="Mevcut Çift: Bekleniyor...", foreground="gray", anchor=tk.W)
        self.current_pair_label.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        self.common_rows_label = ttk.Label(info_frame, text="Ortak Kayıt: N/A", foreground="gray", anchor=tk.E)
        self.common_rows_label.pack(side=tk.RIGHT, padx=5)

        # Log Alanı
        self.status_text = tk.Text(status_frame, height=15, wrap=tk.WORD, state=tk.DISABLED, bg="#f0f0f0", fg="#333333", relief=tk.SUNKEN, borderwidth=1)
        scrollbar = ttk.Scrollbar(status_frame, orient=tk.VERTICAL, command=self.status_text.yview)
        self.status_text.config(yscrollcommand=scrollbar.set)
        self.status_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Tag konfigürasyonları (renklendirme için)
        self.status_text.tag_configure("INFO", foreground="black")
        self.status_text.tag_configure("WARN", foreground="orange")
        self.status_text.tag_configure("ERROR", foreground="red", font=('TkDefaultFont', 9, 'bold'))
        self.status_text.tag_configure("SUCCESS", foreground="green", font=('TkDefaultFont', 9, 'bold'))
        self.status_text.tag_configure("DEBUG", foreground="gray")

        self.update_bg_input_state()

    def log_status(self, message, level="INFO"):
        """Durum metin alanına seviyeli mesaj ekler."""
        # Ana thread'den çağrılmasını garantile
        self.root.after(0, self._append_status_text, message, level.upper())

    def _append_status_text(self, message, level):
        """Durum metin alanına güvenli bir şekilde mesaj ekler (main thread)."""
        if not self.root or not tk.Toplevel.winfo_exists(self.root): return # Pencere kapandıysa işlem yapma
        try:
            self.status_text.config(state=tk.NORMAL)
            timestamp = datetime.now().strftime("%H:%M:%S")
            prefix = f"[{timestamp}] "
            self.status_text.insert(tk.END, prefix)
            self.status_text.insert(tk.END, f"{message}\n", level) # Mesajı seviye tag'i ile ekle
            self.status_text.see(tk.END)
            self.status_text.config(state=tk.DISABLED)
            self.root.update_idletasks()
        except tk.TclError as e:
             # Pencere kapatılırken oluşabilecek hataları yoksay
             if "application has been destroyed" in str(e):
                 print("Loglama hatası: Uygulama kapatılmış.")
             else:
                 raise e # Başka bir Tcl hatasıysa tekrar yükselt
        except Exception as e:
             print(f"Log yazma hatası: {e}") # Genel hatalar için

    def update_info_labels(self, pair_text, row_count_text):
        """GUI bilgi etiketlerini günceller (main thread)."""
        if not self.root or not tk.Toplevel.winfo_exists(self.root): return
        try:
             self.current_pair_label.config(text=f"Mevcut Çift: {pair_text}", foreground="black" if pair_text != "Bekleniyor..." else "gray")
             self.common_rows_label.config(text=f"Ortak Kayıt: {row_count_text}", foreground="black" if row_count_text != "N/A" and "Hata" not in str(row_count_text) else ("red" if "Hata" in str(row_count_text) else "gray"))
             self.root.update_idletasks()
        except tk.TclError as e:
             if "application has been destroyed" in str(e):
                 print("Etiket güncelleme hatası: Uygulama kapatılmış.")
             else:
                 raise e
        except Exception as e:
             print(f"Etiket güncelleme hatası: {e}")

    def select_folder(self, variable):
        """Klasör seçim diyaloğunu açar."""
        initial_dir = variable.get() if os.path.isdir(variable.get()) else os.getcwd()
        folder_path = filedialog.askdirectory(initialdir=initial_dir, parent=self.root, title="Klasör Seç")
        if folder_path:
            variable.set(folder_path)

    def select_output_folder(self):
        """PDF'lerin kaydedileceği klasörü belirler."""
        self.select_folder(self.output_folder)

    def update_bg_input_state(self):
        """Arka plan türü seçimine göre giriş alanını etkinleştirir/devre dışı bırakır."""
        bg_type = self.background_type.get()
        if bg_type == "None":
            self.bg_entry.config(state=tk.DISABLED)
            self.bg_button.config(state=tk.DISABLED)
            self.background_value.set("")
        elif bg_type == "Watermark Text":
            self.bg_entry.config(state=tk.NORMAL)
            self.bg_button.config(state=tk.DISABLED)
        elif bg_type == "Background Image":
            self.bg_entry.config(state=tk.NORMAL) # Resim yolunu elle de girebilsin
            self.bg_button.config(state=tk.NORMAL)

    def select_bg_image(self):
        """Arka plan resmi seçmek için dosya diyaloğunu açar."""
        if self.background_type.get() == "Background Image":
            current_val = self.background_value.get()
            initial_dir = os.path.dirname(current_val) if current_val and os.path.isdir(os.path.dirname(current_val)) else os.getcwd()
            file_path = filedialog.askopenfilename(
                title="Arka Plan Resmini Seç", initialdir=initial_dir,
                filetypes=[("Resim Dosyaları", "*.png *.jpg *.jpeg *.bmp *.gif"), ("Tüm Dosyalar", "*.*")],
                parent=self.root
            )
            if file_path:
                self.background_value.set(file_path)

    def edit_renames(self):
        """Sütun adlarını düzenlemek için diyalog açar."""
        current_map_str = '; '.join([f"{k}->{v}" for k, v in self.column_rename_map.items()])
        new_map_str = simpledialog.askstring(
            "Sütun Adı Değiştir",
            "Değişiklikleri 'EskiAd1->YeniAd1; EskiAd2->YeniAd2' formatında girin:\n"
            "(Boş bırakırsanız varsayılana döner)",
            initialvalue=current_map_str, parent=self.root
        )

        if new_map_str is not None: # Cancel'a basılmadıysa
            try:
                temp_map = {}
                if new_map_str.strip():
                    pairs = new_map_str.split(';')
                    for pair in pairs:
                        if '->' in pair:
                            old, new = pair.split('->', 1)
                            old = old.strip()
                            new = new.strip()
                            if old: # Eski isim boş olamaz
                                temp_map[old] = new
                self.column_rename_map = temp_map if temp_map else DEFAULT_COLUMN_RENAME_MAP.copy() # Boşsa varsayılana dön
                self.rename_label.config(text=f"Aktif: {self.column_rename_map}")
                self.log_status(f"Sütun değiştirme kuralları güncellendi: {self.column_rename_map}", "INFO")
            except Exception as e:
                messagebox.showerror("Format Hatası", f"Sütun adı değiştirme formatı hatalı.\n'EskiAd->YeniAd; ...' kullanın.\nHata: {e}", parent=self.root)

    def select_files_and_start(self):
        """Dosya seçme diyaloğunu açar ve seçilen dosyalarla işlemi başlatır."""
        if self.is_processing:
             messagebox.showwarning("Devam Eden İşlem", "Mevcut karşılaştırma işlemi devam ediyor. Lütfen bitmesini bekleyin.", parent=self.root)
             return

        initial_dir = os.getcwd()
        file_paths = filedialog.askopenfilenames(
            title="Karşılaştırılacak Excel (.xlsx) Dosyalarını Seçin (En az 2)",
            initialdir=initial_dir,
            filetypes=[("Excel Dosyaları", "*.xlsx")],
            parent=self.root
        )

        if not file_paths:
            self.log_status("Dosya seçimi iptal edildi.", "INFO")
            return

        file_paths_list = list(file_paths)

        if len(file_paths_list) < 2:
            messagebox.showwarning("Yetersiz Dosya", "Karşılaştırma yapmak için en az 2 Excel (.xlsx) dosyası seçmelisiniz.", parent=self.root)
            self.log_status("Uyarı: Karşılaştırma için yetersiz dosya seçildi.", "WARN")
            return

        # Çok sayıda dosya seçimi onayı
        num_files = len(file_paths_list)
        if num_files > MAX_FILES_NO_CONFIRM:
            num_pairs = len(list(combinations(file_paths_list, 2)))
            confirm = messagebox.askyesno(
                "Çok Sayıda Dosya Seçildi",
                f"{num_files} dosya seçtiniz. Bu, {num_pairs} adet karşılaştırma anlamına geliyor.\n"
                f"Bu işlem uzun sürebilir. Devam etmek istiyor musunuz?",
                parent=self.root
            )
            if not confirm:
                self.log_status(f"{num_files} dosya için işlem kullanıcı tarafından iptal edildi.", "INFO")
                return

        # Kenar boşluklarını doğrula
        try:
            margins_cm = {
                "left": self.left_margin.get(), "right": self.right_margin.get(),
                "top": self.top_margin.get(), "bottom": self.bottom_margin.get()
            }
            if any(m < 0 for m in margins_cm.values()):
                messagebox.showerror("Geçersiz Değer", "Kenar boşlukları negatif olamaz.", parent=self.root)
                self.log_status("Hata: Kenar boşlukları negatif.", "ERROR")
                return
        except tk.TclError:
            messagebox.showerror("Geçersiz Değer", "Kenar boşluğu değerleri sayısal olmalıdır.", parent=self.root)
            self.log_status("Hata: Kenar boşlukları sayısal değil.", "ERROR")
            return

        # Çıkış klasörünü kontrol et/oluştur
        out_folder = self.output_folder.get()
        if not out_folder:
             messagebox.showerror("Eksik Bilgi", "Lütfen PDF'lerin kaydedileceği klasörü seçin.", parent=self.root)
             return
        if not os.path.isdir(out_folder):
            try:
                os.makedirs(out_folder, exist_ok=True) # exist_ok=True ile klasör varsa hata vermez
                self.log_status(f"Çıkış klasörü oluşturuldu/doğrulandı: {out_folder}", "INFO")
            except Exception as e:
                messagebox.showerror("Klasör Hatası", f"Çıkış klasörü oluşturulamadı:\n{out_folder}\nHata: {e}", parent=self.root)
                self.log_status(f"Hata: Çıkış klasörü oluşturulamadı: {e}", "ERROR")
                return

        # GUI'yi hazırlama ve thread'i başlatma
        self.run_button.config(state=tk.DISABLED, text="İşlem Devam Ediyor...")
        self.is_processing = True
        self.status_text.config(state=tk.NORMAL)
        self.status_text.delete('1.0', tk.END) # Logları temizle
        self.status_text.config(state=tk.DISABLED)
        self.update_info_labels("Hazırlanıyor...", "N/A")
        self.log_status(f"Seçilen {len(file_paths_list)} dosya ile işlem başlatılıyor...", "INFO")

        bg_info = {
            "type": self.background_type.get(),
            "value": self.background_value.get() if self.background_type.get() != "None" else None
        }
        if bg_info["type"] == "Background Image" and bg_info["value"]:
            if not os.path.exists(bg_info["value"]):
                messagebox.showerror("Dosya Bulunamadı", f"Seçilen arka plan resim dosyası bulunamadı:\n{bg_info['value']}", parent=self.root)
                self.log_status(f"Hata: Arka plan resmi bulunamadı: {bg_info['value']}", "ERROR")
                self.enable_run_button() # Butonu tekrar aktif et
                return
            # Çok büyük resim dosyaları için uyarı eklenebilir
            try:
                img_size = os.path.getsize(bg_info["value"]) / (1024*1024) # MB cinsinden
                if img_size > 10: # 10 MB'dan büyükse
                    self.log_status(f"Uyarı: Seçilen arka plan resmi ({img_size:.1f} MB) oldukça büyük. PDF oluşturma yavaşlayabilir veya bellek sorunları yaşanabilir.", "WARN")
            except OSError:
                pass # Boyut alınamazsa yoksay

        # Kopyaları gönder (thread içinde GUI değişkenlerine erişmemek için)
        thread_args = (
             file_paths_list,
             out_folder,
             self.page_orientation.get(),
             bg_info.copy(),
             self.column_rename_map.copy(),
             margins_cm.copy()
        )

        # İşlemi ayrı bir thread'de başlat
        self.processing_thread = threading.Thread(
            target=self.run_comparison_wrapper,
            args=thread_args,
            daemon=True
        )
        self.processing_thread.start()

    def run_comparison_wrapper(self, *args):
        """run_comparison'ı çağıran ve bittiğinde GUI'yi güncelleyen sarmalayıcı."""
        try:
            self.run_comparison(*args)
        except Exception as e:
             # run_comparison içindeki genel try/except'in yakalayamadığı hatalar için (nadiren)
             self.log_status(f"İŞLEM SIRASINDA BEKLENMEDİK KRİTİK HATA (Wrapper): {e}", "ERROR")
             self.log_status(f"Detay: {traceback.format_exc()}", "DEBUG")
             # GUI mesajını ana thread'den göster
             self.root.after(0, lambda: messagebox.showerror("Kritik Hata", f"İşlem sırasında beklenmedik bir hata oluştu:\n{e}", parent=self.root))
        finally:
            # İşlem bitince (başarılı veya hatalı) GUI'yi güncelle
            self.root.after(0, self.enable_run_button)
            self.root.after(0, self.update_info_labels, "Bekleniyor...", "N/A")
            self.is_processing = False
            self.processing_thread = None
            gc.collect() # Thread bitiminde GC çağır

    def run_comparison(self, file_paths, output_dir, page_orientation, background_info, column_map, margins_cm):
        """Seçilen dosya çiftlerini karşılaştırır ve PDF oluşturur."""
        pairings = list(combinations(file_paths, 2))
        total_pairs = len(pairings)
        self.log_status(f"Toplam {total_pairs} dosya çifti karşılaştırılacak.", "INFO")

        success_count = 0
        fail_count = 0
        skipped_count = 0

        for i, (file1_path, file2_path) in enumerate(pairings):
            file1_name_base = os.path.splitext(os.path.basename(file1_path))[0]
            file2_name_base = os.path.splitext(os.path.basename(file2_path))[0]
            pdf_base_name = f"{file1_name_base}_vs_{file2_name_base}_Comparison"

            current_pair_text = f"{os.path.basename(file1_path)} vs {os.path.basename(file2_path)} ({i+1}/{total_pairs})"
            self.log_status(f"--- Karşılaştırma ({i+1}/{total_pairs}): {os.path.basename(file1_path)} vs {os.path.basename(file2_path)} ---", "INFO")
            self.root.after(0, self.update_info_labels, current_pair_text, "İşleniyor...")

            processed_data = None # Önce None yapalım
            pdf_success = False

            try:
                # 1. Veri İşleme
                processed_data = process_files(file1_path, file2_path, BASE_COLUMNS, column_map, self.log_status)

                # 2. PDF Oluşturma (eğer veri varsa)
                if processed_data is not None and not processed_data.empty:
                    common_rows_count = len(processed_data)
                    self.root.after(0, self.update_info_labels, current_pair_text, f"{common_rows_count} ortak kayıt")
                    self.log_status(f"Ortak kayıt bulundu: {common_rows_count}. PDF oluşturuluyor...", "INFO")

                    # Benzersiz PDF yolu oluştur
                    output_pdf_path = generate_unique_pdf_path(output_dir, pdf_base_name)

                    pdf_success = build_pdf_report(
                        output_pdf_path, processed_data.copy(), # Kopyasını gönderelim
                        file1_name_base, file2_name_base,
                        page_orientation, background_info, margins_cm,
                        self.log_status
                    )
                    if pdf_success:
                        success_count += 1
                    else:
                        fail_count += 1
                        self.log_status(f"Hata: PDF oluşturulamadı -> {os.path.basename(output_pdf_path)}", "ERROR") # build_pdf_report zaten logluyor ama burada da belirtelim

                elif processed_data is None: # process_files'da hata oluştu
                    fail_count += 1
                    self.log_status(f"Hata: Veri işlenemedi ({os.path.basename(file1_path)} vs {os.path.basename(file2_path)}).", "ERROR")
                    self.root.after(0, self.update_info_labels, current_pair_text, "Veri Hatası")

                else: # processed_data boş DataFrame döndü (ortak yok veya filtre sonucu boş)
                    skipped_count += 1
                    self.log_status(f"Bilgi: Ortak kayıt bulunamadı veya geçerli kayıt kalmadı. PDF oluşturulmuyor.", "INFO")
                    self.root.after(0, self.update_info_labels, current_pair_text, "0 (Atlandı)")

            except Exception as e_pair:
                 # Bu döngü adımında beklenmedik bir hata olursa
                 fail_count += 1
                 self.log_status(f"KRİTİK HATA (Çift İşleme): {os.path.basename(file1_path)} vs {os.path.basename(file2_path)} işlenirken hata: {e_pair}", "ERROR")
                 self.log_status(f"Detay: {traceback.format_exc()}", "DEBUG")
                 self.root.after(0, self.update_info_labels, current_pair_text, "Kritik Hata")
            finally:
                # Her çift işlendikten sonra belleği temizle
                del processed_data # processed_data'yı temizle
                gc.collect() # Garbage Collector'ı çağır

        # Tüm çiftler işlendikten sonra özet
        self.log_status("--- İşlem Tamamlandı ---", "INFO")
        self.log_status(f"Başarılı Oluşturulan PDF: {success_count}", "SUCCESS" if success_count > 0 else "INFO")
        self.log_status(f"Ortak Kayıt Bulunamayan/Atlanan Çift: {skipped_count}", "INFO")
        self.log_status(f"Hata Oluşan veya İşlenemeyen Çift: {fail_count}", "ERROR" if fail_count > 0 else "INFO")

        final_message = (
            f"Karşılaştırma işlemi tamamlandı.\n\n"
            f"Başarıyla oluşturulan PDF sayısı: {success_count}\n"
            f"Ortak kayıt bulunamayan/atlanan çift sayısı: {skipped_count}\n"
            f"Hata oluşan/işlenemeyen çift sayısı: {fail_count}"
        )
        # Mesajı ana thread'den göster
        self.root.after(0, lambda: messagebox.showinfo("İşlem Sonucu", final_message, parent=self.root))


    def enable_run_button(self):
        """Ana thread'den çalıştırma düğmesini güvenli bir şekilde yeniden etkinleştirir."""
        if not self.root or not tk.Toplevel.winfo_exists(self.root): return
        try:
             self.run_button.config(state=tk.NORMAL, text="Excel Dosyalarını Seç ve Karşılaştırmayı Başlat")
             self.is_processing = False # İşlem bitti işaretle
        except tk.TclError as e:
             if "application has been destroyed" in str(e):
                 print("Buton etkinleştirme hatası: Uygulama kapatılmış.")
             else:
                 raise e
        except Exception as e:
             print(f"Buton etkinleştirme hatası: {e}")

    def on_closing(self):
        """Uygulama penceresi kapatılırken çağrılır."""
        if self.is_processing:
            if messagebox.askyesno("İşlem Devam Ediyor", "Karşılaştırma işlemi hala devam ediyor. Çıkmak istediğinize emin misiniz?\n(Devam eden işlem arka planda durdurulacaktır)", parent=self.root):
                # Not: Daemon thread'ler genellikle anında durmaz, ancak yeni iş yapmayı bırakır.
                # Daha kontrollü durdurma için thread'e bir event flag gönderilebilir, ancak bu durumda
                # dosya işlemleri veya PDF oluşturma yarıda kalabilir. Daemon şimdilik yeterli.
                print("Kullanıcı işlemi yarıda keserek çıkmayı onayladı.")
                self.root.destroy() # Pencereyi kapat
            else:
                return # Kapatma işlemini iptal et
        else:
            print("Uygulama kapatılıyor.")
            self.root.destroy() # Normal kapatma


# --- Ana Çalıştırma ---
if __name__ == "__main__":
    # Font yükleme sonucunu kontrol et (isteğe bağlı)
    # if not font_registration_success:
    #     # Belki bir başlangıç uyarısı gösterilebilir
    #     # messagebox.showwarning("Font Uyarısı", "Özel DejaVuSans fontları yüklenemedi. Görünümde farklılıklar olabilir.")
    #     pass # Ama program yine de çalışabilir

    root = tk.Tk()
    app = ComparisonApp(root)
    root.mainloop()
    # Mainloop bittikten sonra (uygulama kapandıktan sonra)
    print("Uygulama kapatıldı.")
    # Gerekirse ek temizlik burada yapılabilir (ama daemon thread ve GC çoğu şeyi halletmeli)
    gc.collect() # Son bir GC