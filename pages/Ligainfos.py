import streamlit as st
from kickbase_singleton import kickbase_singleton
import pandas as pd

if st.session_state.logged:
    if "matches" not in st.session_state:
        m = st.session_state.kb.matches()
        matches_df = pd.DataFrame(m)
        st.session_state.matches = pd.DataFrame(
            {
                "Match Time": pd.to_datetime(matches_df["d"]).dt.strftime(
                    "%Y-%m-%d %H:%M"
                ),
                "Home Team ID": matches_df["t1i"],
                "Home Team": matches_df["t1n"],
                "Home Team Abbreviation": matches_df["t1y"],
                "Home Team Score": matches_df["t1s"],
                "Away Team ID": matches_df["t2i"],
                "Away Team": matches_df["t2n"],
                "Away Team Abbreviation": matches_df["t2y"],
                "Away Team Score": matches_df["t2s"],
                "Matchday": matches_df["md"],
            }
        )
    st.session_state.matches
