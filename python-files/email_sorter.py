#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import csv
import os
import re
from typing import Dict, Set, List

EMAIL_REGEX = re.compile(r"^[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}$")
SPLIT_REGEX = re.compile(r"[,\s;]+")

def extract_candidates(line: str) -> List[str]:
    parts = SPLIT_REGEX.split(line)
    cleaned = []
    for p in parts:
        p = p.strip().strip("<>\"'()[]{}.,;:")
        if p:
            cleaned.append(p)
    return cleaned

def is_valid_email(email: str) -> bool:
    return EMAIL_REGEX.match(email) is not None

def collect_input_paths(path: str) -> List[str]:
    if os.path.isdir(path):
        files = []
        for name in os.listdir(path):
            p = os.path.join(path, name)
            if os.path.isfile(p) and name.lower().endswith(".txt"):
                files.append(p)
        return sorted(files)
    return [path]

def load_ignored_domains(cli_list: List[str], file_path: str) -> Set[str]:
    ignored = set()
    if cli_list:
        ignored.update(d.lower().strip() for d in cli_list if d.strip())
    if file_path:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                dom = line.strip().lower()
                if dom and not dom.startswith("#"):
                    ignored.add(dom)
    return ignored

def write_per_domain_txt(out_dir: str, domains_map: Dict[str, Set[str]], min_count: int) -> int:
    os.makedirs(out_dir, exist_ok=True)
    written = 0
    for domain in sorted(domains_map.keys()):
        emails = sorted(domains_map[domain])
        if len(emails) < min_count:
            continue
        path = os.path.join(out_dir, f"{domain}.txt")
        with open(path, "w", encoding="utf-8") as f:
            for e in emails:
                f.write(e + "\n")
        written += 1
    return written

def write_csv(out_dir: str, domains_map: Dict[str, Set[str]], min_count: int) -> str:
    os.makedirs(out_dir, exist_ok=True)
    csv_path = os.path.join(out_dir, "emails.csv")
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["domain", "email"])
        for domain in sorted(domains_map.keys()):
            emails = sorted(domains_map[domain])
            if len(emails) < min_count:
                continue
            for e in emails:
                w.writerow([domain, e])
    return csv_path

def main():
    parser = argparse.ArgumentParser(
        description="تصنيف الإيميلات حسب الدومين مع تجاهل دومينات وحفظ غير الصالح في ملف منفصل."
    )
    parser.add_argument("input", help="مسار ملف .txt أو مجلد يحتوي ملفات .txt")
    parser.add_argument("-o", "--output", default="resalt", help="مجلد الخرج (افتراضي: resalt)")
    parser.add_argument("--csv", action="store_true", help="إخراج ملف CSV واحد بدل ملفات TXT متعددة")
    parser.add_argument("--encoding", default="utf-8", help="ترميز ملفات الإدخال (افتراضي: utf-8)")
    parser.add_argument("--ignore", nargs="*", help="قائمة دومينات لتجاهلها (مسافة بين كل دومين)")
    parser.add_argument("--ignore-file", help="ملف يحوي دومين في كل سطر لتجاهله")
    parser.add_argument("--global-dedupe", action="store_true", help="إزالة التكرار عالميًا عبر جميع الدومينات")
    parser.add_argument("--min-per-domain", type=int, default=1, help="الحد الأدنى لعدد الإيميلات لكل دومين")
    args = parser.parse_args()

    # تحميل الدومينات المستبعدة
    ignored_domains = load_ignored_domains(args.ignore, args.ignore_file)

    # الحاويات
    domains_map: Dict[str, Set[str]] = {}
    invalid_emails: Set[str] = set()
    seen_global: Set[str] = set()

    input_paths = collect_input_paths(args.input)
    if not input_paths:
        print("لم يتم العثور على ملفات إدخال.")
        return

    total_valid = 0
    total_skipped_ignored = 0
    total_duplicates = 0

    for path in input_paths:
        try:
            with open(path, "r", encoding=args.encoding, errors="ignore") as f:
                for line in f:
                    for candidate in extract_candidates(line):
                        if "@" not in candidate:
                            continue
                        email_norm = candidate.lower()
                        if is_valid_email(candidate):
                            domain = email_norm.split("@", 1)[1]
                            if domain in ignored_domains:
                                total_skipped_ignored += 1
                                continue
                            if args.global_dedupe:
                                if email_norm in seen_global:
                                    total_duplicates += 1
                                    continue
                                seen_global.add(email_norm)
                            # إضافة إلى خريطة الدومينات
                            bucket = domains_map.setdefault(domain, set())
                            if email_norm in bucket:
                                total_duplicates += 1
                            else:
                                bucket.add(email_norm)
                                total_valid += 1
                        else:
                            # نعتبره غير صالح فقط إن كان يشبه الإيميل (فيه @)
                            invalid_emails.add(candidate.strip())
        except FileNotFoundError:
            print(f"تحذير: الملف غير موجود: {path}")
        except Exception as e:
            print(f"تحذير: تعذر قراءة {path}: {e}")

    # كتابة المخرجات
    os.makedirs(args.output, exist_ok=True)
    invalid_path = os.path.join(args.output, "invalid.txt")
    with open(invalid_path, "w", encoding="utf-8") as f:
        for e in sorted(invalid_emails):
            f.write(e + "\n")

    if args.csv:
        csv_path = write_csv(args.output, domains_map, args.min_per_domain)
        print(f"- تم إنشاء CSV: {csv_path}")
    else:
        files_written = write_per_domain_txt(args.output, domains_map, args.min_per_domain)
        print(f"- تم إنشاء {files_written} ملف/ملفات TXT داخل: {args.output}")

    print(f"- الإجمالي الصحيح: {total_valid}")
    print(f"- تم تجاهلها بسبب الدومين: {total_skipped_ignored}")
    print(f"- مكررات تم تجاوزها: {total_duplicates}")
    print(f"- غير صالحة: {len(invalid_emails)} (حُفظت في {invalid_path})")

if __name__ == "__main__":
    main()
