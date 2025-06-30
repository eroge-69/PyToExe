#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import math

# Cabinet layout constants
MCC_HEIGHT = 2036
CABLE_ZONE_HEIGHT = 300
ACTIVE_WIDTH = 600  # width of normal active cabinet
CABLE_ZONE_WIDTH = 300
MAIN_SWITCH_WIDTH = 600
PLC_WIDTH = 800
PLC_CZ_WIDTH = 300

def prompt_positive_int(prompt_text):
    while True:
        try:
            value = int(input(prompt_text))
            if value < 0:
                print("Please enter a non-negative number.")
            else:
                return value
        except ValueError:
            print("Invalid input. Please enter a whole number.")

def main():
    # Inputs
    dol_count = prompt_positive_int("Enter the number of DOL and FCB circuits: ")

    ss_total = prompt_positive_int("Enter the total number of Soft Starters: ")
    ss_under_135a = prompt_positive_int("How many of those SS are under 135A: ")
    while ss_under_135a > ss_total:
        print("You can't have more under-135A SS than total SS.")
        ss_under_135a = prompt_positive_int("How many of those Soft Starters are under 135A: ")

    vsd_total = prompt_positive_int("Enter the total number of VSDs: ")
    vsd_under_37kw = prompt_positive_int("How many of those VSDs are under 37kW: ")
    while vsd_under_37kw > vsd_total:
        print("You can't have more under-37kW VSDs than total VSDs.")
        vsd_under_37kw = prompt_positive_int("How many of those VSDs are under 37kW: ")

    print("\n--- Summary ---")
    print(f"DOL and FCB Circuits: {dol_count}")
    print(f"Soft Starters: {ss_total} total, {ss_under_135a} under 135A")
    print(f"VSDs: {vsd_total} total, {vsd_under_37kw} under 37kW")

    # Apply 20% spare capacity to counts
    dol_count = math.ceil(dol_count * 1.2)
    ss_total = math.ceil(ss_total * 1.2)
    ss_under_135a = math.ceil(ss_under_135a * 1.2)
    vsd_total = math.ceil(vsd_total * 1.2)
    vsd_under_37kw = math.ceil(vsd_under_37kw * 1.2)

    # Ensure under limits don't exceed totals
    ss_under_135a = min(ss_under_135a, ss_total)
    vsd_under_37kw = min(vsd_under_37kw, vsd_total)

    # Cabinet heights (mm)
    dol_heights = [180] * dol_count
    ss_heights = [180] * ss_under_135a + [300] * (ss_total - ss_under_135a)
    vsd_heights = [180] * vsd_under_37kw + [300] * (vsd_total - vsd_under_37kw)

    # Combine active cabinets
    all_active_heights = dol_heights + ss_heights + vsd_heights
    all_active_heights.sort(reverse=True)

    # Stack active cabinets without splitting
    stacks = []
    for h in all_active_heights:
        placed = False
        for i, stack in enumerate(stacks):
            max_h = MCC_HEIGHT if i == 0 else MCC_HEIGHT - CABLE_ZONE_HEIGHT
            if sum(stack) + h <= max_h:
                stack.append(h)
                placed = True
                break
        if not placed:
            stacks.append([h])

    num_stacks = len(stacks)

    # Calculate total active width (active cabinets + cable zones)
    active_width = num_stacks * (ACTIVE_WIDTH + CABLE_ZONE_WIDTH)

    # Calculate full height side cabinets width
    standalone_400mm_count = ss_under_135a + vsd_under_37kw
    standalone_400mm_width = standalone_400mm_count * 400

    standalone_600mm_count = (ss_total - ss_under_135a) + (vsd_total - vsd_under_37kw)
    standalone_600mm_width = standalone_600mm_count * 600

    standalone_total_width = standalone_400mm_width + standalone_600mm_width

    # Add main switch and PLC widths + PLC cable zone
    total_width_mm = MAIN_SWITCH_WIDTH + active_width + standalone_total_width + PLC_WIDTH + PLC_CZ_WIDTH

    print(f"\n--- MCC Layout ---")
    print(f"Total active cabinets (with 20% spare): {len(all_active_heights)}")
    print(f"Active stacks required: {num_stacks}")
    print(f"standalone cabinets: {standalone_400mm_count} @ 400mm wide, {standalone_600mm_count} @ 600mm wide")
    print(f"Total MCC width: {total_width_mm} mm")
    print(f"Includes:")
    print(f"  - {MAIN_SWITCH_WIDTH} mm main switch")
    print(f"  - {active_width} mm active stacks + cable zones")
    print(f"  - {standalone_total_width} mm standalone full height cabinets")
    print(f"  - {PLC_WIDTH} mm PLC + {PLC_CZ_WIDTH} mm cable zone")

    # Stack utilization summary
    print("\n--- Active Stack Utilization ---")
    for i, stack in enumerate(stacks):
        max_h = MCC_HEIGHT if i == 0 else MCC_HEIGHT - CABLE_ZONE_HEIGHT
        used_h = sum(stack)
        utilization = (used_h / max_h) * 100
        print(f"Stack {i+1}: Used {used_h} mm of {max_h} mm ({utilization:.2f}% utilized)")

    # Wait for user to press Enter before exiting
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()


# In[ ]:





# In[ ]:




