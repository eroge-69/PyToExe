# unblock_ps.py
#!/usr/bin/env python3
"""
unblock_ps.py

Removes np.communication.playstation.net from your NextDNS denylist
using only the Python standard library.
"""

import sys
from urllib import request, error

API_KEY    = "a23f02321c933625ef2e5392b518beba1c55d241"
PROFILE_ID = "ab22c7"
DOMAIN     = "np.communication.playstation.net"
URL        = f"https://api.nextdns.io/profiles/{PROFILE_ID}/denylist/{DOMAIN}"

def main():
    req = request.Request(URL, method="DELETE")
    req.add_header("X-Api-Key", API_KEY)

    try:
        with request.urlopen(req):
            print("✅ Unblocked")
    except error.HTTPError as e:
        body = e.read().decode("utf-8")
        print(f"❌ Failed ({e.code}): {body}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
