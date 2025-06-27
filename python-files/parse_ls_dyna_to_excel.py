import pandas as pd

def parse_ls_dyna_file(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    parts = []
    materials = []
    sections = []

    current_section = None
    buffer = []

    for line in lines:
        line = line.strip()
        if line.startswith('*'):
            if current_section and buffer:
                if current_section == '*PART':
                    parts.append(buffer)
                elif current_section.startswith('*MAT'):
                    materials.append((current_section, buffer))
                elif current_section.startswith('*SECTION'):
                    sections.append((current_section, buffer))
                buffer = []
            current_section = line
        elif current_section:
            buffer.append(line)

    # Append the last buffered section
    if current_section and buffer:
        if current_section == '*PART':
            parts.append(buffer)
        elif current_section.startswith('*MAT'):
            materials.append((current_section, buffer))
        elif current_section.startswith('*SECTION'):
            sections.append((current_section, buffer))

    return parts, materials, sections

def export_to_excel(parts, materials, sections, output_file):
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        # Write parts
        parts_df = pd.DataFrame({'Part Data': ['\n'.join(part) for part in parts]})
        parts_df.to_excel(writer, sheet_name='Parts', index=False)

        # Write materials
        mat_data = [{'Material Type': mat_type, 'Material Data': '\n'.join(mat)} for mat_type, mat in materials]
        materials_df = pd.DataFrame(mat_data)
        materials_df.to_excel(writer, sheet_name='Materials', index=False)

        # Write sections
        sec_data = [{'Section Type': sec_type, 'Section Data': '\n'.join(sec)} for sec_type, sec in sections]
        sections_df = pd.DataFrame(sec_data)
        sections_df.to_excel(writer, sheet_name='Sections', index=False)

if __name__ == "__main__":
    input_file = 'C:\Users\hegdeg\Desktop\py\1\model.k'  # Replace with your LS-DYNA input file path
    output_excel = 'ls_dyna_model_data.xlsx'

    parts, materials, sections = parse_ls_dyna_file(input_file)
    export_to_excel(parts, materials, sections, output_excel)
    print(f"Data exported to {output_excel}")
