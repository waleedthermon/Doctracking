
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
        "Drawing Number", "Documents", "Designer", "Drafters", "Checker", "Lead",
        "Status", "RFI Number", "Red Flag", "Location"
    ])

# Filter drawings assigned to the user
assigned_drawings = drawing_df[
    (drawing_df["Designer"] == user) |
    (drawing_df["Checker"] == user) |
    (drawing_df["Lead"] == user) |
    (drawing_df["Drafters"].fillna("").str.contains(user))
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
on_hold = assigned_drawings[assigned_drawings["Status"] == "On-Hold for Missing Info"]
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
status_counts = drawing_df["Status"].value_counts().reset_index()
status_counts.columns = ["Status", "Count"]
st.bar_chart(data=status_counts.set_index("Status"))

designer_counts = drawing_df["Designer"].value_counts().reset_index()
designer_counts.columns = ["Designer", "Count"]
st.bar_chart(data=designer_counts.set_index("Designer"))

# Export
st.subheader("Export Your Assignments")
if not assigned_drawings.empty:
    st.download_button(
        label="Download as Excel",
        data=assigned_drawings.to_excel(index=False, engine="openpyxl"),
        file_name="your_assignments.xlsx"
    )
