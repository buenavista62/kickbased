from understatapi import UnderstatClient
import pandas as pd

from datetime import datetime, timedelta

us = UnderstatClient()


def get_team_info(
    season: str, understat_client=us, league="Bundesliga"
) -> pd.DataFrame:
    data = us.league(league).get_team_data(season)
    rows = []
    for team_id, team_data in data.items():
        for match in team_data["history"]:
            row = match.copy()
            row["team_id"] = team_id
            row["team_title"] = team_data["title"]
            # Flatten 'ppda' and 'ppda_allowed' dictionaries
            row["ppda_att"] = row["ppda"]["att"]
            row["ppda_def"] = row["ppda"]["def"]
            row["ppda_allowed_att"] = row["ppda_allowed"]["att"]
            row["ppda_allowed_def"] = row["ppda_allowed"]["def"]
            del row["ppda"], row["ppda_allowed"]
            rows.append(row)

    df = pd.DataFrame(rows)
    t_df_agg = df.groupby("team_title").sum()
    t_df_agg.drop(["h_a", "result", "date"], inplace=True, axis=1)
    t_df_agg["games_played"] = t_df_agg["wins"] + t_df_agg["draws"] + t_df_agg["loses"]
    t_df_agg["team_id"] = t_df_agg["team_id"].str[0:3]
    return t_df_agg


def flatten_dict(d, parent_key="", sep="_"):
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def transform_team_df(df, team_id):
    df["datetime"] = pd.to_datetime(df["datetime"])

    # Filter out rows where datetime is greater than yesterday
    yesterday = datetime.now() - timedelta(days=1)
    df = df[df["datetime"] <= yesterday]

    def extract_data(row):
        safe_int = lambda x: int(x) if x is not None and x != "" else 0
        safe_float = lambda x: float(x) if x is not None and x != "" else 0.0

        is_home = row["team"] == "home"
        # Extract team name and playground
        team_name = row["h"]["title"] if is_home else row["a"]["title"]
        playground = "home" if is_home else "away"
        # Check if 'a', 'h', 'goals', 'xG', 'forecast' are dictionaries
        opponent = (
            row["a"]["title"]
            if is_home and isinstance(row["a"], dict)
            else row["h"]["title"]
            if isinstance(row["h"], dict)
            else "Unknown"
        )
        goals = (
            safe_int(row["goals"]["h"])
            if is_home and isinstance(row["goals"], dict)
            else safe_int(row["goals"]["a"])
            if isinstance(row["goals"], dict)
            else 0
        )
        goals_against = (
            safe_int(row["goals"]["a"])
            if is_home and isinstance(row["goals"], dict)
            else safe_int(row["goals"]["h"])
            if isinstance(row["goals"], dict)
            else 0
        )
        xG = (
            safe_float(row["xG"]["h"])
            if is_home and isinstance(row["xG"], dict)
            else safe_float(row["xG"]["a"])
            if isinstance(row["xG"], dict)
            else 0.0
        )
        xGA = (
            safe_float(row["xG"]["a"])
            if is_home and isinstance(row["xG"], dict)
            else safe_float(row["xG"]["h"])
            if isinstance(row["xG"], dict)
            else 0.0
        )
        win_prob = (
            safe_float(row["forecast"]["w"])
            if isinstance(row["forecast"], dict)
            else 0.0
        )
        draw_prob = (
            safe_float(row["forecast"]["d"])
            if isinstance(row["forecast"], dict)
            else 0.0
        )
        lose_prob = (
            safe_float(row["forecast"]["l"])
            if isinstance(row["forecast"], dict)
            else 0.0
        )

        return (
            team_name,
            playground,
            opponent,
            goals,
            goals_against,
            xG,
            xGA,
            win_prob,
            draw_prob,
            lose_prob,
        )

    transformed_data = df.apply(extract_data, axis=1)
    new_df = pd.DataFrame(
        transformed_data.tolist(),
        columns=[
            "Team",
            "played",
            "Opponent",
            "goals",
            "goals_against",
            "xG",
            "xGA",
            "home_win_probability",
            "draw_probability",
            "away_win_probability",
        ],
    )
    return new_df


def get_match_info(season: str, league="Bundesliga", understat_client=us):
    team_data = {}
    data = us.league(league).get_match_data(season)
    for match in data:
        # Process for home team
        home_id = match["h"]["id"]
        if home_id not in team_data:
            team_data[home_id] = []
        team_data[home_id].append({**match, "team": "home"})

        # Process for away team
        away_id = match["a"]["id"]
        if away_id not in team_data:
            team_data[away_id] = []
        team_data[away_id].append({**match, "team": "away"})

    # Create DataFrames for each team
    team_dfs = {}
    for team_id, matches in team_data.items():
        df = pd.DataFrame(matches)
        team_dfs[team_id] = transform_team_df(df, team_id)

    return team_dfs


def get_player_info(season: str, league="Bundesliga", understat_client=us):
    temp = us.league(league).get_player_data(season)
    return pd.DataFrame(temp)


def run_player(us):
    c = 0
    for i in range(2017, 2024):
        season = str(i)
        temp = get_player_info(season, understat_client=us)
        temp["season"] = season
        if c == 0:
            df_us_player = temp
        else:
            df_us_player = pd.concat([df_us_player, temp])
        c += 1

    df_us_player.drop(
        columns=[
            "id",
            "goals",
            "shots",
            "assists",
            "red_cards",
            "yellow_cards",
            "npg",
            "position",
            "time",
        ],
        inplace=True,
    )
    return df_us_player


def run_team(us):
    c = 0
    for i in range(2017, 2024):
        season = str(i)
        temp = get_team_info(season, understat_client=us)
        temp["season"] = season
        if c == 0:
            df_us_team = temp
        else:
            df_us_team = pd.concat([df_us_team, temp])
        c += 1
    return df_us_team


if __name__ == "__main__":
    df_us_player = run_player(us)
    df_us_team = run_team(us)

    df_us_player.to_csv("../data/df_us_player.csv")
    df_us_team.to_csv("../data/df_us_team.csv")
