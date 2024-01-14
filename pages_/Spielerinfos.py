import pandas as pd
import streamlit as st
import json
import functions as fn
from streamlit import session_state as ss

from unidecode import unidecode
import plotly.graph_objects as go

from datetime import datetime
from babel.dates import format_datetime
import pytz


import mappings as mp

if __name__ == "__main__":
    if "data_ready" not in ss or not ss.logged:
        st.warning("Bitte zuerst anmelden!")
        st.link_button("Zum Login", "https://kickbased.streamlit.app/")

    else:
        st.write(ss.kb_data_merged.head())
        with open("li_update.txt") as li_datenstand:
            for line in li_datenstand:
                line = line.strip()
                # Parse the UTC timestamp into a datetime object
                utc_time = datetime.strptime(line, "%H:%M:%S %A, %B %d, %Y")

                # Define the UTC timezone
                utc_zone = pytz.timezone("UTC")

                # Associate the parsed time with the UTC timezone
                utc_time = utc_zone.localize(utc_time)

                # Define the Switzerland timezone
                zurich_zone = pytz.timezone("Europe/Zurich")

                # Convert the time to Switzerland's timezone
                zurich_time = utc_time.astimezone(zurich_zone)

                # Format the datetime object into a string using Babel
                formatted_time = format_datetime(
                    zurich_time, "HH:mm 'Uhr,' EEEE, dd. MMMM yyyy", locale="de_DE"
                )

                st.write(f"Ligainsider Datenstand: {formatted_time}")

        if "einzel_select" not in ss:
            ss.einzel_select = pd.DataFrame(
                data={"Name": [None], "Value": [None]},
            )
            ss.einzel_select.drop(0, inplace=True)

        if "einzel_index" not in ss:
            ss.einzel_index = None

        tab1, tab2 = st.tabs(["Alle Spieler", "Spielerstats"])

        with tab1:
            if "df_spieler" not in ss:
                position_mapping = mp.position_mapping
                status_mapping = mp.status_mapping

                ss.df_spieler = ss.kb_data_merged.copy()
                ss.df_spieler.sort_values(
                    by=["Marktwert"], inplace=True, ascending=False
                )

                ss.df_spieler["Status"] = ss.df_spieler["Status"].map(status_mapping)

                ss.df_spieler["Position"] = ss.df_spieler["Position"].map(
                    position_mapping
                )
                ss.df_spieler.drop(["TeamCover", "Trend"], axis=1)

                ss.df_spieler["UserID"] = ss.df_spieler["UserID"].map(ss.user_info)
                ss.df_spieler.loc[ss.df_spieler["UserID"].isna(), "UserID"] = "Kickbase"

            search_query = st.text_input("Spielersuche")
            if search_query:
                st.dataframe(
                    fn.SearchPlayer(ss.df_spieler, search_query),
                    column_config={
                        "Bild": None,
                        "Stats": None,
                        "ID": None,
                        "TeamID": None,
                        "TeamCover": None,
                        "Einsatzquote": st.column_config.NumberColumn(
                            "Einsatzquote",
                            min_value=0,
                            max_value=100,
                            format="%2f%%",
                        ),
                    },
                    hide_index=True,
                )
            else:
                st.dataframe(
                    fn.SearchPlayer(ss.df_spieler, search_query),
                    column_config={
                        "Bild": None,
                        "Stats": None,
                        "ID": None,
                        "TeamID": None,
                        "TeamCover": None,
                        "Einsatzquote": st.column_config.NumberColumn(
                            "Einsatzquotes",
                            min_value=0,
                            max_value=100,
                            format="%2f%%",
                        ),
                    },
                    hide_index=True,
                )
        with tab2:
            one_player_search = st.text_input(
                "Namensuche", max_chars=30, key="einzelspieler"
            )
            suggestions = ss.kb_data_merged[
                (
                    ss.kb_data_merged["Name"]
                    .apply(lambda x: unidecode(x))
                    .str.contains(unidecode(str(one_player_search)), case=False)
                )
                | (
                    ss.kb_data_merged["Name"].str.contains(
                        str(one_player_search), case=False
                    )
                )
            ]

            if not suggestions.empty:
                ss.einzel_select = pd.DataFrame(
                    data={"Name": [None], "Value": [None]},
                )
                ss.einzel_select.drop(0, inplace=True)
                selected_suggestion = st.selectbox(
                    "Select a suggestion:", suggestions["Name"].tolist()
                )
                ss.einzel_select = suggestions.loc[
                    suggestions["Name"] == selected_suggestion, :
                ]
                ss.einzel_index = suggestions["ID"].loc[
                    suggestions["Name"] == selected_suggestion
                ]

                fig = (
                    ss.kb_radarcharts["RadarChart"]
                    .loc[ss.kb_radarcharts["ID"] == ss.einzel_index.values[0]]
                    .values
                )
                # fig extrahieren, annehmen, dass es sich im ersten Element des resultierenden Arrays befindet
                fig_string = fig[0]

                # De-serialisieren Sie die Figur
                fig_dict = json.loads(fig_string)
                plotly_fig = go.Figure(fig_dict)

                col1, col2 = st.columns([0.575, 0.425])
                with col1:
                    col1_1, col2_2 = st.columns(2)
                    with col1_1:
                        st.image(
                            ss.kb_data_merged["Bild"]
                            .loc[ss.kb_data_merged["ID"] == ss.einzel_index.values[0]]
                            .values[0],
                            width=190,
                        )
                    with col2_2:
                        player_mw = ss.kb_data_merged.loc[
                            ss.kb_data_merged["ID"] == ss.einzel_index.values[0],
                            "Marktwert",
                        ].values[0]
                        player_mw_yd = ss.kb.get_player_market_value_last_n_days(
                            days=2,
                            league_id=ss.liga.id,
                            player_id=ss.einzel_index.values[0],
                        )[0]

                        delta = player_mw - player_mw_yd
                        player_mw = fn.market_value_formatter(player_mw)

                        delta = f"{int(delta):,} €"
                        st.metric(
                            label="Marktwert",
                            value=player_mw,
                            delta=delta,
                        )
                    player_stats = ss.kb_data_merged.loc[
                        ss.kb_data_merged["ID"] == ss.einzel_index.values[0],
                        "Stats",
                    ].values[0]
                    player_pos = ss.kb_data_merged.loc[
                        ss.kb_data_merged["ID"] == ss.einzel_index.values[0],
                        "Position",
                    ].values[0]
                    einsatz_quote_spieler = ss.kb_data_merged.loc[
                        ss.kb_data_merged["ID"] == ss.einzel_index.values[0],
                        "Einsatzquote",
                    ].values[0]
                    if einsatz_quote_spieler < 10:
                        st.write("Keine Statistiken verfügbar, da zu wenig gespielt")
                    else:
                        if player_pos == "1":
                            stat_cols = mp.stat_cols_gk
                        else:
                            stat_cols = mp.stat_cols
                        fn.display_selected_stats(
                            player_stats, stat_cols, ss.kb_data_merged
                        )
                    player_team = ss.kb_data_merged.loc[
                        ss.kb_data_merged["ID"] == ss.einzel_index.values[0],
                        "TeamID",
                    ].values[0]
                    ngs = ss.kb.get_next_games(team_id=player_team)
                    ngs_name = []

                    for ng in ngs:
                        team_logo_url = str(
                            ss.kb_data_merged.loc[
                                ss.kb_data_merged["TeamID"] == ng[1],
                                "Logo",
                            ].values[0]
                        )
                        # Set the width and height as per your requirements
                        g = f'<img src="{team_logo_url}" width="50" height="50">'
                        g += f" ({ng[0]})"

                        ngs_name.append(g)
                    teams_line = " ".join(
                        ngs_name
                    )  # This joins all team names with a space
                    st.markdown(
                        f"### Nächste Gegner\n{teams_line}", unsafe_allow_html=True
                    )

                # Zeigen Sie die Figur in Streamlit an
                with col2:
                    plotly_fig.update_layout(
                        autosize=False,
                        width=625,  # Set the width to your preference
                        height=400,  # Set the height to your preference
                        margin_l=20,
                        margin_r=180,
                        title="",
                    )
                    st.plotly_chart(plotly_fig, use_container_width=False)
                    pkt_total = ss.kb_data_merged.loc[
                        ss.kb_data_merged["ID"] == ss.einzel_index.values[0],
                        "Punktetotal",
                    ].values[0]

                    st.markdown(
                        f"<h2 style='text-align: left;'>Gesamtpunkte: {pkt_total}</h2>",
                        unsafe_allow_html=True,
                    )

                    owner_id = ss.kb_data_merged.loc[
                        ss.kb_data_merged["ID"] == ss.einzel_index.values[0],
                        "UserID",
                    ].values[0]

                    if owner_id == "None":
                        st.markdown(
                            "<h4 style='text-align: left;'>Besitzer: Kickbase</h4>",
                            unsafe_allow_html=True,
                        )
                    else:
                        owner_name = ss.user_info.get(owner_id)
                        st.markdown(
                            f"<h4 style='text-align: left;'>Besitzer: {owner_name}</h4>",
                            unsafe_allow_html=True,
                        )

                with st.expander("Marktwertentwicklung"):
                    if "mwslider" not in ss:
                        ss.mwslider = 14
                    st.markdown(
                        f"<h1 style='text-align: center; font-size: 30px;'>Marktwert in den letzten {ss.mwslider} Tagen</h1>",
                        unsafe_allow_html=True,
                    )
                    mw_slider = st.slider(
                        "Anzahl Tage", min_value=2, max_value=360, key="mwslider"
                    )
                    st.plotly_chart(fn.mw_trend(mw_slider), use_container_width=True)

            else:
                st.write("Kein Spieler gefunden")
