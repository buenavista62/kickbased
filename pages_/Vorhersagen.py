import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit import session_state as ss
import functions as fn
from preprocessing import models
import pickle


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
    ss.predicted_df = models.predict_ml_player(
        ss.predict_data, model, cols_for_predict, scaler
    )
    ss.predicted_df = ss.predicted_df.merge(ss.kb_data[["Name", "Team", "ID"]], on="ID")


def main():
    st.title("Player Points Prediction")

    if "predicted_df" not in ss:
        prepare_data()
        perform_prediction()

    # Filters
    team_filter = st.sidebar.multiselect(
        "Select Team", ss.predicted_df["Team"].unique()
    )
    filtered_data = (
        ss.predicted_df[ss.predicted_df["Team"].isin(team_filter)]
        if team_filter
        else ss.predicted_df
    )

    # Data Visualization
    fig = px.bar(
        filtered_data,
        x="Name",
        y="prediction",
        color="Team",
        hover_data=["Team", "prediction"],
    )
    st.plotly_chart(fig, use_container_width=True)

    # Detailed Player Statistics
    selected_player = st.sidebar.selectbox(
        "Select Player", filtered_data["Name"].unique()
    )
    player_stats = filtered_data[filtered_data["Name"] == selected_player]
    st.write(player_stats)


if __name__ == "__main__":
    main()
