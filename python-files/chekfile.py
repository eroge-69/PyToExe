import os
import pandas as pd
import tkinter as tk
from tkinter import filedialog
from difflib import SequenceMatcher
from tqdm import tqdm

def get_similarity_ratio(a, b):
    """બે સ્ટ્રિંગ વચ્ચે સમાનતાનો રેશિયો શોધે છે."""
    if not a or not b:
        return 0.0
    return SequenceMatcher(None, str(a), str(b)).ratio()

def clean_string_for_comparison(text):
    """સરખામણી માટે સ્ટ્રિંગમાંથી ફક્ત અક્ષરો રાખે છે અને તેને lowercase બનાવે છે."""
    if not isinstance(text, str):
        return ""
    # ગુજરાતી અક્ષરોને પણ સપોર્ટ કરવા માટે
    allowed_chars = filter(lambda char: char.isalpha(), text)
    return "".join(allowed_chars).lower()

def process_excel_and_folders():
    """
    મુખ્ય ફંક્શન જે એક્સેલ ફાઇલ અને ફોલ્ડર સિલેક્ટ કરવાનું કહે છે,
    અને પછી ડેટા પ્રોસેસ કરીને નવી ફાઇલમાં સેવ કરે છે.
    """
    root = tk.Tk()
    root.withdraw()

    excel_path = filedialog.askopenfilename(
        title="તમારી એક્સેલ ફાઇલ પસંદ કરો",
        filetypes=[("Excel Files", "*.xlsx *.xls")]
    )
    if not excel_path:
        print("કોઈ એક્સેલ ફાઇલ પસંદ કરવામાં આવી નથી. પ્રોગ્રામ બંધ થઈ રહ્યો છે.")
        return

    folder_path = filedialog.askdirectory(
        title="જે ફોલ્ડરમાં ફાઇલો શોધવી છે તે પસંદ કરો"
    )
    if not folder_path:
        print("કોઈ ફોલ્ડર પસંદ કરવામાં આવ્યું નથી. પ્રોગ્રામ બંધ થઈ રહ્યો છે.")
        return

    print(f"એક્સેલ ફાઇલ લોડ થઈ રહી છે: {excel_path}")
    try:
        df = pd.read_excel(excel_path, header=None)
    except Exception as e:
        print(f"એક્સેલ ફાઇલ વાંચવામાં ભૂલ આવી: {e}")
        return

    print(f"ફોલ્ડરમાં ફાઇલો સ્કેન કરી રહ્યા છીએ: {folder_path}")
    file_map = {}
    for dirpath, _, filenames in os.walk(folder_path):
        for filename in filenames:
            file_map[filename.lower()] = os.path.join(dirpath, filename)
    
    print(f"કુલ {len(file_map)} ફાઇલો મળી.")

    j_col, k_col, l_col, m_col, n_col, o_col, p_col = [], [], [], [], [], [], []

    print("એક્સેલની દરેક રો માટે ફાઇલો શોધી રહ્યા છીએ...")
    for index, row in tqdm(df.iterrows(), total=df.shape[0], desc="પ્રોસેસિંગ"):
        try:
            id_num = str(row[0]).strip() if pd.notna(row[0]) else ""
            first_name = str(row[1]).strip() if pd.notna(row[1]) else ""
            last_name = str(row[2]).strip() if pd.notna(row[2]) else ""
            city = str(row[6]).strip() if pd.notna(row[6]) else ""
        except IndexError:
            for lst in [j_col, k_col, l_col, m_col, n_col, o_col, p_col]: lst.append("")
            continue

        match_id, match_name, match_surname, match_city, similarity_result = "", "", "", "", ""
        found_filename, found_foldername = "", ""
        
        if not id_num:
            for lst in [j_col, k_col, l_col, m_col, n_col, o_col, p_col]: lst.append("")
            continue

        for filename_lower, full_path in file_map.items():
            # --- અહીં મુખ્ય ફેરફાર છે ---
            # જૂની શરત: if id_num in filename_lower:
            # નવી શરત: હવે ફાઈલની શરૂઆત ID થી થતી હોય તે જ તપાસશે
            if filename_lower.startswith(id_num):
                match_id, match_name, match_surname, match_city = id_num, first_name, last_name, city
                found_filename = os.path.basename(full_path)
                found_foldername = os.path.basename(os.path.dirname(full_path))
                
                clean_excel_fname = clean_string_for_comparison(first_name)
                clean_excel_lname = clean_string_for_comparison(last_name)
                filename_text_only = clean_string_for_comparison(os.path.splitext(filename_lower)[0])

                is_match = False
                if filename_text_only:
                    if clean_excel_fname and clean_excel_lname:
                        if clean_excel_fname in filename_text_only and clean_excel_lname in filename_text_only:
                            is_match = True

                    if not is_match and clean_excel_fname:
                        if clean_excel_fname in filename_text_only or filename_text_only in clean_excel_fname:
                            is_match = True
                    
                    if not is_match and clean_excel_fname:
                        ratio1 = get_similarity_ratio(clean_excel_fname, filename_text_only)
                        ratio2 = get_similarity_ratio(clean_excel_lname, filename_text_only)
                        if max(ratio1, ratio2) >= 0.70:
                            is_match = True

                if is_match:
                    similarity_result = 'TRUE'
                
                break
        
        j_col.append(match_id)
        k_col.append(match_name)
        l_col.append(match_surname)
        m_col.append(match_city)
        n_col.append(similarity_result)
        o_col.append(found_filename)
        p_col.append(found_foldername)

    df['J'], df['K'], df['L'], df['M'], df['N'], df['O'], df['P'] = j_col, k_col, l_col, m_col, n_col, o_col, p_col
    
    output_path = os.path.splitext(excel_path)[0] + "_processed.xlsx"

    try:
        df.to_excel(output_path, index=False, header=False) 
        print(f"\nપ્રક્રિયા પૂર્ણ થઈ. નવી ફાઇલ અહીં સેવ કરવામાં આવી છે: {output_path}")
    except Exception as e:
        print(f"\nફાઇલ સેવ કરવામાં ભૂલ આવી: {e}")

if __name__ == "__main__":
    process_excel_and_folders()