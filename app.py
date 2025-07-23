import pandas as pd
import re
import numpy as np
## streamlit
import streamlit as st
## authentication
from utilities.auth_utils import get_app_password
## add logger
from utilities.login_utils import setup_logger
logger = setup_logger(__name__)
##for more info about logger
import io
## gett utilites
from utilities.data_utils import (load_data, 
                                  departure_city,
                                  travel_duration,
                                  get_available_flights,
                                  get_return_flights_to_bom
                                  )
## about the app
logger = setup_logger("Application developed by Euroglobal. For more information, visit https://euroglobal.in/")
logger.info("App started")
## password verification
correct_password = get_app_password()
# Create a Streamlit password input field
st.title("Your journey with EuroGlobal")

# Store login state
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    password_input = st.text_input("Enter app password", type="password")

    if st.button("Login"):
        if password_input == correct_password:
            st.session_state.authenticated = True
            logger.info("User authenticated successfully.")
            st.success("Login successful!")
        else:
            logger.warning("Failed login attempt.")
            st.error("Incorrect password. Try again.")

if st.session_state.authenticated:
    st.write("Welcome to the EuroGlobal journey planner!")
    # Load the data
    file_path=r"data/file_data.xlsx"
    try:
        df = load_data(file_path)
        logger.info("Data loaded successfully.")
    except FileNotFoundError:
        logger.error("Data file not found. Please check the file path.")
        st.error("Data file not found. Please check the file path.")
        df = pd.DataFrame()  # Create an empty DataFrame if the file is not found
    departure_cities = df['Departure'].unique()
    arrival_cities = df['Arrival'].unique()
    all_cities = set(departure_cities) | set(arrival_cities)
    #print("data type of all_cities: ", type(all_cities))
    all_cities = list(all_cities)
    st.write(f"All cities: {all_cities}")  
    selected_date = st.date_input("Please enter your departure date (YYYY-MM-DD)")
    user_departure_date = selected_date.strftime("%Y-%m-%d")
    st.write(f"Date of Departure: {user_departure_date}")
    user_travel_duration = travel_duration()
    st.write(f"Your travel duration is: {user_travel_duration} days")
    user_departure_city = departure_city(all_cities, key="departure")
    st.write(f"Departure from: {user_departure_city}")
    ## possible arrival cities
    if st.button("Show Flights"):
        flights_df, lowest_cost, lowest_arrival = get_available_flights(df, 
                                                                        user_departure_city, 
                                                                        user_departure_date)

        if flights_df.empty:
            st.warning("No flights found for your selection.")
        else:
            st.dataframe(flights_df)
            st.write(f"Lowest cost: ₹{lowest_cost}")
            st.write(f"Arrival city: {lowest_arrival}")
    user_arrival_city = departure_city(all_cities, key="arrival")
    st.write(f"Arrival at: {user_arrival_city}")
    if st.button("Show Return Flights"):
        return_df = get_return_flights_to_bom(df, user_travel_duration, all_cities, user_departure_date)
        if not return_df.empty:
            st.dataframe(return_df)
        else:
            st.warning("No return flights found for given criteria.")
 
