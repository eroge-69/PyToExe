import streamlit as st
import pandas as pd
import os
from datetime import datetime

# ---------------------- File Configuration ---------------------- #
CSV_FILE = "market_requirements.csv"
HISTORY_FILE = "requirement_history.csv"

# Ensure the main CSV file exists
if not os.path.exists(CSV_FILE):
    df = pd.DataFrame(columns=[
        "Customer Name", "Industry Type", "Contact Person", "Email", "Phone",
        "Company Size", "Requirement ID", "Title", "Description", "Impact Level",
        "Urgency Level", "Solution Required", "Current Alternatives", "Expected Outcome",
        "Budget Constraints", "Vehicle Data Available", "Integration Needed", "Data Format",
        "Reporting Requirements", "Decision Maker", "Technical Contact", "User Base",
        "Solution Assigned To", "Status", "Comments", "Implementation Deadline"
    ])
    df.to_csv(CSV_FILE, index=False)

# Load existing data
df = pd.read_csv(CSV_FILE)

# ---------------------- Function to Add a Requirement ---------------------- #
def add_requirement(customer_name, industry, contact_person, email, phone, company_size,
                    title, description, impact, urgency, solution, alternatives, expected_outcome,
                    budget, vehicle_data, integration, data_format, reporting, decision_maker,
                    technical_contact, user_base, assigned_to, status, comments, deadline):

    global df
    requirement_id = f"REQ{len(df) + 1:04d}"  # Generate unique Requirement ID

    new_entry = pd.DataFrame([{
        "Customer Name": customer_name, "Industry Type": industry, "Contact Person": contact_person,
        "Email": email, "Phone": phone, "Company Size": company_size, "Requirement ID": requirement_id,
        "Title": title, "Description": description, "Impact Level": impact, "Urgency Level": urgency,
        "Solution Required": solution, "Current Alternatives": alternatives, "Expected Outcome": expected_outcome,
        "Budget Constraints": budget, "Vehicle Data Available": vehicle_data, "Integration Needed": integration,
        "Data Format": data_format, "Reporting Requirements": reporting, "Decision Maker": decision_maker,
        "Technical Contact": technical_contact, "User Base": user_base, "Solution Assigned To": assigned_to,
        "Status": status, "Comments": comments, "Implementation Deadline": deadline
    }])

    df = pd.concat([df, new_entry], ignore_index=True)
    df.to_csv(CSV_FILE, index=False)
    st.session_state.clear()
    st.success(f"✅ Requirement '{title}' added successfully!")
    st.rerun()

# ---------------------- Function to Fetch Requirements ---------------------- #
def fetch_requirements(title, assigned_to):
    df = pd.read_csv(CSV_FILE)
    filtered_df = df[(df["Title"].str.contains(title, case=False, na=False)) &
                     (df["Solution Assigned To"].str.contains(assigned_to, case=False, na=False))]

    if "Requirement ID" in filtered_df.columns:
        cols = ["Requirement ID"] + [col for col in filtered_df.columns if col != "Requirement ID"]
        filtered_df = filtered_df[cols]

    return filtered_df

# ---------------------- Function to Update a Requirement ---------------------- #
def update_requirement(requirement_id, column, new_value, updated_by="System"):
    global df
    if requirement_id in df["Requirement ID"].values:
        old_value = df.loc[df["Requirement ID"] == requirement_id, column].values[0]
        df.loc[df["Requirement ID"] == requirement_id, column] = new_value
        df.to_csv(CSV_FILE, index=False)
        log_history(requirement_id, column, old_value, new_value, updated_by)
        st.session_state.clear()
        st.success(f"✏️ Requirement {requirement_id} updated successfully!")
        st.rerun()
    else:
        st.error("❌ Requirement ID not found!")

# ---------------------- Function to Delete a Requirement ---------------------- #
def delete_requirement(requirement_id):
    global df
    if requirement_id in df["Requirement ID"].values:
        df = df[df["Requirement ID"] != requirement_id]
        df.to_csv(CSV_FILE, index=False)
        st.session_state.clear()
        st.success(f"🗑️ Requirement {requirement_id} deleted successfully!")
        st.rerun()
    else:
        st.error("❌ Requirement ID not found!")

