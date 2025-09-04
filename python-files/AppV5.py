import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import io
import os

# Streamlit config
st.set_page_config(page_title="Data Cleaning and EDA Tool", layout="wide")
st.title("Auto Data Cleaning & EDA Tool")
st.write("Upload your dataset, and let the magic happen!")
st.sidebar.header("Cleaning Steps in Progress...")

# File upload
uploaded_file = st.file_uploader("Upload your dataset", type=["csv", "xlsx"])

if uploaded_file is not None:
    # Load dataset
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        try:
            import openpyxl  # Ensure dependency is present
        except ImportError:
            st.error("Missing 'openpyxl' dependency. Please install it to read Excel files.")
            st.stop()
        df = pd.read_excel(uploaded_file)

    st.subheader("First 25 rows of the dataset")
    st.write(df.head(25))

    # Make a copy
    df_clean = df.copy()

    # Step 1: Clean column names
    st.sidebar.write("Cleaning column names...")
    df_clean.columns = df_clean.columns.str.strip().str.lower().str.replace(" ", "_")

    # Step 2: Drop completely empty columns
    empty_cols = [col for col in df_clean.columns if df_clean[col].isnull().sum() == len(df_clean)]
    if empty_cols:
        df_clean.drop(columns=empty_cols, inplace=True)
        st.sidebar.write(f"Dropped empty columns: {', '.join(empty_cols)}")

    # Step 3: Handle missing values in remaining columns
    for col in df_clean.columns:
        missing_count = df_clean[col].isnull().sum()
        if missing_count > 0:
            if df_clean[col].dtype == 'object':
                if not df_clean[col].mode().empty:
                    mode_val = df_clean[col].mode()[0]
                else:
                    mode_val = "Unknown"  # fallback if mode is empty
                df_clean[col].fillna(mode_val, inplace=True)
                st.sidebar.write(f"Filled {missing_count} nulls in '{col}' with mode ({mode_val}).")
            else:
                median_val = df_clean[col].median()
                df_clean[col].fillna(median_val, inplace=True)
                st.sidebar.write(f"Filled {missing_count} nulls in '{col}' with median ({median_val}).")

    # Step 4: Remove duplicates
    duplicates_count = df_clean.duplicated().sum()
    if duplicates_count > 0:
        df_clean.drop_duplicates(inplace=True)
        st.sidebar.write(f"Removed {duplicates_count} duplicate rows.")

    # Step 5: Outlier handling (cap using IQR)
    num_cols = df_clean.select_dtypes(include=[np.number]).columns
    for col in num_cols:
        Q1 = df_clean[col].quantile(0.25)
        Q3 = df_clean[col].quantile(0.75)
        IQR = Q3 - Q1
        lower = Q1 - 1.5 * IQR
        upper = Q3 + 1.5 * IQR

        outliers_low = (df_clean[col] < lower).sum()
        outliers_high = (df_clean[col] > upper).sum()

        if outliers_low > 0 or outliers_high > 0:
            df_clean[col] = np.where(df_clean[col] < lower, lower, df_clean[col])
            df_clean[col] = np.where(df_clean[col] > upper, upper, df_clean[col])
            st.sidebar.write(f"Capped outliers in '{col}' ({outliers_low} low, {outliers_high} high).")

    st.sidebar.success("Data cleaning complete!")

    # Show cleaned dataset
    st.subheader("Cleaned Dataset Preview")
    st.write(df_clean.head(25))

    # --- Create cleaned file name dynamically ---
    base_name, ext = os.path.splitext(uploaded_file.name)
    cleaned_file_name = f"{base_name}-clean{ext}"

    # --- Export and download cleaned dataset ---
    if ext.lower() == ".csv":
        csv_data = df_clean.to_csv(index=False).encode("utf-8")
        st.download_button(
            label=f"Download {cleaned_file_name}",
            data=csv_data,
            file_name=cleaned_file_name,
            mime="text/csv"
        )
    else:  # .xlsx
        buffer = io.BytesIO()
        df_clean.to_excel(buffer, index=False)
        st.download_button(
            label=f"Download {cleaned_file_name}",
            data=buffer,
            file_name=cleaned_file_name,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
