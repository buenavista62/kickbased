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
import mappings as mp


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
                    f"<h4 style='text-align: center;'>{player['Name']}</h4>",
                    unsafe_allow_html=True,
                )
                st.image(player["Bild"], width=200)  # Adjust width as needed

                player_mw_yd = st.session_state.kb.get_player_market_value_last_n_days(
                    days=2,
                    league_id=st.session_state.liga.id,
                    player_id=player["ID"],
                )[0]

                delta = player["Marktwert"] - player_mw_yd
                player_mw = fn.market_value_formatter(player["Marktwert"])

                delta = f"{int(delta):,} €"
                st.metric(
                    label="Marktwert",
                    value=player_mw,
                    delta=delta,
                )

                st.markdown(f"**Punkteschnitt:** {player['Punkteschnitt']}")
                st.markdown(f"**Punktetotal:** {player['Punktetotal']}")
                ply_position = mp.position_mapping.get(player["Position"], "Unbekannt")
                st.markdown(f"**Position:** {ply_position}")
                ply_status = mp.status_mapping.get(player["Status"], "Unbekannt")
                st.markdown(f"**Status:** {ply_status}")
        st.divider()


if __name__ == "__main__":
    if "data_ready" not in st.session_state or not st.session_state.logged:
        st.warning("Bitte zuerst anmelden!")
    else:
        col1, col2 = st.columns([0.6, 0.4])

        # Custom CSS to vertically center the content in the container and remove margins
        st.markdown(
            """
            <style>
            .vertical-center {
                display: flex;
                align-items: center;
                justify-content: left;
            }
            .no-margin {
                margin: 0;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )

        with col1:
            st.markdown(
                "<div class='vertical-center'><h1>Mein Team</h1></div>",
                unsafe_allow_html=True,
            )

        with col2:
            budget = st.session_state.kb.league_me(st.session_state.liga).budget
            budget = fn.market_value_formatter(budget)
            budget = budget[:-1]
            st.markdown(
                f"<div class='vertical-center no-margin'><h4>Budget: {budget} €</h4></div>",
                unsafe_allow_html=True,
            )
            team_value = st.session_state.kb.league_me(st.session_state.liga).team_value
            team_value = fn.market_value_formatter(team_value)
            team_value = team_value[:-1]
            st.markdown(
                f"<div class='vertical-center no-margin'><h4>Teamwert: {team_value} €</h4></div>",
                unsafe_allow_html=True,
            )

        my_players = st.session_state.kb.league_user_players(
            st.session_state.liga, st.session_state.kb.user
        )
        my_player_ids = [player.id for player in my_players]
        my_pl_df = st.session_state.kb_data_merged.loc[
            st.session_state.kb_data_merged["ID"].isin(my_player_ids), :
        ]
        display_player_data(my_pl_df)
