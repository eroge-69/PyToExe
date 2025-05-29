Python 3.13.3 (tags/v3.13.3:6280bb5, Apr  8 2025, 14:47:33) [MSC v.1943 64 bit (AMD64)] on win32
Enter "help" below or click "Help" above for more information.
def calculate_tension(machine_type, material_type, width_mm, thickness_micron):
    """
    คำนวณค่า Tension (Unwind) ตามประเภทเครื่องจักรและวัสดุ

    Args:
        machine_type (str): ประเภทเครื่องจักร ("solvent_free" หรือ "solvent_based")
        material_type (str): ประเภทวัสดุ (เช่น "PET", "LLDPE", "BOPA" เป็นต้น)
        width_mm (float): ความกว้างของวัสดุในหน่วยมิลลิเมตร
        thickness_micron (float): ความหนาของวัสดุในหน่วยไมครอน

    Returns:
        tuple: (tension_min, tension_max) หรือ None หากข้อมูลไม่ถูกต้อง
    """

    k_values = {
        "solvent_free": {
            "PET": {"min": 0.00035, "max": 0.0011},
            "LLDPE": {"min": 0.00007, "max": 0.00017},
            "BOPA": {"min": 0.00021, "max": 0.00049},
            "BOPP": {"min": 0.00017, "max": 0.00035},
            "CPP": {"min": 0.00007, "max": 0.00018},
            "VMCPP": {"min": 0.00010, "max": 0.00021},
            "MPET": {"min": 0.00035, "max": 0.0011},
        },
        "solvent_based": {
            "PET": {"min": 0.00035, "max": 0.0011},
            "LLDPE": {"min": 0.00007, "max": 0.00021},
            "BOPA": {"min": 0.00007, "max": 0.00021},
            "BOPP": {"min": 0.00021, "max": 0.00070},
            "CPP": {"min": 0.00014, "max": 0.00035},
            "VMCPP": {"min": 0.00014, "max": 0.00035},
            "MPET": {"min": 0.00035, "max": 0.0011},
        },
    }

    if machine_type not in k_values:
        print(f"Error: ประเภทเครื่องจักร '{machine_type}' ไม่ถูกต้อง กรุณาเลือก 'solvent_free' หรือ 'solvent_based'")
        return None
    
    if material_type not in k_values[machine_type]:
        print(f"Error: ประเภทวัสดุ '{material_type}' ไม่ถูกต้องสำหรับเครื่องจักร '{machine_type}'")
        return None

    k_min = k_values[machine_type][material_type]["min"]
    k_max = k_values[machine_type][material_type]["max"]

    unwind_min = k_min * width_mm * thickness_micron
    unwind_max = k_max * width_mm * thickness_micron

    return unwind_min, unwind_max

def main():
    print("--- โปรแกรมคำนวณค่า Tension ---")
    print("ประเภทเครื่องจักรที่มี: Solvent Free, Solvent Based")
    print("ประเภทวัสดุที่มี:")
    for m_type, materials in K_VALUES.items():
        print(f"- {m_type.replace('_', ' ').title()}: {', '.join(materials.keys())}")

    while True:
        machine = input("\nกรุณาเลือกประเภทเครื่องจักร (solvent_free/solvent_based): ").strip().lower()
        if machine in K_VALUES:
            break
        else:
            print("ประเภทเครื่องจักรไม่ถูกต้อง กรุณาเลือกใหม่")

    while True:
        material = input(f"กรุณาเลือกประเภทวัสดุสำหรับ {machine.replace('_', ' ').title()} ({', '.join(K_VALUES[machine].keys())}): ").strip().upper()
        if material in K_VALUES[machine]:
            break
        else:
            print("ประเภทวัสดุไม่ถูกต้อง กรุณาเลือกใหม่")
            
    while True:
        try:
            width = float(input("กรุณากรอกความกว้าง (mm): "))
            if width <= 0:
                raise ValueError
            break
        except ValueError:
            print("ความกว้างไม่ถูกต้อง กรุณากรอกตัวเลขบวก")

    while True:
        try:
            thickness = float(input("กรุณากรอกความหนา (micron): "))
            if thickness <= 0:
                raise ValueError
            break
        except ValueError:
            print("ความหนาไม่ถูกต้อง กรุณากรอกตัวเลขบวก")

...     tension_min, tension_max = calculate_tension(machine, material, width, thickness)
... 
...     if tension_min is not None and tension_max is not None:
...         print(f"\n--- ผลลัพธ์การคำนวณ ---")
...         print(f"เครื่องจักร: {machine.replace('_', ' ').title()}")
...         print(f"วัสดุ: {material}")
...         print(f"ความกว้าง: {width} mm")
...         print(f"ความหนา: {thickness} micron")
...         print(f"Unwind Tension (Min): {tension_min:.4f}")
...         print(f"Unwind Tension (Max): {tension_max:.4f}")
...     else:
...         print("\nเกิดข้อผิดพลาดในการคำนวณ โปรดตรวจสอบข้อมูล")
...     
...     input("\nกด Enter เพื่อออกจากโปรแกรม...") # เพื่อให้หน้าต่าง cmd ไม่ปิดทันทีหลังแสดงผล
... 
... # Global K_VALUES dict (moved outside function for broader access)
... K_VALUES = {
...     "solvent_free": {
...         "PET": {"min": 0.00035, "max": 0.0011},
...         "LLDPE": {"min": 0.00007, "max": 0.00017},
...         "BOPA": {"min": 0.00021, "max": 0.00049},
...         "BOPP": {"min": 0.00017, "max": 0.00035},
...         "CPP": {"min": 0.00007, "max": 0.00018},
...         "VMCPP": {"min": 0.00010, "max": 0.00021},
...         "MPET": {"min": 0.00035, "max": 0.0011},
...     },
...     "solvent_based": {
...         "PET": {"min": 0.00035, "max": 0.0011},
...         "LLDPE": {"min": 0.00007, "max": 0.00021},
...         "BOPA": {"min": 0.00007, "max": 0.00021},
...         "BOPP": {"min": 0.00021, "max": 0.00070},
...         "CPP": {"min": 0.00014, "max": 0.00035},
...         "VMCPP": {"min": 0.00014, "max": 0.00035},
...         "MPET": {"min": 0.00035, "max": 0.0011},
...     },
... }
... 
... if __name__ == "__main__":
