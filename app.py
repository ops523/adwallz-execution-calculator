import streamlit as st
from datetime import timedelta
import math

st.set_page_config(page_title="On Field Execution Teams Calculator", layout="centered")

# --- HEADER WITH CENTERED LOGO ---
col_logo = st.columns([1,2,1])
with col_logo[1]:
    st.image("logo.png", width=100)

st.markdown("<h2 style='text-align: center;'>ADWALLZ - On Field Execution Calculator</h2>", unsafe_allow_html=True)
st.markdown("---")

# --- INPUT SECTION ---
col1, col2 = st.columns(2)

with col1:
    client_name = st.text_input("Client Name")
    media_type = st.selectbox("Select Media Type", ["Lowrise", "Highrise"])
    num_cities = st.number_input("Number of Cities", min_value=1, step=1)

with col2:
    start_date = st.date_input("Project Start Date")
    end_date = st.date_input("Project End Date")

# --- WALL INPUT ---
st.markdown("### 🧱 Wall Inputs")

wall_input_mode = st.radio(
    "Wall Input Mode",
    ["Same number of walls in each city", "Different number of walls in each city"]
)

walls_per_city = []

if wall_input_mode == "Same number of walls in each city":
    walls = st.number_input("Number of Walls per City", min_value=0, step=1)
    walls_per_city = [walls] * int(num_cities)
else:
    for i in range(int(num_cities)):
        walls = st.number_input(f"City {i+1} - Number of Walls", min_value=0, step=1, key=f"city_{i}")
        walls_per_city.append(walls)

# --- PROGRESS ---
st.markdown("---")
st.markdown("### 📍 Current Progress")

col3, col4, col5 = st.columns(3)

with col3:
    current_teams = st.number_input("Current Teams", min_value=0, step=1)

with col4:
    walls_completed = st.number_input("Walls Completed", min_value=0, step=1)

with col5:
    cities_completed = st.number_input("Cities Completed", min_value=0, max_value=int(num_cities), step=1)

# --- LOGIC ---
def get_productivity(media_type):
    return 12 if media_type == "Lowrise" else 2


if st.button("Calculate"):

    if not client_name:
        st.error("Please enter client name")

    elif start_date >= end_date:
        st.error("End date must be after start date")

    else:
        total_walls = sum(walls_per_city)
        productivity = get_productivity(media_type)
        available_days = (end_date - start_date).days

        # --- TEAM-DAYS MODEL ---
        total_exec_td = total_walls / productivity
        total_travel_td = max(0, num_cities - 1)
        total_team_days = total_exec_td + total_travel_td

        base_teams = max(1, math.ceil(total_team_days / available_days))

        # --- BUFFER ---
        buffered_teams = base_teams * 2

        # --- RESULTS DASHBOARD ---
        st.markdown("---")
        st.markdown("## 📊 Results Summary")

        colr1, colr2, colr3 = st.columns(3)
        colr1.metric("Total Walls", total_walls)
        colr2.metric("Available Days", available_days)
        colr3.metric("Teams Required", buffered_teams)

        # --- STATUS INDICATOR ---
        if current_teams == 0:
            st.info("⚠️ No teams deployed yet")
        elif buffered_teams <= current_teams:
            st.success("🟢 On Track")
        elif buffered_teams <= current_teams * 1.5:
            st.warning("🟡 Slightly Understaffed")
        else:
            st.error("🔴 High Risk - Increase Teams")

        # --- FORECAST ---
        st.markdown("---")
        st.markdown("## 🔮 Bi-Weekly Forecast")

        if current_teams == 0:
            st.info("Forecast assumes no teams deployed yet")

        today = start_date
        cutoff_date = end_date - timedelta(days=7)

        forecast_dates = []
        current_date = today

        while current_date <= cutoff_date:
            if current_date.weekday() in [3, 6]:  # Thu & Sun
                forecast_dates.append(current_date)
            current_date += timedelta(days=1)

        if len(forecast_dates) == 0:
            st.warning("Not enough timeline to generate forecast")

        else:
            for date_point in forecast_dates:

                days_passed = (date_point - start_date).days

                # Work done
                if current_teams == 0:
                    future_work = 0
                else:
                    future_work = current_teams * productivity * days_passed

                work_done = min(total_walls, walls_completed + future_work)

                remaining_walls = max(0, total_walls - work_done)

                # Remaining work
                remaining_exec_td = remaining_walls / productivity
                remaining_cities = max(0, num_cities - cities_completed)
                remaining_travel_td = max(0, remaining_cities - 1)

                remaining_team_days = remaining_exec_td + remaining_travel_td

                days_left = max(1, (end_date - date_point).days)

                teams_needed = math.ceil(remaining_team_days / days_left)

                # Apply buffer
                teams_needed_buffered = teams_needed * 2

                additional_needed = max(0, teams_needed_buffered - current_teams)

                st.markdown(
                    f"**📅 {date_point.strftime('%b %d, %Y')}** → Additional Teams Needed: **{additional_needed}**"
                )

# --- FOOTER ---
st.markdown("---")
st.markdown(
    "<center>Built for Adwallz Operations Team 🚀</center>",
    unsafe_allow_html=True
)
