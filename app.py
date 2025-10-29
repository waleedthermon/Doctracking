import os
import streamlit as st
import pandas as pd
from PIL import Image

# Load data
team_df = pd.read_excel("data/Team List Sample.xlsx", engine="openpyxl")
doc_df = pd.read_excel("data/Sample document list spreadsheet.xlsx", engine="openpyxl")

# Load logo
logo = Image.open("assets/thermon_logo.png")
st.image(logo, width=200)
st.title("Thermon Tracking")

# User login
user = st.selectbox("Select your name", team_df["Name"].unique())
user_role = team_df[team_df["Name"] == user]["Role"].values[0]
user_location = team_df[team_df["Name"] == user]["Location"].values[0]

st.markdown(f"**Role:** {user_role}  |  **Location:** {user_location}")

# Drawing assignment data
if os.path.exists("data/drawing_assignments.xlsx"):
    drawing_df = pd.read_excel("data/drawing_assignments.xlsx", engine="openpyxl")
else:
    drawing_df = pd.DataFrame(columns=[
        "Drawing Number", "Documents", "Designer", "Drafter", "Checker", "Lead",
        "Status", "RFI Number", "Red Flag", "Location"
    ])

# Filter drawings assigned to the user
assigned_drawings = drawing_df[
    (drawing_df["Designer"] == user) |
    (drawing_df["Checker"] == user) |
    (drawing_df["Lead"] == user) |
    (drawing_df["Drafter"].fillna("").str.contains(user))
]

st.subheader("Your Assigned Projects")
st.dataframe(assigned_drawings)

# Notifications
st.subheader("Notifications")

# Red Flags
red_flags = assigned_drawings[assigned_drawings["Red Flag"] == "Revision Mismatch"]
if not red_flags.empty:
    st.warning("⚠️ Revision Mismatches Found")
    st.dataframe(red_flags)

# On-Hold Drawings
on_hold = assigned_drawings[assigned_drawings["Current Status"] == "On-Hold for Missing Info"]
if not on_hold.empty:
    st.warning("🛑 Drawings On-Hold for Missing Info")
    st.dataframe(on_hold[["Drawing Number", "RFI Number", "Status"]])

# Search
st.subheader("Search Drawings")
search_term = st.text_input("Enter drawing or document number")
if search_term:
    search_results = drawing_df[
        drawing_df["Drawing Number"].str.contains(search_term, case=False, na=False) |
        drawing_df["Documents"].astype(str).str.contains(search_term, case=False, na=False)
    ]
    st.dataframe(search_results)

# Charts
st.subheader("Charts")
status_counts = drawing_df["Current Status"].value_counts().reset_index()
status_counts.columns = ["Current Status", "Count"]
st.bar_chart(data=status_counts.set_index("Current Status"))

designer_counts = drawing_df["Designer"].value_counts().reset_index()
designer_counts.columns = ["Designer", "Count"]
st.bar_chart(data=designer_counts.set_index("Designer"))


# Ensure data folder exists
os.makedirs("data", exist_ok=True)

# Load document list
doc_df = pd.read_excel("data/Sample document list spreadsheet.xlsx", engine="openpyxl")

# Load or initialize assignments file
assignments_file = "data/drawing_assignments.xlsx"
if not os.path.exists(assignments_file):
    columns = [
        "Drawing No", "Revision No", "Documents", "Created By", "Created On",
        "Current Status", "Assigned To", "Assignment Date", "Comments", "Red Flag"
    ]
    pd.DataFrame(columns=columns).to_excel(assignments_file, index=False)

assignments_df = pd.read_excel(assignments_file, engine="openpyxl")

# Create New Design Button and Form
st.subheader("Design Management")
if st.button("Create New Design"):
    with st.form("new_design_form", clear_on_submit=True):
        drawing_no = st.text_input("Enter Drawing Number")
        revision_no = st.text_input("Enter Revision Number", value="0")
        selected_documents = st.multiselect("Select Related Documents", doc_df["Document no"].unique())
        submitted = st.form_submit_button("Submit Design")

        if submitted:
            if not drawing_no or not revision_no or not selected_documents:
                st.warning("Please fill all fields and select at least one document.")
            else:
                new_entry = {
                    "Drawing No": drawing_no,
                    "Revision No": revision_no,
                    "Documents": ", ".join(selected_documents),
                    "Created By": user,  # Logged-in user
                    "Created On": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "Current Status": "New",
                    "Assigned To": user,  # ✅ Assign to current user
                    "Assignment Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "Comments": "",
                    "Red Flag": ""
}

                assignments_df = pd.concat([assignments_df, pd.DataFrame([new_entry])], ignore_index=True)
                assignments_df.to_excel(assignments_file, index=False)
                st.success(f"New design '{drawing_no}' with revision '{revision_no}' created successfully.")


# Import New Document List
st.markdown("## 📥 Import New Document List")
uploaded_doc_file = st.file_uploader("Upload new document list Excel file", type=["xlsx"])
if uploaded_doc_file:
    try:
        new_doc_df = pd.read_excel(uploaded_doc_file, engine="openpyxl")
        initial_count = len(doc_df)
        doc_df = pd.concat([doc_df, new_doc_df]).drop_duplicates(subset=["Document no"], keep="last").reset_index(drop=True)
        doc_df.to_excel("data/Sample document list spreadsheet.xlsx", index=False, engine="openpyxl")
        st.success(f"✅ Imported {len(doc_df) - initial_count} new documents successfully.")
    except Exception as e:
        st.error(f"Error importing document list: {e}")


# Export
st.subheader("Export Your Assignments")
if not assigned_drawings.empty:
    st.download_button(
        label="Download as Excel",
        data=assigned_drawings.to_excel(index=False, engine="openpyxl"),
        file_name="your_assignments.xlsx"
    )
