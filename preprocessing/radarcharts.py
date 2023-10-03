import pandas as pd
import plotly.graph_objects as go
from sklearn.preprocessing import MinMaxScaler


def radarcharts(df):
    # df = pd.read_csv("./data/full_df.csv")

    subset_columns = {
        "Torhüter": [
            "gk_pens_allowed",
            "gk_psxg_net",
            "gk_psnpxg_per_shot_on_target_against",
            "gk_pct_passes_launched",
            "gk_crosses_stopped_pct",
        ],
        "Abwehrspieler": [
            "challenge_tackles_pct",
            "blocked_shots",
            "clearances",
            "interceptions",
        ],
        "Mittelfeldspieler": ["passes_pct", "xg_assist", "take_ons_tackled_pct"],
        "Stürmer": ["shots_on_target_pct", "goals_per_shot", "npxg"],
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
        # Separate numerical and string/object columns
        numerical_cols = df.select_dtypes(include=["number"]).columns.tolist()
        string_cols = df.select_dtypes(include=["object"]).columns.tolist()

        # Normalize numerical columns using Min-Max scaling
        scaler = MinMaxScaler()
        normalized_df = df.copy()
        normalized_df[numerical_cols] = scaler.fit_transform(df[numerical_cols])

        for index, row in normalized_df.iterrows():
            position = row["Position"]
            if position in subset_columns:
                # Filter the subset of columns based on the player's position
                columns_to_include = subset_columns[position]
                position_df = row[columns_to_include]
                # Normalize the subset DataFrame
                # min_values = position_df.min()
                # max_values = position_df.max()

                # if min_values != max_values:
                #   normalized_df = (position_df - min_values) / (
                #      max_values - min_values
                # )
                # else:
                # Handle the case where min_values and max_values are equal (division by zero)
                #   normalized_df = position_df.apply(lambda x: 0.0)

                # Radar chart
                categories = position_df.index
                fig = go.Figure()

                fig.add_trace(
                    go.Scatterpolar(
                        r=position_df.values,
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

                radar_charts.append(fig)

        df["RadarChart"] = radar_charts
        return df

    df_new = add_normalized_radar_chart_to_dataframe(df, subset_columns)
    # df_new.to_csv("./data/full_df.csv", index=False)

    return df_new
