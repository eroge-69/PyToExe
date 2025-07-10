import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors
from datetime import datetime
import os

# Duration brackets (in days)
duration_brackets = [7, 15, 21, 30, 60, 90, 180, 365]

# Worldwide premiums
worldwide_premiums = {
    "Basic": {
        "Individual": [15.90, 16.21, 18.92, 22.55, 48.22, 58.48, 103.62, 190.44],
        "Family":     [39.75, 41.79, 47.28, 73.87, 120.54, 146.19, 259.04, 476.08]
    },
    "Plus": {
        "Individual": [16.26, 17.09, 19.33, 30.20, 49.27, 59.76, 105.92, 194.64],
        "Family":     [40.66, 42.73, 48.32, 75.47, 123.18, 149.40, 264.80, 486.60]
    },
    "Extra": {
        "Individual": [30.33, 31.87, 36.06, 56.32, 91.90, 111.45, 197.53, 362.99],
        "Family":     [75.82, 79.68, 90.14, 140.78, 229.76, 278.64, 493.82, 907.49]
    }
}

# Regional premiums
region_premiums = {
    "Africa": {
        "Individual": [10.03, 10.90, 12.21, 17.44, 29.07, 34.59, 47.96, 85.74],
        "Family":     [25.09, 27.25, 30.54, 43.60, 72.66, 86.46, 119.90, 214.36]
    },
    "Asia": {
        "Individual": [11.63, 12.98, 15.06, 20.95, 36.50, 51.76, 70.59, 136.60],
        "Family":     [29.07, 32.44, 39.96, 50.87, 87.19, 116.78, 174.39, 341.52],
    },
    "Europe": {
        "Individual": [13.11, 13.77, 16.85, 22.27, 38.86, 51.41, 83.52, 153.48],
    }
}

def get_base_premium(region, plan, duration):
    try:
        duration = int(duration)
    except:
        return None
    for i, limit in enumerate(duration_brackets):
        if duration <= limit:
            base = region_premiums[region][plan][i]
            print(f"[DEBUG] Duration: {duration}, Bracket Limit: {limit}, Index: {i}, Base Premium: {base}")
            return base
    return None

def get_worldwide_base(tier, duration, plan_type):
    try:
        duration = int(duration)
    except:
        return None
    for i, limit in enumerate(duration_brackets):
        if duration <= limit:
            return worldwide_premiums[tier][plan_type][i]
    return None

def calculate_age(dob_str):
    try:
        dob = datetime.strptime(dob_str, "%d-%m-%Y")
        today = datetime.today()
        return (today - dob).days / 365.25
    except:
        return None

def adjust_age_premium(base, age, region):
    if age < 0.25:
        return None, "Under 3 months not eligible"
    elif age < 18:
        return base * 0.5, "50% discount"
    elif 66 <= age <= 75:
        return base * 1.5, "+50% surcharge"
    elif 76 <= age <= 80:
        return base * 2.0, "+100% surcharge"
    elif age > 80:
        if region != "Europe":
            return None, "Only Europe allowed for over 80"
        return base * 4.0, "+300% surcharge"
    return base, None

def calculate_total_premium(region, plan_type, duration, dob_list, tier=None):
    """
    region: str (e.g., "Africa", "Worldwide")
    plan_type: "Individual" or "Family"
    duration: int
    dob_list: list of DOB strings in "dd-mm-yyyy" format
    tier: "Basic", "Plus", or "Extra" (used only for Worldwide plans)
    """
    try:
        duration = int(duration)
    except:
        return None, ["Invalid duration"]

    # Determine base premium source
    if region.lower().startswith("world"):
        if not tier:
            return None, ["Tier (Basic/Plus/Extra) required for Worldwide plans"]
        base = get_worldwide_base(tier, duration, plan_type)
    else:
        base = get_base_premium(region, plan_type, duration)

    if base is None:
        return None, ["Invalid base premium"]

    total = 0
    warnings = []

    if plan_type == "Individual":
        age = calculate_age(dob_list[0])
        if age is None:
            return None, ["Invalid DOB"]
        adjusted, note = adjust_age_premium(base, age, region)
        if adjusted is None:
            return None, [note]
        total = adjusted
        if note:
            warnings.append(note)
    else:  # Family — no age-based adjustments
        for i, dob in enumerate(dob_list):
            age = calculate_age(dob)
            if age is None:
                warnings.append(f"Traveler {i+1}: Invalid DOB")
                continue
            total += base  # Use base premium directly

    return round(total, 3), warnings

    if plan_type == "Individual":
        age = calculate_age(dob_list[0])
        if age is None:
            return None, ["Invalid DOB"]
        adjusted, note = adjust_age_premium(base, age, region)
        if adjusted is None:
            return None, [note]
        total = adjusted
        if note:
            warnings.append(note)
    else:  # Family
        for i, dob in enumerate(dob_list):
            age = calculate_age(dob)
            if age is None:
                warnings.append(f"Traveler {i+1}: Invalid DOB")
                continue
            adjusted, note = adjust_age_premium(base, age, region)
            if adjusted is None:
                warnings.append(f"Traveler {i+1}: {note}")
                continue
            total += adjusted
            if note:
                warnings.append(f"Traveler {i+1}: {note}")

    return round(total, 3), warnings

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
from datetime import datetime

