import pandas as pd
import streamlit as st
import json
import functions as fn
from kickbase_singleton import kickbase_singleton
import numpy as np
from unidecode import unidecode
import plotly.graph_objects as go
import ast
import datetime
import plotly.express as px


if "logged" not in st.session_state or not st.session_state.logged:
    st.warning("Bitte zuerst anmelden!")

else:
    if "info_auswahl" not in st.session_state:
        st.session_state.info_auswahl = "Nur Standard Infos"

    if "einzel_select" not in st.session_state:
        st.session_state.einzel_select = pd.DataFrame(
            data={"Name": [None], "Value": [None]},
        )
        st.session_state.einzel_select.drop(0, inplace=True)

    if "einzel_index" not in st.session_state:
        st.session_state.einzel_index = None


tab1, tab2 = st.tabs(["Alle Spieler", "Spielerstats"])

with tab1:
    if "df_spieler" not in st.session_state:
        position_mapping = {
            "1": "Tor",
            "2": "Verteidigung",
            "3": "Mittelfeld",
            "4": "Sturm",
        }
        status_mapping = {
            0: "OK",
            1: "Verletzt",
            2: "Erkrankt",
            4: "Reha",
            8: "Rote Karte",
            16: "Gelb-Rote Karte",
            32: "Fünfte Gelbe Karte",
            64: "Nicht im Team",
            128: "Nicht in der Liga",
            256: "Abwesend",
            9999999999: "Unbekannt",
        }

        st.session_state.df_spieler = st.session_state.kb_data_merged.copy()

        # Assuming 'Status' is the column in your DataFrame you wish to map
        st.session_state.df_spieler["Status"] = st.session_state.df_spieler[
            "Status"
        ].map(status_mapping)

        st.session_state.df_spieler["Position"] = st.session_state.df_spieler[
            "Position"
        ].map(position_mapping)
        st.session_state.df_spieler.drop(["TeamCover", "Trend"], axis=1)

        st.session_state.df_spieler["UserID"] = st.session_state.df_spieler[
            "UserID"
        ].map(st.session_state.user_info)

    search_query = st.text_input("Spielersuche")
    if search_query:
        st.dataframe(
            fn.SearchPlayer(st.session_state.df_spieler, search_query),
            column_config={
                "Bild": None,
                "Stats": None,
                "ID": None,
                "TeamID": None,
                "TeamCover": None,
            },
            hide_index=True,
        )
    else:
        st.dataframe(
            fn.SearchPlayer(st.session_state.df_spieler, search_query),
            column_config={
                "Bild": None,
                "Stats": None,
                "ID": None,
                "TeamID": None,
                "TeamCover": None,
            },
            hide_index=True,
        )
with tab2:
    one_player_search = st.text_input("Namensuche", max_chars=30, key="einzelspieler")
    suggestions = st.session_state.kb_data_merged[
        (
            st.session_state.kb_data_merged["Name"]
            .apply(lambda x: unidecode(x))
            .str.contains(unidecode(str(one_player_search)), case=False)
        )
        | (
            st.session_state.kb_data_merged["Name"].str.contains(
                str(one_player_search), case=False
            )
        )
    ]

    if not suggestions.empty:
        st.session_state.einzel_select = pd.DataFrame(
            data={"Name": [None], "Value": [None]},
        )
        st.session_state.einzel_select.drop(0, inplace=True)
        selected_suggestion = st.selectbox(
            "Select a suggestion:", suggestions["Name"].tolist()
        )
        st.session_state.einzel_select = suggestions.loc[
            suggestions["Name"] == selected_suggestion, :
        ]
        st.session_state.einzel_index = suggestions["ID"].loc[
            suggestions["Name"] == selected_suggestion
        ]

        fig = (
            st.session_state.kb_radarcharts["RadarChart"]
            .loc[
                st.session_state.kb_radarcharts["ID"]
                == st.session_state.einzel_index.values[0]
            ]
            .values
        )
        # fig extrahieren, annehmen, dass es sich im ersten Element des resultierenden Arrays befindet
        fig_string = fig[0]

        # De-serialisieren Sie die Figur
        fig_dict = json.loads(fig_string)
        plotly_fig = go.Figure(fig_dict)

        col1, col2 = st.columns([0.6, 0.4])
        with col1:
            st.image(
                st.session_state.kb_data_merged["Bild"]
                .loc[
                    st.session_state.kb_data_merged["ID"]
                    == st.session_state.einzel_index.values[0]
                ]
                .values[0],
                width=350,
            )
            player_stats = st.session_state.kb_data_merged.loc[
                st.session_state.kb_data_merged["ID"]
                == st.session_state.einzel_index.values[0],
                "Stats",
            ].values[0]
            player_pos = st.session_state.kb_data_merged.loc[
                st.session_state.kb_data_merged["ID"]
                == st.session_state.einzel_index.values[0],
                "Position",
            ].values[0]

            if player_pos == "1":
                stat_cols = ["Paraden", "Weiße Weste", "Fehler vor Schuss/Gegentor"]
            else:
                stat_cols = [
                    "Begangene Fouls",
                    "Geklärte Bälle",
                    "Abgefangene Bälle",
                    "Balleroberungen",
                    "Ballverluste",
                    "Torschussvorlagen",
                    "Kreierte Großchancen",
                    "Schüsse aufs Tor",
                    "Fehler vor Schuss/Gegentor",
                    "Geblockte Bälle",
                ]
            fn.display_selected_stats(
                player_stats, stat_cols, st.session_state.kb_data_merged
            )

        # Zeigen Sie die Figur in Streamlit an
        with col2:
            plotly_fig.update_layout(
                autosize=False,
                width=625,  # Set the width to your preference
                height=400,  # Set the height to your preference
                margin_l=45,
                margin_r=200,
                title="",
            )
            st.plotly_chart(plotly_fig, use_container_width=False)
            pkt_total = st.session_state.kb_data_merged.loc[
                st.session_state.kb_data_merged["ID"]
                == st.session_state.einzel_index.values[0],
                "Punktetotal",
            ].values[0]

            st.markdown(
                f"<h2 style='text-align: left;'>Gesamtpunkte: {pkt_total}</h2>",
                unsafe_allow_html=True,
            )

            owner_id = st.session_state.kb_data_merged.loc[
                st.session_state.kb_data_merged["ID"]
                == st.session_state.einzel_index.values[0],
                "UserID",
            ].values[0]

            if owner_id == "None":
                st.markdown(
                    "<h4 style='text-align: left;'>Besitzer: Kickbase</h4>",
                    unsafe_allow_html=True,
                )
            else:
                owner_name = st.session_state.user_info.get(owner_id)
                st.markdown(
                    f"<h4 style='text-align: left;'>Besitzer: {owner_name}</h4>",
                    unsafe_allow_html=True,
                )
        if "mwslider" not in st.session_state:
            st.session_state.mwslider = 14
        st.markdown(
            f"<h1 style='text-align: center; font-size: 30px;'>Marktwert in den letzten {st.session_state.mwslider} Tagen</h1>",
            unsafe_allow_html=True,
        )
        mw_slider = st.slider("Anzahl Tage", min_value=2, max_value=360, key="mwslider")
        st.plotly_chart(fn.mw_trend(mw_slider))

    else:
        st.write("Kein Spieler gefunden")