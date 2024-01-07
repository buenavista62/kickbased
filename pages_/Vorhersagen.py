import streamlit as st
from streamlit import session_state as ss
import functions as fn
import pandas as pd
import pickle
from preprocessing import models
import time

if "predicted_df" not in ss:
    my_bar = st.progress(0, text="Daten werden vorbereitet")
    ss.df_kb_point_hist = fn.get_points_history(ss.players)
    my_bar.progress(5, text="Daten werden vorbereitet")
    ss.df_us_player = pd.read_csv("./data/df_us_player.csv")
    my_bar.progress(10, text="Daten werden vorbereitet")

    ss.predict_data = fn.prepare_pred_page(
        ss.df_kb_point_hist, ss.df_us_player, df_kb=ss.kb_data
    )
    my_bar.progress(20, text="Vorhersagemodell wird initialisiert")

    # Load the model and columns for prediction
    @st.cache_resource
    def load_model():
        with open("./preprocessing/model.pkl", "rb") as file:
            model = pickle.load(file)
        with open("./preprocessing/cols_for_predict.pkl", "rb") as file:
            cols_for_predict = pickle.load(file)
        with open("./preprocessing/scaler.pkl", "rb") as file:
            scaler = pickle.load(file)
        return model, cols_for_predict, scaler

    my_bar.progress(25, text="Vorhersagemodell wird initialisiert")

    model, cols_for_predict, scaler = load_model()
    my_bar.progress(35, text="Vorhersagemodell wird angewendet")

    # Use the model for prediction

    ss.predicted_df = models.predict_ml_player(
        ss.predict_data, model, cols_for_predict, scaler
    )
    my_bar.progress(70, text="Vorhersagemodell wird angewendet")
    kb_join = ss.kb_data.loc[:, ["Name", "Team", "ID"]]
    my_bar.progress(90, text="Letzter Schliff...")
    ss.predicted_df = ss.predicted_df.merge(kb_join, on="ID")
    ss.predicted_df = ss.predicted_df[["Name", "Team", "Points", "prediction"]]
    my_bar.progress(100, text="Fertig!")
    time.sleep(3)
    my_bar.empty()

ss.predicted_df