def generate_pdf(name, region, duration, plan, travelers, total, warnings=[], tier=None):
    logo_path = "logo.png"  # Replace with your actual logo path
    filename = f"{name.replace(' ', '_')}_quote.pdf"
    doc = SimpleDocTemplate(filename, pagesize=A4)
    styles = getSampleStyleSheet()
    flow = []

    # Logo 🖼️
    if os.path.exists(logo_path):
        logo = Image(logo_path, width=500, height=150)
        flow.append(logo)

    # Titles 📝
    flow.append(Spacer(1, 10))
    flow.append(Paragraph("<b>QUOTATION</b>", styles['Title']))
    flow.append(Paragraph(f"<b>TRAVEL INSURANCE FOR {duration} DAYS</b>", styles['Heading2']))
    plan_info = f"{region} | {plan}"
    if region == "Worldwide" and tier:
        plan_info += f" – {tier}"
    flow.append(Paragraph(f"<b>{plan_info} | {duration} Days</b>", styles['Normal']))
    flow.append(Spacer(1, 12))

    # Table 📊
    table_data = [["S/N", "Name of Insured Persons", "Age", "Premium (Up to 11 Days)"]]
    for idx, person in enumerate(travelers, 1):
        table_data.append([
            str(idx),
            person["name"],
            f"{int(person['age'])}",
            f"${person['premium']:.2f}"
        ])
    table = Table(table_data, colWidths=[40, 200, 60, 180])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
    ]))
    flow.append(table)
    flow.append(Spacer(1, 12))

    # Total Premium 💰
    flow.append(Paragraph(f"<b>Total Premium: ${total:.2f}</b>", styles['Normal']))
    flow.append(Spacer(1, 12))

    # Surcharge Details 📉
    surcharge_text = """
    <b>Premium Reduction/Surcharge considering the Insured's Age:</b><br/>
    • 3 months to 18 years: 50% discount<br/>
    • 66–75 years: +50% surcharge<br/>
    • 76–80 years: +100% surcharge<br/>
    • 81+ years: Europe only, +300% surcharge
    """
    flow.append(Paragraph(surcharge_text, styles['Normal']))
    flow.append(Spacer(1, 12))

    # Footer 🕒
    now = datetime.now()
    footer = f"Generated by Winner Mhagama on {now.strftime('%d %b %Y')} at {now.strftime('%I:%M %p')}"
    flow.append(Paragraph(footer, styles['Normal']))

    # Build PDF
    doc.build(flow)
    messagebox.showinfo("PDF Created", f"Quotation saved as: {filename}")


# GUI Setup
root = tk.Tk()
root.title("Travel Insurance Calculator")

tk.Label(root, text="Contact Name").grid(row=0, column=0)
name_entry = tk.Entry(root)
name_entry.grid(row=0, column=1)

tk.Label(root, text="Region").grid(row=1, column=0)
region_var = tk.StringVar()
region_menu = ttk.Combobox(root, textvariable=region_var,
                           values=list(region_premiums.keys()) + ["Worldwide"],
                           state="readonly")
region_menu.grid(row=1, column=1)

tk.Label(root, text="Plan Type").grid(row=2, column=0)
plan_var = tk.StringVar()
plan_menu = ttk.Combobox(root, textvariable=plan_var,
                         values=["Individual", "Family"], state="readonly")
plan_menu.grid(row=2, column=1)

plan_note = tk.Label(root, text="", fg="red")
plan_note.grid(row=2, column=2, columnspan=2, sticky="w")

plan_tier_label = tk.Label(root, text="Worldwide Tier:")
plan_tier_var = tk.StringVar()
plan_tier_menu = ttk.Combobox(root, textvariable=plan_tier_var,
                              values=["Basic", "Plus", "Extra"], state="readonly")
def update_plan_tier_visibility(*args):
    region = region_var.get()
    if region == "Worldwide":
        plan_tier_label.grid(row=3, column=0, sticky="w")
        plan_tier_menu.grid(row=3, column=1, sticky="w")
    else:
        plan_tier_label.grid_remove()
        plan_tier_menu.grid_remove()

