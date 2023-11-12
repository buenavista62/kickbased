import streamlit as st
from kickbase_singleton import kickbase_singleton
import pandas as pd

if "logged" not in st.session_state or not st.session_state.logged:
    st.warning("Bitte zuerst anmelden!")
else:
    st.session_state.matches
