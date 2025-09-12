# -- coding: utf-8 --

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListFlowable, ListItem
# ===== Knowledge Base with all machines + extended problems =====
knowledge_base = {
    "Engine": {
        "Engine vibration": {"symptoms":["excessive vibration","unusual noise","shaking dashboard"],
                             "causes":["worn bearings","loose bolts","imbalanced rotating parts","misaligned crankshaft"],
                             "solutions":["Replace bearings","Tighten bolts","Balance rotating parts","Align crankshaft"]},
        "Engine overheating": {"symptoms":["high temperature","burning smell","coolant warning light"],
                               "causes":["blocked cooling system","low ventilation","overload","faulty thermostat"],
                               "solutions":["Clean cooling system","Improve ventilation","Reduce load","Replace thermostat"]},
        "Oil leakage": {"symptoms":["oil stains","low oil level","smell of oil"],
                        "causes":["damaged gasket","loose bolts","cracked engine block","worn seals"],
                        "solutions":["Replace gasket","Tighten bolts","Repair/replace engine block","Replace seals"]},
        "Fuel system issue": {"symptoms":["engine stutters","loss of power","hard start"], 
                              "causes":["clogged fuel filter","faulty fuel pump","bad injectors"], 
                              "solutions":["Replace fuel filter","Repair fuel pump","Clean/replace injectors"]},
        "Starter failure": {"symptoms":["engine doesn't crank","clicking sound","no response"], 
                            "causes":["dead battery","starter motor fault","loose wiring"], 
                            "solutions":["Recharge/replace battery","Repair/replace starter","Check wiring"]}
    },
    "Pump": {
        "Low pump pressure": {"symptoms":["low pressure","weak flow","pressure gauge low"],
                              "causes":["worn impeller","valve leakage","pipe blockage","air in system"],
                              "solutions":["Replace impeller","Repair/replace valves","Clean pipes","Bleed air"]},
        "Noisy pump": {"symptoms":["loud noise","vibration","rattling sound"],
                       "causes":["air bubbles","worn bearings","blocked suction","misalignment"],
                       "solutions":["Bleed air","Replace bearings","Clean suction inlet","Align pump"]},
        "Pump leakage": {"symptoms":["fluid leaking","puddles on floor","dripping noises"],
                         "causes":["worn seal","cracked casing","loose fittings"], 
                         "solutions":["Replace seal","Repair/replace casing","Tighten fittings"]},
        "Pump cavitation": {"symptoms":["loud rumbling","bubbles in fluid","pressure drop"], 
                            "causes":["insufficient suction","fluid vaporization","obstructed inlet"], 
                            "solutions":["Increase suction head","Reduce fluid temperature","Clear inlet"]},
        "Pump overheating": {"symptoms":["pump is hot","motor trips breaker"], 
                             "causes":["overload","friction in bearings","improper lubrication"], 
                             "solutions":["Check load","Lubricate bearings","Ensure proper lubrication"]}
    },
    "Gearbox": {
        "Gear noise": {"symptoms":["grinding noise","rattling","clicking"], 
                       "causes":["worn gears","insufficient lubrication","misalignment"], 
                       "solutions":["Replace gears","Refill oil","Align gears"]},
        "Overheating gearbox": {"symptoms":["smell of burning","high temp","oil temperature high"], 
                                "causes":["low oil level","excessive friction","blocked vents"], 
                                "solutions":["Add oil","Inspect gears","Clean vents"]},
        "Oil leakage": {"symptoms":["oil stains","low oil level","dripping oil"], 
                        "causes":["worn seal","cracked casing","loose bolts"], 
                        "solutions":["Replace seal","Repair casing","Tighten bolts"]},
        "Gear slipping": {"symptoms":["loss of torque","unexpected stops","jerky movement"], 
                          "causes":["worn teeth","improper lubrication","shaft misalignment"], 
                          "solutions":["Replace gears","Lubricate properly","Align shaft"]}
    },
    "Conveyor": {
        "Belt slipping": {"symptoms":["belt not moving properly","load falling","slipping noise"], 
                          "causes":["loose belt","worn pulley","motor misalignment"], 
                          "solutions":["Tighten belt","Replace pulley","Align motor"]},
        "Conveyor not moving": {"symptoms":["motor runs but belt still","belt stuck","no movement"], 
                                "causes":["jammed roller","motor coupling broken","overload"], 
                                "solutions":["Clear jam","Repair coupling","Reduce load"]},
        "Uneven load": {"symptoms":["items tilt or fall","belt misalignment","uneven distribution"], 
                        "causes":["incorrect loading","worn rollers","belt tension uneven"], 
                        "solutions":["Load evenly","Replace rollers","Adjust tension"]},
        "Motor overheating": {"symptoms":["motor too hot","power trips","smell of burning"], 
                              "causes":["overload","poor ventilation","worn bearings"], 
                              "solutions":["Reduce load","Improve ventilation","Replace bearings"]}
    },
    "Hydraulic Press": {
        "Low pressure": {"symptoms":["weak pressing force","slow action","low pressure reading"], 
                         "causes":["leak","faulty pump","valve stuck"], 
                         "solutions":["Fix leak","Repair pump","Replace valve"]},
        "Cylinder stuck": {"symptoms":["press does not move","strange noise","cylinder jammed"], 
                           "causes":["seal wear","air trapped","contaminated fluid"], 
                           "solutions":["Replace seal","Bleed air","Change fluid"]},
        "Valve malfunction": {"symptoms":["inconsistent pressure","slow response","pressure drops"], 
                              "causes":["stuck valve","leakage","faulty control"], 
                              "solutions":["Repair/replace valve","Fix leak","Inspect control"]}
    },
    "Compressor": {
        "Low output pressure": {"symptoms":["insufficient air","long refill time","low pressure gauge"], 
                                "causes":["worn piston","valve leakage","air leak"], 
                                "solutions":["Replace piston","Fix/replace valves","Repair leaks"]},
        "Excessive noise": {"symptoms":["knocking sound","metallic noise","vibration"], 
                            "causes":["loose bolts","damaged crankshaft","bearing wear"], 
                            "solutions":["Tighten bolts","Repair crankshaft","Replace bearings"]},
        "Oil leak": {"symptoms":["oil puddle","low oil level","oil smell"], 
                     "causes":["seal damage","overfilled","crack"], 
                     "solutions":["Replace seal","Adjust oil","Repair crack"]}
    },
    "Generator": {
        "Generator not starting": {"symptoms":["engine cranks but no start","no response","clicking sound"], 
                                   "causes":["fuel empty","battery weak","faulty starter"], 
                                   "solutions":["Refill fuel","Recharge/replace battery","Repair starter"]},
        "Unstable output voltage": {"symptoms":["lights flicker","voltage fluctuates","equipment trips"], 
                                    "causes":["faulty AVR","loose connections","worn brushes"], 
                                    "solutions":["Replace AVR","Tighten connections","Replace brushes"]}
    },
    "Boiler": {
        "Low steam pressure": {"symptoms":["steam output weak","slow heating","pressure gauge low"], 
                               "causes":["scale buildup","leaking valves","faulty burner"], 
                               "solutions":["Descale boiler","Repair valves","Check/replace burner"]},
        "Boiler overheating": {"symptoms":["safety valve release","high pressure","steam abnormal"], 
                               "causes":["thermostat failure","blocked pipes","low water"], 
                               "solutions":["Replace thermostat","Clean pipes","Check water supply"]}
    },
    "CNC Machine": {
        "Axis not moving": {"symptoms":["stuck axis","motor whining","no movement"], 
                            "causes":["servo failure","controller fault","mechanical jam"], 
                            "solutions":["Replace servo motor","Check controller","Remove jam"]},
        "Poor surface finish": {"symptoms":["rough surface","inaccurate cuts","scratches"], 
                                "causes":["worn tool","loose spindle","wrong speed/feed"], 
                                "solutions":["Replace tool","Tighten spindle","Adjust cutting parameters"]}
    }
}

