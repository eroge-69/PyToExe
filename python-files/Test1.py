import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

# Streamlit page configuration
st.set_page_config(page_title="Data Cleaning and EDA Tool", layout="wide")
st.title("Auto Data Cleaning & EDA Tool")
st.write("Make Data Cleaning and EDA Easier")

# Sidebar info
st.sidebar.header("We show you the steps happening.")

# File upload
uploaded_file = st.file_uploader("Upload your dataset below.", type=["csv", "xlsx"])

if uploaded_file is not None:
    # Read file into raw dataframe
    if uploaded_file.name.endswith(".csv"):
        df_raw = pd.read_csv(uploaded_file)
    else:
        df_raw = pd.read_excel(uploaded_file)

    # Show original dataset preview
    st.subheader("Raw Data Preview (First 25 Rows)")
    st.write(df_raw.head(25))

    # Make a copy for cleaning
    df_clean = df_raw.copy()

    # Sidebar title
    st.sidebar.title("Data Cleaning Progress")

    # Step 1: Clean column names
    st.sidebar.write("🧹 Cleaning column names...")
    df_clean.columns = df_clean.columns.str.strip().str.lower().str.replace(" ", "_")

    # Step 2: Remove duplicates
    duplicates_count = df_clean.duplicated().sum()
    df_clean.drop_duplicates(inplace=True)
    st.sidebar.write(f"🗑 Removed {duplicates_count} duplicate rows.")

    # Step 3: Handle missing values
    for col in df_clean.columns:
        missing_before = df_clean[col].isnull().sum()
        if df_clean[col].dtype == 'object':
            df_clean[col].fillna(df_clean[col].mode()[0], inplace=True)
            if missing_before > 0:
                st.sidebar.write(f"📋 Filled {missing_before} missing values in '{col}' with mode.")
        else:
            df_clean[col].fillna(df_clean[col].median(), inplace=True)
            if missing_before > 0:
                st.sidebar.write(f"🔢 Filled {missing_before} missing values in '{col}' with median.")

    st.sidebar.success("✅ Data cleaning complete!")

    # Show cleaned dataset preview
    st.subheader("Cleaned Data Preview (First 25 Rows)")
    st.write(df_clean.head(25))
