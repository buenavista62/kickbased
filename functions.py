from unidecode import unidecode

import pandas as pd
import plotly.graph_objects as go
from sklearn.preprocessing import MinMaxScaler
import ast
import json
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import datetime
import plotly.express as px


def SearchPlayer(df, search):
    return df.loc[
        (
            df["Name"]
            .apply(lambda x: unidecode(x))
            .str.contains(unidecode(str(search)), case=False)
        )
        | (df["Name"].str.contains(str(search), case=False))
    ]


def mergeKB(df_li, df_kb):
    df = df_li.merge(df_kb, how="inner", on=["ID"])
    return df


import streamlit as st
import pandas as pd
import numpy as np
import ast


def get_player_stat_agg(df, stat_cols):
    # Aggregate player statistics for each stat in stat_cols
    player_stat_agg = {stat: [] for stat in stat_cols}
    for stats_str in df["Stats"]:
        stats_dict = ast.literal_eval(stats_str)
        for stat in stat_cols:
            if stat in stats_dict:
                # Convert values to floats after stripping '%' and replacing ',' with '.'
                value = float(stats_dict[stat].strip("%").replace(",", "."))
                player_stat_agg[stat].append(value)
    return player_stat_agg


def calculate_percentiles(player_stats, player_stat_agg):
    # Calculate percentiles for the player
    percentiles = {}
    for stat, values in player_stat_agg.items():
        player_value = float(player_stats.get(stat, "0").strip("%").replace(",", "."))
        if values:  # Ensure there are values in the population
            percentile = (
                sum(value < player_value for value in values) / len(values) * 100
            )
            percentiles[stat] = percentile
        else:
            percentiles[stat] = 0  # Use 0 if no values in the population
    return percentiles


def display_selected_stats(player_stats_str, stat_cols, df):
    player_stats = ast.literal_eval(player_stats_str)
    player_stat_agg = get_player_stat_agg(df, stat_cols)
    percentiles = calculate_percentiles(player_stats, player_stat_agg)

    # Create DataFrame for display
    data_for_display = [
        {"Stat": stat, "Value": player_stats[stat], "Percentile": percentiles[stat]}
        for stat in stat_cols
    ]
    display_df = pd.DataFrame(data_for_display)
    display_df["Percentile"] = display_df["Percentile"].astype(
        float
    )  # Ensure percentile is float

    # Find the maximum value for the percentile that is greater than 0
    max_percentile_value = max(display_df["Percentile"].max(), 1)

    # Define column configurations for st.data_editor
    column_config = {
        "Percentile": st.column_config.ProgressColumn(
            label="Percentile",
            format="%.2f%%",  # Assuming the percentiles are expressed as floats
            min_value=0,
            max_value=max_percentile_value,  # Ensure a non-zero max value
        ),
    }

    # Display the DataFrame using st.data_editor
    st.dataframe(
        data=display_df,
        column_config=column_config,
        hide_index=True,
    )


def radarcharts(df):
    # df = pd.read_csv("./data/full_df.csv")

    subset_columns = {
        "1": [
            "Abgewehrte Schüsse",
            "Strafraum-beherrschung",
            "Abgewehrte Elfmeter",
            "Großchancen vereitelt",
        ],
        "2": [
            "Passquote",
            "Zweikampfquote",
            "Luftkämpfe",
            "Tacklingquote",
            "Erfolgreiche Dribblings",
            "Schussgenauigkeit",
        ],
        "3": [
            "Passquote",
            "Zweikampfquote",
            "Luftkämpfe",
            "Tacklingquote",
            "Erfolgreiche Dribblings",
            "Schussgenauigkeit",
        ],
        "4": [
            "Passquote",
            "Zweikampfquote",
            "Luftkämpfe",
            "Tacklingquote",
            "Erfolgreiche Dribblings",
            "Schussgenauigkeit",
        ],
    }

    def add_normalized_radar_chart_to_dataframe(df, subset_columns):
        """
        Add a normalized radar chart for each player's position as a new column in the DataFrame.

        Args:
            df (pd.DataFrame): The DataFrame containing the data.
            subset_columns (dict): A dictionary where keys are positions (e.g., "Torhüter", "Abwehrspieler", "Mittelfeldspieler", "Stürmer")
                and values are lists of column names to include in the subset for each position.

        Returns:
            pd.DataFrame: The DataFrame with added columns containing Plotly figure objects.
        """
        radar_charts = []

        for index, row in df.iterrows():
            d = row["Stats"]
            d_dict = ast.literal_eval(d)
            for key, value in list(
                d_dict.items()
            ):  # Verwenden von list(), um während der Iteration Änderungen vorzunehmen
                if isinstance(value, str):  # Überprüfen, ob der Wert ein String ist
                    if "%" in value:
                        d_dict[key] = float(value.replace("%", "").replace(",", "."))
                    elif "," in value:
                        d_dict[key] = float(value.replace(",", "."))
                    else:
                        d_dict[key] = int(value)

            position = row["Position"]
            if position in subset_columns:
                # Filter the subset of columns based on the player's position
                columns_to_include = subset_columns[position]

                position_df = {
                    key: d_dict[key] for key in columns_to_include if key in d_dict
                }

                # Radar chart
                categories = list(position_df.keys())
                fig = go.Figure()

                fig.add_trace(
                    go.Scatterpolar(
                        r=list(position_df.values()),
                        theta=categories,
                        fill="toself",
                        name=row["Name"],
                    )
                )

                fig.update_layout(
                    polar=dict(
                        radialaxis=dict(visible=True),
                    ),
                    showlegend=False,
                    title=f'Radar Chart for {row["Name"]} ({position})',
                )
                figure_string = json.dumps(fig.to_dict())
                radar_charts.append(figure_string)
        df_rc = df["ID"]
        df_rc = df_rc.to_frame()
        df_rc["RadarChart"] = radar_charts
        return df_rc

    df_new = add_normalized_radar_chart_to_dataframe(df, subset_columns)
    # df_new.to_csv("./data/full_df.csv", index=False)

    return df_new


def mw_trend(mwslider):
    today = datetime.date.today()
    # Generate a list of the last 14 days
    last_n_days = [today - datetime.timedelta(days=x) for x in range(mwslider)]
    market_value = st.session_state.kb.get_player_market_value_last_n_days(
        player_id=st.session_state.einzel_index.values[0],
        league_id=st.session_state.kb.leagues()[0].id,
        days=mwslider,
    )
    market_value.reverse()
    mw_data = pd.DataFrame(
        {
            "Day": last_n_days,
            "Market Value": market_value,  # Your market values here
        }
    )

    fig = px.line(
        mw_data,
        x="Day",
        y="Market Value",
    )
    return fig


""" def mergeKB(df_full, df_kb):
    df_kb.drop(
        ["ID", "Position", "Status", "Punkteschnitt", "Trend", "Bild"],
        axis=1,
        inplace=True,
    )
    df_kb["Name_uni"] = df_kb["Name"].apply(lambda x: unidecode(x))
    df_full["Marktwert"] = df_full["Value"].str.replace(".", "")
    df_full["Marktwert"] = df_full["Marktwert"].astype("float64")
    df_full["Name_uni"] = df_full["Name"].apply(lambda x: unidecode(x))
    df = df_full.merge(df_kb, how="inner", on=["Name_uni", "Marktwert"])
    df = df.loc[:, ~df.columns.str.endswith("_y")]
    df.columns = df.columns.str.removesuffix("_x")
    df.drop(["Name_uni", "Marktwert"], axis=1, inplace=True)

    return df
 """
