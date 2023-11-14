import streamlit as st
from kickbase_singleton import kickbase_singleton
import pandas as pd
from mplsoccer import VerticalPitch
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from PIL import Image
import requests
from io import BytesIO
import numpy as np
import functions as fn


def display_player_data(df):
    num_players = len(df)
    for i in range(0, num_players, 3):
        cols = st.columns(3)  # Creating a row of 3 columns
        players_to_display = df.iloc[i : i + 3]  # Select next 3 players

        for idx, (col, (_, player)) in enumerate(
            zip(cols, players_to_display.iterrows())
        ):
            with col:
                st.markdown(
                    f"<h3 style='text-align: center;'>{player['Name']}</h3>",
                    unsafe_allow_html=True,
                )
                st.image(player["Bild"], width=200)  # Adjust width as needed

                ply_mw = fn.market_value_formatter(player["Marktwert"])
                st.markdown(f"**Marktwert:** {ply_mw}")
                st.markdown(f"**Punkteschnitt:** {player['Punkteschnitt']}")
                st.markdown(f"**Punktetotal:** {player['Punktetotal']}")
                st.markdown(f"**Position:** {player['Position']}")
                st.markdown(f"**Status:** {player['Status']}")
        st.divider()


if __name__ == "__main__":
    if "logged" not in st.session_state or not st.session_state.logged:
        st.warning("Bitte zuerst anmelden!")
    else:
        st.title("Mein Team")
        my_players = st.session_state.kb.league_user_players(
            st.session_state.liga, st.session_state.kb.user
        )
        my_player_ids = [player.id for player in my_players]
        my_pl_df = st.session_state.kb_data_merged.loc[
            st.session_state.kb_data_merged["ID"].isin(my_player_ids), :
        ]
        display_player_data(my_pl_df)
