import pymem
from offsets import Offsets

def get_weapon_id():
    pm = pymem.Pymem("cs2.exe")
    client = pymem.process.module_from_name(pm.process_handle, "client.dll").lpBaseOfDll

    local_pawn = pm.read_ulonglong(client + Offsets.dwLocalPlayerPawn)
    if not local_pawn:
        print("[!] Local player pawn not found")
        return

    weapon_ptr = pm.read_ulonglong(local_pawn + Offsets.m_pClippingWeapon)
    if not weapon_ptr:
        print("[!] No weapon equipped")
        return

    weapon_id_addr = weapon_ptr + Offsets.m_AttributeManager + Offsets.m_Item + Offsets.m_iItemDefinitionIndex
    weapon_id = pm.read_ushort(weapon_id_addr)
    print(f"Weapon ID: {weapon_id}")

if __name__ == "__main__":
    get_weapon_id()
