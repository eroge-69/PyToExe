import pandas as pd
import os

# Ganti dengan nama file Excel kamu
excel_file = 'gantiGPS.xlsx'

# Baca file Excel
df = pd.read_excel(excel_file)

# Loop setiap baris
for index, row in df.iterrows():
    filename = row['Filename']
    lat = float(row['Latitude'])
    lon = float(row['Longitude'])

    # Penentuan arah GPS
    lat_ref = 'N' if lat >= 0 else 'S'
    long_ref = 'E' if lon >= 0 else 'W'
    # lat_ref = 'S'
    # long_ref = 'E'

    # Format nilai GPS (tanpa tanda minus)
    abs_lat = abs(lat)
    abs_lon = abs(lon)

    # Perintah exiftool
    cmd = f'exiftool -overwrite_original ' \
          f'-GPSLatitude={abs_lat} -GPSLatitudeRef={lat_ref} ' \
          f'-GPSLongitude={abs_lon} -GPSLongitudeRef={long_ref} "list_gambar/{filename}"'

    print(f'>>>> Menjalankan: {cmd}')
    os.system(cmd)
