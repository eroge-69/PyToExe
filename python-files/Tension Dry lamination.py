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
            "MPET": {"min": 0.00035, "max": 0.0011}, # แก้ไขตามข้อมูลที่ให้มา (เหมือน PET)
        },
        "solvent_based": {
            "PET": {"min": 0.00035, "max": 0.0011},
            "LLDPE": {"min": 0.00007, "max": 0.00021},
            "BOPA": {"min": 0.00007, "max": 0.00021},
            "BOPP": {"min": 0.00021, "max": 0.00070},
            "CPP": {"min": 0.00014, "max": 0.00035},
            "VMCPP": {"min": 0.00014, "max": 0.00035},
            "MPET": {"min": 0.00035, "max": 0.0011}, # แก้ไขตามข้อมูลที่ให้มา (เหมือน PET)
        },
    }

    if machine_type not in k_values:
        print(f"Error: ประเภทเครื่องจักร '{machine_type}' ไม่ถูกต้อง กรุณาเลือก 'solvent_free' หรือ 'solvent_based'")
        return None
...     
...     if material_type not in k_values[machine_type]:
...         print(f"Error: ประเภทวัสดุ '{material_type}' ไม่ถูกต้องสำหรับเครื่องจักร '{machine_type}'")
...         return None
... 
...     k_min = k_values[machine_type][material_type]["min"]
...     k_max = k_values[machine_type][material_type]["max"]
... 
...     unwind_min = k_min * width_mm * thickness_micron
...     unwind_max = k_max * width_mm * thickness_micron
... 
...     return unwind_min, unwind_max
... 
... ---
... 
... ## วิธีใช้งาน
... 
... ### ตัวอย่างการคำนวณสำหรับเครื่อง Solvent Free
... 
... สมมติว่าคุณต้องการคำนวณ Tension สำหรับ **เครื่อง Solvent Free**, วัสดุ **PET**, ความกว้าง **1000 mm** และความหนา **12 micron**:
... 
... ```python
... # ตัวอย่างการใช้งานสำหรับเครื่อง Solvent Free
... machine = "solvent_free"
... material = "PET"
... width = 1000  # mm
... thickness = 12  # micron
... 
... tension_min, tension_max = calculate_tension(machine, material, width, thickness)
... 
... if tension_min is not None and tension_max is not None:
...     print(f"\n--- ค่า Tension สำหรับเครื่อง {machine.replace('_', ' ').title()} ---")
...     print(f"วัสดุ: {material}")
...     print(f"ความกว้าง: {width} mm")
...     print(f"ความหนา: {thickness} micron")
...     print(f"Unwind Tension (Min): {tension_min:.4f}")