# ===== Rules for diagnosis =====
rules = {
    "Engine": ["Engine vibration","Engine overheating","Oil leakage","Fuel system issue","Starter failure"],
    "Pump": ["Low pump pressure","Noisy pump","Pump leakage","Pump cavitation","Pump overheating"],
    "Gearbox": ["Gear noise","Overheating gearbox","Oil leakage","Gear slipping"],
    "Conveyor": ["Belt slipping","Conveyor not moving","Uneven load","Motor overheating"],
    "Hydraulic Press": ["Low pressure","Cylinder stuck","Valve malfunction"],
    "Compressor": ["Low output pressure","Excessive noise","Oil leak"],
    "Generator": ["Generator not starting","Unstable output voltage"],
    "Boiler": ["Low steam pressure","Boiler overheating"],
    "CNC Machine": ["Axis not moving","Poor surface finish"]
}

all_problems_found = {}

# ===== PDF Functions =====
def get_output_pdf_path(username):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"Complete_Industrial_Machine_Report_{timestamp}.pdf"
    download_folder = Path("/storage/emulated/0/Download")
    download_folder.mkdir(parents=True, exist_ok=True)
    return download_folder / filename

def save_pdf(all_problems, username):
    if not all_problems:
        messagebox.showinfo("No Problems", "No problems to save in PDF.")
        return

    filename = get_output_pdf_path(username)
    styles = getSampleStyleSheet()
    story = []
    story.append(Paragraph(" Industrial Machine Troubleshooting Report", styles["Title"]))
    story.append(Paragraph(f"User: {username}", styles["Normal"]))
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles["Normal"]))
    story.append(Spacer(1, 12))

    for machine_type, problems in all_problems.items():
        story.append(Paragraph(f" Machine: {machine_type}", styles["Heading1"]))
        for idx, (problem, data) in enumerate(problems.items(), 1):
            story.append(Paragraph(f"{idx}. Problem: {problem}", styles["Heading2"]))
            story.append(Paragraph(" Causes:", styles["Heading3"]))
            story.append(ListFlowable([ListItem(Paragraph(c, styles["Normal"])) for c in data["causes"]]))
            story.append(Paragraph(" Solutions:", styles["Heading3"]))
            story.append(ListFlowable([ListItem(Paragraph(s, styles["Normal"])) for s in data["solutions"]]))
            story.append(Spacer(1, 12))

    doc = SimpleDocTemplate(str(filename), pagesize=A4)
    doc.build(story)
    messagebox.showinfo("PDF Saved", f"Report saved at:\n{filename}")

