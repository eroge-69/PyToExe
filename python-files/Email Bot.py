import requests
import json
import csv
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

# -------------------------
# Banner
# -------------------------
def print_banner():
    print("\n" + "=" * 70)
    print("   S   M   S   P   O   F")
    print("=" * 70)
    print("               Made by @smithpof")
    print("     S M S P O F   Email Extractor Via Domain")
    print("=" * 70 + "\n")

# -------------------------
# Config loader
# -------------------------
def load_config(config_file="config.json"):
    try:
        with open(config_file, "r", encoding="utf-8") as f:
            cfg = json.load(f)
        cfg.setdefault("max_workers", 10)
        cfg.setdefault("output_file", "result.csv")
        cfg.setdefault("job_titles", [])  # default empty = no filter
        return cfg
    except FileNotFoundError:
        raise SystemExit(f"Config file '{config_file}' not found. Create it with your api_key.")
    except json.JSONDecodeError as e:
        raise SystemExit(f"Error parsing '{config_file}': {e}")

# -------------------------
# Domains read
# -------------------------
def read_domains(file_path):
    with open(file_path, 'r', encoding="utf-8") as file:
        domains = file.readlines()
    return [domain.strip() for domain in domains if domain.strip()]

# -------------------------
# API call
# -------------------------
def enrich_company(domain, api_key):
    url = "https://myapiconnect.com/api-product/incoming-webhook/enrich-company"
    headers = {'Content-Type': 'application/json'}
    data = {"api_key": api_key, "domain": domain}

    try:
        response = requests.post(url, json=data, headers=headers, timeout=30)
        response.raise_for_status()
        return domain, response.json()
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] {domain}: {e}")
        return domain, None

# -------------------------
# CSV writer (LibreOffice-friendly, with filtering)
# -------------------------
def save_all_results_csv(results, output_file, job_titles):
    # Normalize filter keywords (lowercase)
    job_titles = [jt.lower() for jt in job_titles]

    # Gather all possible employee keys for header
    fieldnames = set(["domain"])
    for res in results:
        for emp in res.get("employees", []):
            fieldnames.update(emp.keys())
    fieldnames = list(fieldnames)

    with open(output_file, "w", newline="", encoding="utf-8-sig") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for res in results:
            domain = res.get("domain", "")
            employees = res.get("employees") or []
            for emp in employees:
                if job_titles:
                    job_title = emp.get("job_title", "").lower()
                    if not any(keyword in job_title for keyword in job_titles):
                        continue  # skip if not matching
                row = {"domain": domain}
                row.update(emp)
                writer.writerow(row)

    print(f"[DONE] All results saved to {output_file}")

# -------------------------
# Main processing
# -------------------------
def process_domains(domain_file, api_key, max_workers=10, output_file="result.csv", job_titles=None):
    domains = read_domains(domain_file)
    if not domains:
        print("[WARN] No domains found in the domain file.")
        return

    all_results = []
    print(f"[INFO] Processing {len(domains)} domains with {max_workers} workers...")

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_domain = {executor.submit(enrich_company, domain, api_key): domain for domain in domains}

        for idx, future in enumerate(as_completed(future_to_domain), 1):
            domain, result = future.result()
            print(f"[{idx}/{len(domains)}] Processed: {domain}")
            if result:
                all_results.append({"domain": domain, "employees": result.get("employees", [])})
            else:
                all_results.append({"domain": domain, "employees": []})

    save_all_results_csv(all_results, output_file, job_titles or [])

# -------------------------
# Entrypoint
# -------------------------
if __name__ == "__main__":
    print_banner()
    cfg = load_config("config.json")
    domain_file = "domains.txt"
    api_key = cfg.get("api_key")
    if not api_key:
        raise SystemExit("api_key missing in config.json")

    max_workers = cfg.get("max_workers", 10)
    output_file = cfg.get("output_file", "result.csv")
    job_titles = cfg.get("job_titles", [])

    start = time.time()
    process_domains(domain_file, api_key, max_workers=max_workers, output_file=output_file, job_titles=job_titles)
    elapsed = time.time() - start
    print("-" * 70)
    print(f"[SUMMARY] Completed in {elapsed:.2f}s")
