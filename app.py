import streamlit as st
from streamlit import session_state as ss
from kickbase_api.kickbase import Kickbase  # Import the appropriate class
from kickbase_api.exceptions import KickbaseLoginException
import pandas as pd
from kickbase_singleton import kickbase_singleton
import functions as fn
from st_pages import hide_pages, show_pages_from_config


def loadKBPlayer():
    # kb = kickbase_singleton.kb
    try:
        if "kb_data_merged" not in st.session_state:
            players = st.session_state.kb.get_all_players(st.session_state.liga.id)
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
                }
            )
            st.session_state.players = players
    except:
        pass

    return df


def main():
    st.title("Kickbased")

    if "logged" not in ss:
        ss.logged = False
        hide_pages(["Spieler", "Mein Verein", "Meine Liga", "Kickbot", "Vorhersagen"])

    elif ss.logged == True:
        st.success("eingeloggt")

    if ss.logged == False:
        st.warning("Logge dich bei Kickbase ein")
        with st.form(key="login_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            login_checkbox = st.form_submit_button("Login")

            if login_checkbox and email and password:
                with st.spinner("Logging in..."):
                    logging = kickbase_singleton.login(email, password)
                    if logging:
                        st.success("Logged in successfully!")
                        ss.logged = True
                    else:
                        st.error("Invalid email or password. Please try again.")
                        ss.logged = False

    if ss.logged == True:
        if "kb" not in ss:
            ss.kb = kickbase_singleton.kb
        league_names = ["Wähle eine Liga..."] + [
            ss.kb.leagues()[i].name for i in range(len(ss.kb.leagues()))
        ]
        selected_league = st.selectbox("Liga", league_names)
        if selected_league != "Wähle eine Liga...":
            if "liga" not in ss:
                ss.liga = ss.kb.leagues()[league_names.index(selected_league) - 1]
            if "user_info" not in ss:
                keys = [x.id for x in ss.kb.league_users(ss.liga)]
                values = [x.name for x in ss.kb.league_users(ss.liga)]
                ss.user_info = dict(zip(keys, values))

            if "kb_data" not in ss:
                with st.status("Data preperation"):
                    st.write("Downloading Kickbase data...")
                    ss.kb_data = loadKBPlayer()
                    st.write("Merging data with ligainsider...")
                    df_li = pd.read_csv("./data/ligainsider_df.csv")
                    df_li.ID = df_li.ID.astype("str")
                    df_li.drop(columns=(["Name", "Team", "birth_year"]), inplace=True)
                    ss.kb_data_merged = fn.mergeKB(df_li, ss.kb_data)

                    ss.kb_radarcharts = fn.radarcharts(ss.kb_data_merged)

                    team_logos = pd.DataFrame(ss.kb.TeamsInfo())
                    team_logos.drop(columns=("Name"), inplace=True)
                    ss.kb_data_merged = ss.kb_data_merged.merge(
                        team_logos, on="TeamID", how="left"
                    )

                    if "matches" not in ss:
                        m = ss.kb.matches()
                        matches_df = pd.DataFrame(m)
                        ss.matches = pd.DataFrame(
                            {
                                "Match Time": pd.to_datetime(
                                    matches_df["d"]
                                ).dt.strftime("%Y-%m-%d %H:%M"),
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
                    st.write("Data is ready")
                    st.toast("Daten sind geladen!")
                    if "data_ready" not in ss:
                        ss.data_ready = True

                    if "data_ready" in ss:
                        show_pages_from_config()

            logout_button = st.button("Logout")
            if logout_button:
                del ss.logged
                st.rerun()


if __name__ == "__main__":
    main()
