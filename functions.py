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
from rapidfuzz import process, fuzz


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


def get_player_stat_agg(df, stat_cols, exclude_at=10):
    df_filtered = df[df["Einsatzquote"] >= exclude_at]
    # Aggregate player statistics for each stat in stat_cols
    player_stat_agg = {stat: [] for stat in stat_cols}
    for stats_str in df_filtered["Stats"]:
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


def market_value_formatter(market_value):
    market_value = str(market_value)
    market_value = market_value[:-2]
    return f"{int(market_value):,} €"


def get_points_history(df):
    id = []
    name = []
    year_season = []
    points = []

    for player in df:
        for season in player.seasons:
            id.append(player.id)
            name.append(str(player.first_name) + " " + str(player.last_name))
            year_season.append(season["season"])
            if "points" in season:
                points.append(season["points"])
            else:
                points.append(None)

    df_hist = pd.DataFrame(
        {"ID": id, "Name": name, "Season": year_season, "Points": points}
    )
    df_hist.dropna(inplace=True)
    return df_hist


def prepare_pred_page(df_kb_point_hist, df_us_player, df_kb):
    def load_fbref_hist(season):
        temp = pd.read_csv(f"./data/{season}fbref_full.csv")

        return temp

    c = 0
    for i in range(2017, 2024):
        season = str(i) + "-" + str(i + 1)
        temp = load_fbref_hist(season)
        temp["season"] = str(i)
        if c == 0:
            df_fbref_hist = temp
        else:
            df_fbref_hist = pd.concat([df_fbref_hist, temp], axis=0)
        c += 1

    cols_to_drop = list(
        df_fbref_hist.columns[df_fbref_hist.columns.str.endswith("_pct")]
    )
    cols_to_drop = cols_to_drop + list(
        df_fbref_hist.columns[df_fbref_hist.columns.str.endswith("_per90")]
    )
    cols_to_drop = cols_to_drop + ["nationality", "minutes_90s"]

    df_fbref_hist = df_fbref_hist.drop(cols_to_drop, axis=1)
    df_fbref_hist.rename(columns={"player": "Name"}, inplace=True)

    df_fbref_hist.drop_duplicates(subset=["Name", "season", "team"], inplace=True)

    df_li = pd.read_csv("./data/ligainsider_df.csv")
    df_li = df_li.iloc[:, :4]
    # Combine 'Name' and 'birth_year' into a single column for each dataframe
    df_fbref_hist["name_year"] = (
        df_fbref_hist["Name"].astype(str)
        + "_"
        + df_fbref_hist["birth_year"].astype(str)
    )
    df_li["name_year"] = (
        df_li["Name"].astype(str) + "_" + df_li["birth_year"].astype(str)
    )

    def get_best_match(name_year, candidate_list):
        name, year = name_year.split("_")

        # Filter candidates with the exact year match
        filtered_candidates = [c for c in candidate_list if c.endswith("_" + year)]

        # Apply fuzzy matching on the name part
        best_match = process.extractOne(
            name,
            [c.split("_")[0] for c in filtered_candidates],
            scorer=fuzz.token_set_ratio,
            score_cutoff=85,
        )

        # Return the full candidate string if a match is found
        return (
            next(
                (c for c in filtered_candidates if c.startswith(best_match[0] + "_")),
                None,
            )
            if best_match
            else None
        )

    # Create a list of combined name_year from the second dataframe
    name_year_candidates = df_li["name_year"].tolist()

    # Apply fuzzy matching to each row in the first dataframe
    df_fbref_hist["matched_name_year"] = df_fbref_hist["name_year"].apply(
        lambda x: get_best_match(x, name_year_candidates)
    )

    # Merge the dataframes based on the matched name_year
    final_df_lihist = pd.merge(
        df_fbref_hist,
        df_li,
        left_on="matched_name_year",
        right_on="name_year",
        suffixes=("_fbref", "_li"),
    )

    # Optionally, filter out rows without a match
    final_df_lihist = final_df_lihist[final_df_lihist["matched_name_year"].notnull()]
    final_df_lihist = final_df_lihist.drop_duplicates(
        subset=["name_year_fbref", "season", "team"]
    )

    def get_aggregation_method(column):
        if column in [
            "Name_fbref",
            "Name_li",
            "birth_year_fbref",
            "age",
            "matches",
            "season",
            "ID",
            "birth_year_li",
        ]:
            return "first"
        elif column in ["position", "team"]:
            return lambda x: ", ".join(
                x.dropna().astype(str).unique()
            )  # Convert to string and drop NaN
        else:
            return "sum"

    # Create a dictionary of aggregation methods for each column
    aggregation_methods = {
        col: get_aggregation_method(col) for col in final_df_lihist.columns
    }

    final_df_lihist_grouped = final_df_lihist.groupby(
        ["name_year_fbref", "season"], as_index=False
    ).agg(aggregation_methods)
    # Optionally, if you want to remove the 'team' column now
    final_df_lihist_grouped = final_df_lihist_grouped.drop(
        columns=[
            "birth_year_fbref",
            "birth_year_li",
            "name_year_fbref",
            "name_year_li",
            "Name_li",
            "matches",
            "matched_name_year",
        ]
    )
    final_df_lihist_grouped["age"] = (
        final_df_lihist_grouped["age"].astype("str").str.slice(0, 2)
    )
    final_df_lihist_grouped.ID = final_df_lihist_grouped.ID.astype("string")

    final_df_lihist_grouped.drop(columns=["xg", "npxg"], inplace=True)

    final_df_lihist_grouped_gk = final_df_lihist_grouped.loc[
        final_df_lihist_grouped["position"] == "GK"
    ]
    final_df_lihist_grouped_field = final_df_lihist_grouped.loc[
        final_df_lihist_grouped["position"] != "GK"
    ]
    final_df_lihist_grouped_field = final_df_lihist_grouped_field.drop(
        ["position", "games_starts"], axis=1
    )
    final_df_lihist_grouped_gk = final_df_lihist_grouped_gk.drop(
        ["position", "games_starts"], axis=1
    )

    gkcols = list(final_df_lihist_grouped_gk.columns[0:13])
    gkcols = gkcols + list(
        final_df_lihist_grouped_gk.columns[
            final_df_lihist_grouped_gk.columns.str.startswith("gk")
        ]
    )

    gkcols = gkcols + ["season", "ID"]

    final_df_lihist_grouped_gk = final_df_lihist_grouped_gk[
        final_df_lihist_grouped_gk.columns.intersection(gkcols)
    ]

    final_df_lihist_grouped_field = final_df_lihist_grouped_field.loc[
        :, ~final_df_lihist_grouped_field.columns.str.startswith("gk_")
    ]

    df_kb_point_hist["Season"] = df_kb_point_hist["Season"].str[0:4]
    df_kb_point_hist.rename(columns=({"Season": "season"}), inplace=True)

    merged_df_field = final_df_lihist_grouped_field.merge(
        df_kb_point_hist, on=["ID", "season"]
    )
    merged_df_field.drop(columns=["Name_fbref"], inplace=True)

    merged_df_gk = final_df_lihist_grouped_gk.merge(
        df_kb_point_hist, on=["ID", "season"]
    )
    merged_df_gk.drop(columns=["Name_fbref"], inplace=True)
    df_kb_position = df_kb.loc[:, ["ID", "Position"]]

    merged_df_field["minutes"] = merged_df_field.minutes.str.replace(",", "")
    merged_df_gk["minutes"] = merged_df_gk.minutes.str.replace(",", "")
    data_field = merged_df_field.merge(df_kb_position, on=["ID"])
    data_gk = merged_df_gk.merge(df_kb_position, on=["ID"])

    data_field["matching"] = (
        data_field["Name"]
        + "_"
        + data_field["team"]
        + "_"
        + data_field["season"]
        + "_"
        + data_field["games"].astype("str")
    )
    data_gk["matching"] = (
        data_gk["Name"]
        + "_"
        + data_gk["team"]
        + "_"
        + data_gk["season"]
        + "_"
        + data_gk["games"].astype("str")
    )
    df_us_player["matching"] = (
        df_us_player["player_name"]
        + "_"
        + df_us_player["team_title"]
        + "_"
        + df_us_player["season"].astype("str")
        + "_"
        + df_us_player["games"].astype("str")
    )

    def get_best_match_us(matching_string, candidate_list, score_cutoff=80):
        parts = matching_string.split("_")
        fuzzy_part = "_".join(
            parts[:-2]
        )  # All except last two parts for fuzzy matching
        exact_part = "_".join(parts[-2:])  # Last two parts for exact matching

        # Filter candidates with the exact match for season and games
        filtered_candidates = [
            c for c in candidate_list if c.endswith("_" + exact_part)
        ]

        # Apply fuzzy matching on the remaining parts
        best_match = process.extractOne(
            fuzzy_part,
            [c.rsplit("_", 2)[0] for c in filtered_candidates],
            scorer=fuzz.token_set_ratio,
            score_cutoff=score_cutoff,
        )

        # Return the full candidate string if a match is found
        return (
            next(
                (c for c in filtered_candidates if c.startswith(best_match[0] + "_")),
                None,
            )
            if best_match
            else None
        )

    # The rest of your code for creating the 'matching' strings, applying the match function, and merging the dataframes remains the same

    # Step 1: Create a list of combined 'matching' from one of the dataframes
    matching_candidates = df_us_player["matching"].tolist()

    # Step 2: Apply fuzzy matching to each row in the other dataframe
    data_field["matched_matching"] = data_field["matching"].apply(
        lambda x: get_best_match_us(x, matching_candidates)
    )

    # Step 3: Merge the dataframes based on the matched 'matching'
    final_df_field = pd.merge(
        data_field,
        df_us_player,
        left_on="matched_matching",
        right_on="matching",
        suffixes=("_datafield", "_usplayer"),
    )

    # Step 4: Optionally, filter out rows without a match
    final_df_field = final_df_field[final_df_field["matched_matching"].notnull()]
    final_df_field = final_df_field.drop_duplicates(
        subset=["matching_datafield", "team", "season_datafield"]
    )

    # Step 2: Apply fuzzy matching to each row in the other dataframe
    data_gk["matched_matching"] = data_gk["matching"].apply(
        lambda x: get_best_match_us(x, matching_candidates)
    )

    # Step 3: Merge the dataframes based on the matched 'matching'
    final_df_gk = pd.merge(
        data_gk,
        df_us_player,
        left_on="matched_matching",
        right_on="matching",
        suffixes=("_datagk", "_usplayer"),
    )

    # Step 4: Optionally, filter out rows without a match
    final_df_gk = final_df_gk[final_df_gk["matched_matching"].notnull()]
    final_df_gk = final_df_gk.drop_duplicates(
        subset=["matching_usplayer", "team", "season_usplayer"]
    )

    def find_non_numeric_columns(df):
        non_numeric_columns = []
        for column in df.columns:
            print(type(column))
            try:
                pd.to_numeric(df[column])
            except ValueError:
                non_numeric_columns.append(column)
        return non_numeric_columns

    # Usage
    for column in final_df_field.columns:
        # Try converting each column to numeric type
        final_df_field[column] = pd.to_numeric(final_df_field[column], errors="coerce")

    for column in final_df_gk.columns:
        # Try converting each column to numeric type
        final_df_gk[column] = pd.to_numeric(final_df_gk[column], errors="coerce")

    final_df_field["Position"] = final_df_field["Position"].astype("category")
    final_df_gk["Position"] = final_df_gk["Position"].astype("category")
    final_df_field.dropna(axis=1, how="all", inplace=True)
    final_df_gk.dropna(axis=1, how="all", inplace=True)

    # List comprehension to find columns ending with '_usplayer'
    cols_to_drop = [col for col in final_df_field.columns if col.endswith("_usplayer")]

    # Drop these columns from the dataframe
    final_df_field = final_df_field.drop(columns=cols_to_drop)
    # List comprehension to find columns ending with '_usplayer'
    cols_to_drop = [col for col in final_df_gk.columns if col.endswith("_usplayer")]

    # Drop these columns from the dataframe
    final_df_gk = final_df_gk.drop(columns=cols_to_drop)

    final_df_field.columns = final_df_field.columns.str.removesuffix("_datafield")
    final_df_gk.columns = final_df_gk.columns.str.removesuffix("_datagk")

    predict_field = final_df_field.loc[final_df_field["season"] == 2023]

    return predict_field
