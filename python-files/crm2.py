import pandas as pd
import requests
from collections import defaultdict

def main():
    # 1) Prompt for your session_id
    session_id = input("Paste your session_id cookie value: ").strip()
    # 1a) Prompt for your UID
    user_uid = int(input("Paste your user UID (e.g. 3426): ").strip())

    # 2) Read student codes from Excel (column A, header in A1)
    df = pd.read_excel("ILA.xlsx", header=0)
    codes = df.iloc[:, 0].dropna().astype(str).tolist()

    # 3) Prepare HTTP session
    BASE_URL = "https://crm.ila.edu.vn"
    session = requests.Session()
    session.headers.update({
        "Content-Type": "application/json; charset=utf-8",
        "Cookie": f"session_id={session_id}"
    })

    # 4) Stage 1: batch-fetch student IDs + student names
    payload_students = {
        "jsonrpc": "2.0", "method": "call", "id": 1,
        "params": {
            "model": "crm.student.ila", "method": "web_search_read",
            "args": [], "kwargs": {
                "specification": {
                    "student_code": {},     # code
                    "name": {},             # student name
                },
                "domain": [["student_code", "in", codes]],
                "limit": len(codes), "offset": 0, "order": "",
                "context": {
                    "lang": "en_US",
                    "tz": "Asia/Bangkok",
                    "uid": user_uid
                }
            }
        }
    }
    resp1 = session.post(
        f"{BASE_URL}/web/dataset/call_kw/crm.student.ila/web_search_read",
        json=payload_students
    )
    resp1.raise_for_status()
    student_recs = resp1.json().get("result", {}).get("records", [])

    # Build mappings: code -> student_id, student_id -> student_name
    code_to_id = {r["student_code"]: r["id"] for r in student_recs}
    id_to_name = {r["id"]: r["name"] for r in student_recs}

    # 5) Stage 2: per-student call_button to get account IDs
    code_to_acct_ids = {}
    all_acct_ids = []
    for code, sid in code_to_id.items():
        payload_dom = {
            "jsonrpc": "2.0", "method": "call", "id": 2,
            "params": {
                "model": "crm.student.ila", "method": "view_ila_account",
                "args": [[sid]],
                "kwargs": {
                    "context": {
                        "lang": "en_US",
                        "tz": "Asia/Bangkok",
                        "uid": user_uid
                    }
                }
            }
        }
        r2 = session.post(f"{BASE_URL}/web/dataset/call_button", json=payload_dom)
        r2.raise_for_status()
        domain = r2.json().get("result", {}).get("domain", [])
        acct_ids = domain[0][2] if domain else []
        code_to_acct_ids[code] = acct_ids
        all_acct_ids.extend(acct_ids)

    # 6) Stage 3: batch-fetch all account records
    unique_acct_ids = list(set(all_acct_ids))
    payload_bal = {
        "jsonrpc": "2.0", "method": "call", "id": 3,
        "params": {
            "model": "erp.ila.account", "method": "web_search_read",
            "args": [], "kwargs": {
                "specification": {
                    "student_id": {"fields": {"display_name": {}}},
                    "product_category_code": {},
                    "current_amount": {}
                },
                "domain": [["id", "in", unique_acct_ids]],
                "limit": len(unique_acct_ids), "offset": 0, "order": "",
                "context": {
                    "lang": "en_US",
                    "tz": "Asia/Bangkok",
                    "uid": user_uid
                }
            }
        }
    }
    r3 = session.post(
        f"{BASE_URL}/web/dataset/call_kw/erp.ila.account/web_search_read",
        json=payload_bal
    )
    r3.raise_for_status()
    acct_recs = r3.json().get("result", {}).get("records", [])

    # 7) Group non-zero balances by student_id
    grouped = defaultdict(list)
    for rec in acct_recs:
        sid = rec["student_id"]["id"]
        amt_str = rec["current_amount"]
        try:
            if float(amt_str.replace(",", "")) > 0:
                grouped[sid].append(f"{rec['product_category_code']}: {amt_str}")
        except ValueError:
            continue

    # 8) Add "Name" and "Balances" columns
    df["Name"] = df.iloc[:, 0].map(lambda c: id_to_name.get(code_to_id.get(c), "Access Denied"))
    def format_balances(code):
        sid = code_to_id.get(code)
        if sid is None:
            return "Access Denied"
        items = grouped.get(sid, [])
        return "\n".join(items) if items else "0"
    df["Balances"] = df.iloc[:, 0].map(format_balances)

    # 9) Save to Excel
    output_file = "ILA_with_balances.xlsx"
    df.to_excel(output_file, index=False)
    print(f"Completed. Results saved to {output_file}")

if __name__ == "__main__":
    main()
