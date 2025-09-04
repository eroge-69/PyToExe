from concurrent.futures import ThreadPoolExecutor, as_completed
import pandas as pd
import requests

# === CONFIG ===
EXCEL_FILE = "citrev-ReuqestForReviewsTestData-v2.xlsx"
INPUT_SHEET = "RequestPayload"
OUTPUT_SHEET = "ResponsePayload"

# DEV environment
# API_URL = "https://api-dev.servicereview.gov.gr/dev-cr-reviews-api/reviews"
# API_KEY = "AEBEF4F0-D045-4C05-BAC6-A13D4D983F42"

# UAT environment
API_URL = "https://api-uat.servicereview.gov.gr/uat-cr-reviews-api/reviews"
API_KEY = "8486288ac8ac4ff8a9c0aa0b8d47f35e"

# === LOAD DATA FROM EXCEL ===
df = pd.read_excel(EXCEL_FILE, sheet_name=INPUT_SHEET)

headers = {
    "api-key": API_KEY,
    "x-cr-apikey": "",
    "Content-Type": "application/json"
}

def try_cast(val, to_type):
    try:
        return to_type(val)
    except (ValueError, TypeError):
        return None

def make_request(row):
    if row.get("performRequest") == 0:
        return None  # skip row completely
    try:
        headers["x-cr-apikey"] = try_cast(row.get("x-cr-apikey"), str)
        # --- Build request payload ---
        payload = {
            "extRefId": try_cast(row.get("extRefId"), str),
            "organizationData": {
                "orgCode": try_cast(row.get("orgCode"), int),
                "servicePointCode": try_cast(row.get("servicePointCode"), int),
                "deptCode": try_cast(row.get("deptCode"), str),
                "deptDescr": try_cast(row.get("deptDescr"), str)
            },
            "serviceData": {
                "serviceCode": try_cast(row.get("serviceCode"), int),
                "serviceProvisionTimestamp": row.get("serviceProvisionTimestamp").isoformat().replace("+00:00", "Z"),
                "serviceStatus": try_cast(row.get("serviceStatus"), int)
            },
            "citizenData": {
                "citizenIdType": try_cast(row.get("citizenIdType"), int),
                "citizenId": try_cast(row.get("citizenId"), str)
            },
            "userDefinedVar": try_cast(row.get("userDefinedVar"), str),
            "communicationPreference": try_cast(row.get("communicationPreference", 1), int)
        }
        # payload = {
        #     "extRefId": "REQ-WEB",
        #     "organizationData": {
        #         "orgCode": 11000002,
        #         "servicePointCode": 13000004,
        #         "deptCode": "DEP-12",
        #         "deptDescr": "Γραφείο Εξυπηρέτησης Κοινού"
        #     },
        #     "serviceData": {
        #         "serviceCode": 12000004,
        #         "serviceProvisionTimestamp": "2025-08-28T08:38:00Z",
        #         "serviceStatus": 3
        #     },
        #     "citizenData": {
        #         "citizenIdType": 1,
        #         "citizenId": "061428663"
        #     },
        #     "userDefinedVar": "this should be for web",
        #     "communicationPreference": 1
        # }
    except Exception as e:
        print(f"⚠️  Skipping row due to error in payload construction: {e}")
        return {
            "extRefId": None,
            "reviewCaseID": None,
            "reviewToken": None,
            "reviewShortUrl": None,
            "status": "FAILED",
            "errorCode": None,
            "errorDescription": str(e)
        }

    try:
        # --- Make API call ---
        response = requests.post(API_URL, json=payload, headers=headers, timeout=50)
        response.raise_for_status()
        data = response.json()

        # Success Response
        return {
            "extRefId": data.get("extRefId"),
            "reviewCaseID": data.get("reviewCaseId"),
            "reviewToken": data.get("reviewToken"),
            "reviewShortUrl": data.get("reviewShortUrl"),
            "status": "SUCCESS",
            "errorCode": None,
            "errorDescription": None
        }

    except requests.exceptions.HTTPError:
        # Try to parse error body
        try:
            err = response.json()
            return {
                "extRefId": payload["extRefId"],
                "reviewCaseID": None,
                "reviewToken": None,
                "reviewShortUrl": None,
                "status": f"ERROR {err.get('status')}",
                "errorCode": err.get("error", {}).get("code"),
                "errorDescription": err.get("error", {}).get("description")
            }
        except Exception:
            return {
                "extRefId": payload["extRefId"],
                "reviewCaseID": None,
                "reviewToken": None,
                "reviewShortUrl": None,
                "status": f"ERROR {response.status_code}",
                "errorCode": None,
                "errorDescription": response.text
            }

    except Exception as e:
        # Network / unexpected errors
        return {
            "extRefId": payload["extRefId"],
            "reviewCaseID": None,
            "reviewToken": None,
            "reviewShortUrl": None,
            "status": "FAILED",
            "errorCode": None,
            "errorDescription": str(e)
        }

# === Ask user ===
#mode = input("Run API calls (s)equentially or (p)arallel? [s/p]: ").strip().lower()

mode="s"

response_rows = []

if mode == "p":
    print("⚡ Running in parallel...")
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(make_request, row) for _, row in df.iterrows()]
        for future in as_completed(futures):
            result = future.result()
            if result:  # skip None
                response_rows.append(result)
else:
    print("🐢 Running sequentially...")
    for _, row in df.iterrows():
        result = make_request(row)
        if result:  # skip None
            response_rows.append(result)

# === SAVE RESPONSES TO NEW SHEET ===
response_df = pd.DataFrame(response_rows)

with pd.ExcelWriter(EXCEL_FILE, engine="openpyxl", mode="a", if_sheet_exists="replace") as writer:
    response_df.to_excel(writer, sheet_name=OUTPUT_SHEET, index=False)

print(f"✅ Done. Responses saved in sheet '{OUTPUT_SHEET}' of {EXCEL_FILE}")
input("Press Enter to continue...")
