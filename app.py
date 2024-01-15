import pandas as pd
import streamlit as st
from st_pages import hide_pages, show_pages_from_config
from streamlit import session_state as ss

import functions as fn
from kickbase_singleton import kickbase_singleton


def loadKBPlayer():
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

        df = pd.DataFrame(player_data)
        ss["kb_data_merged"] = df
        return df
    except Exception as e:
        st.error(f"Failed to load player data: {e}")
        return pd.DataFrame()


def logging_process():
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


def load_kickbase_data():
    ss.kb_data = loadKBPlayer()


def data_prep():
    df_li = pd.read_csv("./data/ligainsider_df.csv")
    df_li.ID = df_li.ID.astype("str")
    df_li.drop(columns=(["Name", "Team", "birth_year"]), inplace=True)
    ss.kb_data_merged = fn.mergeKB(df_li, ss.kb_data)

    ss.kb_radarcharts = fn.radarcharts(ss.kb_data_merged)

    team_logos = pd.DataFrame(ss.kb.TeamsInfo())
    team_logos.drop(columns=("Name"), inplace=True)
    ss.kb_data_merged = ss.kb_data_merged.merge(team_logos, on="TeamID", how="left")


def load_matches():
    if "matches" not in ss:
        m = ss.kb.matches()
        matches_df = pd.DataFrame(m)
        ss.matches = pd.DataFrame(
            {
                "Match Time": pd.to_datetime(matches_df["d"]).dt.strftime(
                    "%Y-%m-%d %H:%M"
                ),
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


def main():
    st.title("Kickbased")

    logging_process()

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
                    load_kickbase_data()
                    st.write("Merging data with ligainsider...")
                    data_prep()
                    st.write("Loading matches...")
                    load_matches()
                    st.write("Data is ready")

            if "data_ready" not in ss:
                ss.data_ready = True

            st.toast("Daten sind geladen!")

            if "data_ready" in ss:
                show_pages_from_config()

            logout_button = st.button("Logout")
            if logout_button:
                del ss.logged
                st.rerun()


if __name__ == "__main__":
    main()