# ---------------------- Function to Log History ---------------------- #
def log_history(requirement_id, field, old_value, new_value, updated_by):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    history_entry = pd.DataFrame([{
        "Timestamp": timestamp,
        "Requirement ID": requirement_id,
        "Updated By": updated_by,
        "Field": field,
        "Old Value": old_value,
        "New Value": new_value
    }])
    if os.path.exists(HISTORY_FILE) and os.path.getsize(HISTORY_FILE) > 0:
        history_df = pd.read_csv(HISTORY_FILE)
        history_df = pd.concat([history_df, history_entry], ignore_index=True)
    else:
        history_df = history_entry
    history_df.to_csv(HISTORY_FILE, index=False)

# ---------------------- Streamlit UI Styling ---------------------- #

st.set_page_config(page_title="Market Requirements", layout="wide")

st.markdown(
    """
    <style>
        .stApp {
            background-color: #f9f9fb;
            color: #2e2e2e;
        }
        .stSidebar {
            background-color: #f0f2f6;
        }
        h1, h2, h3, h4, h5, h6 {
            color: #336699;
        }
        .stButton>button {
            background-color: #e6f0ff;
            color: #003366;
        }
        .stTextInput>div>input, .stSelectbox>div>div, .stTextArea>div>textarea {
            background-color: #ffffff;
        }
        .stDataFrame {
            background-color: #ffffff;
        }
    </style>
    """,
    unsafe_allow_html=True
)

with st.container():
    st.markdown("""
    <h2 style='text-align: center; font-size: 24px;'>Market Requirements Management Dashboard</h2>
    <p style='text-align: center; font-size: 16px; color: #555;'>Track, assign, and manage client requirements in a structured, professional way.</p>
    <hr style='border-top: 1px solid #ccc;'>
    """, unsafe_allow_html=True)

# ---------------------- Top Navigation ---------------------- #
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "Add Requirement", "View Requirements", "Update Requirement",
    "Delete Requirement", "Communication", "View History"])

# Form data holders
if "add_form_data" not in st.session_state:
    st.session_state.add_form_data = {
        "customer_name": "", "industry": "", "contact_person": "", "email": "", "phone": "", "company_size": "",
        "title": "", "description": "", "impact": "Medium", "urgency": "Short-term", "solution": "", "alternatives": "",
        "expected_outcome": "", "budget": "", "vehicle_data": "", "integration": "", "data_format": "", "reporting": "",
        "decision_maker": "", "technical_contact": "", "user_base": "", "assigned_to": "", "status": "New", "comments": "", "deadline": datetime.today()
    }

with tab1:
    st.subheader("Add Requirement")
    section = st.radio("Select Section", [
        "Customer Details", "Requirement Details",
        "Implementation Details", "Assignee and Status"], horizontal=True)

    with st.form("add_requirement_form"):
        form_data = st.session_state.add_form_data

        if section == "Customer Details":
            form_data["customer_name"] = st.text_input("Customer Name", value=form_data["customer_name"])
            form_data["industry"] = st.text_input("Industry Type", value=form_data["industry"])
            form_data["contact_person"] = st.text_input("Contact Person", value=form_data["contact_person"])
            form_data["email"] = st.text_input("Email", value=form_data["email"])
            form_data["phone"] = st.text_input("Phone", value=form_data["phone"])
            form_data["company_size"] = st.text_input("Company Size", value=form_data["company_size"])
            next_btn = st.form_submit_button("Next")

        elif section == "Requirement Details":
            form_data["title"] = st.text_input("Title", value=form_data["title"])
            form_data["description"] = st.text_area("Description", value=form_data["description"])
            form_data["impact"] = st.selectbox("Impact Level", ["High", "Medium", "Low"], index=["High", "Medium", "Low"].index(form_data["impact"]))
            form_data["urgency"] = st.selectbox("Urgency Level", ["Immediate", "Short-term", "Long-term"], index=["Immediate", "Short-term", "Long-term"].index(form_data["urgency"]))
            form_data["solution"] = st.text_input("Solution Required", value=form_data["solution"])
            form_data["alternatives"] = st.text_input("Current Alternatives", value=form_data["alternatives"])
            form_data["expected_outcome"] = st.text_area("Expected Outcome", value=form_data["expected_outcome"])
            next_btn = st.form_submit_button("Next")

        elif section == "Implementation Details":
            form_data["budget"] = st.text_input("Budget Constraints", value=form_data["budget"])
            form_data["vehicle_data"] = st.text_input("Vehicle Data Available", value=form_data["vehicle_data"])
            form_data["integration"] = st.text_input("Integration Needed", value=form_data["integration"])
            form_data["data_format"] = st.text_input("Data Format", value=form_data["data_format"])
            form_data["reporting"] = st.text_input("Reporting Requirements", value=form_data["reporting"])
            next_btn = st.form_submit_button("Next")

        elif section == "Assignee and Status":
            form_data["decision_maker"] = st.text_input("Decision Maker", value=form_data["decision_maker"])
            form_data["technical_contact"] = st.text_input("Technical Contact", value=form_data["technical_contact"])
            form_data["user_base"] = st.text_input("User Base", value=form_data["user_base"])
            form_data["assigned_to"] = st.text_input("Solution Assigned To", value=form_data["assigned_to"])
            form_data["status"] = st.selectbox("Status", ["New", "In Progress", "Implemented", "Rejected"], index=["New", "In Progress", "Implemented", "Rejected"].index(form_data["status"]))
            form_data["comments"] = st.text_area("Comments", value=form_data["comments"])
            form_data["deadline"] = st.date_input("Implementation Deadline", value=form_data["deadline"])
            submitted = st.form_submit_button("Submit Requirement")
            if submitted:
                add_requirement(**form_data)

