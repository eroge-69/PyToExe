import plyvel
import os
import zipfile

# Open the database
db_path = "./users.db.data"
output_txt = "db_dump.txt"
output_zip = "db_dump.zip"

print(f"Opening database at {db_path}...")
db = plyvel.DB(db_path, create_if_missing=False)

# Dump all entries
with open(output_txt, "w", encoding="utf-8") as f:
    for key, value in db:
        try:
            key_decoded = key.decode("utf-8", errors="ignore")
            value_decoded = value.decode("utf-8", errors="ignore")
            # Highlight VIN-related entries
            if "SAJAA4BX6JCP40284" in key_decoded or "asBuilt" in key_decoded or "vbf" in key_decoded:
                f.write(f"[**HIT**] {key_decoded} => {value_decoded}\n")
            else:
                f.write(f"{key_decoded} => {value_decoded}\n")
        except:
            f.write(f"{key} => {value}\n")
db.close()

# Zip the dump automatically
with zipfile.ZipFile(output_zip, "w", zipfile.ZIP_DEFLATED) as z:
    z.write(output_txt)

print(f"Done! Dump saved to {output_txt} and zipped as {output_zip}.")
