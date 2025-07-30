import pandas as pd
import json
import os

TEMPLATE_COLUMNS = [
    "Order No.", "Project", "Language", "File", "Repitition", "Context Match", "100%",
    "95% - 99%", "85% - 94%", "75% - 84%", "50% - 74%", "No Match",
    "Total Words", "WWC", "IST- Deadline", "Project IDs"
]

def compute_wwc(row):
    try:
        return (
            (float(row["50% - 74%"]) + float(row["No Match"])) * 0.5 +
            (float(row["85% - 94%"]) + float(row["75% - 84%"])) * 0.35 +
            float(row["95% - 99%"]) * 0.2 +
            float(row["100%"]) * 0.1 +
            float(row["Repitition"]) * 0.1
        )
    except Exception:
        return 0.0

def convert_phrase_json_to_template(json_path):
    with open(json_path, 'r') as file:
        json_data = json.load(file)

    output_rows = []
    for lang_part in json_data.get("analyseLanguageParts", []):
        source_lang = lang_part.get("sourceLang", "")
        target_lang = lang_part.get("targetLang", "")
        project = json_data.get("projectName", "")

        for job in lang_part.get("jobs", []):
            file_name = job.get("fileName", "")
            data = job.get("data", {})

            context_match = (
                data.get("contextMatch", {}).get("words", 0)
                or data.get("match101", {}).get("words", {}).get("sum", 0)
            )

            row = {
                "Order No.": "",
                "Project": project,
                "Language": f"{source_lang} → {target_lang}",
                "File": file_name,
                "Repitition": float(data.get("repetitions", {}).get("words", 0)),
                "Context Match": float(context_match),
                "100%": float(data.get("match100", {}).get("words", {}).get("sum", 0)),
                "95% - 99%": float(data.get("match95", {}).get("words", {}).get("sum", 0)),
                "85% - 94%": float(data.get("match85", {}).get("words", {}).get("sum", 0)),
                "75% - 84%": float(data.get("match75", {}).get("words", {}).get("sum", 0)),
                "50% - 74%": float(data.get("match50", {}).get("words", {}).get("sum", 0)),
                "No Match": float(data.get("match0", {}).get("words", {}).get("sum", 0)),
                "WWC": "",
                "IST- Deadline": "",
                "Project IDs": ""
            }

            row["Total Words"] = sum([
                row["Repitition"], row["Context Match"], row["100%"], row["95% - 99%"],
                row["85% - 94%"], row["75% - 84%"], row["50% - 74%"], row["No Match"]
            ])

            row["WWC"] = compute_wwc(row)
            output_rows.append(row)

    return pd.DataFrame(output_rows).reindex(columns=TEMPLATE_COLUMNS)

def convert_log_file_to_template(log_path):
    with open(log_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    entries = []
    current_entry = {}
    for line in lines:
        line = line.strip()
        if line.startswith("File:"):
            current_entry = {"File": line.replace("File:", "").strip()}
        elif line.startswith("Project:"):
            current_entry["Project"] = line.replace("Project:", "").strip()
        elif line.startswith("Language direction:"):
            current_entry["Language"] = line.replace("Language direction:", "").strip().replace(">", "→")
        elif any(mt in line for mt in ["100%", "101%", "95% - 99%", "85% - 94%", "75% - 84%", "50% - 74%", "No Match", "Repetitions"]):
            try:
                parts = line.split()
                match_type = parts[0]
                words = float(parts[2])
                if match_type == "101%" or match_type.lower() == "context":
                    current_entry["Context Match"] = words
                elif match_type == "Repetitions":
                    current_entry["Repitition"] = words
                else:
                    current_entry[match_type] = words
            except:
                continue
        elif line.startswith("Total") and "files" not in line:
            try:
                current_entry["Total Words"] = float(line.split()[3])
            except:
                current_entry["Total Words"] = 0.0
            entries.append(current_entry.copy())

    df = pd.DataFrame(entries)

    for col in TEMPLATE_COLUMNS:
        if col not in df.columns:
            df[col] = "" if col in ["Order No.", "WWC", "IST- Deadline", "Project IDs"] else 0.0

    df["Total Words"] = (
        df["Repitition"] + df["Context Match"] + df["100%"] +
        df["95% - 99%"] + df["85% - 94%"] + df["75% - 84%"] +
        df["50% - 74%"] + df["No Match"]
    )

    df["WWC"] = df.apply(compute_wwc, axis=1)
    return df.reindex(columns=TEMPLATE_COLUMNS)

def convert_csv_to_template(csv_path):
    df = pd.read_csv(csv_path)
    df.columns = [col.strip().lower() for col in df.columns]
    rows = []

    for _, row in df.iterrows():
        context_match = float(row.get("context match", row.get("101%", 0)))

        new_row = {
            "Order No.": row.get("order no.", ""),
            "Project": row.get("project", ""),
            "Language": row.get("language", ""),
            "File": row.get("file", ""),
            "Repitition": float(row.get("repitition", 0)),
            "Context Match": context_match,
            "100%": float(row.get("100%", row.get("1", 0))),
            "95% - 99%": float(row.get("95% - 99%", 0)),
            "85% - 94%": float(row.get("85% - 94%", 0)),
            "75% - 84%": float(row.get("75% - 84%", 0)),
            "50% - 74%": float(row.get("50% - 74%", 0)),
            "No Match": float(row.get("no match", 0)),
            "WWC": "",
            "IST- Deadline": row.get("ist- deadline", ""),
            "Project IDs": row.get("project ids", "")
        }

        new_row["Total Words"] = sum([
            new_row["Repitition"], new_row["Context Match"], new_row["100%"],
            new_row["95% - 99%"], new_row["85% - 94%"], new_row["75% - 84%"],
            new_row["50% - 74%"], new_row["No Match"]
        ])

        new_row["WWC"] = compute_wwc(new_row)
        rows.append(new_row)

    return pd.DataFrame(rows).reindex(columns=TEMPLATE_COLUMNS)

def batch_process_all_files(folder_path, output_file="Combined_Wordcount_Report.xlsx"):
    all_dfs = []
    for file_name in os.listdir(folder_path):
        path = os.path.join(folder_path, file_name)
        try:
            if file_name.endswith(".json"):
                all_dfs.append(convert_phrase_json_to_template(path))
            elif file_name.endswith(".log"):
                all_dfs.append(convert_log_file_to_template(path))
            elif file_name.endswith(".csv"):
                all_dfs.append(convert_csv_to_template(path))
        except Exception as e:
            print(f"❌ Failed to process {file_name}: {e}")

    if not all_dfs:
        print("⚠️ No valid files found.")
        return

    final_df = pd.concat(all_dfs, ignore_index=True)
    final_df.to_excel(output_file, index=False)
    print(f"✅ Exported: {output_file}")

if __name__ == "__main__":
    batch_process_all_files(os.getcwd())
