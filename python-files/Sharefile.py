import json
import logging
import os
from datetime import datetime
from pathlib import Path

import requests

# ---------------- Tunables (flip as needed) ----------------
ALLOW_REDIRECTS_TOKEN = False   # PAD used False; try True if you see 3xx
ALLOW_REDIRECTS_REQUEST = True  # PAD used True
VERIFY_SSL = True               # set to False only for debugging

# ---------------- Configuration ----------------
SHAREFILE_SUBDOMAIN = os.getenv("SHAREFILE_SUBDOMAIN", "sturgisbanktrustcompany")

# Use env vars in production; hardcoded defaults here for convenience.
SHAREFILE_CLIENT_ID = os.getenv("SHAREFILE_CLIENT_ID", "YuJb3huPRMXhEvuAyAJwhHDUGc9ImNAH")
SHAREFILE_CLIENT_SECRET = os.getenv("SHAREFILE_CLIENT_SECRET", "fDZjDHNw7rSWNymSgR58JERaEEBFPMoQBmNewoF5YFgxpgkN")
SHAREFILE_USERNAME = os.getenv("SHAREFILE_USERNAME", "rbeachy@sturgis.bank")
SHAREFILE_PASSWORD = os.getenv("SHAREFILE_PASSWORD", "gfre k3lb kazv ir3m")

FOLDER_ID = os.getenv("SHAREFILE_FOLDER_ID", "fo6f5e75-9e5f-4e5c-9f5d-cd36b77e8fe5")
REQUEST_SUBJECT = os.getenv("REQUEST_SUBJECT", "Test File Request from Python API")
REQUEST_BODY = os.getenv(
    "REQUEST_BODY",
    "Please upload a test file. I need this ASAP so that I can download it and quickly delete it"
)
NOTIFY_ON_UPLOAD = True  # must be a bool

# recipients (replace with CSV reader if desired)
EMAILS = ["jcampbell@sturgis.bank","rbeachy@oaknetserv.com]

# User-Agent kept for parity with PAD
USER_AGENT = "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.21) Gecko/20100312 Firefox/3.6"

# ---------------- Logging ----------------
LOG_FOLDER = Path(os.getenv("LOG_FOLDER", r"c:\temp\logs"))
LOG_FOLDER.mkdir(parents=True, exist_ok=True)
log_file = LOG_FOLDER / f"sharefile_request_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
logging.basicConfig(
    filename=str(log_file),
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
console.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
logging.getLogger().addHandler(console)


def _debug_http(resp: requests.Response, label: str) -> None:
    """Emit compact debug lines for HTTP responses."""
    try:
        body_preview = resp.text[:500]
    except Exception:
        body_preview = "<unreadable>"
    logging.error(
        f"{label} failed: HTTP {resp.status_code} {resp.reason}\n"
        f"URL: {resp.request.method} {resp.request.url}\n"
        f"Headers: {dict(resp.request.headers)}\n"
        f"Body: {resp.request.body!r}\n"
        f"Response: {body_preview}"
    )


def get_access_token(
    subdomain: str,
    client_id: str,
    client_secret: str,
    username: str,
    password: str,
    timeout: int = 30,
) -> str:
    """
    POST form-encoded to /oauth/token with grant_type=password.
    Returns access_token string.
    """
    url = f"https://sturgisbanktrustcompany.sharefile.com/oauth/token"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": USER_AGENT,
    }
    data = {
        "grant_type": "password",
        "client_id": client_id,
        "client_secret": client_secret,
        "username": username,
        "password": password,
    }

    logging.info(f"Requesting access token from {url}")
    resp = requests.post(
        url, headers=headers, data=data, timeout=timeout,
        allow_redirects=ALLOW_REDIRECTS_TOKEN, verify=VERIFY_SSL
    )
    if not resp.ok:
        _debug_http(resp, "Token request")
        resp.raise_for_status()

    payload = resp.json()
    token = payload.get("access_token")
    if not token:
        logging.error(f"No access_token in response: {payload}")
        raise RuntimeError("ShareFile token response missing access_token.")
    logging.info("Access token acquired.")
    return token


def create_file_request(
    subdomain: str,
    token: str,
    emails: list,
    folder_id: str,
    subject: str,
    body: str,
    notify_on_upload: bool,
    timeout: int = 30,
) -> dict:
    """
    POST JSON to /sf/v3/Shares/Request with Bearer token.
    """
    url = f"https://{subdomain}.sf-api.com/sf/v3/Shares/Request"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
        "User-Agent": USER_AGENT,
    }
    payload = {
        "Emails": emails,
        "FolderID": folder_id,
        "Subject": subject,
        "Body": body,
        "NotifyOnUpload": notify_on_upload,
    }

    logging.info(f"Creating file request for {len(emails)} recipient(s) in folder {folder_id}")
    resp = requests.post(
        url, headers=headers, json=payload, timeout=timeout,
        allow_redirects=ALLOW_REDIRECTS_REQUEST, verify=VERIFY_SSL
    )
    if not resp.ok:
        _debug_http(resp, "Shares/Request")
        resp.raise_for_status()

    result = resp.json()
    logging.info("File request created successfully.")
    return result


def _validate_inputs():
    problems = []
    if not SHAREFILE_SUBDOMAIN:
        problems.append("SHAREFILE_SUBDOMAIN is empty")
    if not SHAREFILE_CLIENT_ID:
        problems.append("SHAREFILE_CLIENT_ID is empty")
    if not SHAREFILE_CLIENT_SECRET:
        problems.append("SHAREFILE_CLIENT_SECRET is empty")
    if not SHAREFILE_USERNAME:
        problems.append("SHAREFILE_USERNAME is empty")
    if not SHAREFILE_PASSWORD:
        problems.append("SHAREFILE_PASSWORD is empty")
    if not FOLDER_ID or not FOLDER_ID.startswith("fo"):
        problems.append("FOLDER_ID looks wrong (expecting an id starting with 'fo')")
    if not EMAILS:
        problems.append("No recipients in EMAILS")
    if problems:
        raise SystemExit("Config error(s):\n- " + "\n- ".join(problems))


def main():
    _validate_inputs()

    token = get_access_token(
        SHAREFILE_SUBDOMAIN,
        SHAREFILE_CLIENT_ID,
        SHAREFILE_CLIENT_SECRET,
        SHAREFILE_USERNAME,
        SHAREFILE_PASSWORD,
    )

    result = create_file_request(
        SHAREFILE_SUBDOMAIN,
        token,
        EMAILS,
        FOLDER_ID,
        REQUEST_SUBJECT,
        REQUEST_BODY,
        NOTIFY_ON_UPLOAD,
    )

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()