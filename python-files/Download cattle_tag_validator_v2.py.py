import tkinter as tk
from tkinter import messagebox

def validate_tag(tag_number):
    if not tag_number.isdigit() or len(tag_number) != 11:
        return None, "Invalid input. Must be an 11-digit number."

    herd_mark_raw = tag_number[:6]
    check_digit_raw = tag_number[6]
    animal_number_raw = tag_number[7:]

    try:
        herd_mark = int(herd_mark_raw)
        check_digit_input = int(check_digit_raw)
        animal_number = int(animal_number_raw)
    except ValueError:
        return None, "Tag contains non-numeric characters."

    combined = herd_mark * 100000 + animal_number
    check_digit_expected = (combined % 7) + 1
    is_check_digit_valid = (check_digit_input == check_digit_expected)

    tag_full = f"UK {herd_mark_raw} {check_digit_raw}{animal_number_raw}"

    details = {
        "Full Tag Number": (tag_full, "✅ Generated"),
        "Country": ("UK", "✅ Correct"),
        "Herd Mark": (herd_mark_raw, "✅ Correct"),
        "Check Digit": (
            f"{check_digit_input}",
            "✅ Correct" if is_check_digit_valid else f"❌ Incorrect – Expected: {check_digit_expected}"
        ),
        "Animal Number": (animal_number_raw.zfill(5), "✅ Correct"),
    }

    return is_check_digit_valid, details


def on_validate():
    tag_input = tag_entry.get().strip()
    result_label.config(text="")
    for widget in details_frame.winfo_children():
        widget.destroy()

    is_valid, result = validate_tag(tag_input)

    if result is None:
        messagebox.showerror("Invalid Input", result)
        return

    result_label.config(
        text="✔ Tag is VALID" if is_valid else "❌ Tag is INVALID",
        fg="green" if is_valid else "red"
    )

    header_label = tk.Label(details_frame, text="Tag Information:", font=("Arial", 12, "bold"), bg="#f7f7f7")
    header_label.pack(anchor="w", pady=(5, 2))

    for key, (value, status) in result.items():
        display_text = f"{key}: {value}  {status}"
        color = "#008000" if "✅" in status else "#cc0000"
        tk.Label(details_frame, text=display_text, anchor="w", font=("Arial", 10), fg=color, bg="#f7f7f7").pack(fill="x")

    # Add diagram/explanation
    tk.Label(details_frame, text="\nVisual Tag Format:", font=("Arial", 11, "bold"), bg="#f7f7f7").pack(anchor="w", pady=(10, 2))
    diagram = [
        "UK 303565 401234",
        "↑   ↑       ↑",
        "|   |       └── Animal Number (5 digits)",
        "|   └────────── Herd Mark (6 digits)",
        "└────────────── Country Code (always 'UK')"
    ]
    for line in diagram:
        tk.Label(details_frame, text=line, anchor="w", font=("Courier New", 9), bg="#f7f7f7", fg="#555").pack(anchor="w")


# --- UI Setup ---
root = tk.Tk()
root.title("Cattle Ear Tag Validator")
root.geometry("540x500")
root.configure(bg="#f7f7f7")
root.resizable(False, False)

tk.Label(root, text="🐄 Cattle Ear Tag Validator", font=("Arial", 16, "bold"), bg="#f7f7f7", fg="#333").pack(pady=(20, 10))

tk.Label(root, text="Enter 11-digit Animal Tag Number:", bg="#f7f7f7").pack()
tag_entry = tk.Entry(root, font=("Arial", 12), justify="center", width=30)
tag_entry.pack(pady=5)

tk.Button(root, text="Validate Tag", command=on_validate, bg="#4CAF50", fg="white", font=("Arial", 12), width=20).pack(pady=10)

result_label = tk.Label(root, text="", font=("Arial", 14, "bold"), bg="#f7f7f7")
result_label.pack(pady=10)

details_frame = tk.Frame(root, bg="#f7f7f7")
details_frame.pack(pady=5, fill="both", expand=True)

root.mainloop()
