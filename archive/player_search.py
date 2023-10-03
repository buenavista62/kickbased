import streamlit as st
from kickbase_singleton import kickbase_singleton
import pandas as pd

if "added" not in st.session_state:
    st.session_state.added = False

if "addcounter" not in st.session_state:
    st.session_state.addcounter = 0


def adding():
    st.session_state.added = True
    st.session_state.addcounter += 1


if "created" not in st.session_state:
    st.session_state.created = False


@st.cache_data
def init_df():
    df_compare = pd.Series(dtype=str)
    st.session_state.created = True
    return df_compare


st.write(st.session_state.created)
# Player search
if st.session_state.logged:
    df_compare = init_df()
    kb = kickbase_singleton.kb
    user = kickbase_singleton.user
    leagues = kickbase_singleton.leagues

    player_search = st.text_input("Search Player")
    search_button = st.button("Search")
    if search_button:
        col1, col2 = st.columns(2)
        players = kb.search_player(player_search)
        st.subheader("Search Results")
        df = pd.DataFrame(
            {
                "Name": [
                    str(player.first_name) + " " + str(player.last_name)
                    for player in players
                ],
                "Postion": [str(player.position) for player in players],
                "Marktwert": [player.market_value for player in players],
                "Trend": [player.market_value_trend for player in players],
                "Bild": [player.profile_big_path for player in players],
                "Status": [player.status for player in players],
                "Punkteschnitt": [player.average_points for player in players],
            }
        )
        df["Status"] = df["Status"].replace(
            {
                0: "OK",
                1: "Verletzt",
                2: "Angeschlagen",
                4: "Reha",
                8: "Rote Karte",
                16: "Gelb-Rote Karte",
                32: "Fünfte Gelbe Karte",
                64: "Nicht im Team",
                128: "Nicht in Liga",
                256: "Abwesend",
                9999999999: "Unbekannt",
            }
        )
        df["Auswahl"] = False
        df_edited = st.data_editor(
            df,
            column_config={
                "Bild": st.column_config.ImageColumn(),
                "Auswahl": st.column_config.CheckboxColumn(default=False),
            },
            hide_index=True,
            use_container_width=True,
            num_rows="fixed",
            disabled=df.columns[0:-1],
            key="data_editor",
        )

        add = st.button("Ausgewählte Spieler hinzufügen", on_click=adding)
        if add:
            df_compare = pd.concat(
                [
                    df_compare,
                    df_edited["Name"].loc[df_edited["Auswahl"] == True],
                ],
                ignore_index=True,
            )
st.dataframe(df_compare)
