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

walls_per_city = []
st.subheader("Enter Number of Walls per City")
for i in range(int(num_cities)):
    walls = st.number_input(f"City {i+1} - Number of Walls", min_value=0, step=1, key=f"city_{i}")
    walls_per_city.append(walls)

start_date = st.date_input("Project Start Date")
end_date = st.date_input("Project End Date")

# --- CALCULATION LOGIC ---
def calculate_execution_days(media_type, walls_per_city):
    total_days = 0
    total_walls = sum(walls_per_city)

    if media_type == "Lowrise":
        # Assume team of 2 by default → 12 walls/day
        productivity_per_day = 12
        total_days = total_walls / productivity_per_day

    elif media_type == "Highrise":
        # 2 walls per day per team
        productivity_per_day = 2
        total_days = total_walls / productivity_per_day

    return total_days, total_walls


def calculate_travel_days(num_cities):
    if num_cities <= 1:
        return 0
    return num_cities - 1  # 1 extra day per city move


# --- SUBMIT BUTTON ---
if st.button("Calculate"):
    if not client_name:
        st.error("Please enter client name")
    elif start_date >= end_date:
        st.error("End date must be after start date")
    else:
        execution_days, total_walls = calculate_execution_days(media_type, walls_per_city)
        travel_days = calculate_travel_days(num_cities)

        total_required_days = execution_days + travel_days

        available_days = (end_date - start_date).days

        # Teams required = total work / available days
        if available_days > 0:
            teams_required = total_required_days / available_days
        else:
            teams_required = 0

        teams_required = round(teams_required + 0.5)

        # --- OUTPUT ---
        st.subheader("Results")
        st.write(f"Client: {client_name}")
        st.write(f"Total Walls: {total_walls}")
        st.write(f"Execution Days Required: {round(execution_days, 2)}")
        st.write(f"Travel Days Required: {travel_days}")
        st.write(f"Total Days Required: {round(total_required_days, 2)}")
        st.write(f"Available Days: {available_days}")
        st.success(f"Teams Required: {teams_required}")

        # Additional insights
        if teams_required > 1:
            st.info("Multiple teams required to meet deadline")
        else:
            st.info("Single team is sufficient")
