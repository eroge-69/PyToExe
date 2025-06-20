
import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="Sloučení položek z Excelu", layout="centered")

st.title("🧾 Úprava Excelu – sloučení položek a součty množství")

uploaded_file = st.file_uploader("Nahraj soubor .xlsx", type=["xlsx"])

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file, sheet_name=0)

        # Zkontroluj, zda obsahuje požadované sloupce
        if {'Název 1', 'Množství', 'MJ'}.issubset(df.columns):
            df['Plný název'] = df['Název 1'] + ' [' + df['MJ'] + ']'
            grouped = df.groupby('Plný název', as_index=False)['Množství'].sum()
            grouped[['Název položky', 'MJ']] = grouped['Plný název'].str.extract(r'^(.*) \[(.*)\]$')
            final_df = grouped[['Název položky', 'Množství', 'MJ']]

            st.success("✅ Soubor byl úspěšně zpracován.")
            st.dataframe(final_df)

            # Tlačítko ke stažení
            output = BytesIO()
            final_df.to_excel(output, index=False, engine='openpyxl')
            st.download_button(
                label="📥 Stáhnout výsledek jako Excel",
                data=output.getvalue(),
                file_name="Souhrn_polozek.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

        else:
            st.error("❌ Soubor neobsahuje požadované sloupce: 'Název 1', 'Množství', 'MJ'.")

    except Exception as e:
        st.error(f"Chyba při zpracování souboru: {e}")
