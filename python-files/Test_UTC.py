from datetime import datetime, timezone

# Get the current UTC datetime object
utc_now = datetime.now(timezone.utc)

# Convert the UTC datetime object to a Unix timestamp (seconds since epoch)
utc_timestamp = utc_now.timestamp()

print(f"Current UTC Timestamp: {utc_timestamp}")