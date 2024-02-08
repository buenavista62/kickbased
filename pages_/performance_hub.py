import pickle

import numpy as np
import pandas as pd
import streamlit as st
from streamlit import session_state as ss

import functions as fn
import mappings as mp
from preprocessing import models


@st.cache_resource
def load_model():
    with open("./preprocessing/model.pkl", "rb") as file:
        model = pickle.load(file)

    with open("./preprocessing/scaler.pkl", "rb") as file:
        scaler = pickle.load(file)
    return model, scaler


@st.cache_data
def load_model_ext():
    with open("./preprocessing/cols_for_predict.pkl", "rb") as file:
        cols_for_predict = pickle.load(file)
    return cols_for_predict


# Function to prepare data
def prepare_data():
    ss.df_kb_point_hist = fn.get_points_history(ss.players)
    ss.df_us_player = pd.read_csv("./data/df_us_player.csv")
    ss.predict_data = fn.prepare_pred_page(
        ss.df_kb_point_hist, ss.df_us_player, df_kb=ss.kb_data
    )


def perform_prediction():
    model, scaler = load_model()
    cols_for_predict = load_model_ext()
    cmd = ss.kb.get_current_md()
    ss.predict_data = ss.predict_data.loc[ss.predict_data.minutes >= 600 * cmd / 34]
    ss.predicted_df = models.predict_ml_player(
        ss.predict_data, model, cols_for_predict, scaler
    )
    ss.predicted_df.ID = ss.predicted_df.ID.astype("str")
    ss.kb_data.ID = ss.kb_data.ID.astype("str")
    ss.predicted_df.drop(columns=("Position"), inplace=True)
    ss.predicted_df = ss.predicted_df.merge(
        ss.kb_data[["Name", "Team", "ID", "Position", "Status"]], on="ID", how="right"
    )


@st.cache_resource
def load_team_model():
    with open("./preprocessing/team_model.pkl", "rb") as file:
        print("loading team_model")
        team_model = pickle.load(file)
    return team_model


@st.cache_data
def run_team_prediction():
    df = pd.read_csv("./data/df_us_team.csv")
    df = df.loc[df.season.astype("str") == "2023"]
    print("init teammodel")
    team_model = load_team_model()
    print("predicting teams")
    team_predicted = models.predict_ml_team(team_model, df)
    return team_predicted


def manipulate_data(predict_data):
    data = predict_data.copy()
    data["ppg"] = np.round(data.Points / data.games, 0)
    data["ppg_exp"] = np.round(data["ppg_exp"], 0)
    data["performance"] = data.ppg_exp - data.ppg
    data["prediction"] = np.round(data.prediction, 0)
    data.Position = data.Position.astype("str")
    data = data.loc[data.Position != "1"]
    data = data[
        [
            "Name",
            "Team",
            "Position",
            "Status",
            "Points",
            "prediction",
            "ppg",
            "ppg_exp",
            "performance",
        ]
    ]
    data.Position = data.Position.map(mp.position_mapping)
    data.Status = data.Status.map(mp.status_mapping)
    return data


def main():
    st.title("Performance Hub")
    tab1, tab2 = st.tabs(["Spieler", "Teams"])

    if "team_pred_df" not in ss:
        ss.team_pred_df = run_team_prediction()
    team_df_cols = {
        "all": ss.team_pred_df.columns,
        "relevant": ["pts", "prediction", "strength_score"],
    }

    with tab1:
        if "predicted_df" not in ss:
            prepare_data()
            perform_prediction()

        ss.player_predict_df = manipulate_data(ss.predicted_df)
        ss.ppdf_true = ss.player_predict_df.dropna()
        show_true = st.toggle("Zeige nur für die Vorhersage gültige Spieler an", True)
        if show_true:
            st.dataframe(
                ss.ppdf_true.style.background_gradient(
                    subset="performance", cmap="RdYlGn"
                ).format(precision=0),
                column_config={
                    "ppg": "PPS",
                    "ppg_exp": "xPPS",
                    "prediction": "xPunkte",
                    "Points": "Punkte",
                },
                hide_index=True,
            )
        else:
            st.dataframe(
                ss.player_predict_df.style.background_gradient(
                    subset="performance", cmap="RdYlGn"
                ),
                column_config={
                    "ppg": "PPS",
                    "ppg_exp": "xPPS",
                    "prediction": "xPunkte",
                    "Points": "Punkte",
                },
                hide_index=True,
            )
    with tab2:
        show_relevant = st.toggle("Zeige nur Hauptinfos an", True)
        if show_relevant:
            st.dataframe(
                ss.team_pred_df.loc[
                    :, team_df_cols["relevant"]
                ].style.background_gradient(subset="strength_score", cmap="RdYlGn")
            )
        else:
            st.dataframe(
                ss.team_pred_df.style.background_gradient(
                    subset="strength_score", cmap="RdYlGn"
                )
            )

            st.write("hello")


if __name__ == "__main__":
    main()
