
from __future__ import annotations
import csv
import json
import os
import sys
import tempfile
import time
from typing import Dict, List, Optional

try:
    import requests
except Exception as _e:  # pragma: no cover
    print("Missing dependency: requests. Install with: pip install requests", file=sys.stderr)
    raise

# -----------------------------
# EDIT THESE SETTINGS (or use env vars)
# -----------------------------
TOKEN = os.getenv("WHATSAPP_TOKEN", "YOUR_ACCESS_TOKEN")
PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID", "YOUR_PHONE_ID")
CSV_FILE = os.getenv("CSV_FILE", "recipients.csv")  # Accept from env or default
TEMPLATE_NAME = os.getenv("WA_TEMPLATE", "order_update")  # Approved template name
LANG_CODE = os.getenv("WA_LANG", "en")  # e.g., en, en_GB, ur
DRY_RUN = os.getenv("DRY_RUN", "1") not in ("0", "false", "False")  # default True
RATE_LIMIT = float(os.getenv("RATE_LIMIT", "1.0"))  # messages per second
AUTO_CREATE_SAMPLE = os.getenv("AUTO_CREATE_SAMPLE", "1") not in ("0", "false", "False")
# -----------------------------

GRAPH_VERSION = "v21.0"
API_BASE = f"https://graph.facebook.com/{GRAPH_VERSION}"

# ========= Utilities =========

def _script_dir() -> str:
    try:
        return os.path.dirname(os.path.abspath(__file__))
    except NameError:
        return os.getcwd()


def resolve_csv_path(path: str) -> Optional[str]:
    """Return an existing path to the CSV, searching sensible locations.
    Order: given path (abs/rel to CWD) -> same name in script dir.
    """
    # 1) as provided (absolute or relative to current working dir)
    if os.path.isabs(path) and os.path.isfile(path):
        return path
    if os.path.isfile(path):  # relative to CWD
        return os.path.abspath(path)
    # 2) relative to the script directory
    candidate = os.path.join(_script_dir(), path)
    if os.path.isfile(candidate):
        return candidate
    return None


def create_sample_csv(target_path: str) -> str:
    os.makedirs(os.path.dirname(target_path) or ".", exist_ok=True)
    with open(target_path, "w", newline="", encoding="utf-8") as f:
        f.write("phone,var1,var2\n")
        f.write("923001112223,Ali,AB-123\n")
        f.write("447911123456,Sara,ZX-999\n")
    return target_path


# ========= WhatsApp Client =========
class WhatsAppClient:
    def __init__(self, token: str, phone_number_id: str, timeout: int = 30):
        if not token or token == "YOUR_ACCESS_TOKEN":
            raise SystemExit("Set WHATSAPP_TOKEN or edit TOKEN constant in the script.")
        if not phone_number_id or phone_number_id == "YOUR_PHONE_ID":
            raise SystemExit("Set WHATSAPP_PHONE_NUMBER_ID or edit PHONE_NUMBER_ID in the script.")
        self.token = token
        self.phone_number_id = phone_number_id
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        })

    def send_template(
        self,
        to_number: str,
        template_name: str,
        lang: str = "en",
        body_vars: Optional[List[str]] = None,
        components: Optional[List[Dict]] = None,
    ) -> requests.Response:
        url = f"{API_BASE}/{self.phone_number_id}/messages"
        payload: Dict = {
            "messaging_product": "whatsapp",
            "to": str(to_number),
            "type": "template",
            "template": {
                "name": template_name,
                "language": {"code": lang},
            },
        }
        if components is not None:
            payload["template"]["components"] = components
        elif body_vars:
            payload["template"]["components"] = [
                {
                    "type": "body",
                    "parameters": [{"type": "text", "text": str(v)} for v in body_vars],
                }
            ]
        resp = self.session.post(url, data=json.dumps(payload), timeout=self.timeout)
        return resp


# ========= CSV handling =========

def parse_csv(path: str) -> List[Dict[str, str]]:
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        rows = [dict(r) for r in reader]
        if not rows:
            raise ValueError("CSV is empty")
        for r in rows:
            if "phone" not in r or not str(r["phone"]).strip():
                raise ValueError(f"Missing phone in row: {r}")
        return rows


# ========= Orchestration =========

