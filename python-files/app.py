from flask import Flask, render_template, abort, request, jsonify
from collections import defaultdict

from src.msg_lookup import get_text_description

import re

app = Flask(__name__)

SCP_FILE_PATH = "src/World_drop.scp"

def parse_scp_file(filepath):
    sections = defaultdict(lambda: {"header": [], "rows": []})
    current_section = None

    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            # Ellenőrizzük, hogy szekciósor-e (pl. "[Box_Main]  Col1  Col2")
            if line.startswith("[") and "]" in line:
                parts = line.split("\t")
                section_match = re.match(r"\[(.+?)\]", parts[0])
                if section_match:
                    current_section = section_match.group(1)
                    # A szekció neve is az első oszlop neve!
                    header = [f"[{current_section}]"] + parts[1:]
                    sections[current_section]["header"] = header
                continue

            if current_section:
                sections[current_section]["rows"].append(line.split("\t"))

    return sections


@app.route("/")
def index():
    data = parse_scp_file(SCP_FILE_PATH)
    section_summaries = {
        name: {"columns": len(sec["header"]), "rows": len(sec["rows"])}
        for name, sec in data.items()
    }
    return render_template("index.html", sections=section_summaries)


@app.route("/section/<section_name>")
def view_section(section_name):
    data = parse_scp_file(SCP_FILE_PATH)

    if section_name not in data:
        abort(404, description="Nincs ilyen szekció.")

    section = data[section_name]

    # 🔽 IDE kerül a leképezés
    boxidx_to_species = {}

    if "Box_Main" in data:
        box_main = data["Box_Main"]
        header = box_main["header"]
        rows = box_main["rows"]

        try:
            idx_boxidx = header.index("BoxIdx")
            idx_species = header.index("SpeciesIdx")
        except ValueError:
            idx_boxidx = idx_species = None

        if idx_boxidx is not None and idx_species is not None:
            for row in rows:
                if len(row) > max(idx_boxidx, idx_species):
                    boxidx = row[idx_boxidx].strip()
                    species_id = row[idx_species].strip()
                    boxidx_to_species[boxidx] = species_id

    return render_template(
        "section.html",
        section_name=section_name,
        header=section["header"],
        rows=section["rows"],
        get_description=get_text_description,
        box_to_species=boxidx_to_species
    )


@app.route("/save", methods=["POST"])
def save_modified_data():
    payload = request.get_json()
    section_name = payload.get("section")
    changes = payload.get("changes", {})

    data = parse_scp_file(SCP_FILE_PATH)
    if section_name not in data:
        return jsonify({"error": "Invalid section name"}), 400

    section = data[section_name]
    header = section["header"]
    rows = section["rows"]

    # Alkalmazzuk a változásokat a megfelelő sor/oszlop helyre
    for row_str, changes_for_row in changes.items():
        row_index = int(row_str)
        for col_name, new_value in changes_for_row.items():
            if col_name in header:
                col_index = header.index(col_name)
                # Bővítjük a sort, ha rövidebb
                while len(rows[row_index]) <= col_index:
                    rows[row_index].append("")
                rows[row_index][col_index] = new_value

    # Fájl mentése új néven
    output_path = "modified_World_drop.scp"
    with open(output_path, "w", encoding="utf-8") as f:
        for sec_name, sec_data in data.items():
            f.write("\n")  # üres sor a szekciók között
            f.write(f"[{sec_name}]\t" + "\t".join(sec_data["header"][1:]) + "\n")
            for row in sec_data["rows"]:
                f.write("\t".join(row) + "\n")

    return jsonify({"success": True, "filename": output_path})

@app.route("/describe")
def describe():
    col = request.args.get("col", "")
    val = request.args.get("val", "")
    desc = get_text_description(col, val)
    return desc or ""

@app.route("/save_full_table", methods=["POST"])
def save_full_table():
    data = request.get_json()
    section = data["section"]
    header = data["header"]
    rows = data["rows"]

    full_data = parse_scp_file(SCP_FILE_PATH)
    if section not in full_data:
        return jsonify({"error": "Invalid section name"}), 400

    full_data[section]["header"] = header
    full_data[section]["rows"] = rows

    output_path = "modified_World_drop.scp"
    with open(output_path, "w", encoding="utf-8") as f:
        for name, sec in full_data.items():
            f.write("\n")
            f.write(f"[{name}]\t" + "\t".join(sec["header"][1:]) + "\n")
            for row in sec["rows"]:
                f.write("\t".join(row) + "\n")

    return jsonify({"filename": output_path})

if __name__ == "__main__":
    app.run(debug=True)
