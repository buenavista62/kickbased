import pandas as pd
from unidecode import unidecode


def merge():
    fbref_pd = pd.read_csv("./data/fbref_full.csv")
    li_pd = pd.read_csv("./data/li_pd.csv")

    df = li_pd.merge(
        fbref_pd,
        how="left",
        left_on=["Name", "Born"],
        right_on=["player", "birth_year"],
    )
    df.drop(
        [
            "player",
            "birth_year",
            "matches",
            "position",
            "team",
            "age",
            "games",
            "matches",
        ],
        axis=1,
        inplace=True,
    )

    df.drop(
        [
            "gk_psxg_net_per90",
            "gk_free_kick_goals_against",
            "gk_crosses",
            "gk_own_goals_against",
            "gk_corner_kick_goals_against",
            "gk_goal_kicks",
            "gk_passes_launched",
            "gk_passes",
            "gk_passes_throws",
            "gk_crosses_stopped",
            "gk_def_actions_outside_pen_area_per90",
            "gk_passes_completed_launched",
            "gk_psxg",
            "gk_goal_kick_length_avg",
            "gk_def_actions_outside_pen_area",
        ],
        axis=1,
        inplace=True,
    )

    df.drop(
        [
            "take_ons_tackled",
            "carries",
            "shots",
            "shots_on_target",
            "goals_per_shot_on_target",
            "average_shot_distance",
            "shots_free_kicks",
            "pens_made",
            "pens_att",
        ],
        axis=1,
        inplace=True,
    )

    df.drop(
        [
            "take_ons_won",
            "passes_completed",
            "passes",
            "passes_total_distance",
            "passes_progressive_distance",
            "passes_completed_short",
            "passes_short",
            "passes_completed_medium",
            "passes_medium",
            "passes_completed_long",
            "passes_long",
            "pass_xa",
            "assisted_shots",
            "passes_into_final_third",
            "passes_into_penalty_area",
            "crosses_into_penalty_area",
            "progressive_passes",
        ],
        axis=1,
        inplace=True,
    )

    df.drop(
        [
            "sca",
            "sca_passes_live",
            "sca_passes_dead",
            "sca_take_ons",
            "sca_shots",
            "sca_fouled",
            "sca_defense",
            "gca",
            "gca_passes_live",
            "gca_passes_dead",
            "gca_take_ons",
            "gca_shots",
            "gca_fouled",
            "gca_defense",
        ],
        axis=1,
        inplace=True,
    )

    df.drop(
        [
            "tackles",
            "tackles_won",
            "tackles_def_3rd",
            "tackles_mid_3rd",
            "tackles_att_3rd",
            "challenge_tackles",
            "challenges_lost",
            "blocked_passes",
            "tackles_interceptions",
        ],
        axis=1,
        inplace=True,
    )

    df.drop(
        [
            "touches",
            "touches_def_pen_area",
            "touches_def_3rd",
            "touches_mid_3rd",
            "touches_att_3rd",
            "touches_att_pen_area",
            "touches_live_ball",
            "take_ons",
        ],
        axis=1,
        inplace=True,
    )
    df.fillna(0, inplace=True)

    df.drop_duplicates(inplace=True, subset=["Name", "Value"])

    df.drop(df[df.Value == "-"].index, inplace=True)
    df.reset_index(inplace=True)
    df.to_csv("./data/full_df.csv", index=False)
