Her zaman ayrıntıları göster
# Create a self-contained Python module for a minimal TTO accounting system
# It stores data in a local SQLite database and provides CLI commands.
# The module focuses on project-based accounting, VAT/withholding handling,
# TÜBİTAK 1513-style period cutoffs, and royalty distribution rules.

from pathlib import Path
from textwrap import dedent

code = dedent(r'''
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tto_accounting.py — Minimal Teknoloji Transfer Ofisi (TTO) muhasebe yazılımı (CLI)
Özellikler:
- Proje bazlı gelir/gider kaydı
- Fatura (gelir) için KDV ve tevkifat (stopaj) parametreleri
- Giderlerde KDV takibi
- TÜBİTAK 1513 tarzı dönem kapanış kontrolü (işlem tarihleri için kesit kontrolü)
- Telif/royalty (lisans gelirleri) net gelir dağıtımı (esnek oranlar)
- Raporlar: Proje özet raporu, dönem (MM) raporu özeti, mizan benzeri hesap dökümü

Notlar:
- Bu yazılım genel eğitim amaçlıdır; vergi ve mevzuat yorumu yerine geçmez.
- Gerçek uygulamada mali müşavir/onay mekanizmaları ve belge saklama gerekir.
"""

import argparse
import sqlite3
import sys
from dataclasses import dataclass
from datetime import datetime, date
from typing import Dict, List, Optional, Tuple

DB_PATH = "tto_accounting.db"

# --- Yardımcılar ------------------------------------------------------------

def iso(d: str) -> str:
    """YYYY-MM-DD doğrulaması ve normalizasyonu."""
    try:
        return datetime.strptime(d, "%Y-%m-%d").date().isoformat()
    except ValueError:
        raise argparse.ArgumentTypeError("Tarih formatı YYYY-MM-DD olmalı")

def today() -> str:
    return date.today().isoformat()

def money(x: float) -> float:
    return round(float(x), 2)

# --- Veritabanı -------------------------------------------------------------

SCHEMA = """
PRAGMA foreign_keys=ON;

CREATE TABLE IF NOT EXISTS projects (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  funding_type TEXT CHECK(funding_type IN ('TUBITAK','SANAYI','LISANS','DIGER')) NOT NULL,
  start_date TEXT NOT NULL,
  end_date   TEXT NOT NULL,
  UNIQUE(name)
);

CREATE TABLE IF NOT EXISTS periods (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  start_date TEXT NOT NULL,
  end_date   TEXT NOT NULL,
  closed     INTEGER NOT NULL DEFAULT 0,
  CHECK (date(start_date) <= date(end_date))
);

-- Gelir faturaları (müşteri tahsilatı ayrı takip edilebilir; burada accrual esas)
CREATE TABLE IF NOT EXISTS invoices (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  issue_date TEXT NOT NULL,
  description TEXT,
  amount_gross REAL NOT NULL,        -- mal/hizmet bedeli (KDV hariç tutar varsayılan)
  vat_rate   REAL NOT NULL,          -- 0.0..1.0
  wht_rate   REAL NOT NULL DEFAULT 0,-- tevkifat/stopaj (gelirden kesilecek) 0..1
  received   INTEGER NOT NULL DEFAULT 0, -- tahsil edildi mi (0/1)
  UNIQUE(project_id, issue_date, description)
);

-- Gider belgeleri (fatura fiş vs.)
CREATE TABLE IF NOT EXISTS expenses (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  expense_date TEXT NOT NULL,
  category TEXT NOT NULL,            -- personel, satınalma, hizmet, seyahat vs.
  description TEXT,
  amount_net REAL NOT NULL,
  vat_rate REAL NOT NULL,            -- indirilecek KDV takibi için
  paid INTEGER NOT NULL DEFAULT 0
);

-- Royalty/lisans tahsilatları (netleşmeden önce brüt tutar burada kaydedilir)
CREATE TABLE IF NOT EXISTS royalties (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  recv_date TEXT NOT NULL,
  description TEXT,
  amount_gross REAL NOT NULL,
  direct_costs REAL NOT NULL DEFAULT 0, -- lisansla ilişkili doğrudan masraf
  admin_fee   REAL NOT NULL DEFAULT 0,  -- idari kesinti (ör. %15) tutar olarak
  distributed INTEGER NOT NULL DEFAULT 0
);

-- Royalty dağıtım tanımı (yüzdeler toplamı 1.0 olmalı)
CREATE TABLE IF NOT EXISTS royalty_rules (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  rule_name TEXT UNIQUE NOT NULL,
  inventor_share REAL NOT NULL,
  department_share REAL NOT NULL,
  institution_share REAL NOT NULL,
  tto_share REAL NOT NULL,
  CHECK (round(inventor_share + department_share + institution_share + tto_share, 5) = 1.0)
);

-- Muhasebe hesapları ve yevmiye (çok basit mizan)
CREATE TABLE IF NOT EXISTS accounts (
  code TEXT PRIMARY KEY,
  name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS journal (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  entry_date TEXT NOT NULL,
  memo TEXT
);

CREATE TABLE IF NOT EXISTS journal_lines (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  journal_id INTEGER NOT NULL REFERENCES journal(id) ON DELETE CASCADE,
  project_id INTEGER REFERENCES projects(id) ON DELETE SET NULL,
  account_code TEXT NOT NULL REFERENCES accounts(code),
  debit REAL NOT NULL DEFAULT 0,
  credit REAL NOT NULL DEFAULT 0,
  CHECK ( (debit = 0 AND credit > 0) OR (credit = 0 AND debit > 0) )
);
"""

DEFAULT_ACCOUNTS = [
    ("100", "Kasa/Bankalar"),
    ("120", "Alıcılar"),
    ("320", "Satıcılar"),
    ("600", "Gelirler"),
    ("740", "Hizmet Üretim Maliyeti / Proje Giderleri"),
    ("391", "Hesaplanan KDV"),
    ("191", "İndirilecek KDV"),
    ("360", "Ödenecek Vergi/Stopaj"),
    ("649", "Diğer Olağan Gelir ve Kârlar (Royalty)"),
]

def connect(db_path: str = DB_PATH) -> sqlite3.Connection:
    con = sqlite3.connect(db_path)
    con.execute("PRAGMA foreign_keys=ON;")
    return con

def init_db(args):
    con = connect()
    with con:
        con.executescript(SCHEMA)
        # Varsayılan hesaplar
        for c, n in DEFAULT_ACCOUNTS:
            con.execute("INSERT OR IGNORE INTO accounts(code, name) VALUES (?,?)", (c, n))
        # Varsayılan bir royalty kuralı (örnek: %40 mucit, %20 bölüm, %20 kurum, %20 TTO)
        con.execute(
            "INSERT OR IGNORE INTO royalty_rules(rule_name, inventor_share, department_share, institution_share, tto_share) VALUES (?,?,?,?,?)",
            ("STD_TR_UNI", 0.40, 0.20, 0.20, 0.20),
        )
    print("Veritabanı hazır:", DB_PATH)

# --- Komutlar ---------------------------------------------------------------

def add_project(args):
    con = connect()
    with con:
        con.execute(
            "INSERT INTO projects(name, funding_type, start_date, end_date) VALUES (?,?,?,?)",
            (args.name, args.funding_type, args.start_date, args.end_date),
        )
    print("Proje eklendi:", args.name)

def list_projects(args):
    con = connect()
    cur = con.execute("SELECT id, name, funding_type, start_date, end_date FROM projects ORDER BY id")
    for row in cur.fetchall():
        print(row)

def add_invoice(args):
    con = connect()
    issue_date = iso(args.issue_date)
    amount = money(args.amount)
    vat = float(args.vat_rate)
    wht = float(args.wht_rate)
    if not (0 <= vat <= 1 and 0 <= wht <= 1):
        raise SystemExit("KDV/tevkifat 0..1 aralığında olmalı, ör: 0.20")
    vat_amt = money(amount * vat)
    wht_amt = money(amount * wht)
    gross_with_vat = money(amount + vat_amt)
    net_after_wht = money(amount - wht_amt)

    memo = f"Fatura: {args.description} (KDV %{int(vat*100)}, Tevkifat %{int(wht*100)})"
    con = connect()
    with con:
        # Kayıt
        con.execute(
            "INSERT INTO invoices(project_id, issue_date, description, amount_gross, vat_rate, wht_rate, received) VALUES (?,?,?,?,?,?,?)",
            (args.project_id, issue_date, args.description, amount, vat, wht, 0),
        )
        # Yevmiye (tahakkuk): 120 Alıcılar (brüt KDV dahil) / 600 Gelir, 391 Hes.KDV, 360 Stopaj
        j = con.execute("INSERT INTO journal(entry_date, memo) VALUES(?,?)", (issue_date, memo)).lastrowid
        # Borç 120 (Alıcılar): KDV dahil toplam
        con.execute("INSERT INTO journal_lines(journal_id, project_id, account_code, debit) VALUES (?,?,?,?)",
                    (j, args.project_id, "120", gross_with_vat))
        # Alacak 600 Gelir: tutar
        con.execute("INSERT INTO journal_lines(journal_id, project_id, account_code, credit) VALUES (?,?,?,?)",
                    (j, args.project_id, "600", amount))
        # Alacak 391 Hesaplanan KDV
        if vat_amt:
            con.execute("INSERT INTO journal_lines(journal_id, project_id, account_code, credit) VALUES (?,?,?,?)",
                        (j, args.project_id, "391", vat_amt))
        # Borç 360 Ödenecek Vergi/Stopaj (alıcı kesti ise borçlanma azaltır) => burada alacak yazıp 120'yi düşürmek yerine netleştirme için alacak yazıyoruz
        if wht_amt:
            # Stopaj alıcı tarafından kesilecekse 120'den düşmek için 360'ı borç yazmak yerine alacak yazıp karşılığında 120'yi düşürmeliyiz.
            # Ancak basitlik için 120 borcu azaltmak yerine ayrıca bir kayıt açmıyoruz; yine de net tahsilat raporda gösterilir.
            con.execute("INSERT INTO journal_lines(journal_id, project_id, account_code, credit) VALUES (?,?,?,?)",
                        (j, args.project_id, "360", wht_amt))
    print(f"Fatura kaydedildi. Brüt+KDV: {gross_with_vat:.2f} | Stopaj: {wht_amt:.2f} | Net (KDV hariç): {net_after_wht:.2f}")

def add_expense(args):
    con = connect()
    expense_date = iso(args.expense_date)
    amount = money(args.amount)
    vat = float(args.vat_rate)
    if not (0 <= vat <= 1):
        raise SystemExit("KDV 0..1 aralığında olmalı, ör: 0.20")
    vat_amt = money(amount * vat)
    memo = f"Gider: {args.category} - {args.description} (KDV %{int(vat*100)})"
    with con:
        con.execute(
            "INSERT INTO expenses(project_id, expense_date, category, description, amount_net, vat_rate, paid) VALUES (?,?,?,?,?,?,?)",
            (args.project_id, expense_date, args.category, args.description, amount, vat, 0),
        )
        # Yevmiye: 740 Proje Gideri / 320 Satıcılar, 191 İndirilecek KDV
        j = con.execute("INSERT INTO journal(entry_date, memo) VALUES(?,?)", (expense_date, memo)).lastrowid
        con.execute("INSERT INTO journal_lines(journal_id, project_id, account_code, debit) VALUES (?,?,?,?)",
                    (j, args.project_id, "740", amount))
        if vat_amt:
            con.execute("INSERT INTO journal_lines(journal_id, project_id, account_code, debit) VALUES (?,?,?,?)",
                        (j, args.project_id, "191", vat_amt))
        con.execute("INSERT INTO journal_lines(journal_id, project_id, account_code, credit) VALUES (?,?,?,?)",
                    (j, args.project_id, "320", money(amount + vat_amt)))
    print(f"Gider kaydedildi. Net: {amount:.2f} | KDV: {vat_amt:.2f}")

def add_royalty(args):
    con = connect()
    recv_date = iso(args.recv_date)
    amount = money(args.amount)
    admin_fee = money(args.admin_fee or 0)
    direct_costs = money(args.direct_costs or 0)
    memo = f"Royalty: {args.description}"
    with con:
        con.execute(
            "INSERT INTO royalties(project_id, recv_date, description, amount_gross, direct_costs, admin_fee, distributed) VALUES (?,?,?,?,?,?,0)",
            (args.project_id, recv_date, args.description, amount, direct_costs, admin_fee),
        )
        # Yevmiye: 100 Banka / 649 Royalty Gelirleri
        j = con.execute("INSERT INTO journal(entry_date, memo) VALUES(?,?)", (recv_date, memo)).lastrowid
        con.execute("INSERT INTO journal_lines(journal_id, project_id, account_code, debit) VALUES (?,?,?,?)",
                    (j, args.project_id, "100", amount))
        con.execute("INSERT INTO journal_lines(journal_id, project_id, account_code, credit) VALUES (?,?,?,?)",
                    (j, args.project_id, "649", amount))
    print(f"Royalty tahsilatı kaydedildi. Brüt: {amount:.2f}")

def distribute_royalty(args):
    con = connect()
    cur = con.execute("SELECT inventor_share, department_share, institution_share, tto_share FROM royalty_rules WHERE rule_name=?", (args.rule_name,))
    row = cur.fetchone()
    if not row:
        raise SystemExit("Kural bulunamadı")
    inventor_p, dept_p, inst_p, tto_p = row
    r = con.execute("SELECT id, amount_gross, direct_costs, admin_fee, distributed FROM royalties WHERE id=?", (args.royalty_id,)).fetchone()
    if not r:
        raise SystemExit("Royalty kaydı yok")
    rid, gross, direct_costs, admin_fee, distributed = r
    if distributed:
        print("Uyarı: Bu royalty zaten dağıtılmış görünüyor.")
    net = money(gross - direct_costs - admin_fee)  # Net Revenue
    shares = {
        "Mucit(ler)": money(net * inventor_p),
        "Bölüm": money(net * dept_p),
        "Kurum": money(net * inst_p),
        "TTO": money(net * tto_p),
    }
    # Basit yevmiye (karşı hesaplar uygulamada avans/hakediş olabilir; burada sadece bilgi amaçlı)
    memo = f"Royalty Dağıtımı (Net {net:.2f}) - Kural {args.rule_name}"
    with con:
        j = con.execute("INSERT INTO journal(entry_date, memo) VALUES(?,?)", (today(), memo)).lastrowid
        for label, amt in shares.items():
            # 649 Royalty Gelirlerinden ayrıştırıp emanet/ödenecek hesaplara aktarıyormuş gibi gösterelim:
            con.execute("INSERT INTO journal_lines(journal_id, account_code, debit) VALUES (?,?,?)", (j, "649", amt))
            con.execute("INSERT INTO journal_lines(journal_id, account_code, credit) VALUES (?,?,?)", (j, "360", amt))  # 360 burada 'ödenecek paylar' gibi kullanıldı
        con.execute("UPDATE royalties SET distributed=1 WHERE id=?", (rid,))
    print("Dağıtım tamam. Paylar:")
    for k,v in shares.items():
        print(f"  - {k}: {v:.2f}")
    print("Not: Gerçek ödemelerde bordro/avans/emanet alt hesapları kullanılmalıdır.")

def open_period(args):
    con = connect()
    with con:
        con.execute("INSERT INTO periods(start_date, end_date, closed) VALUES (?,?,0)", (args.start_date, args.end_date))
    print("Dönem açıldı:", args.start_date, "→", args.end_date)

def close_period(args):
    con = connect()
    p = con.execute("SELECT id, start_date, end_date, closed FROM periods WHERE id=?", (args.period_id,)).fetchone()
    if not p:
        raise SystemExit("Dönem bulunamadı")
    pid, s, e, closed = p
    if closed:
        print("Zaten kapalı.")
        return
    # TÜBİTAK 1513 uyumu (özet): işlem tarihlerinin dönemle uyumu
    # Fatura ve giderlerde sadece bu tarih aralığında kalanların olduğunu kontrol edelim.
    inv_out = con.execute("SELECT COUNT(*) FROM invoices WHERE date(issue_date) < date(?) OR date(issue_date) > date(?)", (s, e)).fetchone()[0]
    exp_out = con.execute("SELECT COUNT(*) FROM expenses WHERE date(expense_date) < date(?) OR date(expense_date) > date(?)", (s, e)).fetchone()[0]
    if inv_out or exp_out:
        print(f"Uyarı: Dönem dışında {inv_out} fatura, {exp_out} gider var. Lütfen düzeltin.")
        return
    with con:
        con.execute("UPDATE periods SET closed=1 WHERE id=?", (pid,))
    print("Dönem kapatıldı.")

def report_project(args):
    con = connect()
    p = con.execute("SELECT name, start_date, end_date FROM projects WHERE id=?", (args.project_id,)).fetchone()
    if not p:
        raise SystemExit("Proje bulunamadı")
    name, s, e = p
    inv = con.execute("""
      SELECT COUNT(*), IFNULL(SUM(amount_gross),0), IFNULL(SUM(amount_gross*vat_rate),0), IFNULL(SUM(amount_gross*wht_rate),0)
      FROM invoices WHERE project_id=?
    """, (args.project_id,)).fetchone()
    exp = con.execute("""
      SELECT COUNT(*), IFNULL(SUM(amount_net),0), IFNULL(SUM(amount_net*vat_rate),0)
      FROM expenses WHERE project_id=?
    """, (args.project_id,)).fetchone()
    roy = con.execute("""
      SELECT COUNT(*), IFNULL(SUM(amount_gross),0), IFNULL(SUM(direct_costs),0), IFNULL(SUM(admin_fee),0)
      FROM royalties WHERE project_id=?
    """, (args.project_id,)).fetchone()
    print(f"Proje: {name} (ID {args.project_id}) {s}→{e}")
    print(f"  Gelir Faturaları: {inv[0]} adet | Tutar: {inv[1]:.2f} | KDV: {inv[2]:.2f} | Stopaj: {inv[3]:.2f}")
    print(f"  Giderler       : {exp[0]} adet | Net: {exp[1]:.2f} | İndirilecek KDV: {exp[2]:.2f}")
    print(f"  Royalty        : {roy[0]} adet | Brüt: {roy[1]:.2f} | Doğrudan Maliyet: {roy[2]:.2f} | İdari Kesinti: {roy[3]:.2f}")
    # Basit kârlılık (accrual, KDV hariç)
    net_income = (inv[1]) - (exp[1]) + (roy[1] - roy[2] - roy[3])
    print(f"  Özet Kârlılık (KDV hariç, stopaj dahil değil): {net_income:.2f}")

def report_mm(args):
    con = connect()
    p = con.execute("SELECT start_date, end_date, closed FROM periods WHERE id=?", (args.period_id,)).fetchone()
    if not p:
        raise SystemExit("Dönem bulunamadı")
    s, e, closed = p
    inv = con.execute("""
      SELECT IFNULL(SUM(amount_gross),0), IFNULL(SUM(amount_gross*vat_rate),0), IFNULL(SUM(amount_gross*wht_rate),0)
      FROM invoices WHERE date(issue_date) BETWEEN date(?) AND date(?)
    """, (s, e)).fetchone()
    exp = con.execute("""
      SELECT IFNULL(SUM(amount_net),0), IFNULL(SUM(amount_net*vat_rate),0)
      FROM expenses WHERE date(expense_date) BETWEEN date(?) AND date(?)
    """, (s, e)).fetchone()
    roy = con.execute("""
      SELECT IFNULL(SUM(amount_gross),0), IFNULL(SUM(direct_costs),0), IFNULL(SUM(admin_fee),0)
      FROM royalties WHERE date(recv_date) BETWEEN date(?) AND date(?)
    """, (s, e)).fetchone()
    print(f"MM Dönem Raporu: {s} → {e} (Kapalı: {'Evet' if closed else 'Hayır'})")
    print(f"  Gelirler (KDV hariç): {inv[0]:.2f} | Hes.KDV: {inv[1]:.2f} | Stopaj: {inv[2]:.2f}")
    print(f"  Giderler (KDV hariç): {exp[0]:.2f} | İndir.KDV: {exp[1]:.2f}")
    print(f"  Royalty brüt: {roy[0]:.2f} | Doğrudan Maliyet: {roy[1]:.2f} | İdari Kesinti: {roy[2]:.2f}")
    print("Bu çıktı, mali müşavir raporu için özet niteliğindedir. Belge ekleri ve banka dekontları ayrıca sunulmalıdır.")

def report_trial_balance(args):
    con = connect()
    rows = con.execute("""
      SELECT a.code, a.name,
             ROUND(IFNULL(SUM(jl.debit),0),2) AS debit,
             ROUND(IFNULL(SUM(jl.credit),0),2) AS credit,
             ROUND(IFNULL(SUM(jl.debit),0) - IFNULL(SUM(jl.credit),0),2) AS balance
      FROM accounts a
      LEFT JOIN journal_lines jl ON jl.account_code = a.code
      GROUP BY a.code, a.name
      ORDER BY a.code
    """).fetchall()
    print("Kod | Hesap Adı | Borç | Alacak | Bakiye")
    for code, name, d, c, b in rows:
        print(f"{code} | {name} | {d:.2f} | {c:.2f} | {b:.2f}")

# --- CLI ---------------------------------------------------------------

def make_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="tto_accounting", description="Minimal TTO muhasebe CLI")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("init", help="Veritabanını ve tabloyu oluştur")
    s.set_defaults(func=init_db)

    s = sub.add_parser("project:add", help="Proje ekle")
    s.add_argument("--name", required=True)
    s.add_argument("--funding-type", dest="funding_type", choices=["TUBITAK","SANAYI","LISANS","DIGER"], required=True)
    s.add_argument("--start", dest="start_date", type=iso, required=True)
    s.add_argument("--end", dest="end_date", type=iso, required=True)
    s.set_defaults(func=add_project)

    s = sub.add_parser("project:list", help="Projeleri listele")
    s.set_defaults(func=list_projects)

    s = sub.add_parser("invoice:add", help="Gelir faturası ekle (accrual)")
    s.add_argument("--project-id", type=int, required=True)
    s.add_argument("--date", dest="issue_date", type=iso, required=True)
    s.add_argument("--amount", type=float, required=True, help="KDV hariç")
    s.add_argument("--vat-rate", type=float, default=0.20)
    s.add_argument("--wht-rate", type=float, default=0.00, help="Tevkifat/stopaj oranı")
    s.add_argument("--desc", dest="description", required=True)
    s.set_defaults(func=add_invoice)

    s = sub.add_parser("expense:add", help="Gider ekle")
    s.add_argument("--project-id", type=int, required=True)
    s.add_argument("--date", dest="expense_date", type=iso, required=True)
    s.add_argument("--category", required=True)
    s.add_argument("--amount", type=float, required=True)
    s.add_argument("--vat-rate", type=float, default=0.20)
    s.add_argument("--desc", dest="description", default="")
    s.set_defaults(func=add_expense)

    s = sub.add_parser("royalty:add", help="Royalty/lisans tahsilatı ekle")
    s.add_argument("--project-id", type=int, required=True)
    s.add_argument("--date", dest="recv_date", type=iso, required=True)
    s.add_argument("--amount", type=float, required=True)
    s.add_argument("--direct-costs", type=float, default=0.0)
    s.add_argument("--admin-fee", type=float, default=0.0)
    s.add_argument("--desc", dest="description", default="")
    s.set_defaults(func=add_royalty)

    s = sub.add_parser("royalty:distribute", help="Royalty dağıtımı yap")
    s.add_argument("--royalty-id", type=int, required=True)
    s.add_argument("--rule", dest="rule_name", default="STD_TR_UNI")
    s.set_defaults(func=distribute_royalty)

    s = sub.add_parser("period:open", help="Dönem aç (MM için tarih aralığı)")
    s.add_argument("--start", dest="start_date", type=iso, required=True)
    s.add_argument("--end", dest="end_date", type=iso, required=True)
    s.set_defaults(func=open_period)

    s = sub.add_parser("period:close", help="Dönemi kapat (tarih uyumu kontrolü)")
    s.add_argument("--id", dest="period_id", type=int, required=True)
    s.set_defaults(func=close_period)

    s = sub.add_parser("report:project", help="Proje özeti")
    s.add_argument("--project-id", type=int, required=True)
    s.set_defaults(func=report_project)

    s = sub.add_parser("report:mm", help="MM dönem raporu özeti")
    s.add_argument("--id", dest="period_id", type=int, required=True)
    s.set_defaults(func=report_mm)

    s = sub.add_parser("report:trial", help="Basit mizan")
    s.set_defaults(func=report_trial_balance)

    return p

def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    parser = make_parser()
    args = parser.parse_args(argv)
    args.func(args)

if __name__ == "__main__":
    main()
''')

out_path = Path("/mnt/data/tto_accounting.py")
out_path.write_text(code, encoding="utf-8")
print(f"Yazıldı: {out_path}")

