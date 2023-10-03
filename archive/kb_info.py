import streamlit as st
from kickbase_singleton import kickbase_singleton
import pandas as pd


st.write("test kb")
if st.session_state.logged:
    kb = kickbase_singleton.kb
    players = kb.get_all_user_players(st.session_state.liga)
    df = pd.DataFrame(
        {
            "ID": [str(player.id) for player in players],
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
            "UserID": [str(player.user_id) for player in players],
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
    df
