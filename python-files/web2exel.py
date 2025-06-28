#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

import pandas as pd

def fetch_tables(url):
    """
    با pandas.read_html تمام جداول داخل یک URL را استخراج می‌کند
    بر می‌گرداند: لیست DataFrame
    """
    try:
        tables = pd.read_html(url)
        print(f"[+] یافتن {len(tables)} جدول در {url}")
        return tables
    except Exception as e:
        print(f"[!] خطا در واکشی {url}: {e}")
        return []

def write_excel(output_path: Path, url_list: list[str]):
    """
    داده‌های url_list را استخراج و در فایل Excel با نام output_path می‌نویسد.
    اگر فایل وجود داشته باشد، overwrite می‌کند.
    """
    # حالت write: چون می‌خواهیم هر بار کل شیت‌ها را مجدداً بسازیم
    mode = 'w'
    with pd.ExcelWriter(output_path, engine='openpyxl', mode=mode) as writer:
        for url in url_list:
            tables = fetch_tables(url)
            # نام شیت از hostname + شماره جدول
            host = url.replace('https://','').replace('http://','').split('/')[0]
            for idx, df in enumerate(tables, start=1):
                sheet_name = f"{host[:25]}_{idx}"
                # در صورت طولانی بودن، pandas خودش کوتاهش می‌کند
                df.to_excel(writer, sheet_name=sheet_name, index=False)
    print(f"[✓] فایل Excel ذخیره شد: {output_path}")

def load_urls_from_json(path: Path) -> list[str]:
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    # فرض می‌کنیم فرمتی مثل { "urls": ["https://...", ...] }
    return data.get("urls", [])

def main():
    p = argparse.ArgumentParser(
        prog="web2excel",
        description="استخراج جداول وب و ذخیره / بروزرسانی در Excel"
    )
    p.add_argument(
        '-u','--urls', nargs='+', help="لیست URL ها (مثلاً -u https://a.com https://b.com)"
    )
    p.add_argument(
        '-c','--config', type=Path,
        help="فایل JSON که شامل { \"urls\": [ ... ] } باشد"
    )
    p.add_argument(
        '-o','--output', type=Path, default=Path("output.xlsx"),
        help="نام فایل اکسل خروجی (پیش‌فرض: output.xlsx)"
    )
    args = p.parse_args()

    # آماده‌سازی لیست URL
    urls = []
    if args.urls:
        urls.extend(args.urls)
    if args.config:
        urls.extend(load_urls_from_json(args.config))
    urls = list(dict.fromkeys(urls))  # حذف تکراری

    if not urls:
        print("[!] هیچ URL‌ای داده نشده. یا با -u یا -c وارد کنید.")
        return

    write_excel(args.output, urls)

if __name__ == "__main__":
    main()