with tab2:
    st.subheader("View Requirements")
    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            title = st.text_input("Search by Title", key="view_title")
        with col2:
            assigned_to = st.text_input("Search by Assignee", key="view_assignee")

        if st.button("Fetch", key="fetch_view"):
            result_df = fetch_requirements(title, assigned_to)
            if not result_df.empty:
                st.dataframe(result_df)
            else:
                st.info("No matching requirements found.")

with tab3:
    st.subheader("Update Requirement")
    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            requirement_id = st.text_input("Enter Requirement ID", key="update_id")
            updated_by = st.text_input("Updated By", key="update_by")
        with col2:
            column = st.selectbox("Select Column to Update", df.columns, key="update_column")
            new_value = st.text_input("Enter New Value", key="update_value")

        if st.button("Update Requirement", key="update_btn"):
            update_requirement(requirement_id, column, new_value, updated_by)

with tab4:
    st.subheader("Delete Requirement")
    requirement_id = st.text_input("Enter Requirement ID to Delete", key="delete_id")
    if st.button("Delete Requirement", key="delete_btn"):
        delete_requirement(requirement_id)

with tab5:
    st.subheader("Communication")
    df = pd.read_csv(CSV_FILE)
    assignees = df["Solution Assigned To"].dropna().unique()
    selected_assignee = st.selectbox("Select Assignee", assignees, key="comm_assignee")
    assignee_requirements = df[df["Solution Assigned To"] == selected_assignee]

    if not assignee_requirements.empty:
        requirement_titles = assignee_requirements["Title"].tolist()
        selected_title = st.selectbox("Select Requirement", requirement_titles, key="comm_title")
        selected_row = assignee_requirements[assignee_requirements["Title"] == selected_title]

        if not selected_row.empty:
            requirement = selected_row.iloc[0]
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**Current Status:** {requirement['Status']}")
                new_status = st.selectbox("Update Status", ["New", "In Progress", "Implemented", "Rejected"], index=["New", "In Progress", "Implemented", "Rejected"].index(requirement['Status']), key="comm_status")
            with col2:
                comments = st.text_area("Comments", value=requirement.get("Comments", ""), key="comm_comments")
                updated_by = st.text_input("Updated By", value=selected_assignee, key="comm_updated_by")

            if st.button("Update Status", key="comm_update_btn"):
                df.loc[(df["Requirement ID"] == requirement["Requirement ID"]), "Status"] = new_status
                df.loc[(df["Requirement ID"] == requirement["Requirement ID"]), "Comments"] = comments
                df.to_csv(CSV_FILE, index=False)
                log_history(requirement["Requirement ID"], "Status", requirement["Status"], new_status, updated_by)
                st.success("Status updated successfully!")
                st.experimental_rerun()

with tab6:
    st.subheader("View History")
    df = pd.read_csv(CSV_FILE)
    assignees = df["Solution Assigned To"].dropna().unique()
    selected_assignee = st.selectbox("Select Assignee", assignees, key="history_assignee")
    assignee_requirements = df[df["Solution Assigned To"] == selected_assignee]

    if not assignee_requirements.empty:
        titles = assignee_requirements["Title"].tolist()
        selected_title = st.selectbox("Select Requirement", titles, key="history_title")
        selected_req = assignee_requirements[assignee_requirements["Title"] == selected_title]

        if not selected_req.empty:
            comments = selected_req["Comments"].values[0]
            status = selected_req["Status"].values[0]

            st.markdown("### Requirement Details")
            st.write(f"**Status:** {status}")
            st.write(f"**Comments:** {comments}")
        else:
            st.warning("Selected requirement not found.")
    else:
        st.warning("No requirements found for the selected assignee.")
