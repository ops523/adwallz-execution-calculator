import streamlit as st
from datetime import timedelta
import math

st.set_page_config(page_title="ADWALLZ - On Field Execution Calculator", layout="centered")

# --- HEADER ---
col_logo = st.columns([1,2,1])
with col_logo[1]:
    st.image("logo.png", width=200)

st.markdown("<h2 style='text-align: center;'>ADWALLZ - On Field Execution Calculator</h2>", unsafe_allow_html=True)
st.markdown("---")

# --- INPUT ---
col1, col2 = st.columns(2)

with col1:
    client_name = st.text_input("Client Name")
    media_type = st.selectbox("Select Media Type", ["Lowrise", "Highrise"])
    num_cities = st.number_input("Number of Cities", min_value=1, step=1)
    wall_size = st.number_input("Wall Size (Sq Ft)", min_value=1, step=1)

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

        # --- TEAM DAYS ---
        total_exec_td = total_walls / productivity
        total_travel_td = max(0, num_cities - 1)
        total_team_days = total_exec_td + total_travel_td

        base_teams = max(1, math.ceil(total_team_days / available_days))
        buffered_teams = base_teams * 2

        # --- TOTAL SQ FT ---
        total_sqft = total_walls * wall_size

        # --- COSTING ---
        # Salaries (monthly → daily)
        exec_salary_daily = 25000 / 30
        helper_salary_daily = 15000 / 30

        salary_per_team_per_day = exec_salary_daily + helper_salary_daily

        # Daily costs
        food_cost = 350 * 2
        travel_daily = 500
        stay_cost = 700
        misc_cost = 100

        daily_cost_per_team = (
            salary_per_team_per_day +
            food_cost +
            travel_daily +
            stay_cost +
            misc_cost
        )

        # Total working days approx
        project_days = available_days

        # Total cost
        total_execution_cost = daily_cost_per_team * buffered_teams * project_days

        # Intercity travel cost
        intercity_travel_cost = (num_cities - 1) * 1200 * buffered_teams

        total_cost = total_execution_cost + intercity_travel_cost

        cost_per_sqft = total_cost / total_sqft if total_sqft > 0 else 0

        # --- RESULTS ---
        st.markdown("---")
        st.markdown("## 📊 Results Summary")

        colr1, colr2, colr3 = st.columns(3)
        colr1.metric("Total Walls", total_walls)
        colr2.metric("Available Days", available_days)
        colr3.metric("Teams Required", buffered_teams)

        # --- COST DISPLAY ---
        st.markdown("## 💰 Cost Breakdown")

        st.write(f"Total Project Cost: ₹ {round(total_cost):,}")
        st.write(f"Cost per Sq Ft: ₹ {round(cost_per_sqft, 2)}")

        st.markdown("### Detailed Costs")

        st.write(f"Salary Cost (Total): ₹ {round(salary_per_team_per_day * buffered_teams * project_days):,}")
        st.write(f"Food Cost: ₹ {round(food_cost * buffered_teams * project_days):,}")
        st.write(f"Daily Travel Cost: ₹ {round(travel_daily * buffered_teams * project_days):,}")
        st.write(f"Stay Cost: ₹ {round(stay_cost * buffered_teams * project_days):,}")
        st.write(f"Misc Cost: ₹ {round(misc_cost * buffered_teams * project_days):,}")
        st.write(f"Intercity Travel Cost: ₹ {round(intercity_travel_cost):,}")

        # --- FORECAST ---
        st.markdown("---")
        st.markdown("## 🔮 Bi-Weekly Forecast")

        today = start_date
        cutoff_date = end_date - timedelta(days=7)

        current_date = today

        while current_date <= cutoff_date:

            if current_date.weekday() in [3, 6]:

                days_passed = (current_date - start_date).days

                future_work = current_teams * productivity * days_passed
                work_done = min(total_walls, walls_completed + future_work)

                remaining_walls = max(0, total_walls - work_done)

                remaining_exec_td = remaining_walls / productivity
                remaining_cities = max(0, num_cities - cities_completed)
                remaining_travel_td = max(0, remaining_cities - 1)

                remaining_team_days = remaining_exec_td + remaining_travel_td

                days_left = max(1, (end_date - current_date).days)

                teams_needed = math.ceil(remaining_team_days / days_left)
                teams_needed_buffered = teams_needed * 2

                additional_needed = max(0, teams_needed_buffered - current_teams)

                st.markdown(
                    f"**📅 {current_date.strftime('%b %d, %Y')}** → Additional Teams Needed: **{additional_needed}**"
                )

            current_date += timedelta(days=1)
