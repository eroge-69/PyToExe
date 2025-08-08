from datetime import datetime

# Dosya isimleri
input_filename = 'data.txt'
output_filename = 'filtrelenmis_veriler.txt'

# Kullanıcıdan başlangıç ve bitiş tarih/saatini girmesini isteyelim
start_datetime_str = input("Başlangıç tarih ve saatini (ör: 19-06-2025 10:20:00) girin: ")
end_datetime_str = input("Bitiş tarih ve saatini (ör: 19-06-2025 10:30:00) girin: ")

# Dosyadaki tarih ve saat formatı
datetime_format = '%d-%m-%Y %H:%M:%S'

try:
    # Kullanıcının girdiği tarih ve saatleri kontrol edelim
    start_datetime = datetime.strptime(start_datetime_str, datetime_format)
    end_datetime = datetime.strptime(end_datetime_str, datetime_format)
    
    # Dosyayı okumak için farklı kodlama formatlarını deneyelim
    encoding_to_try = ['utf-8', 'latin-1', 'cp1254', 'utf-16', 'utf-16-le']
    
    infile = None
    for enc in encoding_to_try:
        try:
            infile = open(input_filename, 'r', encoding=enc)
            print(f"\n'{input_filename}' dosyası '{enc}' kodlamasıyla açıldı.")
            break
        except UnicodeDecodeError:
            continue  # Bu kodlamayla açılmazsa diğerini denemeye devam et
        except FileNotFoundError:
            print(f"'{input_filename}' dosyası bulunamadı. Lütfen dosya adını kontrol edin.")
            infile = None
            break

    if infile:
        with infile, open(output_filename, 'w', encoding='utf-8') as outfile:
            for line in infile:
                try:
                    # Satırı en fazla 3 parçaya ayıralım: tarih, saat ve geri kalan
                    parts = line.strip().split(maxsplit=2)
                    
                    if len(parts) >= 2:
                        line_datetime_str = f"{parts[0]} {parts[1]}"
                        line_datetime = datetime.strptime(line_datetime_str, datetime_format)

                        if start_datetime <= line_datetime <= end_datetime:
                            outfile.write(line)
                            
                except (ValueError, IndexError) as e:
                    # Tarih formatı uymayan veya satır yapısı hatalı olan satırları atlayalım
                    print(f"Hatalı satır atlandı: {line.strip()} (Hata: {e})")

        print(f"\nİşlem tamamlandı. Seçilen aralıktaki {output_filename} dosyasına yazıldı.")

except ValueError:
    print("\nGirdiğiniz tarih ve saat formatı yanlış. Lütfen 'GG-AA-YYYY HH:MM:SS' formatında giriş yapın.")
except Exception as e:
    print(f"\nGenel bir hata oluştu: {e}")
finally:
    if infile and not infile.closed:
        infile.close()