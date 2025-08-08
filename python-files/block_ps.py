# block_ps_domain.py
#!/usr/bin/env python3
"""
block_ps_domain.py

Adds np.communication.playstation.net to your NextDNS denylist.
"""

import sys
import requests

# ⚙️ Configuration (hard-coded)
API_KEY    = "a23f02321c933625ef2e5392b518beba1c55d241"
PROFILE_ID = "ab22c7"
DOMAIN     = "np.communication.playstation.net"
API_URL    = f"https://api.nextdns.io/profiles/{PROFILE_ID}/denylist"

def main():
    headers = {
        "X-Api-Key": API_KEY,
        "Content-Type": "application/json",
    }
    payload = {"id": DOMAIN, "active": True}

    resp = requests.post(API_URL, headers=headers, json=payload)
    if resp.ok:
        print(f"✅ Successfully blocked {DOMAIN}")
    else:
        print(f"❌ Failed ({resp.status_code}): {resp.text}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
