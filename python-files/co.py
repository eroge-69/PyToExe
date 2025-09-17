import os
from openpyxl import load_workbook, Workbook

def find_combination(nums, target):
    result = []

    def backtrack(start, path, total):
        if total == target:
            result.extend(path)
            return True
        if total > target:
            return False

        for i in range(start, len(nums)):
            if backtrack(i + 1, path + [nums[i]], total + nums[i]):
                return True
        return False

    if backtrack(0, [], 0):
        return result
    else:
        return None

# 📁 File paths
input_file = r"E:\Pyhton\test154.xlsx"
output_file = r"E:\Pyhton\result.xlsx"

# 📂 Open Excel file for manual input
if os.path.exists(input_file):
    print("Opening Excel file for data entry...")
    os.startfile(input_file)

    input("📥 Paste numbers into A2 to A11 (under header 'DATA') and put target in B2. Save and then press Enter...")

    # Load workbook
    wb = load_workbook(input_file)
    sheet = wb.active

    # ✅ Read values from A2 to A11 (below header)
    nums = []
    for row in sheet['A2':'A11']:
        for cell in row:
            if isinstance(cell.value, (int, float)):
                nums.append(cell.value)

    # ✅ Read target from B2
    target_cell = sheet['B2'].value
    if isinstance(target_cell, (int, float)):
        target = target_cell
    else:
        print("❌ Target in B2 is missing or invalid.")
        exit()

    print(f"📊 Input numbers: {nums}")
    print(f" Target: {target}")

    #  Find combination
    result = find_combination(nums, target)

    # 🧾 Write result to new Excel file
    wb_result = Workbook()
    result_sheet = wb_result.active
    result_sheet.title = "Result"

    if result:
        for idx, num in enumerate(result, start=1):
            result_sheet[f"A{idx}"] = num
        result_sheet["C1"] = "Target"
        result_sheet["D1"] = target
        result_sheet["C2"] = "Sum"
        result_sheet["D2"] = sum(result)
        print(f" Combination found: {result} → sum = {sum(result)}")
    else:
        result_sheet["A1"] = "No combination found"
        print("❌ No combination found.")

    wb_result.save(output_file)
    print(f" Result saved to: {output_file}")
    os.startfile(output_file)  # Open result Excel file

else:
    print("❌ Input Excel file not found.")
    