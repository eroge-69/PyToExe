import datetime
import holidays
import jpype
import jaydebeapi
import pandas as pd
import getpass

# --- Fungsi cek hari kerja berdasarkan libur nasional & cuti bersama ---
def load_cuti_bersama(filepath):
    try:
        with open(filepath, 'r') as f:
            return {datetime.datetime.strptime(line.strip(), "%Y-%m-%d").date() for line in f if line.strip()}
    except FileNotFoundError:
        return set()

def is_working_day(date, indo_holidays, cuti_bersama):
    return date.weekday() < 5 and date not in indo_holidays and date not in cuti_bersama

# --- Cari hari kerja terakhir sebelum tanggal tertentu ---
def get_last_working_day(start_date, indo_holidays, cuti_bersama):
    date = start_date - datetime.timedelta(days=1)
    while not is_working_day(date, indo_holidays, cuti_bersama):
        date -= datetime.timedelta(days=1)
    return date

def main():
    user_input = input("Masukkan tanggal (format YYYYMMDD): ").strip()
    try:
        input_date = datetime.datetime.strptime(user_input, "%Y%m%d").date()
    except ValueError:
        print("❌ Format tanggal salah. Gunakan format YYYYMMDD.")
        return

    indo_holidays = holidays.Indonesia(years=input_date.year)
    cuti_bersama = load_cuti_bersama("cuti_bersama.txt")

    working_date = get_last_working_day(input_date, indo_holidays, cuti_bersama)

    print(f"\n📅 Tanggal kerja terakhir yang dipilih: {working_date.strftime('%A, %d %B %Y')}")
    confirm = input("Apakah akan diproses? (Y/N): ").strip().upper()
    if confirm != "Y":
        print("⛔ Proses dibatalkan.")
        return

    # --- Parameter waktu ---
    yyyymm = working_date.strftime("%Y%m")
    gabl_dd = working_date.strftime("%d")
    gabl_col = f"GABL{gabl_dd}"

    # --- Input kredensial ---
    username = input("Masukkan username AS400: ").strip()
    password = getpass.getpass("Masukkan password AS400: ")

    # --- Path konfigurasi Java & JDBC ---
    JVM_PATH = r"C:\\Program Files\\Java\\jdk-22\\bin\\server\\jvm.dll"
    JAR_PATH = r"C:\\Users\\ASUS ZENBOOK\\Downloads\\LPSCleansing\\jt400-11.1.jar"
    CORE_HOST = "192.100.1.225"
    JDBC_URL = f"jdbc:as400://{CORE_HOST};naming=sql;errors=full"
    DRIVER_CLASS = "com.ibm.as400.access.AS400JDBCDriver"

    # --- SQL QUERY (dinamis berdasarkan tanggal kerja) ---
    QUERY = f"""
WITH CABANG_UNIK AS (
  SELECT KODE_CABANG FROM (
    SELECT REBRCO AS KODE_CABANG FROM mlklbu.M5RE WHERE RESTAT = 1
    UNION
    SELECT DOBRCO AS KODE_CABANG FROM MLKLBU.D5DO WHERE DOSTAT = 1
    UNION
    SELECT GABRCO AS KODE_CABANG FROM MLKGLDTA.GLABLDOWN WHERE GAYYMM = '{yyyymm}'
  ) AS ALL_CABANG
), 
TABUNGAN_NOMINATIF AS (
  SELECT REBRCO AS KODE_CABANG, SUM(RECLBL / 100) AS TOTAL_TABUNGAN_NOMINATIF 
  FROM mlklbu.M5RE 
  WHERE REATCO IN ('TM1', 'TS1', 'TBK', 'SPL') AND RESTAT = 1 AND RECLBL > 0 
  GROUP BY REBRCO
), 
TABUNGAN_NERACA AS (
  SELECT GABRCO AS KODE_CABANG, SUM({gabl_col}) AS TOTAL_TABUNGAN_NERACA 
  FROM MLKGLDTA.GLABLDOWN 
  WHERE GAGLCO IN ('20401', '20402', '20403', '20404') AND GAYYMM = '{yyyymm}' 
  GROUP BY GABRCO
), 
GIRO_SWASTA_NOMINATIF AS (
  SELECT REBRCO AS KODE_CABANG, SUM(RECLBL / 100) AS TOTAL_GIRO_SWASTA_NOMINATIF 
  FROM mlklbu.M5RE 
  WHERE REATCO IN ('GS1', 'GS2', 'GS3', 'GS4', 'GS5', 'GS6', 'GS8', 'GS9') AND RESTAT = 1 AND RECLBL > 0 
  GROUP BY REBRCO
), 
GIRO_SWASTA_NERACA AS (
  SELECT GABRCO AS KODE_CABANG, SUM({gabl_col}) AS TOTAL_GIRO_SWASTA_NERACA 
  FROM MLKGLDTA.GLABLDOWN 
  WHERE GAGLCO IN ('20120', '21501') AND GAYYMM = '{yyyymm}' 
  GROUP BY GABRCO
), 
GIRO_PEMERINTAH_NOMINATIF AS (
  SELECT REBRCO AS KODE_CABANG, SUM(RECLBL / 100) AS TOTAL_GIRO_PEMERINTAH_NOMINATIF 
  FROM mlklbu.M5RE 
  WHERE REATCO LIKE 'GP%' AND RESTAT = 1 AND RECLBL > 0 
  GROUP BY REBRCO
), 
GIRO_PEMERINTAH_NERACA AS (
  SELECT GABRCO AS KODE_CABANG, SUM({gabl_col}) AS TOTAL_GIRO_PEMERINTAH_NERACA 
  FROM MLKGLDTA.GLABLDOWN 
  WHERE GAGLCO IN ('20110') AND GAYYMM = '{yyyymm}' 
  GROUP BY GABRCO
), 
DEPOSITO_NOMINATIF AS (
  SELECT DOBRCO AS KODE_CABANG, SUM(DOCLBL / 100) AS TOTAL_DEPOSITO_NOMINATIF 
  FROM MLKLBU.D5DO 
  WHERE DOSTAT = 1 
  GROUP BY DOBRCO
), 
DEPOSITO_NERACA AS (
  SELECT GABRCO AS KODE_CABANG, SUM({gabl_col}) AS TOTAL_DEPOSITO_NERACA 
  FROM MLKGLDTA.GLABLDOWN 
  WHERE GAGLCO IN ('20501','20502','20503','20504','20505','20507','20508','20510','20511','20517','21504') AND GAYYMM = '{yyyymm}' 
  GROUP BY GABRCO
)
SELECT 
  cu.KODE_CABANG,
  COALESCE(tn.TOTAL_TABUNGAN_NOMINATIF, 0) AS TOTAL_TABUNGAN_NOMINATIF,
  COALESCE(tg.TOTAL_TABUNGAN_NERACA, 0) AS TOTAL_TABUNGAN_NERACA,
  COALESCE(tn.TOTAL_TABUNGAN_NOMINATIF, 0) - COALESCE(tg.TOTAL_TABUNGAN_NERACA, 0) AS SELISIH_TABUNGAN,

  COALESCE(gs.TOTAL_GIRO_SWASTA_NOMINATIF, 0) AS TOTAL_GIRO_SWASTA_NOMINATIF,
  COALESCE(gsn.TOTAL_GIRO_SWASTA_NERACA, 0) AS TOTAL_GIRO_SWASTA_NERACA,
  COALESCE(gs.TOTAL_GIRO_SWASTA_NOMINATIF, 0) - COALESCE(gsn.TOTAL_GIRO_SWASTA_NERACA, 0) AS SELISIH_GIRO_SWASTA,

  COALESCE(gp.TOTAL_GIRO_PEMERINTAH_NOMINATIF, 0) AS TOTAL_GIRO_PEMERINTAH_NOMINATIF,
  COALESCE(gpn.TOTAL_GIRO_PEMERINTAH_NERACA, 0) AS TOTAL_GIRO_PEMERINTAH_NERACA,
  COALESCE(gp.TOTAL_GIRO_PEMERINTAH_NOMINATIF, 0) - COALESCE(gpn.TOTAL_GIRO_PEMERINTAH_NERACA, 0) AS SELISIH_GIRO_PEMERINTAH,

  COALESCE(dp.TOTAL_DEPOSITO_NOMINATIF, 0) AS TOTAL_DEPOSITO_NOMINATIF,
  COALESCE(dn.TOTAL_DEPOSITO_NERACA, 0) AS TOTAL_DEPOSITO_NERACA,
  COALESCE(dp.TOTAL_DEPOSITO_NOMINATIF, 0) - COALESCE(dn.TOTAL_DEPOSITO_NERACA, 0) AS SELISIH_DEPOSITO
FROM 
  CABANG_UNIK cu
  LEFT JOIN TABUNGAN_NOMINATIF tn ON cu.KODE_CABANG = tn.KODE_CABANG
  LEFT JOIN TABUNGAN_NERACA tg ON cu.KODE_CABANG = tg.KODE_CABANG
  LEFT JOIN GIRO_SWASTA_NOMINATIF gs ON cu.KODE_CABANG = gs.KODE_CABANG
  LEFT JOIN GIRO_SWASTA_NERACA gsn ON cu.KODE_CABANG = gsn.KODE_CABANG
  LEFT JOIN GIRO_PEMERINTAH_NOMINATIF gp ON cu.KODE_CABANG = gp.KODE_CABANG
  LEFT JOIN GIRO_PEMERINTAH_NERACA gpn ON cu.KODE_CABANG = gpn.KODE_CABANG
  LEFT JOIN DEPOSITO_NOMINATIF dp ON cu.KODE_CABANG = dp.KODE_CABANG
  LEFT JOIN DEPOSITO_NERACA dn ON cu.KODE_CABANG = dn.KODE_CABANG
ORDER BY cu.KODE_CABANG
"""

    # Mulai JVM
    if not jpype.isJVMStarted():
        jpype.startJVM(JVM_PATH, "-Djava.class.path=" + JAR_PATH)

    # Koneksi ke AS400
    conn = jaydebeapi.connect(DRIVER_CLASS, JDBC_URL, [username, password], JAR_PATH)
    cursor = conn.cursor()
    cursor.execute(QUERY.strip().rstrip(";"))

    # Ambil hasil ke DataFrame
    columns = [desc[0] for desc in cursor.description]
    rows = cursor.fetchall()
    df = pd.DataFrame(rows, columns=columns)

    # Simpan ke Excel
    filename = f"output_nominatif_neraca_{yyyymm}.xlsx"
    df.to_excel(filename, index=False)
    print(f"✅ File berhasil disimpan: {filename}")

    # Deteksi selisih
    print("\n🔍 Mengecek selisih data...")
    ada_selisih = False

    for index, row in df.iterrows():
        if abs(row['TOTAL_TABUNGAN_NOMINATIF'] - row['TOTAL_TABUNGAN_NERACA']) > 0.001:
            print(f"Selisih pada TABUNGAN cabang {row['KODE_CABANG']} sebesar {abs(row['TOTAL_TABUNGAN_NOMINATIF'] - row['TOTAL_TABUNGAN_NERACA']):,.2f}")
            ada_selisih = True
        if abs(row['TOTAL_GIRO_SWASTA_NOMINATIF'] - row['TOTAL_GIRO_SWASTA_NERACA']) > 0.001:
            print(f"Selisih pada GIRO_SWASTA cabang {row['KODE_CABANG']} sebesar {abs(row['TOTAL_GIRO_SWASTA_NOMINATIF'] - row['TOTAL_GIRO_SWASTA_NERACA']):,.2f}")
            ada_selisih = True
        if abs(row['TOTAL_GIRO_PEMERINTAH_NOMINATIF'] - row['TOTAL_GIRO_PEMERINTAH_NERACA']) > 0.001:
            print(f"Selisih pada GIRO_PEMERINTAH cabang {row['KODE_CABANG']} sebesar {abs(row['TOTAL_GIRO_PEMERINTAH_NOMINATIF'] - row['TOTAL_GIRO_PEMERINTAH_NERACA']):,.2f}")
            ada_selisih = True
        if abs(row['TOTAL_DEPOSITO_NOMINATIF'] - row['TOTAL_DEPOSITO_NERACA']) > 0.001:
            print(f"Selisih pada DEPOSITO cabang {row['KODE_CABANG']} sebesar {abs(row['TOTAL_DEPOSITO_NOMINATIF'] - row['TOTAL_DEPOSITO_NERACA']):,.2f}")
            ada_selisih = True

    # Konfirmasi apakah mau dilanjutkan
    if ada_selisih:
        lanjut = input("\n❓ Masih ada selisih data. Apakah Anda ingin melanjutkan proses? (Y/N): ").strip().upper()
        if lanjut != 'Y':
            print("⛔ Proses dihentikan oleh pengguna.")
            cursor.close()
            conn.close()
            exit()
        else:
            print("✅ OK. Proses dilanjutkan...\n")
    else:
        print("✅ Tidak ada selisih. Proses dilanjutkan...\n")

    # Tutup koneksi
    cursor.close()
    conn.close()


if __name__ == "__main__":
    main()
