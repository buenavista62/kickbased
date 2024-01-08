import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit import session_state as ss
import functions as fn
from preprocessing import models
import pickle
import numpy as np
import mappings as mp


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
    st.title("Vorhersage der Spielerpunkte")

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


if __name__ == "__main__":
    main()
