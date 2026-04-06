import streamlit as st
from datetime import datetime

st.set_page_config(page_title="ADWALLZ - On Field Execution Calculator", layout="centered")

st.title("ADWALLZ - On Field Execution Calculator")

# --- INPUTS ---
client_name = st.text_input("Client Name")

media_type = st.selectbox(
    "Select Media Type",
    ["Lowrise", "Highrise"]
)

num_cities = st.number_input("Number of Cities", min_value=1, step=1)

# NEW: Wall input mode selection
wall_input_mode = st.radio(
    "Wall Input Mode",
    [
        "Same number of walls in each city",
        "Different number of walls in each city"
    ]
)

walls_per_city = []

st.subheader("Wall Inputs")

if wall_input_mode == "Same number of walls in each city":
    walls = st.number_input("Number of Walls per City", min_value=0, step=1)
    walls_per_city = [walls] * int(num_cities)

else:
    for i in range(int(num_cities)):
