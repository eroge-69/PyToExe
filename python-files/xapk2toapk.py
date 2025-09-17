import zipfile
import os
import sys

def xapk_to_apk(xapk_path):
    if not zipfile.is_zipfile(xapk_path):
        print("❌ Geçerli bir XAPK değil:", xapk_path)
        return

    base_dir = os.path.dirname(xapk_path)
    with zipfile.ZipFile(xapk_path, 'r') as z:
        # APK dosyasını bul
        apk_files = [f for f in z.namelist() if f.endswith(".apk")]
        if not apk_files:
            print("❌ APK bulunamadı:", xapk_path)
            return
        
        apk_name = os.path.basename(apk_files[0])
        output_path = os.path.join(base_dir, apk_name)

        # APK çıkar
        with z.open(apk_files[0]) as source, open(output_path, "wb") as target:
            target.write(source.read())
        print(f"✅ APK çıkarıldı: {output_path}")

        # OBB dosyalarını da çıkar
        obb_files = [f for f in z.namelist() if f.startswith("Android/obb/")]
        if obb_files:
            print("📂 OBB dosyaları bulundu, çıkarılıyor...")
            for f in obb_files:
                z.extract(f, base_dir)
            print(f"✅ OBB klasörü çıkarıldı: {os.path.join(base_dir, 'Android/obb')}")
        else:
            print("ℹ️ OBB klasörü bulunamadı (belki oyun küçük).")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Kullanım: xapk2toapk.py <dosya.xapk>")
        input("Çıkmak için Enter’a bas...")
    else:
        for file in sys.argv[1:]:
            xapk_to_apk(file)
        input("\nBitti! Çıkmak için Enter’a bas...")
