
import hashlib

def generate_license_key(hardware_id):
    return hashlib.sha256(hardware_id.encode()).hexdigest()[:16].upper()

uuid_input = input("أدخل UUID الزبون: ").strip()
key = generate_license_key(uuid_input)
print(f"مفتاح التفعيل لهذا الجهاز هو: {key}")
