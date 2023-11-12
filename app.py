import streamlit as st
from kickbase_api.kickbase import Kickbase  # Import the appropriate class
from kickbase_api.exceptions import KickbaseLoginException
import pandas as pd
from kickbase_singleton import kickbase_singleton
import functions as fn


@st.cache_data
def loadKBPlayer():
    kb = kickbase_singleton.kb
    try:
        players = kb.get_all_players(st.session_state.liga.id)
        df = pd.DataFrame(
            {
                "ID": [str(player.id) for player in players],
                "Name": [
                    str(player.first_name) + " " + str(player.last_name)
                    for player in players
                ],
                "Team": [player.teamName for player in players],
                "Position": [str(player.position) for player in players],
                "Marktwert": [player.market_value for player in players],
                "Trend": [player.market_value_trend for player in players],
                "Bild": [player.profile_big_path for player in players],
                "Status": [player.status for player in players],
                "Punkteschnitt": [player.average_points for player in players],
                "Punktetotal": [player.totalPoints for player in players],
                "UserID": [str(player.user_id) for player in players],
                "TeamID": [str(player.team_id) for player in players],
                "TeamCover": [str(player.team_cover_path) for player in players],
            }
        )
    except:
        pass

    return df


def main():
    st.title("Kickbased")

    if "logged" not in st.session_state:
        st.session_state.logged = False
        # Use kickbase_singleton.kb, kickbase_singleton.user, kickbase_singleton.leagues
    elif st.session_state.logged == True:
        st.write("Logged in")

    if st.session_state.logged == False:
        st.write("Please log in")
        with st.form(key="login_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            login_checkbox = st.form_submit_button("Login")

            if login_checkbox and email and password:
                with st.spinner("Logging in..."):
                    logging = kickbase_singleton.login(email, password)
                    if logging:
                        st.success("Logged in successfully!")
                        st.session_state.logged = True
                    else:
                        st.error("Invalid email or password. Please try again.")
                        st.session_state.logged = False

    if st.session_state.logged == True:
        if "kb" not in st.session_state:
            st.session_state.kb = kickbase_singleton.kb
        league_names = [
            st.session_state.kb.leagues()[i].name
            for i in range(len(st.session_state.kb.leagues()))
        ]
        selected_league = st.selectbox("Wähle eine Liga", league_names)
        if "liga" not in st.session_state:
            st.session_state.liga = st.session_state.kb.leagues()[
                league_names.index(selected_league)
            ]
        if "user_info" not in st.session_state:
            keys = [
                x.id for x in st.session_state.kb.league_users(st.session_state.liga)
            ]
            values = [
                x.name for x in st.session_state.kb.league_users(st.session_state.liga)
            ]
            st.session_state.user_info = dict(zip(keys, values))

        logout_button = st.button("Logout")
        if logout_button:
            del st.session_state.logged
            st.rerun()

        if "kb_data" not in st.session_state:
            with st.status("Data preperation"):
                st.write("Downloading Kickbase data...")
                st.session_state.kb_data = loadKBPlayer()
                st.write("Merging data with ligainsider...")
                df_li = pd.read_csv("./data/ligainsider_df.csv")
                df_li.ID = df_li.ID.astype("str")
                st.session_state.kb_data_merged = fn.mergeKB(
                    df_li, st.session_state.kb_data
                )
                st.session_state.kb_radarcharts = fn.radarcharts(
                    st.session_state.kb_data_merged
                )
                st.write("Data is ready")


if __name__ == "__main__":
    main()
