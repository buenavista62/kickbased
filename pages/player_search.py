import pandas as pd
import streamlit as st
import json
import functions as fn
from kickbase_singleton import kickbase_singleton
import numpy as np
from unidecode import unidecode
import plotly.graph_objects as go
import preprocessing.radarcharts as rc

if "info_auswahl" not in st.session_state:
    st.session_state.info_auswahl = "Nur Standard Infos"

if "comparing_df" not in st.session_state:
    st.session_state.comparing_df = pd.DataFrame(
        data={"Name": [None], "Value": [None]},
    )
    st.session_state.comparing_df.drop(0, inplace=True)

if "einzel_select" not in st.session_state:
    st.session_state.einzel_select = pd.DataFrame(
        data={"Name": [None], "Value": [None]},
    )
    st.session_state.einzel_select.drop(0, inplace=True)


def searching_player():
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
                "Auswahl": st.column_config.CheckboxColumn("Vergleich", default=False),
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
                "Auswahl": st.column_config.CheckboxColumn("Vergleich", default=False),
                "Born": st.column_config.NumberColumn("Geburtsjahr", format="%d"),
            },
            hide_index=True,
            disabled=[
                x
                for x in (df[column_chooser.get(st.session_state.info_auswahl)])
                if x != "Auswahl"
            ],
        )


def addToCompare(edit_df):
    st.session_state.comparing_df = st.session_state.comparing_df.merge(
        edit_df.loc[edit_df["Auswahl"] == True, ["Name", "Value"]],
        on=["Name", "Value"],
        how="outer",
    )
    outer = st.session_state.comparing_df.merge(
        edit_df.loc[edit_df["Auswahl"] == False, ["Name", "Value"]],
        how="outer",
        indicator=True,
    )
    st.session_state.comparing_df = outer[(outer._merge == "left_only")].drop(
        "_merge", axis=1
    )


""" @st.cache_data
def load_data(path="data/full_df.csv"):
    df = pd.read_csv(path)
    cb = [False for x in df.iloc[:, 0]]
    if "Auswahl" not in df.columns:
        df.insert(0, "Auswahl", cb)

    df = rc.radarcharts(df)
    return df
 """


def load_data():
    df = st.session_state.kb_data_merged
    cb = [False for x in df.iloc[:, 0]]
    if "Auswahl" not in df.columns:
        df.insert(0, "Auswahl", cb)

    df = rc.radarcharts(df)
    return df


df = load_data()

# df["Punkteschnitt"] = df["Punkteschnitt"].str.replace(",", ".")
# df["Punkteschnitt"] = df["Punkteschnitt"].astype(float)

standard_columns = [
    "Auswahl",
    "Name",
    "Position",
    "Value",
    "Squad",
    "Zustand",
    "Einsätze",
    "Punkteschnitt",
    "Punktetotal",
]
gk_columns = list(df.columns[df.columns.str.startswith("gk")].values)
def_columns = [
    "challenges",
    "challenge_tackles_pct",
    "blocks",
    "blocked_shots",
    "interceptions",
    "clearances",
    "errors",
]
mid_columns = [
    "take_ons_won_pct",
    "take_ons_tackled_pct",
    "carries_distance",
    "carries_progressive_distance",
    "progressive_carries",
    "carries_into_final_third",
    "carries_into_penalty_area",
    "miscontrols",
    "dispossessed",
    "passes_received",
    "progressive_passes_received",
    "passes_pct",
    "passes_pct_short",
    "passes_pct_medium",
    "passes_pct_long",
    "assists",
    "xg_assist",
    "xg_assist_net",
]
att_columns = [
    "goals",
    "shots_on_target_pct",
    "shots_per90",
    "shots_on_target_per90",
    "goals_per_shot",
    "xg",
    "npxg",
    "npxg_per_shot",
    "xg_net",
    "npxg_net",
]

column_chooser = {
    "Nur Standard Infos": standard_columns,
    "Abwehrspieler": standard_columns + def_columns,
    "Mittelfeldspieler": standard_columns + mid_columns,
    "Stürmer": standard_columns + att_columns,
    "Torhüter": standard_columns + gk_columns,
}


tab1, tab2 = st.tabs(["Einzelspieler", "Spielervergleich"])

with tab1:
    one_player_search = st.text_input("Namensuche", max_chars=30, key="einzelspieler")
    suggestions = df[
        (
            df["Name"]
            .apply(lambda x: unidecode(x))
            .str.contains(unidecode(str(one_player_search)), case=False)
        )
        | (df["Name"].str.contains(str(one_player_search), case=False))
    ]

    if not suggestions.empty:
        st.session_state.einzel_select = pd.DataFrame(
            data={"Name": [None], "Value": [None]},
        )
        st.session_state.einzel_select.drop(0, inplace=True)
        selected_suggestion = st.selectbox(
            "Select a suggestion:", suggestions["Name"].tolist()
        )
        st.write("You selected:", selected_suggestion)
        st.session_state.einzel_select = suggestions.loc[
            suggestions["Name"] == selected_suggestion, :
        ]

        fig = st.session_state.einzel_select.iloc[0, -1]
        fig
    else:
        st.write("No suggestions found.")


with tab2:
    with st.container():
        col1, col2 = st.columns(2)

        with col1:
            input = st.text_input("Namensuche", max_chars=30, key="spielervergleich")

        with col2:
            info_auswahl = st.selectbox(
                "Zeige Informationen für",
                index=0,
                options=(
                    "Nur Standard Infos",
                    "Abwehrspieler",
                    "Mittelfeldspieler",
                    "Stürmer",
                    "Torhüter",
                ),
                key="info_auswahl",
            )

        edit_df = searching_player()

        st.button("Hinzufügen/Entfernen", on_click=addToCompare, args=(edit_df,))

    st.header("VERGLEICH")

    col3, col4 = st.columns([4, 1])
    with col3:
        st.data_editor(st.session_state.comparing_df, num_rows="dynamic")

    with col4:
        rc = st.button("Radar Chart")