def main() -> None:
    # Resolve CSV path first to avoid FileNotFoundError
    resolved = resolve_csv_path(CSV_FILE)
    if resolved is None:
        # Optionally create a sample CSV to help the user
        default_path = os.path.join(_script_dir(), os.path.basename(CSV_FILE) or "recipients.csv")
        if AUTO_CREATE_SAMPLE:
            created = create_sample_csv(default_path)
            print(
                "[setup] recipients.csv not found. A sample file was created at:\n  "
                + created
                + "\nEdit this file (keep header) and re-run the script.\n"
                + "If your CSV lives elsewhere, set the CSV_FILE env var or edit CSV_FILE in the script.",
                file=sys.stderr,
            )
            return
        else:
            raise SystemExit(
                f"CSV file not found: {CSV_FILE}. Place it next to this script or provide an absolute path."
            )

    # Load rows safely
    try:
        rows = parse_csv(resolved)
    except FileNotFoundError:
        # Should not happen due to resolve step, but handle defensively
        raise SystemExit(
            f"CSV not found at {resolved}. Ensure the file exists or change CSV_FILE."
        )
    except ValueError as ve:
        raise SystemExit(f"CSV validation error: {ve}")

    client = WhatsAppClient(token=TOKEN, phone_number_id=PHONE_NUMBER_ID)

    interval = 1.0 / max(0.1, RATE_LIMIT)
    successes, failures = 0, 0

    for i, row in enumerate(rows, start=1):
        phone = str(row.get("phone", "")).strip()
        # Gather var1, var2, ... in order
        body_vars: List[str] = []
        j = 1
        while True:
            key = f"var{j}"
            if key in row and str(row[key]).strip() != "":
                body_vars.append(str(row[key]))
                j += 1
            else:
                break

        if DRY_RUN:
            print(
                f"[DRY RUN] {i}/{len(rows)} -> {phone} template={TEMPLATE_NAME} lang={LANG_CODE} vars={body_vars}"
            )
            time.sleep(interval)
            continue

        try:
            resp = client.send_template(
                to_number=phone,
                template_name=TEMPLATE_NAME,
                lang=LANG_CODE,
                body_vars=body_vars or None,
            )
            if 200 <= resp.status_code < 300:
                print(f"OK {i}/{len(rows)} -> {phone}: {resp.status_code}")
                successes += 1
            else:
                # Try to surface error body for debugging
                try:
                    err = resp.json()
                except Exception:
                    err = resp.text
                print(f"ERR {i}/{len(rows)} -> {phone}: {resp.status_code} {err}")
                failures += 1
        except Exception as e:
            print(f"EXC {i}/{len(rows)} -> {phone}: {e}")
            failures += 1

        time.sleep(interval)

    print(f"\nDone. Success: {successes} Failures: {failures}")


# ========= Self tests =========

def _self_tests() -> None:
    """Minimal tests for parsing and path resolution."""
    print("[tests] starting self tests…")
    with tempfile.TemporaryDirectory() as td:
        # 1) Valid CSV
        good = os.path.join(td, "ok.csv")
        with open(good, "w", newline="", encoding="utf-8") as f:
            f.write("phone,var1,var2\n")
            f.write("923001111111,Ali,AB-1\n")
            f.write("447911222222,Sara,ZX-9\n")
        rows = parse_csv(good)
        assert len(rows) == 2 and rows[0]["phone"] == "923001111111"
        print("[tests] parse_csv valid file — OK")

        # 2) Empty CSV
        empty = os.path.join(td, "empty.csv")
        with open(empty, "w", newline="", encoding="utf-8") as f:
            f.write("phone\n")
        try:
            parse_csv(empty)
            raise AssertionError("Expected ValueError for empty CSV")
        except ValueError:
            print("[tests] parse_csv empty file — OK")

        # 3) Missing phone column
        bad = os.path.join(td, "bad.csv")
        with open(bad, "w", newline="", encoding="utf-8") as f:
            f.write("var1\n")
            f.write("Ali\n")
        try:
            parse_csv(bad)
            raise AssertionError("Expected ValueError for missing phone")
        except ValueError:
            print("[tests] parse_csv missing phone — OK")

        # 4) resolve_csv_path: script dir and CWD variants
        name = "test.csv"
        # Not present anywhere initially
        assert resolve_csv_path(name) is None
        # Create in script dir and find it
        sd = _script_dir()
        p = os.path.join(sd, name)
        with open(p, "w", encoding="utf-8") as f:
            f.write("phone\n923001234567\n")
        try:
            assert resolve_csv_path(name) == os.path.abspath(p)
            print("[tests] resolve_csv_path script dir — OK")
        finally:
            try:
                os.remove(p)
            except OSError:
                pass

    print("[tests] all tests passed")


if __name__ == "__main__":
    if os.getenv("SELF_TEST") == "1":
        _self_tests()
        sys.exit(0)
    main()
