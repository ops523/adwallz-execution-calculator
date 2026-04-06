import streamlit as st
from datetime import datetime

st.set_page_config(page_title="ADWALLZ - On Field Execution Calculator", layout="centered")

st.title("ADWALLZ - On Field Execution Calculator")

# --- INPUTS ---
client_name = st.text_input("Client Name")

media_type = st.selectbox("Select Media Type", ["Lowrise", "Highrise"])

num_cities = st.number_input("Number of Cities", min_value=1, step=1)

wall_input_mode = st.radio(
    "Wall Input Mode",
    ["Same number of walls in each city", "Different number of walls in each city"]
)

walls_per_city = []
st.subheader("Wall Inputs")

if wall_input_mode == "Same number of walls in each city":
    walls = st.number_input("Number of Walls per City", min_value=0, step=1)
    walls_per_city = [walls] * int(num_cities)
else:
    for i in range(int(num_cities)):
        walls = st.number_input(f"City {i+1} - Number of Walls", min_value=0, step=1, key=f"city_{i}")
        walls_per_city.append(walls)

start_date = st.date_input("Project Start Date")
end_date = st.date_input("Project End Date")

st.subheader("Current Progress (Optional)")
current_teams = st.number_input("Current Teams on Field", min_value=0, step=1)
walls_completed = st.number_input("Walls Completed So Far", min_value=0, step=1)

# --- CALCULATION LOGIC ---
def get_productivity(media_type):
    return 12 if media_type == "Lowrise" else 2


def calculate_travel_days(num_cities):
    return max(0, num_cities - 1)


if st.button("Calculate"):
    if not client_name:
        st.error("Please enter client name")
    elif start_date >= end_date:
        st.error("End date must be after start date")
    else:
        total_walls = sum(walls_per_city)
        productivity = get_productivity(media_type)

        remaining_walls = max(0, total_walls - walls_completed)

        travel_days = calculate_travel_days(num_cities)
        available_days = (end_date - start_date).days

        # Total days needed for full work
        total_execution_days = total_walls / productivity
        total_required_days = total_execution_days + travel_days

        # Base teams required
        base_teams_required = max(1, round((total_required_days / available_days) + 0.5))

        # --- OUTPUT ---
        st.subheader("Results")
        st.write(f"Client: {client_name}")
        st.write(f"Total Walls: {total_walls}")
        st.write(f"Available Days: {available_days}")
        st.success(f"Teams Required: {base_teams_required}")

        if base_teams_required > 1:
            st.info("Multiple teams required to meet deadline")
        else:
            st.info("Single team is sufficient")

        # --- FORECAST LOGIC ---
        st.subheader("Bi-Weekly Forecast Scenario")

        delayed_teams = st.number_input("Teams deployed initially (Day 1)", min_value=0, step=1)
        added_teams_later = st.number_input("Additional teams added after 7 days", min_value=0, step=1)

        if delayed_teams > 0:
            # Work done in first 7 days
            work_done_first_phase = delayed_teams * productivity * 7

            remaining_after_7_days = max(0, total_walls - work_done_first_phase)

            remaining_days = max(1, available_days - 7)

            teams_needed_after = remaining_after_7_days / (productivity * remaining_days)
            teams_needed_after = max(0, round(teams_needed_after + 0.5))

            additional_needed = max(0, teams_needed_after - added_teams_later)

            st.write(f"Remaining Walls after 7 days: {remaining_after_7_days}")
            st.write(f"Teams needed after Day 7: {teams_needed_after}")
            st.warning(f"Additional Teams Required: {additional_needed}")

        # --- CURRENT PROGRESS ADJUSTMENT ---
        if current_teams > 0 and remaining_walls > 0:
            st.subheader("Live Project Adjustment")

            days_left = max(1, available_days)

            teams_required_now = remaining_walls / (productivity * days_left)
            teams_required_now = max(1, round(teams_required_now + 0.5))

            extra_teams_needed = max(0, teams_required_now - current_teams)

            st.write(f"Remaining Walls: {remaining_walls}")
            st.write(f"Teams Required Now: {teams_required_now}")
            st.warning(f"Additional Teams Needed: {extra_teams_needed}")
