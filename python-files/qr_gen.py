import qrcode

def generate_payment_qr(iban, name, amount, comment, filename="utalas_qr.png"):
    """
    Magyar HCT QR kód generátor átutaláshoz.
    - iban: kedvezményezett számlaszám (IBAN formátumban)
    - name: kedvezményezett neve
    - amount: összeg forintban (string vagy int)
    - comment: közlemény
    - filename: mentett fájl neve (png)
    """
    qr_content = f"""BCD
001
1
SCT

{iban}
{name}
{amount}
HUF
{comment}"""

    img = qrcode.make(qr_content)
    img.save(filename)
    print(f"QR kód elmentve ide: {filename}")


# Példa használat:
generate_payment_qr(
    iban="HU42117730161111111111111111",
    name="Konyvelo Kft.",
    amount="25000",
    comment="Számla 2025/09",
    filename="szamla_qr.png"
)
