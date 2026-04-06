import streamlit as st
from datetime import datetime, timedelta

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
cities_completed = st.number_input("Number of Cities Completed", min_value=0, max_value=int(num_cities), step=1)

# --- LOGIC ---
def get_productivity(media_type):
    return 12 if media_type == "Lowrise" else 2


def total_travel_days(num_cities):
    return max(0, num_cities - 1)


def remaining_travel_days(num_cities, cities_completed):
    remaining_cities = max(0, num_cities - cities_completed)
    return max(0, remaining_cities - 1)


if st.button("Calculate"):
    if not client_name:
        st.error("Please enter client name")
    elif start_date >= end_date:
        st.error("End date must be after start date")
    else:
        total_walls = sum(walls_per_city)
        productivity = get_productivity(media_type)
        available_days = (end_date - start_date).days

        # --- BASE CALCULATION (includes full travel) ---
        travel_days_full = total_travel_days(num_cities)
        total_execution_days = total_walls / productivity
        total_required_days = total_execution_days + travel_days_full

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

        # --- BI-WEEKLY FORECAST (WITH TRAVEL + PROGRESS) ---
        if current_teams > 0:
            st.subheader("Bi-Weekly Team Requirement Forecast")

            today = start_date
            cutoff_date = end_date - timedelta(days=7)

            forecast_dates = []
            current_date = today

            # Generate Thursdays & Sundays
            while current_date <= cutoff_date:
                if current_date.weekday() == 3 or current_date.weekday() == 6:
                    forecast_dates.append(current_date)
                current_date += timedelta(days=1)

            for date_point in forecast_dates:
                days_passed = (date_point - start_date).days

                # Work done till this point (actual + simulated)
                future_work = current_teams * productivity * days_passed
                work_done = walls_completed + future_work

                remaining_walls = max(0, total_walls - work_done)

                # Remaining time
                days_left = max(1, (end_date - date_point).days)

                # Remaining travel impact
                travel_left = remaining_travel_days(num_cities, cities_completed)
                effective_days_left = max(1, days_left - travel_left)

                # Teams needed including travel constraint
                teams_needed_total = remaining_walls / (productivity * effective_days_left)
                teams_needed_total = max(1, round(teams_needed_total + 0.5))

                additional_needed = max(0, teams_needed_total - current_teams)

                st.write(
                    f"Additional teams to be deployed after {date_point.strftime('%B %d, %Y')}: {additional_needed}"
                )

            if len(forecast_dates) == 0:
                st.warning("Not enough timeline to generate bi-weekly forecast")
