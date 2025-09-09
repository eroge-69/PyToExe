# This work is free. You can redistribute it and/or modify it under the
# terms of the Do What The Fuck You Want To Public License, Version 2,
# as published by Sam Hocevar. See http://www.wtfpl.net/ for more details.
import json
import hashlib
import os
import argparse
import shutil
from datetime import datetime, timedelta
import sys


def json_stringify_alphabetical(obj: dict):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


def buf_to_bigint(buf: bytes):
    return int.from_bytes(buf, byteorder="little")


def bigint_to_buf(i: int):
    return i.to_bytes((i.bit_length() + 7) // 8, byteorder="little")


class RSA:
    def __init__(self):
        self.hexrays_modulus_bytes = bytes.fromhex(
            "edfd425cf978546e8911225884436c57140525650bcf6ebfe80edbc5fb1de68f4c66c29cb22eb668788afcb0abbb718044584b810f8970cddf227385f75d5dddd91d4f18937a08aa83b28c49d12dc92e7505bb38809e91bd0fbd2f2e6ab1d2e33c0c55d5bddd478ee8bf845fcef3c82b9d2929ecb71f4d1b3db96e3a8e7aaf93"
        )
        self.hexrays_modulus = buf_to_bigint(self.hexrays_modulus_bytes)

        self.patched_modulus_bytes = bytearray(self.hexrays_modulus_bytes)
        self.patched_modulus_bytes[17] ^= 1 << 4 # peak of the golfing! only 1 bit changed
        # if you want the old patched modulus, comment the line above and uncomment the line below
        # self.patched_modulus_bytes[3] = 0xcb

        self.patched_modulus = buf_to_bigint(self.patched_modulus_bytes)
        self.exponent = 0x13
        # Small update: A lot of people were curious how was the private key generated, so let me explain.
        # You know how RSA works, right?
        # The private key usually consists of two or more prime numbers, and the public key is the product of those prime numbers.
        # p - prime number 1
        # q - prime number 2
        # n = p * q - public modulus
        # e - public exponent
        # They are being used to compute a private exponent d, which in this case is used to sign the payload.
        # d = e^-1 mod (p-1)(q-1)
        # Did you see what exactly was done to the public modulus?
        # It's a prime number! But RSA is usually used with two prime numbers, right?
        # And the only reason RSA is secure is because we assume that it's very hard to find the factors of a public modulus.
        # And if n is a prime number, then the only factor is n - which means - RSA essentially becomes a symmetric cipher.
        # So how do we get the private key? It's simple: d = e^-1 mod (n-1)
        # ~ alula
        self.private_key = pow(self.exponent, -1, self.patched_modulus - 1)
        # print("private_key:", bigint_to_buf(private_key).hex())

    def decrypt(self, message: bytes):
        decrypted = pow(buf_to_bigint(message), self.exponent, self.patched_modulus)
        decrypted = bigint_to_buf(decrypted)
        return decrypted[::-1]

    def encrypt(self, message: bytes):
        encrypted = pow(
            buf_to_bigint(message[::-1]), self.private_key, self.patched_modulus
        )
        encrypted = bigint_to_buf(encrypted)
        return encrypted


def create_license(
    name: str,
    license_type: str,
    owner="hi@hex-rays.com",
    start_date: str | None = None,
    end_date: str | None = None,
):
    if start_date is None:
        start_date = datetime.now().strftime("%Y-%m-%d")

    if end_date is None:
        # Default to 10 years - 1 day from start date
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = start_dt + timedelta(days=10 * 365 - 1)
        end_date = end_dt.strftime("%Y-%m-%d")

    id = "48-2137-ACAB-69"
    license = {
        "header": {"version": 1},
        "payload": {
            "name": owner,
            "email": owner,
            "licenses": [
                {
                    "description": "IDA Expert-2",
                    "edition_id": "ida-pro",
                    "id": id,
                    "product_id": "IDAPRO",
                    "product_version": "9.1", # does not really matter
                    "license_type": license_type,
                    # "product": "IDA",
                    "seats": 1,
                    "start_date": start_date,
                    "end_date": end_date,
                    "issued_on": f"{start_date} 00:00:00",
                    "owner": name, # should be email, but this is for custom text in about dialog
                    "add_ons": get_addons(
                        owner=id,
                        start_date=start_date,
                        end_date=end_date,
                    ),
                    "features": [],
                }
            ],
        },
    }

    return license


def get_addons(owner: str, start_date: str, end_date: str) -> list[dict]:
    # Not used anymore since 9.0
    # platforms = [
    #     "W",  # Windows
    #     "L",  # Linux
    #     "M",  # macOS
    # ]
    addons = [
        "HEXX86",
        "HEXX64",
        "HEXARM",
        "HEXARM64",
        "HEXMIPS",
        "HEXMIPS64",
        "HEXPPC",
        "HEXPPC64",
        "HEXRV",
        "HEXRV64",
        "HEXARC",
        # Cloud, but obviously we can't use it cracked
        # "HEXCX86",
        # "HEXCX64",
        # "HEXCARM",
        # "HEXCARM64",
        # "HEXCMIPS",
        # "HEXCMIPS64",
        # "HEXCPPC",
        # "HEXCPPC64",
        # "HEXCRV",
        # "HEXCRV64",
        # "HEXCARC",
    ]

    result = []

    i = 0
    for addon in addons:
        i += 1
        result.append(
            {
                "id": f"48-1337-DEAD-{i:02}",
                "code": addon,
                "owner": owner,
                "start_date": start_date,
                "end_date": end_date,
            }
        )
    # for addon in addons:
    #     for platform in platforms:
    #         i += 1
    #         result.append(
    #             {
    #                 "id": f"48-1337-DEAD-{i:02}",
    #                 "code": addon + platform,
    #                 "owner": owner,
    #                 "start_date": start_date,
    #                 "end_date": end_date,
    #             }
    #         )
    return result


def generate_license_file(license_data, filename="idapro.hexlic"):
    license_data["signature"] = sign_hexlic(license_data["payload"])
    serialized = json_stringify_alphabetical(license_data)

    with open(filename, "w") as f:
        f.write(serialized)

    print(f"Saved new license to {filename}!")
    return True


def patch_ida_files(apply=False):
    """Patch all IDA files"""
    files_to_patch = [
        "ida32.dll",
        "ida.dll",
        "libida32.so",
        "libida.so",
        "libida32.dylib",
        "libida.dylib",
    ]

    success_count = 0
    for filename in files_to_patch:
        if generate_patched_dll(filename, apply):
            success_count += 1

    if apply:
        # if we're on macOS, try to run codesign
        if sys.platform == "darwin":
            parent_path = os.path.abspath(os.curdir)
            if not parent_path.endswith("Contents/MacOS"):
                print(
                    "Error: Unexpected path structure. In order to re-sign the bundle, this script should be run from xxx.app/Contents/MacOS/"
                )
                return success_count

            bundle_dir = os.path.abspath(os.path.join(parent_path, "../.."))

            try:
                result = os.system(f"xattr -c '{bundle_dir}'")
                if result != 0:
                    print(
                        "Error: Failed to clear extended attributes on the IDA bundle."
                    )
            except Exception as e:
                print(f"Error while trying to clear extended attributes: {e}")

            try:
                result = os.system(f"codesign --verbose -f -s - --deep '{bundle_dir}'")
                if result != 0:
                    print("Error: Failed to re-sign the IDA bundle.")
            except Exception as e:
                print(f"Error while trying to re-sign the IDA bundle: {e}")

    return success_count


rsa = RSA()


def sign_hexlic(payload: dict) -> str:
    data = {"payload": payload}
    data_str = json_stringify_alphabetical(data)

    buffer = bytearray(128)
    # first 33 bytes are random
    for i in range(33):
        buffer[i] = 0x42

    # compute sha256 of the data
    sha256 = hashlib.sha256()
    sha256.update(data_str.encode())
    digest = sha256.digest()

    # copy the sha256 digest to the buffer
    for i in range(32):
        buffer[33 + i] = digest[i]

    # encrypt the buffer
    encrypted = rsa.encrypt(buffer)

    return encrypted.hex().upper()


def generate_patched_dll(filename, apply=False):
    if not os.path.exists(filename):
        # print(f"Didn't find {filename}, skipping patch generation")
        return False

    with open(filename, "rb") as f:
        data = f.read()

        if data.find(rsa.patched_modulus_bytes) != -1:
            print(f"{filename} looks to be already patched :)")
            return True

        if data.find(rsa.hexrays_modulus_bytes) == -1:
            print(f"{filename} doesn't contain the original modulus.")
            return False

        data = data.replace(
            rsa.hexrays_modulus_bytes, rsa.patched_modulus_bytes
        )

        patched_filename = f"{filename}.patched"
        with open(patched_filename, "wb") as f:
            f.write(data)

        print(f"Generated patch: {patched_filename}")

    if apply:
        # Check if file is writable
        try:
            with open(filename, "r+b"):
                pass
        except Exception:
            print(f"Error: {filename} is not writable. Cannot swap files.")
            return False

        backup_filename = f"{filename}.bak"
        try:
            if not os.path.exists(backup_filename):
                shutil.copy2(filename, backup_filename)
                print(f"Created backup: {backup_filename}")
            else:
                print(
                    f"Backup already exists: {backup_filename}, skipping backup creation."
                )

            # Replace original with patched
            shutil.move(patched_filename, filename)
            print(f"Swapped {filename} with patched version")
            return True
        except Exception as e:
            print(f"Error swapping files: {e}")
            return False
    else:
        print(
            "To apply the patch, replace the original files with the patched files"
        )
        return True


class ArgumentParserWithHelp(argparse.ArgumentParser):
    def error(self, message):
        sys.stderr.write("error: %s\n" % message)
        self.print_help()
        sys.exit(2)


def main():
    parser = ArgumentParserWithHelp(
        description="IDA Pro 9.x keygen",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --patch                   : Generate .patched files only
  %(prog)s --patch --apply           : Generate patches and apply them to current IDA installation
                                     : on macOS attempts to also re-sign the bundle
  %(prog)s --license                 : Generate license only
  %(prog)s --oneshot                 : Patch IDA then generate license - equivalent to running --patch --apply then --license
  %(prog)s --license --name "bnuuy"  : Custom name
  %(prog)s --oneshot --license-type floating --end-date 2030-12-31

How to use:
  1. Place this script in the directory where IDA is installed and all .dll/.so/.dylib files are located.
     On Windows it's C:\\Program Files\\IDA Professional 9.x\\
     On Linux it's ~/ida-pro-9.x/
     On macOS it's /Applications/IDA Professional 9.x.app/Contents/MacOS/
  2. You most likely just want to run the script with --oneshot option, which will do everything automatically.
  3. If you want run individual steps, see the options above.

Note: This version of the keygen uses a different modulus patch than the previous version. 
      See the source code in case you want to use the old patch.
        """,
    )

    mode_group = parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument(
        "--patch", action="store_true", help="Generate patched DLL files"
    )
    mode_group.add_argument(
        "--license", action="store_true", help="Generate license file only"
    )
    mode_group.add_argument(
        "--oneshot", action="store_true", help="Patch IDA files and generate license"
    )

    parser.add_argument(
        "--apply",
        action="store_true",
        help="Apply patches to original files (creates .bak backups)",
    )

    parser.add_argument(
        "--name",
        # idgaf what you do, but if you republish this script as your own without 
        # any meaningful changes, you're just a skid
        default="cracked by alula :3",
        help="License holder name (default: %(default)s)",
    )
    parser.add_argument(
        "--license-type",
        choices=["named", "floating", "computer"],
        default="named",
        help="License type (default: %(default)s)",
    )
    parser.add_argument(
        "--start-date", help="License start date (YYYY-MM-DD, default: today)"
    )
    parser.add_argument(
        "--end-date",
        help="License end date (YYYY-MM-DD, default: 10 years from start date)",
    )

    args = parser.parse_args()

    args.apply = args.apply or args.oneshot

    # Validate date format if provided
    for date_arg in [args.start_date, args.end_date]:
        if date_arg:
            try:
                datetime.strptime(date_arg, "%Y-%m-%d")
            except ValueError:
                print(
                    f"Error: Invalid date format '{date_arg}'. Use YYYY-MM-DD format."
                )
                return 1

    # end date must not be before start date and must not be more than 10 years from start date
    if args.start_date and args.end_date:
        start_dt = datetime.strptime(args.start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(args.end_date, "%Y-%m-%d")

        if end_dt < start_dt:
            print("Error: End date must not be before start date.")
            return 1

        if (end_dt - start_dt).days >= 3650:
            print("Error: End date must not be more than 10 years from start date.")
            return 1

    success = True

    if args.patch or args.oneshot:
        success_count = patch_ida_files(args.apply)
        success = success_count > 0

        if success_count == 0:
            print(
                "No files were patched. Ensure that you run this script from the IDA installation directory."
            )
            parser.print_help()
            return 1

    if args.license or args.oneshot:
        print("Generating license...")
        license_data = create_license(
            name=args.name,
            license_type=args.license_type,
            start_date=args.start_date,
            end_date=args.end_date,
        )

        success = generate_license_file(license_data)

    return 0 if success else 1


if __name__ == "__main__":
    exit(main())
