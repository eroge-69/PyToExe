# main.py

def ask_yes_no(prompt):
    while True:
        ans = input(f"{prompt} (yes/no): ").strip().lower()
        if ans in ("yes", "y"):
            return True
        if ans in ("no", "n"):
            return False
        print("Please type yes or no.")

def ask_nonneg_int(prompt):
    while True:
        s = input(prompt).strip()
        if s.isdigit():
            return int(s)
        print("Please enter a nonnegative whole number (0, 1, 2, ...).")

def collect_items(count_prompt, item_label):
    items = []
    count = ask_nonneg_int(count_prompt)
    if count == 0:
        return items
    for i in range(count):
        val = input(f"Enter {item_label} #{i+1}: ").strip()
        items.append(val)
    return items

def print_numbered(items):
    for idx, txt in enumerate(items, start=1):
        print(f"{idx}. {txt}")

def main():
    # ---------------------------- USER INPUTS ---------------------------- #
    nem_address = input("Input NEM address: ")
    xfmr_id = input("Enter xfmr ID on CTG: ")
    feeder_number = input("Enter feeder number: ")
    feeder_name = input("Enter feeder name: ")
    voltage = input("Enter voltage: ")

    # ---------------------------- SOLAR LOGIC ---------------------------- #
    solar_results = []
    if not ask_yes_no("Is there any existing solar?"):
        solar_results.append("There are no existing solar.")
    else:
        existed_before = ask_yes_no("Did any exist before 1/1/2024?")
        existing_before = []
        if existed_before:
            existing_before = collect_items(
                "How many existed before 1/1/2024? ",
                "details for existing solar (before 1/1/2024)"
            )
            if len(existing_before) == 0:
                solar_results.append("No existing solar before 1/1/2024")
            else:
                before_str = ", ".join(existing_before)
                solar_results.append(f"{len(existing_before)} existing solars: {before_str} prior to 1/1/24. Solar power factors set to 1")
        else:
            solar_results.append("There is no existing solar.")

        existed_after = ask_yes_no("Did any exist after 1/1/2024?")
        existing_after = []
        if existed_after:
            existing_after = collect_items(
                "How many existed after 1/1/2024? ",
                "details for existing solar (after 1/1/2024)"
            )
            if len(existing_after) == 0:
                solar_results.append("No existing solar after 1/1/2024")
            else:
                after_str = ", ".join(existing_after)
                solar_results.append(f"{len(existing_after)} existing solars: {after_str} on or after 1/1/24. Solar power factors set to 1")
        else:
            solar_results.append("No existing solar after 1/1/2024")

        has_pending = ask_yes_no("Is there any pending solar?")
        if not has_pending:
            solar_results.append("There is no pending solar")
        else:
            pending = collect_items(
                "How many pending solar(s)? ",
                "details for pending solar"
            )
            if len(pending) == 0:
                solar_results.append("No pending solar")
            else:
                pending_str = ", ".join(pending)
                solar_results.append(f"{len(pending)} pending solars: {pending_str}. Solar power factors set to 1")

    # ---------------------------- BEFORE & AFTER CASE PROMPTS ---------------------------- #
    final_lines = {
        "before": {"service_drop": [], "mainline": [], "xfmr": [], "notes": []},
        "after": {"service_drop": [], "mainline": [], "xfmr": [], "notes": []},
    }
    data_store = {
        "before": {"service_drop": [], "mainline": {"facilities": [], "existing_sizes": [], "proposed_sizes": []}, "xfmr": []},
        "after":  {"service_drop": [], "mainline": {"facilities": [], "existing_sizes": [], "proposed_sizes": []}, "xfmr": []},
    }

    # ---- BEFORE: Service drop failures
    has_before_drop_fail = ask_yes_no("Are there any before case service drop failures?")
    if has_before_drop_fail:
        num_failed = ask_nonneg_int("How many service drops failed? ")
        for i in range(num_failed):
            addr = input(f"Enter failed service address #{i+1}: ").strip()
            fac = input(f"Enter service drop facility ID for address #{i+1}: ").strip()
            existing_wire = input(f"What is the existing wire size for {addr}? ").strip()
            proposed_wire = input(f"What is the proposed upgrade wire size for {addr}? ").strip()
            data_store["before"]["service_drop"].append({
                "address": addr, "facility_id": fac, "existing": existing_wire, "proposed": proposed_wire
            })
        for info in data_store["before"]["service_drop"]:
            final_lines["before"]["service_drop"].append(f"failure for for service drop: {info['address']}")
        for info in data_store["before"]["service_drop"]:
            final_lines["before"]["service_drop"].append(
                f"existing service drop to {info['address']} is {info['existing']} upgrade to {info['proposed']}"
            )
    else:
        final_lines["before"]["notes"].append("No before case service drop failures. Proceed to after case section.")

    # ---- BEFORE: Mainline failures
    has_mainline_fail = ask_yes_no("Are there any before case mainline failures?")
    if not has_mainline_fail:
        final_lines["before"]["notes"].append("No before case mainline failures. Continue to xfmr upgrades section.")
    else:
        spans = ask_nonneg_int("How many spans are being upgraded? ")
        if spans == 0:
            final_lines["before"]["notes"].append("0 spans provided. No mainline entries to process.")
        else:
            for i in range(spans + 1):
                fid = input(f"Enter MH/Pole facility ID for item {i+1}: ").strip()
                data_store["before"]["mainline"]["facilities"].append(fid)
            for i in range(spans):
                ex = input(f"Enter existing mainline cable/wire size from {data_store['before']['mainline']['facilities'][i]} to {data_store['before']['mainline']['facilities'][i+1]}: ").strip()
                data_store["before"]["mainline"]["existing_sizes"].append(ex)
            for i in range(spans):
                pr = input(f"Enter proposed upgrade mainline cable/wire size from {data_store['before']['mainline']['facilities'][i]} to {data_store['before']['mainline']['facilities'][i+1]}: ").strip()
                data_store["before"]["mainline"]["proposed_sizes"].append(pr)
            for i in range(spans):
                a = data_store["before"]["mainline"]["facilities"][i]
                b = data_store["before"]["mainline"]["facilities"][i+1]
                ex = data_store["before"]["mainline"]["existing_sizes"][i]
                pr = data_store["before"]["mainline"]["proposed_sizes"][i]
                final_lines["before"]["mainline"].append(
                    f"existing mainline at {a} to {b} is {ex} to be upgraded to {pr}"
                )

    # ---- BEFORE: XFMR failures
    has_before_xfmr_fail = ask_yes_no("Are there any before case xfmr failures?")
    if not has_before_xfmr_fail:
        final_lines["before"]["notes"].append("No before case xfmr failures.")
    else:
        n_fail = ask_nonneg_int("How many xfmrs fail? ")
        for i in range(n_fail):
            is_upgrade = ask_yes_no(f"For xfmr #{i+1}: Is this xfmr being upgraded? (If no, a new one is being added)")
            if is_upgrade:
                facility_id = input("Enter the xfmr facility ID: ").strip()
                existing_size = input("Enter the existing xfmr size: ").strip()
                upgrade_size = input("Enter the upgraded xfmr size: ").strip()
                data_store["before"]["xfmr"].append({
                    "kind": "upgrade", "facility_id": facility_id, "existing": existing_size, "proposed": upgrade_size, "new_size": None
                })
                final_lines["before"]["xfmr"].append(
                    f"The existing {facility_id} rated {existing_size} is to be upgraded to {upgrade_size}"
                )
            else:
                mh_pole_id = input("Enter the MH/Pole facility ID where it will be placed: ").strip()
                new_size = input("Enter the new installed xfmr size: ").strip()
                data_store["before"]["xfmr"].append({
                    "kind": "new", "facility_id": mh_pole_id, "existing": None, "proposed": None, "new_size": new_size
                })
                final_lines["before"]["xfmr"].append(
                    f"New proposed xfmr rate {new_size} will be placed on MH/Pole {mh_pole_id}"
                )

    # ---- AFTER: Service drop failures
    has_after_drop_fail = ask_yes_no("Are there any after case service drop failures?")
    if has_after_drop_fail:
        num_failed_after = ask_nonneg_int("How many service drops failed after case? ")
        for i in range(num_failed_after):
            addr = input(f"Enter failed service address after case #{i+1}: ").strip()
            fac = input(f"Enter service drop facility ID for after case address #{i+1}: ").strip()
            existing_wire = input(f"After case existing wire size for {addr}? ").strip()
            proposed_wire = input(f"After case proposed upgrade wire size for {addr}? ").strip()
            data_store["after"]["service_drop"].append({
                "address": addr, "facility_id": fac, "existing": existing_wire, "proposed": proposed_wire
            })
        for info in data_store["after"]["service_drop"]:
            final_lines["after"]["service_drop"].append(f"failure for for service drop: {info['address']}")
        for info in data_store["after"]["service_drop"]:
            final_lines["after"]["service_drop"].append(
                f"existing service drop to {info['address']} is {info['existing']} upgrade to {info['proposed']}"
            )
    else:
        final_lines["after"]["notes"].append("No after case service drop failures.")

    # ---- AFTER: Mainline failures
    has_mainline_fail_after = ask_yes_no("Are there any after case mainline failures?")
    if not has_mainline_fail_after:
        final_lines["after"]["notes"].append("No after case mainline failures.")
    else:
        spans_after = ask_nonneg_int("How many spans are being upgraded after case? ")
        if spans_after == 0:
            final_lines["after"]["notes"].append("0 spans provided after case. No mainline entries to process.")
        else:
            for i in range(spans_after + 1):
                fid = input(f"Enter MH/Pole facility ID after case for item {i+1}: ").strip()
                data_store["after"]["mainline"]["facilities"].append(fid)
            for i in range(spans_after):
                ex = input(f"Enter after case existing mainline size from {data_store['after']['mainline']['facilities'][i]} to {data_store['after']['mainline']['facilities'][i+1]}: ").strip()
                data_store["after"]["mainline"]["existing_sizes"].append(ex)
            for i in range(spans_after):
                pr = input(f"Enter after case proposed mainline size from {data_store['after']['mainline']['facilities'][i]} to {data_store['after']['mainline']['facilities'][i+1]}: ").strip()
                data_store["after"]["mainline"]["proposed_sizes"].append(pr)
            for i in range(spans_after):
                a = data_store["after"]["mainline"]["facilities"][i]
                b = data_store["after"]["mainline"]["facilities"][i+1]
                ex = data_store["after"]["mainline"]["existing_sizes"][i]
                pr = data_store["after"]["mainline"]["proposed_sizes"][i]
                final_lines["after"]["mainline"].append(
                    f"existing mainline at {a} to {b} is {ex} to be upgraded to {pr}"
                )

    # ---- AFTER: XFMR failures
    has_after_xfmr_fail = ask_yes_no("Are there any after case xfmr failures?")
    if not has_after_xfmr_fail:
        final_lines["after"]["notes"].append("No after case xfmr failures.")
    else:
        n_fail_after = ask_nonneg_int("How many xfmrs fail after case? ")
        for i in range(n_fail_after):
            is_upgrade_after = ask_yes_no(f"For xfmr after case #{i+1}: Is this xfmr being upgraded? (If no, a new one is being added)")
            if is_upgrade_after:
                facility_id = input("Enter the xfmr facility ID after case: ").strip()
                existing_size = input("Enter the existing xfmr size after case: ").strip()
                upgrade_size = input("Enter the upgraded xfmr size after case: ").strip()
                data_store["after"]["xfmr"].append({
                    "kind": "upgrade", "facility_id": facility_id, "existing": existing_size, "proposed": upgrade_size, "new_size": None
                })
                final_lines["after"]["xfmr"].append(
                    f"The existing {facility_id} rated {existing_size} is to be upgraded to {upgrade_size}"
                )
            else:
                mh_pole_id = input("Enter the MH/Pole facility ID after case where it will be placed: ").strip()
                new_size = input("Enter the new installed xfmr size after case: ").strip()
                data_store["after"]["xfmr"].append({
                    "kind": "new", "facility_id": mh_pole_id, "existing": None, "proposed": None, "new_size": new_size
                })
                final_lines["after"]["xfmr"].append(
                    f"New proposed xfmr rate {new_size} will be placed on MH/Pole {mh_pole_id}"
                )

    # ---------------------------- FINAL PRINTS (ALL OUTPUT AT END) ---------------------------- #
    print("\n--- User Input Summary ---")
    print("NEM Address:", nem_address)
    print("Transformer ID:", xfmr_id)
    print("Feeder Number:", feeder_number)
    print("Feeder Name:", feeder_name)
    print("Voltage:", voltage)

    print("\n--- Solar System Summary ---")
    if solar_results:
        for r in solar_results:
            print(r)
    else:
        print("No solar info to display.")

    print("\n=== BEFORE CASE SERVICE DROP SUMMARY ===")
    if final_lines["before"]["service_drop"]:
        for line in final_lines["before"]["service_drop"]:
            print(line)
    else:
        print("No service drop summary to display for before case.")

    print("\n=== BEFORE CASE MAINLINE SUMMARY ===")
    if final_lines["before"]["mainline"]:
        for line in final_lines["before"]["mainline"]:
            print(line)
    else:
        print("No mainline summary to display for before case.")

    print("\n=== BEFORE CASE XFMR SUMMARY ===")
    if final_lines["before"]["xfmr"]:
        for line in final_lines["before"]["xfmr"]:
            print(line)
    else:
        print("No xfmr summary to display for before case.")

    print("\n=== BEFORE CASE NOTES ===")
    if final_lines["before"]["notes"]:
        for line in final_lines["before"]["notes"]:
            print(line)
    else:
        print("No notes for before case.")

    print("\n=== AFTER CASE SERVICE DROP SUMMARY ===")
    if final_lines["after"]["service_drop"]:
        for line in final_lines["after"]["service_drop"]:
            print(line)
    else:
        print("No service drop summary to display for after case.")

    print("\n=== AFTER CASE MAINLINE SUMMARY ===")
    if final_lines["after"]["mainline"]:
        for line in final_lines["after"]["mainline"]:
            print(line)
    else:
        print("No mainline summary to display for after case.")

    print("\n=== AFTER CASE XFMR SUMMARY ===")
    if final_lines["after"]["xfmr"]:
        for line in final_lines["after"]["xfmr"]:
            print(line)
    else:
        print("No xfmr summary to display for after case.")

    print("\n=== AFTER CASE NOTES ===")
    if final_lines["after"]["notes"]:
        for line in final_lines["after"]["notes"]:
            print(line)
    else:
        print("No notes for after case.")

    # -------- FIELD TEAM NOTES (Bottom) --------
    print("\n=== FIELD TEAM NOTES — BEFORE CASE ===")
    if data_store["before"]["service_drop"]:
        print("\nService addresses that failed:")
        print_numbered([d["address"] for d in data_store["before"]["service_drop"]])
        print("\nNotes for service addresses:")
        print_numbered([f"Generate a topo for address: {d['address']}" for d in data_store["before"]["service_drop"]])
        print("\nService drop facility IDs that failed:")
        print_numbered([d["facility_id"] for d in data_store["before"]["service_drop"]])
        print("\nNotes for service drops:")
        print_numbered([f"Field team needs to sketch/investigate service drop at facility ID: {d['facility_id']}" for d in data_store["before"]["service_drop"]])
    else:
        print("\nNo failed service addresses or drops before case.")
    bf_ml = data_store["before"]["mainline"]["facilities"]
    if len(bf_ml) >= 2:
        print("\nMainline spans that failed:")
        spans_desc = [f"{bf_ml[i]} to {bf_ml[i+1]}" for i in range(len(bf_ml) - 1)]
        print_numbered(spans_desc)
        print("\nNotes for mainline spans:")
        print_numbered([f"Field team needs to sketch/investigate span: {pair}" for pair in spans_desc])
    else:
        print("\nNo failed mainline spans before case.")
    if data_store["before"]["xfmr"]:
        print("\nXfmr facility IDs that failed:")
        print_numbered([x["facility_id"] for x in data_store["before"]["xfmr"]])
        print("\nNotes for xfmrs:")
        print_numbered([f"Please sketch manhole or pole for existing xfmr at facility ID: {x['facility_id']}" for x in data_store["before"]["xfmr"]])
    else:
        print("\nNo failed xfmrs before case.")

    print("\n=== FIELD TEAM NOTES — AFTER CASE ===")
    if data_store["after"]["service_drop"]:
        print("\nService addresses that failed:")
        print_numbered([d["address"] for d in data_store["after"]["service_drop"]])
        print("\nNotes for service addresses:")
        print_numbered([f"Generate a topo for address: {d['address']}" for d in data_store["after"]["service_drop"]])
        print("\nService drop facility IDs that failed:")
        print_numbered([d["facility_id"] for d in data_store["after"]["service_drop"]])
        print("\nNotes for service drops:")
        print_numbered([f"Field team needs to sketch/investigate service drop at facility ID: {d['facility_id']}" for d in data_store["after"]["service_drop"]])
    else:
        print("\nNo failed service addresses or drops after case.")
    af_ml = data_store["after"]["mainline"]["facilities"]
    if len(af_ml) >= 2:
        print("\nMainline spans that failed:")
        spans_desc_after = [f"{af_ml[i]} to {af_ml[i+1]}" for i in range(len(af_ml) - 1)]
        print_numbered(spans_desc_after)
        print("\nNotes for mainline spans:")
        print_numbered([f"Field team needs to sketch/investigate span: {pair}" for pair in spans_desc_after])
    else:
        print("\nNo failed mainline spans after case.")
    if data_store["after"]["xfmr"]:
        print("\nXfmr facility IDs that failed:")
        print_numbered([x["facility_id"] for x in data_store["after"]["xfmr"]])
        print("\nNotes for xfmrs:")
        print_numbered([f"Please sketch manhole or pole for existing xfmr at facility ID: {x['facility_id']}" for x in data_store["after"]["xfmr"]])
    else:
        print("\nNo failed xfmrs after case.")

if __name__ == "__main__":
    main()