# ===== GUI Functions =====
def diagnose_machine():
    machine = machine_var.get()
    if not machine:
        messagebox.showwarning("Select Machine", "Please select a machine first.")
        return

    machine_problems = knowledge_base.get(machine, {})
    found_problems = {}

    for problem, data in machine_problems.items():
        match = False
        for symptom in data["symptoms"]:
            ans = messagebox.askyesno("Symptom Check", f"Do you have symptom: {symptom}?")
            if ans:
                match = True
                break
        if match:
            found_problems[problem] = data

    if found_problems:
        all_problems_found[machine] = found_problems
        result_text = ""
        for prob, info in found_problems.items():
            result_text += f" Problem: {prob}\n"
            result_text += "Causes:\n" + "\n".join([f" - {c}" for c in info["causes"]]) + "\n"
            result_text += "Solutions:\n" + "\n".join([f" - {s}" for s in info["solutions"]]) + "\n\n"

        result_window = tk.Toplevel(root)
        result_window.title(f"Diagnosis for {machine}")
        tk.Label(result_window, text=f"Diagnosis Result for {machine}", font=("Arial", 12, "bold")).pack(pady=5)
        text_widget = tk.Text(result_window, height=20, width=60)
        text_widget.pack()
        text_widget.insert(tk.END, result_text)
        text_widget.config(state="disabled")
        ttk.Button(result_window, text="Diagnose Another Machine", command=result_window.destroy).pack(pady=5)
    else:
        messagebox.showinfo("No Match", "No problems matched for selected machine.")

def add_problem():
    machine = simpledialog.askstring("New Problem", "Enter machine type:")
    if not machine:
        return
    problem = simpledialog.askstring("New Problem", "Enter problem name:")
    symptoms = simpledialog.askstring("New Problem", "Enter symptoms (comma separated):")
    causes = simpledialog.askstring("New Problem", "Enter causes (comma separated):")
    solutions = simpledialog.askstring("New Problem", "Enter solutions (comma separated):")

    if machine not in knowledge_base:
        knowledge_base[machine] = {}
    knowledge_base[machine][problem] = {
        "symptoms": [s.strip() for s in symptoms.split(",")],
        "causes": [c.strip() for c in causes.split(",")],
        "solutions": [s.strip() for s in solutions.split(",")],
    }
    messagebox.showinfo("Added", f"Problem {problem} added to {machine}.")

def exit_program():
    save_pdf(all_problems_found, username)
    root.destroy()

# ===== Main GUI =====
root = tk.Tk()
root.title(" Industrial Machine Troubleshooting")
root.geometry("500x400")

username = simpledialog.askstring("Username", "Enter your name:")

ttk.Label(root, text="Select a Machine", font=("Arial", 14, "bold")).pack(pady=10)

machine_var = tk.StringVar()
machine_combo = ttk.Combobox(root, textvariable=machine_var, values=list(knowledge_base.keys()), state="readonly")
machine_combo.pack(pady=5)

ttk.Button(root, text="Diagnose Machine", command=diagnose_machine).pack(pady=5)
ttk.Button(root, text="Add New Problem", command=add_problem).pack(pady=5)
ttk.Button(root, text="Save PDF Report", command=lambda: save_pdf(all_problems_found, username)).pack(pady=5)
ttk.Button(root, text="Exit", command=exit_program).pack(pady=5)

root.mainloop()