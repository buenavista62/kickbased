import pandas as pd
import streamlit as st
import json
import functions as fn
from kickbase_singleton import kickbase_singleton
import numpy as np
from unidecode import unidecode
import plotly.graph_objects as go
import ast

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

    def searching_player(df):
        if st.session_state.info_auswahl == "Nur Standard Infos":
            return st.data_editor(
                fn.SearchPlayer(
                    df.loc[
                        :,
                        column_chooser.get(st.session_state.info_auswahl),
                    ],
                    input,
                ),
                column_config={
                    "Auswahl": st.column_config.CheckboxColumn(
                        "Vergleich", default=False
                    ),
                    "Born": st.column_config.NumberColumn("Geburtsjahr", format="%d"),
                },
                hide_index=True,
                disabled=[
                    x
                    for x in (df[column_chooser.get(st.session_state.info_auswahl)])
                    if x != "Auswahl"
                ],
            )

        else:
            return st.data_editor(
                fn.SearchPlayer(
                    df.loc[
                        df["Position"] == st.session_state.info_auswahl,
                        column_chooser.get(st.session_state.info_auswahl),
                    ],
                    input,
                ),
                column_config={
                    "Auswahl": st.column_config.CheckboxColumn(
                        "Vergleich", default=False
                    ),
                    "Born": st.column_config.NumberColumn("Geburtsjahr", format="%d"),
                },
                hide_index=True,
                disabled=[
                    x
                    for x in (df[column_chooser.get(st.session_state.info_auswahl)])
                    if x != "Auswahl"
                ],
            )

    tab1, tab2 = st.tabs(["Alle Spieler", "Spielerstats"])

    with tab1:
        st.session_state.kb_data_merged

    with tab2:
        one_player_search = st.text_input(
            "Namensuche", max_chars=30, key="einzelspieler"
        )
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

            col1, col2 = st.columns(2)
            with col1:
                st.image(
                    st.session_state.kb_data_merged["Bild"]
                    .loc[
                        st.session_state.kb_data_merged["ID"]
                        == st.session_state.einzel_index.values[0]
                    ]
                    .values[0]
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
                    width=650,  # Set the width to your preference
                    height=450,  # Set the height to your preference
                    margin_l=10,
                    margin_r=100,
                    title="",
                )
                st.plotly_chart(plotly_fig, use_container_width=False)
        else:
            st.write("No suggestions found.")
