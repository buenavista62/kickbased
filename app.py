from typing import Optional

import pandas as pd
import streamlit as st
from st_pages import hide_pages, show_pages_from_config
from streamlit import session_state as ss

import functions as fn
from kickbase_singleton import kickbase_singleton


def loadKBPlayer(liga_id: str) -> Optional[pd.DataFrame]:
    """Fetches and processes all players for a given league ID.

    Args:
        liga_id (str): The ID of the league from which to fetch players.

    Returns:
        Optional[pd.DataFrame]: A DataFrame containing player data, or None if an error occurs.
    """
    if "kb_data_merged" in ss:
        return ss["kb_data_merged"]

    try:
        players = ss.kb.get_all_players(ss.liga.id)
        player_data = [
            {
                "ID": str(player.id),
                "Name": f"{player.first_name} {player.last_name}",
                "Team": player.teamName,
                "Position": str(player.position),
                "Marktwert": player.market_value,
                "Trend": player.market_value_trend,
                "Bild": player.profile_big_path,
                "Status": player.status,
                "Punkteschnitt": player.average_points,
                "Punktetotal": player.totalPoints,
                "UserID": str(player.user_id),
                "TeamID": str(player.team_id),
            }
            for player in players
        ]
        ss.players = players
        df = pd.DataFrame(player_data)
        ss["kb_data_merged"] = df
        return df
    except Exception as e:
        st.error(f"Failed to load player data: {e}")
        return None


def handle_login():
    """Manages the user login process, updating the UI based on the login status."""
    default_pages = ["Spieler", "Mein Verein", "Meine Liga", "Kickbot", "Vorhersagen"]
    if ss.get("logged", False) is False:
        hide_pages(default_pages)
        show_login_form()
    elif ss.logged:
        st.success("Eingeloggt")


def show_login_form():
    """Displays the login form and processes login attempts."""
    with st.form(key="login_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        login_checkbox = st.form_submit_button("Login")

        if login_checkbox and email and password:
            attempt_login(email, password)


def attempt_login(email: str, password: str):
    """Attempts to log the user in with the provided credentials."""
    with st.spinner("Logging in..."):
        logging_in = kickbase_singleton.login(email, password)
        if logging_in:
            st.success("Logged in successfully!")
            ss.logged = True
            show_pages_from_config()  # Assuming this function shows pages relevant post-login
        else:
            st.error("Invalid email or password. Please try again.")
            ss.logged = False


def load_kickbase_data():
    ss.kb_data = loadKBPlayer(ss.liga.id)


def prepare_data():
    """Prepares Kickbase data by merging with additional sources and processing."""
    df_li = load_and_prepare_ligainsider_data()
    merge_with_kickbase_data(df_li)
    process_for_visualization()


def load_and_prepare_ligainsider_data() -> pd.DataFrame:
    """Loads Ligainsider data and prepares it for merging."""
    df_li = pd.read_csv("./data/ligainsider_df.csv")
    df_li.ID = df_li.ID.astype(str)
    df_li.drop(columns=["Name", "Team", "birth_year"], inplace=True)
    return df_li


def merge_with_kickbase_data(df_li: pd.DataFrame):
    """Merges Ligainsider data with Kickbase player data."""
    ss.kb_data_merged = fn.mergeKB(df_li, ss.kb_data)
    ss.kb_radarcharts = fn.radarcharts(ss.kb_data_merged)


def process_for_visualization():
    """Processes data for visualization, adding team logos."""
    team_logos = pd.DataFrame(ss.kb.TeamsInfo())
    team_logos.drop(columns=["Name"], inplace=True)
    ss.kb_data_merged = ss.kb_data_merged.merge(team_logos, on="TeamID", how="left")


def load_and_prepare_matches():
    """Loads match data from Kickbase API and prepares it for presentation."""
    if "matches" not in ss:
        matches = ss.kb.matches()
        ss.matches = format_matches_dataframe(matches)


def format_matches_dataframe(matches: list) -> pd.DataFrame:
    """Formats the list of matches into a structured pandas DataFrame."""
    matches_df = pd.DataFrame(matches)
    formatted_df = pd.DataFrame(
        {
            "Match Time": pd.to_datetime(matches_df["d"]).dt.strftime("%Y-%m-%d %H:%M"),
            "Home Team ID": matches_df["t1i"],
            "Home Team": matches_df["t1n"],
            "Home Team Abbreviation": matches_df["t1y"],
            "Home Team Score": matches_df["t1s"],
            "Away Team ID": matches_df["t2i"],
            "Away Team": matches_df["t2n"],
            "Away Team Abbreviation": matches_df["t2y"],
            "Away Team Score": matches_df["t2s"],
            "Matchday": matches_df["md"],
        }
    )
    return formatted_df


def main():
    st.title("Kickbased")

    # Updated to use the refactored login handling function
    handle_login()

    # Check if user is logged in before proceeding
    if ss.get("logged", False):
        initialize_kickbase_singleton()
        selected_league = select_league()

        if selected_league != "Wähle eine Liga...":
            setup_selected_league(selected_league)
            prepare_and_load_data()
            display_data_ready_message()

            # Provide an option for the user to log out
            if st.button("Logout"):
                perform_logout()
                st.rerun()


def initialize_kickbase_singleton():
    """Ensures the Kickbase API singleton is initialized."""
    if "kb" not in ss:
        ss.kb = kickbase_singleton.kb


def select_league() -> str:
    """Displays a dropdown for league selection and returns the selected league."""
    league_names = ["Wähle eine Liga..."] + [league.name for league in ss.kb.leagues()]
    return st.selectbox("Liga", league_names)


def setup_selected_league(selected_league: str):
    """Sets up the selected league in the session state."""
    if "liga" not in ss:
        league_names = [league.name for league in ss.kb.leagues()]
        ss.liga = ss.kb.leagues()[league_names.index(selected_league) - 1]
    if "user_info" not in ss:
        league_users = ss.kb.league_users(ss.liga)
        ss.user_info = {user.id: user.name for user in league_users}


def prepare_and_load_data():
    """Prepares and loads all necessary data for the application."""
    if "data_ready" not in ss:
        with st.spinner("Data preparation in progress..."):
            if "kb_data" not in ss:
                load_and_prepare_kickbase_data()
            if "matches" not in ss:
                load_and_prepare_matches()
        ss.data_ready = True


def load_and_prepare_kickbase_data():
    """Wrapper function to load Kickbase data and prepare it for use."""
    load_kickbase_data()  # Ensure this function now calls the appropriate data loading functions
    prepare_data()  # Adjusted to call the new data preparation function


def display_data_ready_message():
    """Displays a message indicating that data is ready for use."""
    st.toast("Daten sind geladen!")


def perform_logout():
    """Performs user logout, clearing the session state as needed."""
    if "logged" in ss:
        del ss["logged"]
    # Optionally, clear other session state data related to the user session


if __name__ == "__main__":
    main()
