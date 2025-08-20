#!/usr/bin/env python3
"""
Yedekleme Klasör Yapısı Oluşturucu
----------------------------------
İstediğiniz hiyerarşi:

data/
  └─ <Marka>/
      └─ <Model>/
          └─ <ECU>/
              └─ <MüşteriVIN>/
                  ├─ ORIGINAL/
                  ├─ MOD/
                  └─ ID.txt

Kullanım
  # Etkileşimli mod (sorarak oluşturur)
  python backup_builder.py

  # Komut satırı argümanları ile
  python backup_builder.py --base ./data \
      --brand "BMW" --model "F30 320d" --ecu "EDC17C50" --vin "WBA3A5C51DF123456" \
      --customer "Ali Veli" --open

  # CSV ile toplu (başlıklar: brand,model,ecu,vin,customer)
  python backup_builder.py --csv kayitlar.csv --base ./data --open

Notlar
- Geçersiz dosya karakterleri otomatik temizlenir.
- Zaten varsa tekrar oluşturmaz, yolu ekranda gösterir.
- ID.txt içine özet bilgiler ve benzersiz UUID yazılır.
"""
from __future__ import annotations

import argparse
import csv
import os
from pathlib import Path
from datetime import datetime
import getpass
import platform
import re
import sys
import uuid

SAFE_RE = re.compile(r"[^A-Za-z0-9_.\- ]+")


def sanitize(name: str) -> str:
    name = name.strip()
    name = SAFE_RE.sub("_", name)
    # art arda altçizgileri sadeleştir
    name = re.sub(r"_+", "_", name)
    # baş/son boşlukları temizle
    return name.strip(" ._") or "NA"


def make_structure(base: Path, brand: str, model: str, ecu: str, vin: str, customer: str | None = None) -> Path:
    brand_s = sanitize(brand)
    model_s = sanitize(model)
    ecu_s = sanitize(ecu)
    vin_s = sanitize(vin)

    # Hiyerarşi
    target = base / brand_s / model_s / ecu_s / vin_s
    (target / "ORIGINAL").mkdir(parents=True, exist_ok=True)
    (target / "MOD").mkdir(parents=True, exist_ok=True)

    # ID.txt
    id_file = target / "ID.txt"
    if not id_file.exists():
        info = {
            "UUID": str(uuid.uuid4()),
            "Created": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "CreatedBy": getpass.getuser(),
            "Host": platform.node(),
            "Brand": brand,
            "Model": model,
            "ECU": ecu,
            "VIN": vin,
            "Customer": customer or "",
        }
        with id_file.open("w", encoding="utf-8") as f:
            for k, v in info.items():
                f.write(f"{k}: {v}\n")
    return target


def open_folder(path: Path) -> None:
    try:
        if sys.platform.startswith("win"):
            os.startfile(str(path))  # type: ignore[attr-defined]
        elif sys.platform == "darwin":
            os.system(f"open '{str(path)}'")
        else:
            os.system(f"xdg-open '{str(path)}' >/dev/null 2>&1 &")
    except Exception:
        pass


def interactive_flow(base: Path, do_open: bool) -> None:
    print("— Etkileşimli oluşturma —")
    brand = input("Marka: ").strip()
    model = input("Model: ").strip()
    ecu = input("ECU: ").strip()
    vin = input("Müşteri VIN: ").strip()
    customer = input("Müşteri adı (opsiyonel): ").strip()
    path = make_structure(base, brand, model, ecu, vin, customer or None)
    print(f"\n✅ Oluşturuldu/var: {path}")
    if do_open:
        open_folder(path)


def from_csv(csv_path: Path, base: Path, do_open: bool) -> None:
    created_paths = []
    with csv_path.open("r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        required = {"brand", "model", "ecu", "vin"}
        missing = required - {h.lower() for h in reader.fieldnames or []}
        if missing:
            raise SystemExit(f"CSV başlıkları eksik: {', '.join(sorted(missing))}")
        for row in reader:
            brand = row.get("brand", "").strip()
            model = row.get("model", "").strip()
            ecu = row.get("ecu", "").strip()
            vin = row.get("vin", "").strip()
            customer = (row.get("customer") or "").strip()
            if not (brand and model and ecu and vin):
                print(f"Atlandı (eksik alan): {row}")
                continue
            path = make_structure(base, brand, model, ecu, vin, customer or None)
            created_paths.append(path)
            print(f"✅ {path}")
    if do_open and created_paths:
        open_folder(created_paths[-1])


def main(argv=None) -> None:
    p = argparse.ArgumentParser(description="Yedekleme klasör yapısı oluşturur.")
    p.add_argument("--base", default="./data", help="Kök klasör (varsayılan: ./data)")
    p.add_argument("--brand", help="Marka")
    p.add_argument("--model", help="Model")
    p.add_argument("--ecu", help="ECU")
    p.add_argument("--vin", help="Müşteri VIN")
    p.add_argument("--customer", help="Müşteri adı (opsiyonel)")
    p.add_argument("--csv", help="Toplu oluşturma için CSV dosyası yolu")
    p.add_argument("--open", action="store_true", help="Oluşturulan klasörü aç")
    args = p.parse_args(argv)

    base = Path(args.base).resolve()
    base.mkdir(parents=True, exist_ok=True)

    if args.csv:
        from_csv(Path(args.csv), base, args.open)
        return

    if args.brand and args.model and args.ecu and args.vin:
        path = make_structure(base, args.brand, args.model, args.ecu, args.vin, args.customer)
        print(f"✅ Oluşturuldu/var: {path}")
        if args.open:
            open_folder(path)
    else:
        interactive_flow(base, args.open)


if __name__ == "__main__":
    main()
