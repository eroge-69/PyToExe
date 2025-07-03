import streamlit as st
import pandas as pd
import plotly.graph_objs as go
import plotly.express as px
from datetime import datetime
from fpdf import FPDF
from io import BytesIO
import tempfile
import numpy as np
import re

# --- Constants ---
BIOMASS_CONVERSION_FACTOR = 1000
HILOMEN_REFERENCE = "Reference: Hilomen, V.V., Nañola, C.L. and Dantis, A.L. (2000). Status of Philippine reef communities."

# Define categories for data-driven categorization
SPECIES_RICHNESS_CATEGORIES = [
    (0, 25, "Very Poor", "red", "↓"),
    (26, 47, "Poor", "orange", "↓"),
    (48, 74, "Moderate", "gray", ""),
    (75, 100, "High", "green", "↑"),
    (101, float('inf'), "Very High", "darkgreen", "↑"),
]

DENSITY_CATEGORIES = [
    (0, 200, "Very Poor", "red", "↓"),
    (201, 676, "Low", "orange", "↓"),
    (677, 2267, "Moderate", "gray", ""),
    (2268, 7592, "High", "green", "↑"),
    (7593, float('inf'), "Very High", "darkgreen", "↑"),
]

BIOMASS_CATEGORIES = [
    (float('-inf'), 10, "Very Low to Low", "orange", "↓"),
    (11, 20, "Moderate", "gray", ""),
    (21, 40, "High", "green", "↑"),
    (41, float('inf'), "Very High", "darkgreen", "↑"),
]

# A diverse set of colors for the pie chart (still useful if px.pie doesn't pick enough distinct colors, but px is usually good)
PIE_CHART_COLORS = [
    '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
    '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf',
    '#aec7e8', '#ffbb78', '#98df8a', '#ff9896', '#c5b0d5',
    '#c49c94', '#f7b6d2', '#c7c7c7', '#dbdb8d', '#9edae5'
]

# --- Set wide layout and font scaling ---
st.set_page_config(layout="wide")
st.markdown("""
    <style>
    html, body, [class*="css"]  {
        font-size: 20px !important;
    }
    h1, h2, h3, h4 {
        font-weight: 600;
    }
    .element-container { padding: 0rem 1rem; }
    .block-container { padding-top: 1rem; padding-bottom: 2rem; }
    </style>
""", unsafe_allow_html=True)

# --- Helper functions for biological calculations ---
def length_weight(length: float, a: float, b: float) -> float:
    """Calculates fish weight based on length-weight regression."""
    return a * (length ** b)

def categorize_value(val: float, categories: list) -> tuple[str, str, str]:
    """Categorizes a numerical value based on predefined ranges.

    Args:
        val: The numerical value to categorize.
        categories: A list of tuples, where each tuple is
                    (lower_bound, upper_bound, label, color, arrow_symbol).

    Returns:
        A tuple containing (label, color, arrow_symbol) for the category.
    """
    for lower, upper, label, color, arrow in categories:
        if lower <= val <= upper:
            return (label, color, arrow)
    return ("Undefined", "black", "") # Fallback for values outside defined ranges

def clean_text_for_pdf(text: str) -> str:
    """Removes or replaces characters that might cause encoding issues in PDF."""
    # Replace common problematic characters like curly quotes, dashes, etc.
    # with their ASCII equivalents.
    text = text.replace('\u201c', '"').replace('\u201d', '"') # Left/right double curly quotes
    text = text.replace('\u2018', "'").replace('\u2019', "'") # Left/right single curly quotes
    text = text.replace('\u2013', '-').replace('\u2014', '--') # En dash, Em dash
    text = text.replace('\u2026', '...') # Ellipsis
    text = re.sub(r'[^\x00-\x7F]+', '', text) # Remove any remaining non-ASCII characters
    return text


