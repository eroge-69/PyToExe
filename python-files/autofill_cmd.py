import json
import pyperclip
from pathlib import Path

STORE_PATH = Path.home() / ".full_card_cmd.json"

def load_card():
    if STORE_PATH.exists():
        try:
            return json.loads(STORE_PATH.read_text())
        except:
            return {}
    return {}

def save_card(data):
    STORE_PATH.write_text(json.dumps(data))

def menu():
    card = load_card()
    while True:
        print("\n=== Card Manager CMD ===")
        print("1. ذخیره/ویرایش کارت")
        print("2. نمایش کارت")
        print("3. کپی شماره کارت")
        print("4. کپی تاریخ انقضا")
        print("5. کپی CVV")
        print("6. کپی نام دارنده")
        print("7. خروج")
        choice = input("انتخاب: ").strip()

        if choice == "1":
            card["number"] = input("شماره کارت: ").strip()
            card["expiry"] = input("تاریخ انقضا (MM/YY): ").strip()
            card["cvv"] = input("CVV: ").strip()
            card["holder"] = input("نام دارنده: ").strip()
            save_card(card)
            print(":white_check_mark: کارت ذخیره شد")
        elif choice == "2":
            if not card:
                print("کارت ذخیره نشده")
            else:
                print(json.dumps(card, indent=2, ensure_ascii=False))
        elif choice == "3":
            if "number" in card:
                pyperclip.copy(card["number"])
                print(":clipboard: شماره کارت کپی شد")
        elif choice == "4":
            if "expiry" in card:
                pyperclip.copy(card["expiry"])
                print(":clipboard: تاریخ انقضا کپی شد")
        elif choice == "5":
            if "cvv" in card:
                pyperclip.copy(card["cvv"])
                print(":clipboard: CVV کپی شد")
        elif choice == "6":
            if "holder" in card:
                pyperclip.copy(card["holder"])
                print(":clipboard: نام دارنده کپی شد")
        elif choice == "7":
            break
        else:
            print("گزینه نامعتبر!")

if name == "__main__":
    menu()