def on_region_change(*args):
    region = region_var.get()
    if region == "Europe":
        plan_var.set("Individual")
        plan_menu.configure(values=["Individual"])
        plan_note.config(text="Family plan not allowed for Europe", fg="red")
    else:
        plan_menu.configure(values=["Individual", "Family"])
        plan_note.config(text="")
    update_traveler_fields()
    update_plan_tier_visibility()

region_var.trace_add("write", on_region_change)
plan_var.trace_add("write", lambda *args: update_traveler_fields())

tk.Label(root, text="Trip Duration (days)").grid(row=4, column=0)
duration_entry = tk.Entry(root)
duration_entry.grid(row=4, column=1)

tk.Label(root, text="Student Plan").grid(row=5, column=0)
student_var = tk.BooleanVar()
tk.Checkbutton(root, variable=student_var).grid(row=5, column=1)

traveler_frame = tk.Frame(root)
traveler_frame.grid(row=6, column=0, columnspan=4)
traveler_entries = []

def update_traveler_fields():
    for widget in traveler_frame.winfo_children():
        widget.destroy()
    traveler_entries.clear()
    if plan_var.get() == "Family":
        for role in ["Insured", "Spouse", "Child 1", "Child 2", "Child 3"]:
            add_traveler_row(role)
    else:
        add_traveler_row("Insured")
        tk.Button(traveler_frame, text="+", width=3, command=add_traveler_row).grid(row=0, column=4, padx=5)

def add_traveler_row(role=None):
    i = len(traveler_entries)
    role = role or f"Traveler {i + 1}"
    tk.Label(traveler_frame, text=role).grid(row=i, column=0)
    name_e = tk.Entry(traveler_frame)
    name_e.grid(row=i, column=1)
    dob_e = DateEntry(traveler_frame, date_pattern='dd-mm-yyyy', width=14,
                      background='darkblue', foreground='white', borderwidth=2)
    dob_e.grid(row=i, column=2)
    tk.Label(traveler_frame, text="DOB").grid(row=i, column=3, sticky="w")
    traveler_entries.append((role, name_e, dob_e))

def calculate():
    contact = name_entry.get().strip()
    region = region_var.get()
    plan = plan_var.get()
    tier = plan_tier_var.get()
    is_student = student_var.get()

    if not contact:
        messagebox.showerror("Missing", "Enter contact name.")
        return

    try:
        duration = int(duration_entry.get().strip())
        if duration <= 0:
            raise ValueError
    except:
        messagebox.showerror("Invalid", "Enter positive trip duration.")
        return

    if duration > (365 if is_student else 92):
        messagebox.showerror("Duration Error", f"Max {365 if is_student else 92} days allowed.")
        return

    if region == "Worldwide":
        if tier not in ["Basic", "Plus", "Extra"]:
            messagebox.showerror("Missing", "Select a plan tier.")
            return
        base = get_worldwide_base(tier, duration, plan)
        if base is None:
            messagebox.showerror("Duration Error", "No plan available for entered duration.")
            return
    else:
        base = get_base_premium(region, plan, duration)
        if base is None:
            messagebox.showerror("Duration Error", f"No plan available for {region} with {duration} days.")
            return

    travelers, total, warnings = [], 0, []

    for role, name_e, dob_e in traveler_entries:
        name = name_e.get().strip()
        dob = dob_e.get().strip()
        if not name or not dob:
            continue
        age = calculate_age(dob)
        if age is None:
            warnings.append(f"{role} ({name}) has invalid DOB.")
            continue
        if age > 81:
            messagebox.showerror("Approval Required", "Over 81 requires Suniva Insurance approval.")
            return
        if "Child" in role and age > 18:
            messagebox.showerror("Age Restriction", f"{role} must be 18 or younger.")
            return

        if plan == "Individual":
            adj_premium, note = adjust_age_premium(base, age, region)
            if adj_premium is None:
                warnings.append(f"{role} ({name}) not eligible: {note}")
                continue
            total += adj_premium
        else:
            adj_premium, note = base, None  # Use base once for the whole family

        travelers.append({"role": role, "name": name, "age": age, "premium": adj_premium, "note": note})

    if plan == "Family":
        if len(travelers) != 5:
            messagebox.showerror("Plan Error", "All 5 family traveler fields must be completed.")
            return
        total = base  # Apply base premium once for the whole family

    result_label.config(text=f"Total Premium: ${total:.2f}")
    generate_pdf(contact, region, duration, plan, travelers, total, warnings)

tk.Button(root, text="Calculate & Generate PDF", command=calculate).grid(row=7, column=1, pady=10)
result_label = tk.Label(root, text="", fg="green", font=("Helvetica", 12))
result_label.grid(row=8, column=1)

update_traveler_fields()
update_plan_tier_visibility()
root.mainloop()