# --- Core functions ---
def load_and_validate_data(uploaded_file: BytesIO) -> pd.DataFrame:
    """Loads and validates an uploaded file (xlsx or csv).

    Args:
        uploaded_file: The file uploaded via Streamlit.

    Returns:
        A cleaned and validated Pandas DataFrame.

    Raises:
        ValueError: If essential columns are missing or data is invalid.
    """
    if uploaded_file.name.endswith('.xlsx'):
        df = pd.read_excel(uploaded_file)
    else:
        df = pd.read_csv(uploaded_file)

    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    df = df.dropna(subset=['Species']) # Ensure Species column has no NaNs

    required_cols = {'Species', 'Length', 'a', 'b', 'Count', 'Family'}
    if not required_cols.issubset(df.columns):
        missing = required_cols - set(df.columns)
        raise ValueError(f"Missing required columns: {', '.join(sorted(missing))}")

    # Convert to numeric, coercing errors to NaN
    for col in ['Length', 'a', 'b', 'Count']:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # Drop rows where essential numeric columns are NaN after conversion
    original_rows = len(df)
    df = df.dropna(subset=['Length', 'a', 'b', 'Count'])
    if len(df) < original_rows:
        st.warning(f"Removed {original_rows - len(df)} rows due to missing or invalid numeric data in 'Length', 'a', 'b', or 'Count'.")

    if df.empty:
        raise ValueError("No valid data rows remaining after cleaning and validation. Please check your data.")

    return df


def export_analysis_pdf(info: dict, top_density_family: pd.Series, top_biomass_family: pd.Series,
                        richness: float, richness_cat: tuple, density_avg: float, density_cat: tuple,
                        biomass_avg: float, biomass_cat: tuple, main_fig: go.Figure, compare_fig: go.Figure,
                        ai_analysis_text: str = None, raw_data_df: pd.DataFrame = None) -> BytesIO:
    """Generates a PDF report of the FVC data analysis, optionally including AI insights and raw data.

    Args:
        info: Dictionary containing survey metadata.
        top_density_family: Pandas Series for the family with highest density.
        top_biomass_family: Pandas Series for the family with highest biomass.
        richness: Calculated species richness (average).
        richness_cat: Categorization of species richness.
        density_avg: Calculated average fish density.
        density_cat: Categorization of fish density.
        biomass_avg: Calculated average fish biomass.
        biomass_cat: Categorization of fish biomass.
        main_fig: The main plot (e.g., family distribution).
        compare_fig: The comparison plot (e.g., density/biomass by source).
        ai_analysis_text: Optional string containing AI-generated analysis and recommendations. (Will be ignored if None)
        raw_data_df: Optional DataFrame containing the raw data to be included.

    Returns:
        BytesIO object containing the PDF data.
    """
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Fish Visual Census (FVC) Data Analysis Report", ln=True, align='C')
    pdf.ln(10)

    # Clean text content before passing to PDF
    report_summary_text = (
        f"Date Collected: {info.get('date', 'N/A')}\n"
        f"Region: {info.get('region', 'N/A')}\nProvince: {info.get('province', 'N/A')}\nMunicipality: {info.get('municipality', 'N/A')}\nBarangay: {info.get('barangay', 'N/A')}\n"
        f"Coordinates: {info.get('latitude', 'N/A')}, {info.get('longitude', 'N/A')}\n\n"
        f"Average Species Richness: {richness:.2f} species/1,000m² ({richness_cat[0]})\n"
        f"Average Fish Density: {density_avg:.2f} ind/1,000m² ({density_cat[0]})\n"
        f"Average Fish Biomass: {biomass_avg:.2f} kg/1,000m² ({biomass_cat[0]})\n\n"
        f"Top Density Family (Combined Data): {top_density_family['Family']} ({top_density_family['Count']})\n"
        f"Top Biomass Family (Combined Data): {top_biomass_family['Family']} ({top_biomass_family['Biomass']:.2f} kg)\n\n"
        f"{HILOMEN_REFERENCE}"
    )
    pdf.multi_cell(0, 10, txt=clean_text_for_pdf(report_summary_text))

    # Save and embed main_fig
    if main_fig: # Check if figure exists
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as img_tmp:
            main_fig.write_image(img_tmp.name)
            pdf.image(img_tmp.name, x=10, w=190)

    # Add a new page for comparison fig
    if compare_fig: # Check if figure exists
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="FVC Comparison per MPA", ln=True, align='C')
        pdf.ln(5)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as compare_img:
            compare_fig.write_image(compare_img.name)
            pdf.image(compare_img.name, x=10, w=190)

    # AI Analysis section is intentionally NOT included here based on user request.

    # Add Raw Data if provided
    if raw_data_df is not None and not raw_data_df.empty:
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="Raw Data", ln=True, align='C')
        pdf.ln(5)

        # Convert DataFrame to string, then clean
        df_string = raw_data_df.to_string(index=False)
        df_string = clean_text_for_pdf(df_string)
        
        lines_per_page = 40
        df_lines = df_string.split('\n')
        
        for i in range(0, len(df_lines), lines_per_page):
            chunk = '\n'.join(df_lines[i:i + lines_per_page])
            if i > 0:
                pdf.add_page()
                pdf.set_font("Arial", size=12)
                pdf.cell(200, 10, txt=f"Raw Data (Continued)", ln=True, align='C')
                pdf.ln(5)
            pdf.set_font("Courier", size=8) # Use a monospace font for dataframes
            pdf.multi_cell(0, 4, txt=chunk)
            pdf.ln(2)
        pdf.set_font("Arial", size=12)


    pdf_output = BytesIO()
    pdf_bytes = pdf.output(dest='S')
    
    if isinstance(pdf_bytes, str):
        pdf_bytes = pdf_bytes.encode('latin-1')

    pdf_output.write(pdf_bytes)
    pdf_output.seek(0)
    return pdf_output.read()


