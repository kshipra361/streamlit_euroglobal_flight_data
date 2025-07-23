import pandas as pd
import re
import numpy as np
import streamlit as st
## add logger
from utilities.login_utils import setup_logger
logger = setup_logger(__name__)
##load all data and return a dataframe
def load_data(file_path):
    """
    Load data from a CSV file and return a DataFrame.
    
    Args:
        file_path (str): The path to the CSV file.
        
    Returns:
        pd.DataFrame: DataFrame containing the loaded data.
    """
    try:
        df = pd.read_excel(file_path)
        ## change the data types
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df['Cost'] = df['Cost'].replace('[^0-9.]', '', regex=True).astype(float)
        #logger.info(f"columns of df:   {df.columns}")
        #logger.info(f"df.info  {df.info()}")
        return df
    except Exception as e:
        logger.info(f"Error loading data: {e}")
        return None
##  departure city
def departure_city(all_cities, key):
    """Displays a dropdown of available cities for the user to choose the departure or arrival city."""
    st.subheader(f"Select {key.capitalize()} City")
    departure_city = st.selectbox(f"Choose your {key.capitalize()} city:", all_cities, key=key)
    if not departure_city:
        st.error(f"Please select a valid {key} city.")
        return None
    return departure_city

##date input 
def date_input():
    date_input=input("Please enter your departure date (YYYY-MM-DD): ").strip( )
    return date_input
## duration input 
def travel_duration():
    input_duration = st.number_input(
        "Enter the travel duration in days:",
        min_value=1,
        max_value=365,
        value=7,  # default value
        step=1
    )
    return int(input_duration)
## available flights
def get_available_flights(df, user_departure_city, user_departure_date):
    """
    Get all available flights on a specific date from a start city.
    
    Args:
        df (DataFrame): Flights data.
        user_departure_city (str): Departure city (uppercase).
        user_departure_date (str): Date string in YYYY-MM-DD format.
        
    Returns:
        DataFrame: Filtered flights.
        float: Lowest cost.
        str: Lowest arrival city.
    """
    logger.info(f"user_departure_city: {user_departure_city}")
    logger.info(f"user_departure_date: {user_departure_date}")

    try:
        date_obj = pd.to_datetime(user_departure_date, format="%Y-%m-%d")
    except ValueError:
        logger.info("Invalid date format. Use YYYY-MM-DD.")
        return pd.DataFrame(), None, None  # Return empty if invalid

    filtered_df = df[
        (df['Departure'].str.upper() == user_departure_city) & 
        (df['Date'] == date_obj)
    ].copy()

    if filtered_df.empty:
        return pd.DataFrame(), None, None

    filtered_df = filtered_df.sort_values(by='Cost', ascending=True).reset_index(drop=True)
    lowest_cost = filtered_df.iloc[0]['Cost']
    lowest_arrival_city = filtered_df.iloc[0]['Arrival']

    return filtered_df, lowest_cost, lowest_arrival_city

## choice of arrival city
def get_arrival_city_or_default(all_cities):
    
    """Ask user to input arrival city, or use the one with lowest cost if not given."""
    logger.info("Available cities: ", all_cities)
    #print("Lowest cost city: ", lowest_arrival_city)
    user_input = input("Enter your arrival city (or press Enter to use the lowest cost city): ").strip().upper()
    return user_input 
## return flights to BOM
def get_return_flights_to_bom(df, user_travel_duration, all_cities, user_departure_date):
    """
    Returns a DataFrame of return flights to BOM after `user_travel_duration` days
    from any city in `all_cities`.

    Args:
        df (pd.DataFrame): Flights data.
        user_travel_duration (int): Travel duration in days.
        all_cities (list): List of city strings.
        user_departure_date (str): Departure date in YYYY-MM-DD format.

    Returns:
        pd.DataFrame: Filtered return flights.
    """
    try:
        departure_date_obj = pd.to_datetime(user_departure_date)
    except Exception as e:
        logger.error(f"Invalid departure date format: {user_departure_date}")
        return pd.DataFrame()

    return_date = departure_date_obj + pd.to_timedelta(user_travel_duration, unit='D')

    return_df = df[
        (df['Departure'].str.upper().isin([city.upper() for city in all_cities])) &
        (df['Arrival'].str.upper() == "BOM") &
        (df['Date'] == return_date)
    ].copy()

    return_df.sort_values(by="Cost", inplace=True)
    return_df.reset_index(drop=True, inplace=True)

    return return_df


## final output 
# def departure_arrival_combination_based_on_user_input_date(df, all_cities, user_departure_date):
#     """ For this function we will take inputs from user and user  the above two dfs"""
#     #user_departure_city=departure_city(all_cities)   
#    # user_departure_date = date_input()
#     user_travel_duration = travel_duration()
#     all_possible_routes_df, lowest_cost, lowest_arrival_city=get_available_flights(df, all_cities)
#     logger.info("Available flights based on user input:")
#     logger.info(all_possible_routes_df)
#     logger.info("Lowest cost flight: ", lowest_cost)
#     logger.info("Lowest arrival city: ", lowest_arrival_city)
    

#     # Get available flights based on user input
#     available_flights_df, lowest_cost, lowest_arrival_city = get_available_flights(df, all_cities)

#     # Get return flights to BOM
#     return_flights_df = get_return_flights_to_bom(df, user_travel_duration, all_cities, user_departure_date)

#     return available_flights_df, return_flights_df, lowest_cost, lowest_arrival_city    
def departure_arrival_combination_based_on_user_input_date(df, all_cities, user_departure_date, user_travel_duration):
    """Streamlit-compatible version of the travel planning logic"""

    # Get travel duration from Streamlit input
    #user_travel_duration = travel_duration()

    # Get available flights
    all_possible_routes_df, lowest_cost, lowest_arrival_city = get_available_flights(df, all_cities)

    st.write("### Available Flights Based on Your Input:")
    st.dataframe(all_possible_routes_df)

    st.write(f"**Lowest cost flight:** ₹{lowest_cost}")
    st.write(f"**Lowest arrival city:** {lowest_arrival_city}")

    # Get return flights to BOM
    return_flights_df = get_return_flights_to_bom(
        df, user_travel_duration, all_cities, user_departure_date
    )

    st.write("### Return Flights to BOM:")
    st.dataframe(return_flights_df)

    return all_possible_routes_df, return_flights_df, lowest_cost, lowest_arrival_city