# --- Main App ---
def main():
    st.title("Fish Visual Census (FVC) Data Analysis")
    st.info("Based on Hilomen et al. (2000), Nañola et al. (2006), and Corrales et al. (2015)")

    # Initialize metadata in session state if not already present
    if 'metadata' not in st.session_state:
        st.session_state['metadata'] = {
            'date': datetime.now().strftime("%Y-%m-%d"),
            'region': '', 'province': '', 'municipality': '', 'barangay': '',
            'mpa_name': '', 'latitude': '', 'longitude': ''
        }
    if 'submitted' not in st.session_state:
        st.session_state['submitted'] = False
    if 'include_raw_data_pdf' not in st.session_state:
        st.session_state['include_raw_data_pdf'] = False

    with st.expander("📍 Enter Survey Metadata"):
        st.session_state.metadata['date'] = st.date_input("Date of Data Collected",
                                                      value=datetime.strptime(st.session_state.metadata['date'], "%Y-%m-%d").date()
                                                     ).strftime("%Y-%m-%d")
        st.session_state.metadata['region'] = st.text_input("Region", value=st.session_state.metadata['region'])
        st.session_state.metadata['province'] = st.text_input("Province", value=st.session_state.metadata['province'])
        st.session_state.metadata['municipality'] = st.text_input("Municipality", value=st.session_state.metadata['municipality'])
        st.session_state.metadata['barangay'] = st.text_input("Barangay", value=st.session_state.metadata['barangay'])
        st.session_state.metadata['mpa_name'] = st.text_input("MPA Name", value=st.session_state.metadata['mpa_name'])
        st.session_state.metadata['latitude'] = st.text_input("Latitude", value=st.session_state.metadata['latitude'])
        st.session_state.metadata['longitude'] = st.text_input("Longitude", value=st.session_state.metadata['longitude'])

    uploaded_files = st.file_uploader("📂 Upload one or more .xlsx or .csv files", type=['xlsx', 'csv'], accept_multiple_files=True)

    st.session_state['include_raw_data_pdf'] = st.checkbox("📄 Include Raw Data Table in PDF Report", value=st.session_state['include_raw_data_pdf'])

    col_submit, col_reset = st.columns([1, 1])
    with col_submit:
        if st.button("Analyze Data", key="submit_button"):
            if not uploaded_files:
                st.warning("Please upload at least one file to analyze.")
            else:
                st.session_state['submitted'] = True
    with col_reset:
        if st.button("Reset Inputs", key="reset_button"):
            st.session_state['submitted'] = False
            st.session_state['metadata'] = {
                'date': datetime.now().strftime("%Y-%m-%d"),
                'region': '', 'province': '', 'municipality': '', 'barangay': '',
                'mpa_name': '', 'latitude': '', 'longitude': ''
            }
            st.session_state['include_raw_data_pdf'] = False
            st.experimental_rerun()


    if uploaded_files and st.session_state.submitted:
        with st.spinner("Processing your data..."):
            try:
                data_list = []
                for file in uploaded_files:
                    df_single = load_and_validate_data(file)
                    df_single['Source'] = file.name
                    data_list.append(df_single)

                df = pd.concat(data_list, ignore_index=True)

                df['Biomass'] = length_weight(df['Length'], df['a'], df['b']) * df['Count'] / BIOMASS_CONVERSION_FACTOR

                richness_list = [sub_df['Species'].nunique() for sub_df in data_list]
                density_list = [sub_df['Count'].sum() for sub_df in data_list]
                biomass_list = []
                for sub_df in data_list:
                    if 'Biomass' in sub_df.columns and not sub_df['Biomass'].empty:
                        biomass_list.append(sub_df['Biomass'].sum())
                    else:
                        biomass_list.append(0)


                richness_avg = np.mean(richness_list) if richness_list else 0
                density_avg = np.mean(density_list) if density_list else 0
                biomass_avg = np.mean(biomass_list) if biomass_list else 0

                richness_cat = categorize_value(richness_avg, SPECIES_RICHNESS_CATEGORIES)
                density_cat = categorize_value(density_avg, DENSITY_CATEGORIES)
                biomass_cat = categorize_value(biomass_avg, BIOMASS_CATEGORIES)

                family_group = df.groupby('Family').agg({'Count': 'sum', 'Biomass': 'sum'}).reset_index()

                if not family_group.empty:
                    top_density_family = family_group.loc[family_group['Count'].idxmax()]
                    top_biomass_family = family_group.loc[family_group['Biomass'].idxmax()]
                else:
                    st.warning("No families found in data to determine top density/biomass. Showing placeholders.")
                    top_density_family = pd.Series({'Family': 'N/A', 'Count': 0})
                    top_biomass_family = pd.Series({'Family': 'N/A', 'Biomass': 0.0})


                st.subheader("📊 Summary Metrics (Averaged Across Files)")
                col1, col2, col3 = st.columns(3)
                col1.markdown(f"<div style='font-size:20px'><strong>Average Species Richness:</strong><br>{richness_avg:.2f} species/1,000m² <span style='color:{richness_cat[1]}'>{richness_cat[2]} {richness_cat[0]}</span></div>", unsafe_allow_html=True)
                col2.markdown(f"<div style='font-size:20px'><strong>Average Fish Density:</strong><br>{density_avg:.2f} ind/1,000m² <span style='color:{density_cat[1]}'>{density_cat[2]} {density_cat[0]}</span></div>", unsafe_allow_html=True)
                col3.markdown(f"<div style='font-size:20px'><strong>Average Fish Biomass:</strong><br>{biomass_avg:.2f} kg/1,000m² <span style='color:{biomass_cat[1]}'>{biomass_cat[2]} {biomass_cat[0]}</span></div>", unsafe_allow_html=True)

                st.markdown(f"**Top Density Family (Combined Data):** {top_density_family['Family']} ({top_density_family['Count']})")
                st.markdown(f"**Top Biomass Family (Combined Data):** {top_biomass_family['Family']} ({top_biomass_family['Biomass']:.2f} kg)")

                family_counts = df.groupby('Family')['Count'].sum().reset_index()
                if not family_counts.empty:
                    main_fig = px.pie(family_counts, values='Count', names='Family', hole=.3,
                                     title='Fish Count Distribution by Family (Combined Data)')
                else:
                    main_fig = go.Figure().add_annotation(text="No family data to display.", showarrow=False)

                st.subheader("Distribution by Family (Combined Data)")
                st.plotly_chart(main_fig, use_container_width=True)


                st.subheader("📈 Parameter Categorization Summary by Source File")
                summary_data = []
                for source in df['Source'].unique():
                    sub = df[df['Source'] == source]
                    richness_sub = sub['Species'].nunique()
                    density_sub = sub['Count'].sum()
                    if 'Biomass' not in sub.columns:
                        sub['Biomass'] = length_weight(sub['Length'], sub['a'], sub['b']) * sub['Count'] / BIOMASS_CONVERSION_FACTOR
                    biomass_sub = sub['Biomass'].sum()
                    richness_cat_sub = categorize_value(richness_sub, SPECIES_RICHNESS_CATEGORIES)
                    density_cat_sub = categorize_value(density_sub, DENSITY_CATEGORIES)
                    biomass_cat_sub = categorize_value(biomass_sub, BIOMASS_CATEGORIES)
                    summary_data.append({
                        'File': source,
                        'Species Richness': f"{richness_sub} ({richness_cat_sub[0]})",
                        'Fish Density': f"{density_sub:.2f} ({density_cat_sub[0]})",
                        'Fish Biomass': f"{biomass_sub:.2f} ({biomass_cat_sub[0]})"
                    })
                st.dataframe(pd.DataFrame(summary_data))

                compare_fig = go.Figure()
                if len(uploaded_files) > 1:
                    summary_by_source = df.groupby('Source').agg(
                        Density_Mean=('Count', 'sum'),
                        Density_Std=('Count', lambda x: x.std() if len(x)>1 else 0),
                        Biomass_Mean=('Biomass', 'sum'),
                        Biomass_Std=('Biomass', lambda x: x.std() if len(x)>1 else 0)
                    ).reset_index()

                    compare_fig.add_trace(go.Bar(
                        x=summary_by_source['Source'],
                        y=summary_by_source['Density_Mean'],
                        name='Fish Density (ind/1,000m²)',
                        marker_color='skyblue',
                        error_y=dict(type='data', array=summary_by_source['Density_Std'], visible=True)
                    ))
                    compare_fig.add_trace(go.Bar(
                        x=summary_by_source['Source'],
                        y=summary_by_source['Biomass_Mean'],
                        name='Fish Biomass (kg/1,000m²)',
                        marker_color='salmon',
                        error_y=dict(type='data', array=summary_by_source['Biomass_Std'], visible=True)
                    ))
                    compare_fig.update_layout(
                        barmode='group',
                        title='FVC Comparison per Source File',
                        xaxis_title='Source File',
                        yaxis_title='Value',
                        legend_title='Metric'
                    )
                else:
                    single_file_density_std = df['Count'].std() if df['Count'].nunique() > 1 else 0
                    single_file_biomass_std = df['Biomass'].std() if df['Biomass'].nunique() > 1 else 0

                    compare_fig.add_trace(go.Bar(
                        x=['Fish Density'],
                        y=[density_avg],
                        name='Fish Density (ind/1,000m²)',
                        marker_color='skyblue',
                        error_y=dict(type='data', array=[single_file_density_std], visible=True),
                        text=[f"{density_avg:.2f}"],
                        textposition='auto'
                    ))
                    compare_fig.add_trace(go.Bar(
                        x=['Fish Biomass'],
                        y=[biomass_avg],
                        name='Fish Biomass (kg/1,000m²)',
                        marker_color='salmon',
                        error_y=dict(type='data', array=[single_file_biomass_std], visible=True),
                        text=[f"{biomass_avg:.2f}"],
                        textposition='auto'
                    ))
                    compare_fig.update_layout(
                        barmode='group',
                        title='Combined FVC Metrics',
                        xaxis_title='Metric',
                        yaxis_title='Value',
                        legend_title='Metric'
                    )
                st.plotly_chart(compare_fig, use_container_width=True)

                species_list = sorted(set(df['Species'].dropna().unique()))
                families = sorted(set(df['Family'].dropna().unique()))

                filter_family = st.selectbox("Filter by Family (optional)", options=["All"] + families)
                filter_text = st.text_input("Search species name")

                filtered_species = [sp for sp in species_list if (filter_family == "All" or df[df['Species'] == sp]['Family'].iloc[0] == filter_family)]
                filtered_species = [sp for sp in filtered_species if filter_text.lower() in sp.lower()]

                expand_ref = True if len(filtered_species) <= 10 and filtered_species else False
                with st.expander("🔗 Species Reference Links", expanded=expand_ref):
                    if not filtered_species:
                        st.write("No species found matching your filter criteria.")
                    for sp in filtered_species:
                        if sp.strip() and sp.lower() not in ["unknown", "unidentified"]:
                            sp_query = sp.replace(" ", "+")
                            fishbase_species_part = '_'.join(sp_query.split('+')[1:]) if len(sp_query.split('+')) > 1 else ''
                            fishbase_url = f"https://www.fishbase.se/summary/SpeciesSummary.php?genusname={sp_query.split('+')[0]}&speciesname={fishbase_species_part}"
                            worms_url = f"https://www.marinespecies.org/aphia.php?p=search&q={sp_query}"
                            google_url = f"https://www.google.com/search?q={sp_query}+fish+Philippines"
                            st.markdown(f"**__{sp}__**: ", unsafe_allow_html=True)
                            st.markdown(f"- [WoRMS]({worms_url}) | [FishBase]({fishbase_url}) | [Google]({google_url})", unsafe_allow_html=True)

                st.subheader("📝 Uploaded Raw Data (Combined)")
                # Select and reorder columns for display
                display_cols = ['Family', 'Species', 'Count', 'Length', 'a', 'b', 'Biomass', 'Source']
                # Ensure all display_cols exist in df before trying to display,
                # to prevent potential KeyError if any column is somehow missing
                existing_display_cols = [col for col in display_cols if col in df.columns]
                st.dataframe(df[existing_display_cols])

                st.markdown("""
                **Note on Biomass Calculation:**
                Fish biomass is computed using the length-weight relationship formula:
                $$W = aL^b$$
                Where:
                * $W$ = weight of fish (in grams)
                * $L$ = length of fish (in cm)
                * $a$ and $b$ = species-specific regression parameters obtained from FishBase.

                The calculated weight is then converted to kilograms per 1,000m² for the report.
                """)


                ai_analysis_content = None

                st.subheader("📤 Export Report")
                
                raw_data_to_pdf = df[existing_display_cols] if st.session_state['include_raw_data_pdf'] else None

                pdf_data = export_analysis_pdf(st.session_state.metadata, top_density_family, top_biomass_family,
                                                 richness_avg, richness_cat, density_avg, density_cat, biomass_avg, biomass_cat,
                                                 main_fig, compare_fig, ai_analysis_content, raw_data_to_pdf)

                filename_date = st.session_state.metadata['date'].replace('-', '')
                filename = f"fish_survey_{st.session_state.metadata['mpa_name']}_{filename_date}_report.pdf" if st.session_state.metadata['mpa_name'] else f"fish_survey_combined_{filename_date}_report.pdf"
                st.download_button("📥 Download PDF Report", pdf_data, file_name=filename, mime='application/pdf')

                csv_output = df.to_csv(index=False).encode('utf-8')
                st.download_button("📥 Download Cleaned Data as CSV", csv_output, file_name='combined_cleaned_fish_survey.csv', mime='text/csv')

            except ValueError as ve:
                st.error(f"Data validation error: {ve}")
                st.info("Please ensure your uploaded files contain the required columns ('Species', 'Length', 'a', 'b', 'Count', 'Family') and valid numeric data.")
            except Exception as e:
                st.error(f"An unexpected error occurred during data processing: {e}")
                st.exception(e)

if __name__ == "__main__":
    main()